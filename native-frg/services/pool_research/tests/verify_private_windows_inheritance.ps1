# Verify that a harmless file created in an already-provisioned private directory
# inherits ONLY the current user, SYSTEM, and Administrators. Never writes secrets.
param([Parameter(Mandatory=$true)][string]$Directory)
$ErrorActionPreference = "Stop"
$path = [IO.Path]::GetFullPath($Directory)
$item = Get-Item -LiteralPath $path -Force
if (-not $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
  throw "Not a normal directory"
}
$ident = [Security.Principal.WindowsIdentity]::GetCurrent()
$allowed = @($ident.User.Value,"S-1-5-18","S-1-5-32-544")
$directoryAcl = Get-Acl -LiteralPath $path
if (-not $directoryAcl.AreAccessRulesProtected) {throw "Directory ACL inherits from parent"}
$probe = Join-Path $path ("probe-" + [guid]::NewGuid().ToString("N") + ".txt")
try {
  $stream = [IO.File]::Open($probe,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
  try {
    $message = [Text.Encoding]::UTF8.GetBytes("no sensitive data")
    $stream.Write($message,0,$message.Length)
  } finally {$stream.Dispose()}
  $acl = Get-Acl -LiteralPath $probe
  $rules = @($acl.Access)
  if ($rules.Count -ne 3) {throw "Unexpected inherited file rule count"}
  foreach($rule in $rules) {
    $sid = $rule.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value
    if ($sid -notin $allowed -or -not $rule.IsInherited -or
      $rule.AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow) {
      throw "Unsafe file ACL"
    }
  }
  Write-Output "PASS: harmless probe inherited only the 3 permitted principals"
} finally {
  if (Test-Path -LiteralPath $probe) {Remove-Item -LiteralPath $probe -Force}
}
