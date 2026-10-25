# Research-only native NT directory-handle-relative file creation proof.
# Writes only fixed harmless probe bytes. Not wired to wallet/template capture.
param([Parameter(Mandatory=$true)][string]$Directory)
$ErrorActionPreference = 'Stop'
Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Security.AccessControl;
using System.Security.Principal;
using System.Text;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
public static class NtRootProbe {
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
      string me=WindowsIdentity.GetCurrent().User.Value;
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
  public static string Run(string directory) {
    using(var parent=CreateFileW(directory,0x80000000,7,IntPtr.Zero,3,
      0x02000000 | 0x00200000, IntPtr.Zero)) {
      if(parent.IsInvalid) throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
      CheckParent(parent);
      string name="nt-probe-"+Guid.NewGuid().ToString("N")+".txt";
      IntPtr namePtr=Marshal.StringToHGlobalUni(name);
      IntPtr structPtr=IntPtr.Zero;
      try {
        UNICODE_STRING uni=new UNICODE_STRING();
        uni.Length=(ushort)(name.Length*2); uni.MaximumLength=(ushort)(uni.Length+2);
        uni.Buffer=namePtr;
        structPtr=Marshal.AllocHGlobal(Marshal.SizeOf(typeof(UNICODE_STRING)));
        Marshal.StructureToPtr(uni,structPtr,false);
        OBJECT_ATTRIBUTES attrs=new OBJECT_ATTRIBUTES();
        attrs.Length=Marshal.SizeOf(typeof(OBJECT_ATTRIBUTES));
        attrs.RootDirectory=parent.DangerousGetHandle();
        attrs.ObjectName=structPtr; attrs.Attributes=0x40;
        IO_STATUS_BLOCK ios=new IO_STATUS_BLOCK();
        SafeFileHandle child;
        int result=NtCreateFile(out child,0xC0000000|0x00020000|0x00100000,
          ref attrs,ref ios,IntPtr.Zero,0x80,0,2,0x40|0x20|0x00200000,IntPtr.Zero,0);
        if(result!=0) throw new InvalidOperationException("NtCreateFile NTSTATUS 0x"+result.ToString("X8"));
        using(child) {
          var final=new StringBuilder(32768);
          uint n=GetFinalPathNameByHandleW(child,final,(uint)final.Capacity,0);
          if(n==0 || n>=final.Capacity) throw new InvalidOperationException("Could not resolve final handle");
          // Inspect the security descriptor from the already OPEN child handle.
          // This probe must remain zero-byte; do not use for real capture data.
          using(var stream=new FileStream(child,FileAccess.ReadWrite)) {
            var rules=stream.GetAccessControl().GetAccessRules(true,true,typeof(SecurityIdentifier));
            string current=WindowsIdentity.GetCurrent().User.Value;
            var permitted=new System.Collections.Generic.HashSet<string> {
              current,"S-1-5-18","S-1-5-32-544"
            };
            if(rules.Count!=3) throw new InvalidOperationException("Unexpected child ACL count");
            foreach(FileSystemAccessRule rule in rules) {
              string sid=((SecurityIdentifier)rule.IdentityReference).Value;
              if(!permitted.Contains(sid) || rule.AccessControlType!=AccessControlType.Allow)
                throw new InvalidOperationException("Unexpected child ACL principal");
            }
            if(stream.Length!=0) throw new InvalidOperationException("Unexpected probe contents");
          }
          return final.ToString();
        }
      } finally {
        if(structPtr!=IntPtr.Zero) Marshal.FreeHGlobal(structPtr);
        Marshal.FreeHGlobal(namePtr);
      }
    }
  }
}
'@
$dir=(Get-Item -LiteralPath $Directory -Force -ErrorAction Stop)
if(-not $dir.PSIsContainer -or (($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {throw "Invalid directory"}
$acl=Get-Acl -LiteralPath $dir.FullName
if(-not $acl.AreAccessRulesProtected) {throw "Directory must have protected ACL"}
$before=@(Get-ChildItem -LiteralPath $dir.FullName -Force | Select-Object -ExpandProperty Name)
$final=[NtRootProbe]::Run($dir.FullName)
$after=@(Get-ChildItem -LiteralPath $dir.FullName -Force | Where-Object {$_.Name -notin $before})
if($after.Count -ne 1) {throw "Unexpected number of probe files"}
try {
  $expected="\\?\$($after[0].FullName)"
  if(-not [string]::Equals($final,$expected,[StringComparison]::OrdinalIgnoreCase)) {
    throw "Final opened file path mismatch"
  }
  if($after[0].Length -ne 0) {throw "Probe unexpectedly nonempty"}
  Write-Output "PASS: parent handle security and child handle ACL verified in same NT operation"
} finally {
  if($after.Count -eq 1) {Remove-Item -LiteralPath $after[0].FullName -Force}
}
