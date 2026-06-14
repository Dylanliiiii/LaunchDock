param(
    [string]$Version = "1.0.0",
    [string]$InnoSetupCompiler = ""
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$appDir = Join-Path $Root "dist/LaunchDock"
if (-not (Test-Path (Join-Path $appDir "LaunchDock.exe"))) {
    throw "Missing dist/LaunchDock/LaunchDock.exe. Run scripts/build-windows.ps1 first."
}

$iconPath = Join-Path $Root "build/launchdock.ico"
if (-not (Test-Path $iconPath)) {
    powershell -ExecutionPolicy Bypass -File "scripts/build-windows.ps1" -Version "v$Version"
}

if (-not $InnoSetupCompiler) {
    $command = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
    if ($command) {
        $InnoSetupCompiler = $command.Source
    }
}

if (-not $InnoSetupCompiler) {
    $candidatePaths = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
    )
    foreach ($candidate in $candidatePaths) {
        if ($candidate -and (Test-Path $candidate)) {
            $InnoSetupCompiler = $candidate
            break
        }
    }
}

if (-not $InnoSetupCompiler -or -not (Test-Path $InnoSetupCompiler)) {
    throw "Inno Setup Compiler was not found. Install Inno Setup 6, then rerun this script."
}

$scriptPath = Join-Path $Root "installer/launchdock.iss"
& $InnoSetupCompiler `
    "/DAppVersion=$Version" `
    "/DSourceDir=$appDir" `
    "/DOutputDir=$(Join-Path $Root 'dist')" `
    "/DIconPath=$iconPath" `
    $scriptPath

$setupPath = Join-Path $Root "dist/LaunchDock-v$Version-windows-setup.exe"
if (-not (Test-Path $setupPath)) {
    throw "Installer was not generated: $setupPath"
}

Write-Host "Installer completed: $setupPath"
