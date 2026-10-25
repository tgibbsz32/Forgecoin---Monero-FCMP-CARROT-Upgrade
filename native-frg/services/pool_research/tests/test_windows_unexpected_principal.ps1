# Negative regression for open-file ACL verifier.
# A protected directory with an unexpected principal must be rejected
# BEFORE the harmless probe file is created.
param([Parameter(Mandatory=$true)][string]$Verifier)
$ErrorActionPreference="Stop"
$root=Join-Path $env:TEMP ("frg-unexpected-acl-"+[guid]::NewGuid().ToString("N"))
[IO.Directory]::CreateDirectory($root) | Out-Null
try {
  $acl=Get-Acl -LiteralPath $root
  $acl.SetAccessRuleProtection($true,$false)
  foreach($rule in @($acl.Access)) {[void]$acl.RemoveAccessRuleSpecific($rule)}
  $sid=[Security.Principal.WindowsIdentity]::GetCurrent().User
  $system=New-Object Security.Principal.SecurityIdentifier("S-1-5-18")
  $admin=New-Object Security.Principal.SecurityIdentifier("S-1-5-32-544")
  $unexpected=New-Object Security.Principal.SecurityIdentifier("S-1-1-0")
  foreach($principal in @($sid,$system,$admin,$unexpected)) {
    $rule=New-Object Security.AccessControl.FileSystemAccessRule(
      $principal,"FullControl","ContainerInherit,ObjectInherit","None","Allow")
    [void]$acl.AddAccessRule($rule)
  }
  Set-Acl -LiteralPath $root -AclObject $acl
  $caught=$null
  try {& $Verifier -Directory $root | Out-Null}
  catch {$caught=$_.Exception.Message}
  if (-not $caught -or $caught -notmatch "Unexpected access rule count|Unexpected access principal") {
    throw "Unexpected ACL was not rejected"
  }
  if (@(Get-ChildItem -LiteralPath $root -Force).Count -ne 0) {
    throw "Verifier wrote to an unsafe directory"
  }
  Write-Output "PASS: unexpected NTFS principal rejected before file creation"
} finally {
  if (Test-Path -LiteralPath $root) {[IO.Directory]::Delete($root)}
}
