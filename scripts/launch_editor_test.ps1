$ErrorActionPreference='Stop'
$modRoot=Split-Path $PSScriptRoot -Parent
$devKit='D:\EGS\CEUE5Devkit'
$arguments=@(
    (Join-Path $devKit 'UE4\ConanSandbox.uproject'),
    '-ModDevKit',
    '-EnablePlugins=PythonScriptPlugin',
    ('-ExecCmds="py ' + (Join-Path $PSScriptRoot 'gui_worker.py') + '"'),
    '-unattended','-nosplash','-culture=en','-RenderOffscreen',
    "-abslog=$(Join-Path $modRoot 'evidence\editor_runtime.log')"
)
$editorProcess=Start-Process -FilePath (Join-Path $devKit 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Hidden -PassThru
Write-Output "Dev Kit test editor PID: $($editorProcess.Id)"
