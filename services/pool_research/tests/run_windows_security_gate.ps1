# Harmless Windows pool research gate: run isolated tests in fresh PowerShell processes.
# This is NOT an authorization to capture templates or wallet data.
param([Parameter(Mandatory=$true)][string]$PrivateFixtureDirectory)
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$tests = @(
  @{ Name='protected file handle ACL'; Script='test_windows_open_file_acl.ps1'; Args=@('-Directory',$PrivateFixtureDirectory) },
  @{ Name='inherited ACL rejection'; Script='test_windows_insecure_acl_rejection.ps1'; Args=@('-Verifier',(Join-Path $here 'test_windows_open_file_acl.ps1')) },
  @{ Name='unauthorized principal rejection'; Script='test_windows_unexpected_principal.ps1'; Args=@('-Verifier',(Join-Path $here 'test_windows_open_file_acl.ps1')) },
  @{ Name='native child ACL injection'; Script='test_nt_child_acl_injection.ps1'; Args=@('-Directory',$PrivateFixtureDirectory) },
  @{ Name='native post-create fault cleanup'; Script='test_nt_postcreate_cleanup.ps1'; Args=@('-Directory',$PrivateFixtureDirectory) },
  @{ Name='repeated same-path race diagnosis'; Script='test_nt_shared_race_repeat.ps1'; Args=@('-Runs','10') },
  @{ Name='forced rename and cleanup'; Script='test_nt_forced_rename_cleanup.ps1'; Args=@() }
)
$passed=0
foreach($test in $tests) {
  $path=Join-Path $here $test.Script
  if(-not (Test-Path -LiteralPath $path -PathType Leaf)) {throw "Missing test: $($test.Script)"}
  $output=@(& powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $path @($test.Args) 2>&1)
  if($LASTEXITCODE -ne 0) {
    $output | ForEach-Object {Write-Output "$_"}
    throw "FAILED: $($test.Name) (exit $LASTEXITCODE)"
  }
  if(-not @($output | Where-Object { "$_" -match '^PASS:' }).Count) {
    throw "No PASS marker from $($test.Name)"
  }
  Write-Output "PASS suite: $($test.Name)"
  $passed++
}
Write-Output "PASS: $passed/$($tests.Count) Windows pool research checks"
