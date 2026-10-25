param([switch]$Interactive)
$ErrorActionPreference='Stop'
$workspaceRoot=Split-Path $PSScriptRoot -Parent
$gameRoot='D:\Steam\steamapps\common\Conan Exiles'
$exe=Join-Path $gameRoot 'ConanSandbox\Binaries\Win64\ConanSandbox-Win64-Shipping.exe'
$arguments=@('-windowed','-ResX=1280','-ResY=720','-nosplash','-NoStartupMovies',"-abslog=$(Join-Path $workspaceRoot 'evidence\game_runtime.log')")
$windowStyle=if ($Interactive) { 'Normal' } else { 'Hidden' }
$process=Start-Process -FilePath $exe -WorkingDirectory $gameRoot -ArgumentList $arguments -WindowStyle $windowStyle -PassThru
Write-Output "Conan Exiles local test PID: $($process.Id)"
