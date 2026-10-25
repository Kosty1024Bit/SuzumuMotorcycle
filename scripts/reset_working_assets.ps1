$ErrorActionPreference='Stop'
$workspaceRoot=Split-Path $PSScriptRoot -Parent
$expectedSource='D:\EGS\CEUE5Devkit\UE4\Content\Mods\SuzumuMotorcycle\Local'
$sourcePath=(Resolve-Path -LiteralPath $expectedSource).Path
$privateRoot=Join-Path $workspaceRoot 'private'
New-Item -ItemType Directory -Path $privateRoot -Force | Out-Null
$destinationPath=Join-Path (Resolve-Path -LiteralPath $privateRoot).Path 'intermediate-local-path-assets'
if ($sourcePath -ne $expectedSource) { throw 'Unexpected source path' }
if (-not $destinationPath.StartsWith($workspaceRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Backup destination is outside the workspace' }
if (Test-Path -LiteralPath $destinationPath) { throw 'Backup destination already exists' }
if (Get-Process UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue) { throw 'Close the editor before moving mod assets' }
Move-Item -LiteralPath $sourcePath -Destination $destinationPath
New-Item -ItemType Directory -Path $sourcePath | Out-Null
Write-Output "Intermediate assets preserved at $destinationPath; clean mod Local folder ready."
