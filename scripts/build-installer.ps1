param(
    [string]$Version = "1.0.0",
    [string]$InnoSetupCompiler = "",
    [ValidateSet("global", "china")]
    [string]$UpdateChannel = "global",
    [string]$UpdateRepoUrl = "",
    [string]$ReleasePageUrl = "",
    [string]$ReleaseApiUrl = ""
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

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

$buildArguments = @(
    "-ExecutionPolicy", "Bypass",
    "-File", "scripts/build-windows.ps1",
    "-Version", "v$Version",
    "-UpdateChannel", $UpdateChannel
)
if ($UpdateRepoUrl) {
    $buildArguments += @("-UpdateRepoUrl", $UpdateRepoUrl)
}
if ($ReleasePageUrl) {
    $buildArguments += @("-ReleasePageUrl", $ReleasePageUrl)
}
if ($ReleaseApiUrl) {
    $buildArguments += @("-ReleaseApiUrl", $ReleaseApiUrl)
}
powershell @buildArguments

$appDir = Join-Path $Root "dist/LaunchDock"
if (-not (Test-Path (Join-Path $appDir "LaunchDock.exe"))) {
    throw "Missing dist/LaunchDock/LaunchDock.exe. Run scripts/build-windows.ps1 first."
}

$iconPath = Join-Path $Root "build/launchdock.ico"
if (-not (Test-Path $iconPath)) {
    throw "Missing build/launchdock.ico. Run scripts/build-windows.ps1 first."
}

if ($UpdateChannel -eq "china") {
    $channelLabel = "china"
} else {
    $channelLabel = "global"
}

$scriptPath = Join-Path $Root "installer/launchdock.iss"
$versionLabel = $Version
if (-not $versionLabel.StartsWith("v")) {
    $versionLabel = "v$versionLabel"
}
$releaseDir = Join-Path $Root "dist/$versionLabel"
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null

& $InnoSetupCompiler `
    "/DAppVersion=$Version" `
    "/DSourceDir=$appDir" `
    "/DOutputDir=$releaseDir" `
    "/DReleaseChannel=$channelLabel" `
    "/DIconPath=$iconPath" `
    $scriptPath

$setupPath = Join-Path $releaseDir "LaunchDock-v$Version-windows-$channelLabel-setup.exe"
if (-not (Test-Path $setupPath)) {
    throw "Installer was not generated: $setupPath"
}

Write-Host "Installer completed: $setupPath"
