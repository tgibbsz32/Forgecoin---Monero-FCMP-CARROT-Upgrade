# Disposable path-replacement regression. Never run against a real capture path.
# Opens an ordinary empty test directory, renames it while the handle remains
# open, and demonstrates the handle still identifies the original directory.
$ErrorActionPreference = "Stop"
Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
public static class DirectoryIdentityProbe {
  [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)]
  public static extern SafeFileHandle CreateFileW(string path,uint access,uint share,
    IntPtr security,uint disposition,uint flags,IntPtr template);
  [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)]
  static extern uint GetFinalPathNameByHandleW(SafeFileHandle handle,
    StringBuilder buffer,uint size,uint flags);
  public static string FinalPath(SafeFileHandle handle) {
    var buffer=new StringBuilder(32768);
    uint size=GetFinalPathNameByHandleW(handle,buffer,(uint)buffer.Capacity,0);
    if(size==0 || size>=buffer.Capacity) throw new Exception("GetFinalPathNameByHandleW failed");
    return buffer.ToString();
  }
}
'@
$root=Join-Path $env:TEMP ("frg-handle-rename-"+[guid]::NewGuid().ToString("N"))
$old=Join-Path $root "original"
$moved=Join-Path $root "relocated"
[IO.Directory]::CreateDirectory($old) | Out-Null
$handle=$null
try {
  $handle=[DirectoryIdentityProbe]::CreateFileW($old,[uint32]2147483648,7,[IntPtr]::Zero,3,
      (0x02000000 -bor 0x00200000),[IntPtr]::Zero)
  if ($handle.IsInvalid) {throw "Cannot open test directory handle"}
  $before=[DirectoryIdentityProbe]::FinalPath($handle)
  [IO.Directory]::Move($old,$moved)
  [IO.Directory]::CreateDirectory($old) | Out-Null
  $after=[DirectoryIdentityProbe]::FinalPath($handle)
  $expected="\\?\$moved"
  if (-not [string]::Equals($after,$expected,[StringComparison]::OrdinalIgnoreCase)) {
    throw "Open directory handle did not follow relocated object"
  }
  if ([string]::Equals($after,"\\?\$old",[StringComparison]::OrdinalIgnoreCase)) {
    throw "Open handle unexpectedly resolves to replacement path"
  }
  Write-Output "PASS: open directory handle retained original object after pathname replacement"
} finally {
  if ($handle) {$handle.Dispose()}
  if ([IO.Directory]::Exists($old)) {[IO.Directory]::Delete($old)}
  if ([IO.Directory]::Exists($moved)) {[IO.Directory]::Delete($moved)}
  if ([IO.Directory]::Exists($root)) {[IO.Directory]::Delete($root)}
}
