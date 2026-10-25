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
$proc=[Diagnostics.Process]::GetCurrentProcess()
function RunBatch([int]$count) {
  for($i=0;$i -lt $count;$i++) {
    foreach($fault in @('parent','precreate','postcreate','native_error','name_allocated','struct_allocated','sd_allocated','child_open','stream_open')) {
      $expected=switch($fault) { 'parent' {'INJECTED_PARENT_FAULT'} 'precreate' {'INJECTED_PRECREATE_FAULT'} 'postcreate' {'INJECTED_POST_CREATE_FAILURE'} 'native_error' {'EXPECTED_NATIVE_ERROR_NTSTATUS_0xC000003B'} default {'INJECTED_'+$fault.ToUpperInvariant()} }
      try { [NtOwnershipProbe]::Run($dir.FullName,$fault); throw 'Missing injected error' }
      catch { if($_.Exception.GetBaseException().Message -cne $expected){throw} }
    }
  }
  $remaining=@(Get-ChildItem -LiteralPath $dir.FullName -Force | Where-Object {$_.Name -notin $before})
  if($remaining.Count){throw "Unexpected files: $($remaining.Count)"}
}
function Snapshot([string]$label) {
  [GC]::Collect(); [GC]::WaitForPendingFinalizers(); [GC]::Collect()
  $proc.Refresh()
  Write-Output "MEASURE $label handles=$($proc.HandleCount) privateBytes=$($proc.PrivateMemorySize64)"
}
RunBatch 15
Snapshot 'warmed'
RunBatch 200
Snapshot 'middle'
RunBatch 200
Snapshot 'end'
Write-Output 'PASS: 3735 native fault operations across warm-up and two measured phases; zero orphan files'
