# Harmless Windows handle-backed file creation/ACL probe.
# NOT a directory-handle-relative secure writer; private capture stays disabled.
param([Parameter(Mandatory=$true)][string]$Directory)
$ErrorActionPreference="Stop"
$dir=(Get-Item -LiteralPath $Directory -Force -ErrorAction Stop)
if (-not $dir.PSIsContainer -or (($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
  throw "Directory must be ordinary, not a reparse point"
}
$directoryAcl=Get-Acl -LiteralPath $dir.FullName
if (-not $directoryAcl.AreAccessRulesProtected) {throw "Directory must have protected ACL"}
$allowed=@([Security.Principal.WindowsIdentity]::GetCurrent().User.Value,"S-1-5-18","S-1-5-32-544")
function Assert-Rules($acl) {
  $rules=@($acl.Access)
  if ($rules.Count -ne 3) {throw "Unexpected access rule count"}
  foreach($rule in $rules) {
    $sid=$rule.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value
    if ($sid -notin $allowed -or $rule.AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow) {
      throw "Unexpected access principal"
    }
  }
}
Assert-Rules $directoryAcl
$name=("probe-"+[guid]::NewGuid().ToString("N")+".txt")
$path=Join-Path $dir.FullName $name
$created=$false
try {
  $stream=New-Object System.IO.FileStream(
    $path,[IO.FileMode]::CreateNew,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
  $created=$true
  try {
    # Check security on the opened file HANDLE before writing test bytes.
    $fileAcl=$stream.GetAccessControl()
    Assert-Rules $fileAcl
    $bytes=[Text.Encoding]::ASCII.GetBytes("harmless probe")
    $stream.Write($bytes,0,$bytes.Length)
    $stream.Flush($true)
  } finally {$stream.Dispose()}
  $check=Get-Item -LiteralPath $path -Force
  if (($check.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw "Created file is a reparse point"
  }
  Write-Output "PASS: created harmless file exclusively and checked ACL using open file handle"
} finally {
  if ($created -and [IO.File]::Exists($path)) {[IO.File]::Delete($path)}
}
