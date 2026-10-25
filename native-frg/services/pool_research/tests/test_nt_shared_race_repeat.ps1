# Bounded repeat runs of diagnostic NT rename/create race.
# No sensitive input; each iteration uses a disposable GUID path.
param([int]$Runs=20)
$ErrorActionPreference='Stop'
if($Runs -lt 1 -or $Runs -gt 100){throw 'Runs must be between 1 and 100'}
$probe=Join-Path $PSScriptRoot 'test_nt_shared_path_race_diagnostic.ps1'
$counts=@{DENIED=0;RENAMED=0}
for($i=0;$i -lt $Runs;$i++){
  $result=@(& $probe)
  $pass=@($result | Where-Object {$_ -match '^PASS: (DENIED|RENAMED); NT child stayed with original object$'})
  if($pass.Count -ne 1){throw "Unexpected run $($i+1) output"}
  $outcome=([regex]::Match($pass[0],'^PASS: (DENIED|RENAMED);')).Groups[1].Value
  $counts[$outcome]++
}
Write-Output "PASS: $Runs diagnostic runs; denied=$($counts.DENIED), renamed=$($counts.RENAMED)"
