# Research-only probe: verify resolved final file path through the open handle.
# This is NOT handle-relative creation and does not authorize private writes.
param([Parameter(Mandatory=$true)][string]$Directory)
$ErrorActionPreference="Stop"
Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
public static class FinalHandlePath {
  [DllImport("kernel32.dll", EntryPoint="GetFinalPathNameByHandleW", CharSet=CharSet.Unicode, SetLastError=true)]
  private static extern uint GetFinalPathNameByHandle(SafeFileHandle handle,
    StringBuilder name, uint capacity, uint flags);
  public static string Get(SafeFileHandle handle) {
    var result=new StringBuilder(32768);
    uint count=GetFinalPathNameByHandle(handle,result,(uint)result.Capacity,0);
    if(count==0 || count>=result.Capacity) throw new System.ComponentModel.Win32Exception(
      Marshal.GetLastWin32Error());
    return result.ToString();
  }
}
'@
$dir=Get-Item -LiteralPath $Directory -Force -ErrorAction Stop
if(-not $dir.PSIsContainer -or (($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
  throw "Invalid directory"
}
$acl=Get-Acl -LiteralPath $dir.FullName
if(-not $acl.AreAccessRulesProtected) {throw "Directory ACL is not protected"}
$path=Join-Path $dir.FullName ("identity-"+[guid]::NewGuid().ToString("N")+".txt")
$stream=$null
try {
  $stream=New-Object IO.FileStream($path,[IO.FileMode]::CreateNew,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
  $final=[FinalHandlePath]::Get($stream.SafeFileHandle)
  $expected="\\?\$([IO.Path]::GetFullPath($path))"
  if(-not [string]::Equals($final,$expected,[StringComparison]::OrdinalIgnoreCase)) {
    throw "Opened handle resolves to unexpected file path"
  }
  Write-Output "PASS: opened harmless file handle resolves to expected path"
} finally {
  if($stream) {$stream.Dispose()}
  if([IO.File]::Exists($path)) {[IO.File]::Delete($path)}
}
