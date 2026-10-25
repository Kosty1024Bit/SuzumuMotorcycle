param(
    [Parameter(Mandatory=$true)][string]$Script,
    [string]$LogName = 'devkit',
    [string]$DevKit = 'D:\EGS\CEUE5Devkit'
)
$ErrorActionPreference = 'Stop'
$modRoot = Split-Path $PSScriptRoot -Parent
$evidenceDir = Join-Path $modRoot 'evidence'
New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
$scriptPath = (Resolve-Path -LiteralPath $Script).Path
$logPath = Join-Path $evidenceDir ($LogName + '.log')
& (Join-Path $DevKit 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe') (Join-Path $DevKit 'UE4\ConanSandbox.uproject') '-ModDevKit' '-run=pythonscript' "-script=$scriptPath" '-EnablePlugins=PythonScriptPlugin' '-unattended' '-nopause' '-nosplash' '-nullrhi' '-culture=en' "-abslog=$logPath" *> (Join-Path $evidenceDir ($LogName + '.stdout.log'))
$resultCode = $LASTEXITCODE
Get-Content -LiteralPath $logPath | Select-String -Pattern '\[SUZUMU\]|LogPython: Error|Fatal error|Traceback' | ForEach-Object { $_.Line }
exit $resultCode
