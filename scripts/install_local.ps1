param([string]$GameRoot='D:\Steam\steamapps\common\Conan Exiles')
$ErrorActionPreference='Stop'
$workspaceRoot=Split-Path $PSScriptRoot -Parent
$pak=Join-Path $workspaceRoot 'dist\SuzumuMotorcycle.pak'
if (-not (Test-Path -LiteralPath $pak)) { throw 'Build the pak before installation' }
if (Get-Process ConanSandbox,ConanSandbox-Win64-Shipping -ErrorAction SilentlyContinue) { throw 'Close Conan Exiles before updating its mod list' }
$modsRoot=Join-Path $GameRoot 'ConanSandbox\Mods'
$backupRoot=Join-Path $workspaceRoot ('private\install-backup-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
$state=@{modsDirectoryExisted=(Test-Path -LiteralPath $modsRoot); savedDirectoryExisted=(Test-Path -LiteralPath (Join-Path $GameRoot 'ConanSandbox\Saved')); gameRoot=$GameRoot}
$listPath=Join-Path $modsRoot 'modlist.txt'
$targetPak=Join-Path $modsRoot 'SuzumuMotorcycle.pak'
foreach ($oldPath in @($listPath,$targetPak)) {
    if (Test-Path -LiteralPath $oldPath) { Copy-Item -LiteralPath $oldPath -Destination $backupRoot }
}
$state | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $backupRoot 'state.json') -Encoding utf8
New-Item -ItemType Directory -Path $modsRoot -Force | Out-Null
Copy-Item -LiteralPath $pak -Destination $targetPak -Force
$text=if (Test-Path -LiteralPath $listPath) { [System.IO.File]::ReadAllText($listPath) } else { '' }
# The game comments rejected mods out with '#'. Reactivate this mod after updating.
$text=[regex]::Replace($text,'(?im)^\s*#+\s*\*?SuzumuMotorcycle\.pak\s*$','*SuzumuMotorcycle.pak')
if (-not ($text -split '\r?\n' | Where-Object { $_ -match '^\s*\*?SuzumuMotorcycle\.pak\s*$' })) {
    if ($text.Length -gt 0 -and -not $text.EndsWith("`n")) { $text+="`r`n" }
    $text+="*SuzumuMotorcycle.pak`r`n"
}
[System.IO.File]::WriteAllText($listPath,$text,[System.Text.UTF8Encoding]::new($false))
Write-Output "Installed $targetPak"
Write-Output "Previous local mod configuration preserved in $backupRoot"
Get-FileHash -LiteralPath $targetPak -Algorithm SHA256
