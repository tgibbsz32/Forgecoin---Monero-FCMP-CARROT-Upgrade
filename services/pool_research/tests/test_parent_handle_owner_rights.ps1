param([Parameter(Mandatory=$true)][string]$Directory)
$ErrorActionPreference='Stop'
Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.AccessControl;
using System.Security.Principal;
using Microsoft.Win32.SafeHandles;
public static class ParentHandleAclProbe {
  [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)]
  static extern SafeFileHandle CreateFileW(string path,uint access,uint share,IntPtr security,uint disposition,uint flags,IntPtr template);
  [DllImport("advapi32.dll",SetLastError=true)]
  static extern uint GetSecurityInfo(SafeFileHandle handle,uint objectType,uint securityInfo,
    out IntPtr owner,out IntPtr group,out IntPtr dacl,out IntPtr sacl,out IntPtr descriptor);
  [DllImport("advapi32.dll")]
  static extern uint GetSecurityDescriptorLength(IntPtr descriptor);
  [DllImport("kernel32.dll")]
  static extern IntPtr LocalFree(IntPtr ptr);
  public static void Check(string directory) {
    // READ_CONTROL requested to read the exact object opened, not a re-resolved path.
    using(var handle=CreateFileW(directory,0x00020000,7,IntPtr.Zero,3,0x02000000|0x00200000,IntPtr.Zero)) {
      if(handle.IsInvalid) throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
      IntPtr owner,group,dacl,sacl,sd;
      uint status=GetSecurityInfo(handle,1,0x00000001|0x00000004,out owner,out group,out dacl,out sacl,out sd);
      if(status!=0) throw new InvalidOperationException("GetSecurityInfo status "+status);
      try {
        if(sd==IntPtr.Zero) throw new InvalidOperationException("Missing descriptor");
        uint len=GetSecurityDescriptorLength(sd);
        if(len==0 || len>65536) throw new InvalidOperationException("Invalid security descriptor length");
        byte[] raw=new byte[(int)len];
        Marshal.Copy(sd,raw,0,(int)len);
        var parsed=new RawSecurityDescriptor(raw,0);
        if((parsed.ControlFlags & ControlFlags.DiscretionaryAclProtected)==0)
          throw new InvalidOperationException("Directory handle DACL not protected");
        if(parsed.DiscretionaryAcl==null) throw new InvalidOperationException("Null DACL");
        string me=WindowsIdentity.GetCurrent().User.Value;
        var allowed=new System.Collections.Generic.HashSet<string>(StringComparer.OrdinalIgnoreCase){me,"S-1-5-18","S-1-5-32-544"};
        if(parsed.Owner==null || !allowed.Contains(parsed.Owner.Value)) throw new InvalidOperationException("Unexpected directory owner");
        var found=new System.Collections.Generic.HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach(GenericAce entry in parsed.DiscretionaryAcl) {
          var ace=entry as CommonAce;
          if(ace==null || ace.AceQualifier!=AceQualifier.AccessAllowed || ace.IsInherited ||
             !allowed.Contains(ace.SecurityIdentifier.Value)) throw new InvalidOperationException("Unexpected handle ACL entry");
          // Require READ_CONTROL and FILE_ADD_FILE/FILE_WRITE_DATA on each approved ACE.
          const int required = 0x00020000 | 0x00000002;
          if((ace.AccessMask & required)!=required) throw new InvalidOperationException("Approved principal lacks required directory rights");
          found.Add(ace.SecurityIdentifier.Value);
        }
        if(found.Count!=3) throw new InvalidOperationException("Incomplete expected directory ACL");
      } finally {LocalFree(sd);}
    }
  }
}
'@
[ParentHandleAclProbe]::Check($Directory)
Write-Output 'PASS: parent handle DACL, owner, and required access masks verified'
