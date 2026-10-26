param([string]$DevKit='D:\EGS\CEUE5Devkit',[switch]$FinalPakOnly)
$ErrorActionPreference='Stop'
$workspaceRoot=Split-Path $PSScriptRoot -Parent
$contentRoot=Join-Path $DevKit 'UE4\Content'
$modRoot=Join-Path $contentRoot 'Mods\SuzumuMotorcycle'
$localRoot=Join-Path $modRoot 'Local'
$distRoot=Join-Path $workspaceRoot 'dist'
New-Item -ItemType Directory -Path $distRoot -Force | Out-Null
$runningEditors=Get-Process UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue
if ($runningEditors) { throw 'Close the Dev Kit before cooking; assets are still in use.' }
# The native editor stamps this compatibility revision when saving mod details.
# RunUAT packages the JSON verbatim, so stamp the installed SDK's own ModVersion.
$sdkConfig=[System.IO.File]::ReadAllText((Join-Path $DevKit 'UE4\Config\DefaultGame.ini'))
$revisionMatch=[regex]::Match($sdkConfig,'(?m)^ModVersion=(\d+)\s*$')
if (-not $revisionMatch.Success) { throw 'Installed SDK ModVersion is missing.' }
$modInfoPath=Join-Path $modRoot 'modinfo.json'
$modInfo=Get-Content -LiteralPath (Join-Path $workspaceRoot 'source\modinfo.json') -Raw | ConvertFrom-Json
$modInfo.devkitRevisionNumber=[int]$revisionMatch.Groups[1].Value
$modInfo.devkitSnapshotId=0
$modInfo | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $modInfoPath -Encoding utf8
Copy-Item -LiteralPath $modInfoPath -Destination (Join-Path $workspaceRoot 'source\modinfo.json') -Force
Write-Output "SDK compatibility revision: $($modInfo.devkitRevisionNumber):$($modInfo.devkitSnapshotId)"
$assetFiles=Get-ChildItem -LiteralPath $localRoot -Recurse -File -Filter '*.uasset'
if ($assetFiles.Count -lt 30) { throw 'Expected mod assets are missing.' }
$cookLines=@('[/CookInfo]')
foreach ($assetFile in $assetFiles) {
    $relativePath=$assetFile.FullName.Substring($contentRoot.Length+1).Replace('\','/')
    $cookLines+='FilesToCook='+$relativePath
}
$cookLines | Set-Content -LiteralPath (Join-Path $localRoot 'CookInfo.ini') -Encoding ascii
$projectFile=Join-Path $DevKit 'UE4\ConanSandbox.uproject'
$scriptDirectory=Join-Path $DevKit 'UE4'
$logPath=Join-Path $workspaceRoot 'evidence\build.log'
$buildSteps=@(if ($FinalPakOnly) { '-FinalPak' } else { '-Cook'; '-Pak'; '-Compress' })
& (Join-Path $DevKit 'Engine\Build\BatchFiles\RunUAT.bat') '-NoCompile' 'BuildMod' '-Mod=SuzumuMotorcycle' "-Project=$projectFile" @buildSteps "-ScriptDir=$scriptDirectory" *> $logPath
$resultCode=$LASTEXITCODE
Get-Content -LiteralPath $logPath -Tail 30
if ($resultCode -ne 0) { throw "BuildMod failed ($resultCode). See $logPath" }
$pakPath=Join-Path $DevKit 'UE4\Saved\Mods\SuzumuMotorcycle\Output\SuzumuMotorcycle.pak'
if (-not (Test-Path -LiteralPath $pakPath)) { throw 'Build reported success but output pak is missing.' }
Copy-Item -LiteralPath $pakPath -Destination (Join-Path $distRoot 'SuzumuMotorcycle.pak')
Get-FileHash -LiteralPath (Join-Path $distRoot 'SuzumuMotorcycle.pak') -Algorithm SHA256
