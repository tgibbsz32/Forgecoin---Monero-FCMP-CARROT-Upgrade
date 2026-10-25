# Research-only native NT directory-handle-relative file creation proof.
# Writes only fixed harmless probe bytes. Not wired to wallet/template capture.

$ErrorActionPreference = 'Stop'
Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Security.AccessControl;
using System.Security.Principal;
using System.Text;
using System.Threading.Tasks;
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
  public static string Run(string directory) {
    using(var parent=CreateFileW(directory,0x80000000,7,IntPtr.Zero,3,
      0x02000000 | 0x00200000, IntPtr.Zero)) {
      if(parent.IsInvalid) throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
      // Deliberately rename a disposable directory while its handle is pinned.
      string relocated=directory+"-relocated";
      Task renamer=Task.Run(() => { Directory.Move(directory,relocated); Directory.CreateDirectory(directory); });
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
          ref attrs,ref ios,IntPtr.Zero,0x80,7,2,0x40|0x20|0x00200000,IntPtr.Zero,0);
        if(result!=0) throw new InvalidOperationException("NtCreateFile NTSTATUS 0x"+result.ToString("X8"));
        renamer.GetAwaiter().GetResult();
        using(child) {
          var final=new StringBuilder(32768);
          uint n=GetFinalPathNameByHandleW(child,final,(uint)final.Capacity,0);
          if(n==0 || n>=final.Capacity) throw new InvalidOperationException("Could not resolve final handle");
          // Routing-only probe: no content written; ACL tested separately.
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
$ErrorActionPreference='Stop'
$root=Join-Path $env:TEMP ("frg-nt-root-swap-"+[guid]::NewGuid().ToString("N"))
$original=Join-Path $root "original"
$relocated=$original+"-relocated"
[IO.Directory]::CreateDirectory($original) | Out-Null
$created=$null
try {
  $final=[NtRootProbe]::Run($original)
  $files=@(Get-ChildItem -LiteralPath $relocated -File -Force)
  if ($files.Count -ne 1) {throw "File did not appear in relocated original"}
  if (@(Get-ChildItem -LiteralPath $original -Force).Count -ne 0) {
    throw "A file appeared in the replacement directory"
  }
  if (-not $final.EndsWith($files[0].FullName,[StringComparison]::OrdinalIgnoreCase)) {throw "Opened child not in original directory"}
  $created=$files[0].FullName
  Write-Output "PASS: concurrent renamer and NT root-relative create retained original directory"
} finally {
  if($created -and [IO.File]::Exists($created)) {[IO.File]::Delete($created)}
  if([IO.Directory]::Exists($original) -and @([IO.Directory]::GetFileSystemEntries($original)).Count -eq 0) {
    [IO.Directory]::Delete($original)
  }
  if([IO.Directory]::Exists($relocated) -and @([IO.Directory]::GetFileSystemEntries($relocated)).Count -eq 0) {
    [IO.Directory]::Delete($relocated)
  }
  if([IO.Directory]::Exists($root) -and @([IO.Directory]::GetFileSystemEntries($root)).Count -eq 0) {
    [IO.Directory]::Delete($root)
  }
}
