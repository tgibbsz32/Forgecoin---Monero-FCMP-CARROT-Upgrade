# Diagnostic regression for Windows rename sharing conflicts.
# Test only, never used for private template writes.
$ErrorActionPreference = 'Stop'
$root=Join-Path $env:TEMP ("frg-share-denial-"+[guid]::NewGuid().ToString('N'))
$original=Join-Path $root 'original'
$renamed=Join-Path $root 'relocated'
[IO.Directory]::CreateDirectory($original) | Out-Null
$child=Join-Path $original 'harmless-zero-byte.txt'
$handle=$null
try {
  $handle=New-Object IO.FileStream($child,[IO.FileMode]::CreateNew,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
  $denied=$false
  try {[IO.Directory]::Move($original,$renamed)}
  catch [IO.IOException] {$denied=$true}
  if(-not $denied){throw "Rename unexpectedly succeeded despite deny-sharing file handle"}
  if(-not [IO.File]::Exists($child)){throw "Original child missing after denied rename"}
  if([IO.Directory]::Exists($renamed)){throw "Rename unexpectedly redirected child"}
  if($handle.Length -ne 0){throw "Harmless probe was modified"}
  Write-Output 'PASS: denied rename left original zero-byte file in original directory'
} finally {
  if($handle){$handle.Dispose()}
  if([IO.File]::Exists($child)){[IO.File]::Delete($child)}
  if([IO.Directory]::Exists($original)){[IO.Directory]::Delete($original)}
  if([IO.Directory]::Exists($renamed)){[IO.Directory]::Delete($renamed)}
  if([IO.Directory]::Exists($root)){[IO.Directory]::Delete($root)}
}
