# Research only. Use an empty protected disposable fixture, never capture data.
param([Parameter(Mandatory=$true)][string]$Directory)
$ErrorActionPreference='Stop'
$dir=Get-Item -LiteralPath $Directory -Force
if(-not $dir.PSIsContainer -or ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
  throw 'Invalid fixture directory'
}
if(-not (Get-Acl -LiteralPath $dir.FullName).AreAccessRulesProtected) {
  throw 'Fixture must have a protected ACL'
}
if(@(Get-ChildItem -LiteralPath $dir.FullName -Force).Count) {throw 'Fixture must be empty'}
Add-Type -Path @((Join-Path $PSScriptRoot 'NtOwnershipProbe.cs'),(Join-Path $PSScriptRoot 'NtAllocationRegression.cs'))
[NtAllocationRegression]::Run($dir.FullName)
if(@(Get-ChildItem -LiteralPath $dir.FullName -Force).Count) {throw 'Orphan probe files'}
Write-Output 'PASS: 13 allocation ownership cases; exact allocation/free counts; no orphan files'
