# Read-only inspection of a private fixture directory and its ancestors.
# Does not authorize writes: reparse-point checks are susceptible to TOCTOU.
param([Parameter(Mandatory=$true)][string]$Directory)
$ErrorActionPreference = "Stop"
$target = [IO.Path]::GetFullPath($Directory)
if (-not [IO.Path]::IsPathRooted($Directory)) {throw "Absolute path required"}
if ($target.StartsWith('\\')) {throw "Network paths are not permitted"}
$current = Get-Item -LiteralPath $target -Force -ErrorAction Stop
if (-not $current.PSIsContainer) {throw "Target must be a directory"}
while ($null -ne $current) {
  if (($current.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw "Reparse point encountered"
  }
  $current = $current.Parent
}
$acl=Get-Acl -LiteralPath $target
if (-not $acl.AreAccessRulesProtected) {throw "Target inherits ACL"}
$allowed=@([Security.Principal.WindowsIdentity]::GetCurrent().User.Value,
           "S-1-5-18","S-1-5-32-544")
$rules=@($acl.Access)
if ($rules.Count -ne 3) {throw "Unexpected target ACL entries"}
foreach ($rule in $rules) {
  $sid=$rule.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value
  if ($sid -notin $allowed -or $rule.IsInherited -or
      $rule.AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow) {
    throw "Unexpected target ACL principal or rule"
  }
}
Write-Output "PASS: inspected path contains no reparse points; protected target ACL verified"
