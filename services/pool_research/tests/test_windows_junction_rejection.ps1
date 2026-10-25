# Non-sensitive adversarial regression for the private-directory preflight.
# Verifies a junction is rejected; does not write a real template.
param([Parameter(Mandatory=$true)][string]$Inspector)
$ErrorActionPreference="Stop"
$root=Join-Path $env:TEMP ("frg-path-negative-"+[guid]::NewGuid().ToString("N"))
$target=Join-Path $root "real"
$link=Join-Path $root "junction"
[IO.Directory]::CreateDirectory($target) | Out-Null
try {
  $result=New-Item -ItemType Junction -Path $link -Target $target -ErrorAction Stop
  $caught = $null
  try {
    & $Inspector -Directory $link | Out-Null
  } catch {
    $caught = $_.Exception.Message
  }
  if ($null -eq $caught -or -not $caught.Contains("Reparse point")) {
    throw "Junction was not explicitly rejected as a reparse point"
  }
  Write-Output "PASS: junction is rejected by read-only path inspection"
} finally {
  if (Test-Path -LiteralPath $link) {
    # Delete only the junction entry, never traverse the target.
    [IO.Directory]::Delete($link)
  }
  if (Test-Path -LiteralPath $target) {[IO.Directory]::Delete($target)}
  if (Test-Path -LiteralPath $root) {[IO.Directory]::Delete($root)}
}
