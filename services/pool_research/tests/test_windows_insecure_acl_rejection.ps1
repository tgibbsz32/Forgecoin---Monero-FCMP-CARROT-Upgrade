# Regression: the open-file ACL probe must refuse a normal inherited-ACL
# directory before creating any probe. Uses no sensitive data.
param([Parameter(Mandatory=$true)][string]$Verifier)
$ErrorActionPreference = "Stop"
$root = Join-Path $env:TEMP ("frg-insecure-acl-" + [guid]::NewGuid().ToString("N"))
[IO.Directory]::CreateDirectory($root) | Out-Null
try {
  $acl = Get-Acl -LiteralPath $root
  if ($acl.AreAccessRulesProtected) {
    throw "Test environment unexpectedly created a protected temp directory"
  }
  $rejected = $false
  try {
    & $Verifier -Directory $root | Out-Null
  } catch {
    if ($_.Exception.Message -like "*protected ACL*") {
      $rejected = $true
    } else {
      throw "Unexpected rejection: $($_.Exception.Message)"
    }
  }
  if (-not $rejected) {
    throw "Insecure directory was not rejected"
  }
  if (@(Get-ChildItem -LiteralPath $root -Force).Count -ne 0) {
    throw "Verifier unexpectedly wrote into insecure directory"
  }
  Write-Output "PASS: insecure inherited-ACL directory rejected without creating files"
} finally {
  if (Test-Path -LiteralPath $root) {
    [IO.Directory]::Delete($root)
  }
}
