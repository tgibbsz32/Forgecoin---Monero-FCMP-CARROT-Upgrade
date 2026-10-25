# Research-only native NT directory-handle-relative file creation proof.
# Creates only zero-byte disposable probe files. Not wired to wallet/template capture.
param([Parameter(Mandatory=$true)][string]$Directory)
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $PSScriptRoot 'NtOwnershipProbe.cs')
$dir=(Get-Item -LiteralPath $Directory -Force -ErrorAction Stop)
if(-not $dir.PSIsContainer -or (($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {throw "Invalid directory"}
$acl=Get-Acl -LiteralPath $dir.FullName
if(-not $acl.AreAccessRulesProtected) {throw "Directory must have protected ACL"}
$before=@(Get-ChildItem -LiteralPath $dir.FullName -Force | Select-Object -ExpandProperty Name)
foreach($fault in @('parent','precreate','postcreate','native_error','name_allocated','struct_allocated','sd_allocated','child_open','stream_open')) {
  $expected=switch($fault) { 'parent' {'INJECTED_PARENT_FAULT'} 'precreate' {'INJECTED_PRECREATE_FAULT'} 'postcreate' {'INJECTED_POST_CREATE_FAILURE'} 'native_error' {'EXPECTED_NATIVE_ERROR_NTSTATUS_0xC000003B'} default {'INJECTED_'+$fault.ToUpperInvariant()} }
  $caught=$false
  try {[NtOwnershipProbe]::Run($dir.FullName,$fault)|Out-Null} catch {if($_.Exception.GetBaseException().Message -cne $expected){throw}; $caught=$true}
  if(-not $caught){throw "Missing expected failure: $fault"}
  $after=@(Get-ChildItem -LiteralPath $dir.FullName -Force | Where-Object {$_.Name -notin $before})
  if($after.Count -ne 0){throw "Orphan files after $fault : $($after.Count)"}
  Write-Output "PASS: $fault injected, no leaked file"
}
# A successful zero-byte create must also close/delete without a forced GC.
[NtOwnershipProbe]::Run($dir.FullName,'success')
$after=@(Get-ChildItem -LiteralPath $dir.FullName -Force | Select-Object -ExpandProperty Name)
if (($before.Count -ne $after.Count) -or @($after | Where-Object {$_ -notin $before}).Count) {
  throw 'Successful probe changed directory entries'
}
Write-Output 'PASS: successful create, ACL validation and immediate cleanup'
