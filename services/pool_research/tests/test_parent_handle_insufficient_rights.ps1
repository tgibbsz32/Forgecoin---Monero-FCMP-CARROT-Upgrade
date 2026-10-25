# Negative test only. Operates on a fresh disposable directory.
$ErrorActionPreference='Stop'
$target=Join-Path $PSScriptRoot 'test_parent_handle_owner_rights.ps1'
$root=Join-Path $env:TEMP ('frg-parent-rights-negative-'+[guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($root)|Out-Null
try {
  $sid=[Security.Principal.WindowsIdentity]::GetCurrent().User
  $acl=New-Object Security.AccessControl.DirectorySecurity
  $acl.SetAccessRuleProtection($true,$false)
  foreach($entry in @(
    @{SID=$sid;Rights=[Security.AccessControl.FileSystemRights]::FullControl},
    @{SID=(New-Object Security.Principal.SecurityIdentifier 'S-1-5-18');Rights=[Security.AccessControl.FileSystemRights]::FullControl},
    @{SID=(New-Object Security.Principal.SecurityIdentifier 'S-1-5-32-544');Rights=[Security.AccessControl.FileSystemRights]::ReadAndExecute}
  )) {
    $flags=[Security.AccessControl.InheritanceFlags]([int][Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [int][Security.AccessControl.InheritanceFlags]::ObjectInherit)
    $rule=New-Object Security.AccessControl.FileSystemAccessRule($entry.SID,$entry.Rights,$flags,[Security.AccessControl.PropagationFlags]::None,[Security.AccessControl.AccessControlType]::Allow)
    $acl.AddAccessRule($rule)
  }
  [IO.Directory]::SetAccessControl($root,$acl)
  $output=@(& powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $target -Directory $root 2>&1)
  if($LASTEXITCODE -eq 0){throw 'Insecure rights were accepted'}
  if(-not (@($output | Where-Object {"$_" -match 'lacks required directory rights'}).Count)){throw 'Validator rejected for unexpected reason'}
  Write-Output 'PASS: directory handle validator rejected insufficient approved-principal access rights'
} finally {
  if([IO.Directory]::Exists($root)) {
    $reset=New-Object Security.AccessControl.DirectorySecurity
    $reset.SetAccessRuleProtection($true,$false)
    $reset.AddAccessRule((New-Object Security.AccessControl.FileSystemAccessRule([Security.Principal.WindowsIdentity]::GetCurrent().User,[Security.AccessControl.FileSystemRights]::FullControl,[Security.AccessControl.AccessControlType]::Allow)))
    [IO.Directory]::SetAccessControl($root,$reset)
    [IO.Directory]::Delete($root)
  }
}
