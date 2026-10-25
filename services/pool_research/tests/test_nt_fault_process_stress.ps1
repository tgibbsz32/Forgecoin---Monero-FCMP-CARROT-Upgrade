param([Parameter(Mandatory=$true)][string]$Directory,[int]$Iterations=12)
$ErrorActionPreference='Stop'
if($Iterations -lt 3 -or $Iterations -gt 50){throw 'Iterations out of safe bound'}
$target=Join-Path $PSScriptRoot 'test_nt_native_error_fault_matrix.ps1'
if(!(Test-Path -LiteralPath $target)){throw 'Missing fault matrix'}
$before=@(Get-ChildItem -LiteralPath $Directory -Force | Select-Object -ExpandProperty Name)
$peak=0L
for($i=1;$i -le $Iterations;$i++){
  $p=Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',('"' + $target + '"'),'-Directory',('"' + $Directory + '"')) -PassThru -Wait -WindowStyle Hidden
  if($p.ExitCode -ne 0){throw "Fault iteration $i exited $($p.ExitCode)"}
  $peak=[Math]::Max($peak,[long]$p.PeakWorkingSet64)
  $after=@(Get-ChildItem -LiteralPath $Directory -Force | Where-Object {$_.Name -notin $before})
  if($after.Count){throw "Orphan files on iteration $i"}
}
Write-Output "PASS: $Iterations isolated fault-matrix processes exited cleanly with no orphan files"
Write-Output "INFO: peak observed child working set bytes $peak; process-exit cleanup only, not a same-process handle leak proof"
