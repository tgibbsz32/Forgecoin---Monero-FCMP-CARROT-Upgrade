# Provision a dedicated Windows directory for private offline template fixtures.
# Does not store a template or bypass private_capture.py's Windows refusal.
param([Parameter(Mandatory=$true)][string]$Path)
$ErrorActionPreference = "Stop"
if (-not $IsWindows -and $PSVersionTable.PSEdition -eq "Core") {
  throw "This script requires Windows"
}
$target = [System.IO.Path]::GetFullPath($Path)
if ([System.IO.Directory]::Exists($target) -or [System.IO.File]::Exists($target)) {
  throw "Refusing to change ACLs on an existing path"
}
$parent = [System.IO.Path]::GetDirectoryName($target)
if (-not [System.IO.Directory]::Exists($parent)) {throw "Parent must already exist"}
$ident = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$ownerSid = $ident.User.Value
$systemSid = "S-1-5-18"
$adminSid = "S-1-5-32-544"
[System.IO.Directory]::CreateDirectory($target) | Out-Null
try {
  $acl = Get-Acl -LiteralPath $target
  $acl.SetAccessRuleProtection($true,$false)
  foreach ($rule in @($acl.Access)) {
    [void]$acl.RemoveAccessRuleSpecific($rule)
  }
  foreach ($sidValue in @($ownerSid,$systemSid,$adminSid)) {
    $sid = New-Object System.Security.Principal.SecurityIdentifier($sidValue)
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
      $sid,"FullControl","ContainerInherit,ObjectInherit","None","Allow")
    [void]$acl.AddAccessRule($rule)
  }
  Set-Acl -LiteralPath $target -AclObject $acl
  $actual = Get-Acl -LiteralPath $target
  if (-not $actual.AreAccessRulesProtected) {throw "Inherited ACL still enabled"}
  $allowed = @($ownerSid,$systemSid,$adminSid)
  foreach ($rule in $actual.Access) {
    $sidValue = $rule.IdentityReference.Translate(
      [System.Security.Principal.SecurityIdentifier]).Value
    if ($sidValue -notin $allowed -or $rule.IsInherited -or
        $rule.AccessControlType -ne "Allow") {
      throw "Unexpected ACL entry detected"
    }
  }
  if (@($actual.Access).Count -ne 3) {throw "Unexpected ACL entry count"}
  Write-Output "PASS: dedicated private directory ACL verified (current user, SYSTEM, Administrators)"
} catch {
  # On errors leave the path for manual inspection rather than silently
  # deleting another process's files.
  throw "Private capture directory NOT approved: $($_.Exception.Message)"
}
