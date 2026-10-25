// Research only: zero-byte disposable files; never a capture writer.
using System;
using System.IO;
using System.Security.AccessControl;
using System.Security.Principal;
using System.Text;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
// Internal test seam: callers cannot substitute an allocator through Run.
internal interface IProbeAllocator {
  IntPtr Allocate(int bytes);
  void Free(IntPtr pointer);
}
internal sealed class HGlobalProbeAllocator : IProbeAllocator {
  public IntPtr Allocate(int bytes) { return Marshal.AllocHGlobal(bytes); }
  public void Free(IntPtr pointer) { Marshal.FreeHGlobal(pointer); }
}
public static class NtOwnershipProbe {
  [StructLayout(LayoutKind.Sequential)] struct UNICODE_STRING {
    public ushort Length; public ushort MaximumLength; public IntPtr Buffer;
  }
  [StructLayout(LayoutKind.Sequential)] struct OBJECT_ATTRIBUTES {
    public int Length; public IntPtr RootDirectory; public IntPtr ObjectName;
    public uint Attributes; public IntPtr SecurityDescriptor; public IntPtr SecurityQualityOfService;
  }
  [StructLayout(LayoutKind.Sequential)] struct IO_STATUS_BLOCK {
    public IntPtr Status; public IntPtr Information;
  }
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  private static extern SafeFileHandle CreateFileW(string name, uint access, uint share,
    IntPtr security, uint disposition, uint flags, IntPtr template);
  [DllImport("ntdll.dll", ExactSpelling=true)]
  private static extern int NtCreateFile(out SafeFileHandle handle, uint desired,
    ref OBJECT_ATTRIBUTES attrs, ref IO_STATUS_BLOCK status, IntPtr allocation,
    uint fileAttributes, uint share, uint disposition, uint options, IntPtr ea, uint eaLength);
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  private static extern uint GetFinalPathNameByHandleW(SafeFileHandle handle,
    StringBuilder target, uint length, uint flags);
  [DllImport("advapi32.dll",SetLastError=true)] static extern uint GetSecurityInfo(SafeFileHandle h,uint type,uint flags,out IntPtr owner,out IntPtr group,out IntPtr dacl,out IntPtr sacl,out IntPtr sd);
  [DllImport("advapi32.dll")] static extern uint GetSecurityDescriptorLength(IntPtr sd);
  [DllImport("kernel32.dll")] static extern IntPtr LocalFree(IntPtr ptr);
  // Each WindowsIdentity owns a token handle; do not defer it to finalization.
  static string CurrentSid() {
    using(var identity=WindowsIdentity.GetCurrent()) { return identity.User.Value; }
  }
  static void Inject(string fault, string point) {
    if(fault==point) throw new InvalidOperationException("INJECTED_"+point.ToUpperInvariant());
  }
  static void CheckParent(SafeFileHandle handle) {
    IntPtr o,g,d,s,sd;
    uint status=GetSecurityInfo(handle,1,5,out o,out g,out d,out s,out sd);
    if(status!=0) throw new InvalidOperationException("Parent GetSecurityInfo "+status);
    try {
      uint length=GetSecurityDescriptorLength(sd);
      if(length==0||length>65536) throw new InvalidOperationException("Invalid parent SD");
      byte[] raw=new byte[(int)length]; Marshal.Copy(sd,raw,0,(int)length);
      var parsed=new RawSecurityDescriptor(raw,0);
      if((parsed.ControlFlags & ControlFlags.DiscretionaryAclProtected)==0 || parsed.DiscretionaryAcl==null)
        throw new InvalidOperationException("Unprotected or null parent DACL");
      string me=CurrentSid();
      var expected=new System.Collections.Generic.HashSet<string>(StringComparer.OrdinalIgnoreCase){me,"S-1-5-18","S-1-5-32-544"};
      if(parsed.Owner==null || !expected.Contains(parsed.Owner.Value)) throw new InvalidOperationException("Invalid parent owner");
      var seen=new System.Collections.Generic.HashSet<string>(StringComparer.OrdinalIgnoreCase);
      foreach(GenericAce entry in parsed.DiscretionaryAcl) {
        var ace=entry as CommonAce;
        if(ace==null||ace.AceQualifier!=AceQualifier.AccessAllowed||ace.IsInherited||!expected.Contains(ace.SecurityIdentifier.Value))
          throw new InvalidOperationException("Unexpected parent ACL entry");
        if((ace.AccessMask & 0x20002)!=0x20002) throw new InvalidOperationException("Insufficient parent rights");
        seen.Add(ace.SecurityIdentifier.Value);
      }
      if(seen.Count!=3) throw new InvalidOperationException("Missing parent principal");
    } finally {LocalFree(sd);}
  }
  public static void Run(string directory,string fault) {
    RunWithAllocator(directory,fault,new HGlobalProbeAllocator());
  }
  internal static void RunWithAllocator(string directory,string fault,IProbeAllocator allocator) {
    using(var parent=CreateFileW(directory,0x80000000,7,IntPtr.Zero,3,
      0x02000000 | 0x00200000, IntPtr.Zero)) {
      if(parent.IsInvalid) throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
      CheckParent(parent);
      if(fault=="parent") throw new InvalidOperationException("INJECTED_PARENT_FAULT");
      string name="nt-probe-"+Guid.NewGuid().ToString("N")+".txt";
      IntPtr namePtr=IntPtr.Zero;
      IntPtr structPtr=IntPtr.Zero;
      IntPtr sdPtr=IntPtr.Zero;
      SafeFileHandle child=null;
      try {
        byte[] nameBytes=Encoding.Unicode.GetBytes(name+"\0");
        namePtr=allocator.Allocate(nameBytes.Length);
        Inject(fault,"name_allocated");
        Marshal.Copy(nameBytes,0,namePtr,nameBytes.Length);
        UNICODE_STRING uni=new UNICODE_STRING();
        uni.Length=(ushort)(name.Length*2); uni.MaximumLength=(ushort)(uni.Length+2);
        uni.Buffer=namePtr;
        structPtr=allocator.Allocate(Marshal.SizeOf(typeof(UNICODE_STRING)));
        Inject(fault,"struct_allocated");
        Marshal.StructureToPtr(uni,structPtr,false);
        OBJECT_ATTRIBUTES attrs=new OBJECT_ATTRIBUTES();
        attrs.Length=Marshal.SizeOf(typeof(OBJECT_ATTRIBUTES));
        attrs.RootDirectory=parent.DangerousGetHandle();
        attrs.ObjectName=structPtr; attrs.Attributes=0x40;
        string me=CurrentSid();
        var descriptor=new RawSecurityDescriptor("O:"+me+"G:SYD:P(A;;FA;;;"+me+")(A;;FA;;;SY)(A;;FA;;;BA)");
        byte[] sdBytes=new byte[descriptor.BinaryLength];
        descriptor.GetBinaryForm(sdBytes,0);
        sdPtr=allocator.Allocate(sdBytes.Length);
        Inject(fault,"sd_allocated");
        Marshal.Copy(sdBytes,0,sdPtr,sdBytes.Length);
        attrs.SecurityDescriptor=sdPtr;
        if(fault=="precreate") throw new InvalidOperationException("INJECTED_PRECREATE_FAULT");
        if(fault=="native_error") attrs.RootDirectory=IntPtr.Zero;
        IO_STATUS_BLOCK ios=new IO_STATUS_BLOCK();
        int result=NtCreateFile(out child,0xC0000000|0x00020000|0x00100000|0x00010000,
          ref attrs,ref ios,IntPtr.Zero,0x80,0,2,0x40|0x20|0x00200000|0x00001000,IntPtr.Zero,0);
        if(result!=0) {
          if(fault=="native_error") throw new InvalidOperationException("EXPECTED_NATIVE_ERROR_NTSTATUS_0x"+result.ToString("X8"));
          throw new InvalidOperationException("NtCreateFile NTSTATUS 0x"+result.ToString("X8"));
        }
        // The outer finally owns child from the P/Invoke onward, including
        // status rejection and exceptions before FileStream takes ownership.
        {
          Inject(fault,"child_open");
          var final=new StringBuilder(32768);
          uint n=GetFinalPathNameByHandleW(child,final,(uint)final.Capacity,0);
          if(n==0 || n>=final.Capacity) throw new InvalidOperationException("Could not resolve final handle");
          // Inspect the security descriptor from the already OPEN child handle.
          // This probe must remain zero-byte; do not use for real capture data.
          using(var stream=new FileStream(child,FileAccess.ReadWrite)) {
            Inject(fault,"stream_open");
            var security=stream.GetAccessControl();
            var owner=(SecurityIdentifier)security.GetOwner(typeof(SecurityIdentifier));
            var rules=security.GetAccessRules(true,true,typeof(SecurityIdentifier));
            string current=CurrentSid();
            var permitted=new System.Collections.Generic.HashSet<string> {
              current,"S-1-5-18","S-1-5-32-544"
            };
            if(owner==null || !permitted.Contains(owner.Value)) throw new InvalidOperationException("Unexpected child owner");
            if(!security.AreAccessRulesProtected) throw new InvalidOperationException("Child ACL not protected");
            if(rules.Count!=3) throw new InvalidOperationException("Unexpected child ACL count");
            foreach(FileSystemAccessRule rule in rules) {
              string sid=((SecurityIdentifier)rule.IdentityReference).Value;
              if(!permitted.Contains(sid) || rule.AccessControlType!=AccessControlType.Allow || rule.IsInherited ||
                 (rule.FileSystemRights & (FileSystemRights.ReadPermissions|FileSystemRights.WriteData))!=(FileSystemRights.ReadPermissions|FileSystemRights.WriteData))
                throw new InvalidOperationException("Unexpected child ACL principal");
            }
            if(stream.Length!=0) throw new InvalidOperationException("Unexpected probe contents");
          }
          if(fault=="postcreate") throw new InvalidOperationException("INJECTED_POST_CREATE_FAILURE");
        }
      } finally {
        // FileStream also disposes this SafeFileHandle on success; Dispose is
        // idempotent, and this covers failure before stream construction too.
        if(child!=null) child.Dispose();
        if(sdPtr!=IntPtr.Zero) allocator.Free(sdPtr);
        if(structPtr!=IntPtr.Zero) allocator.Free(structPtr);
        if(namePtr!=IntPtr.Zero) allocator.Free(namePtr);
      }
    }
  }
}
