param([Parameter(Mandatory=$true)][string]$Directory)
$ErrorActionPreference='Stop'
$test=Join-Path $PSScriptRoot "probe_nt_cleanup_fault.ps1"
$before=@(Get-ChildItem -LiteralPath $Directory -Force | Select-Object -ExpandProperty Name)
$caught=$null
try {
  & $test -Directory $Directory -InjectPostCreateFailure | Out-Null
} catch {
  $caught=$_.Exception.Message
}
if($caught -ne "INJECTED_POST_CREATE_FAILURE") {throw "Expected injected failure not observed"}
$after=@(Get-ChildItem -LiteralPath $Directory -Force | Select-Object -ExpandProperty Name)
if((Compare-Object $before $after).Count -ne 0) {throw "Orphan probe file detected"}
Write-Output "PASS: injected post-create failure leaves no probe file"
