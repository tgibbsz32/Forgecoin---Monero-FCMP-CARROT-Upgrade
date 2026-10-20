$ErrorActionPreference = 'Stop'
$targetDir = Join-Path $PSScriptRoot '..\src-tauri\target\debug'
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
foreach ($name in @('forged','forge-wallet-rpc')) {
    $source = Join-Path $PSScriptRoot "..\src-tauri\binaries\$name-x86_64-pc-windows-msvc.exe"
    if (!(Test-Path -LiteralPath $source)) { throw "Missing sidecar: $source" }
    Copy-Item -LiteralPath $source -Destination (Join-Path $targetDir "$name.exe") -Force
}
Write-Host 'ForgeCoin node and wallet sidecars staged.'
