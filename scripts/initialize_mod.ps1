$ErrorActionPreference='Stop'
$modsRoot='D:\EGS\CEUE5Devkit\UE4\Content\Mods'
$targetRoot=Join-Path $modsRoot 'SuzumuMotorcycle'
$workspaceRoot=Split-Path $PSScriptRoot -Parent
$backupsRoot=Join-Path $workspaceRoot 'evidence\devkit_selection_backup'
New-Item -ItemType Directory -Path $backupsRoot -Force | Out-Null
foreach ($marker in Get-ChildItem -LiteralPath $modsRoot -Filter 'active.txt' -Recurse -File) {
    if ($marker.DirectoryName -ne $targetRoot) {
        Copy-Item -LiteralPath $marker.FullName -Destination (Join-Path $backupsRoot ($marker.Directory.Name + '_active.txt'))
        Move-Item -LiteralPath $marker.FullName -Destination ($marker.FullName + '.before-suzumu')
    }
}
New-Item -ItemType Directory -Path (Join-Path $targetRoot 'Local') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $targetRoot 'Content') -Force | Out-Null
New-Item -ItemType File -Path (Join-Path $targetRoot 'active.txt') -Force | Out-Null
$sdkConfig=[System.IO.File]::ReadAllText('D:\EGS\CEUE5Devkit\UE4\Config\DefaultGame.ini')
$revisionMatch=[regex]::Match($sdkConfig,'(?m)^ModVersion=(\d+)\s*$')
if (-not $revisionMatch.Success) { throw 'Installed SDK ModVersion is missing.' }
$info=@{
 name='Suzumu Motorcycle'; description='Single rider motorcycle built on horse mechanics.'; changeNote='Initial local development build.'; author='Local mod project'; authorUrl='';
 versionMajor=0; versionMinor=1; versionBuild=0; bRequiresLoadOnStartup=$false; steamPublishedFileId=''; steamTestLivePublishedFileId=''; steamWorkshopFileIds=@{};
 steamVisibility=2; folderName='SuzumuMotorcycle'; devkitRevisionNumber=[int]$revisionMatch.Groups[1].Value; devkitSnapshotId=0; minimumVersion='Enhanced'; requestedHttpOrigins=@()
}
$info | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $targetRoot 'modinfo.json') -Encoding utf8
Write-Output "Created $targetRoot; previous active selection preserved in $backupsRoot"
