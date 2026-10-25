# Bounded parallel regression of NT root-handle-relative rename/create.
# Each worker uses its own GUID disposable directory. No sensitive content.
param([int]$Workers=4,[int]$Rounds=3)
$ErrorActionPreference='Stop'
if($Workers -lt 1 -or $Workers -gt 8 -or $Rounds -lt 1 -or $Rounds -gt 10){
  throw "Workers must be 1-8 and Rounds 1-10"
}
$probe=Join-Path $PSScriptRoot 'test_nt_root_rename_create.ps1'
if(-not (Test-Path -LiteralPath $probe)){throw "Missing probe"}
for($round=1;$round -le $Rounds;$round++){
  $jobs=@()
  try{
    for($i=0;$i -lt $Workers;$i++){
      $jobs+=Start-Job -ArgumentList $probe -ScriptBlock {
        param($path)
        $ErrorActionPreference='Stop'
        & $path
      }
    }
    foreach($job in $jobs){
      $null=Wait-Job $job -Timeout 45
      if($job.State -ne 'Completed'){throw "Parallel worker failed: $($job.State)"}
      $outputs=@(Receive-Job $job -ErrorAction Stop)
      if(@($outputs | Where-Object {$_ -like 'PASS:*'}).Count -ne 1){
        throw "Worker did not report successful isolated handle-relative create"
      }
    }
  } finally {
    foreach($job in $jobs){if($job.State -eq 'Running'){Stop-Job $job};Remove-Job $job -Force}
  }
}
Write-Output "PASS: $($Workers*$Rounds) parallel-worker runs across $Rounds rounds"
