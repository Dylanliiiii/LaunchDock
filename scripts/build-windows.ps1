param(
    [string]$Version = "",
    [ValidateSet("global", "china")]
    [string]$UpdateChannel = "global",
    [string]$UpdateRepoUrl = "",
    [string]$ReleasePageUrl = "",
    [string]$ReleaseApiUrl = ""
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path "assets/icon.png")) {
    throw "Missing assets/icon.png."
}

python -m PyInstaller --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller is not installed. Run: python -m pip install pyinstaller"
}

New-Item -ItemType Directory -Force -Path "build" | Out-Null

if (-not $UpdateRepoUrl) {
    if ($UpdateChannel -eq "china") {
        $UpdateRepoUrl = "https://cnb.cool/DylanLIIIII/LaunchDock.git"
    } else {
        $UpdateRepoUrl = "https://github.com/Dylanliiiii/LaunchDock.git"
    }
}
if (-not $ReleasePageUrl) {
    if ($UpdateChannel -eq "china") {
        $ReleasePageUrl = "https://cnb.cool/DylanLIIIII/LaunchDock/-/releases"
    } else {
        $ReleasePageUrl = "https://github.com/Dylanliiiii/LaunchDock/releases"
    }
}
if (-not $ReleaseApiUrl) {
    if ($UpdateChannel -eq "global") {
        $ReleaseApiUrl = "https://api.github.com/repos/Dylanliiiii/LaunchDock/releases/latest"
    } else {
        $ReleaseApiUrl = ""
    }
}

$updateConfigTarget = Join-Path $Root "build/update-config.json"
$updateConfig = [ordered]@{
    update_channel = $UpdateChannel
    update_repo_url = $UpdateRepoUrl
    release_page_url = $ReleasePageUrl
    release_api_url = $ReleaseApiUrl
}
$updateConfigJson = $updateConfig | ConvertTo-Json
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($updateConfigTarget, $updateConfigJson, $utf8NoBom)

if ($UpdateChannel -eq "china") {
    $channelLabel = "china"
} else {
    $channelLabel = "global"
}

$iconSource = Join-Path $Root "assets/icon.png"
$iconTarget = Join-Path $Root "build/launchdock.ico"

$pngBytes = [System.IO.File]::ReadAllBytes($iconSource)
$iconBytes = New-Object System.Collections.Generic.List[byte]

function Add-U16([int]$value) {
    $iconBytes.Add([byte]($value -band 0xff))
    $iconBytes.Add([byte](($value -shr 8) -band 0xff))
}

function Add-U32([int]$value) {
    $iconBytes.Add([byte]($value -band 0xff))
    $iconBytes.Add([byte](($value -shr 8) -band 0xff))
    $iconBytes.Add([byte](($value -shr 16) -band 0xff))
    $iconBytes.Add([byte](($value -shr 24) -band 0xff))
}

Add-U16 0
Add-U16 1
Add-U16 1
$iconBytes.Add(0)
$iconBytes.Add(0)
$iconBytes.Add(0)
$iconBytes.Add(0)
Add-U16 1
Add-U16 32
Add-U32 $pngBytes.Length
Add-U32 22
$iconBytes.AddRange($pngBytes)
[System.IO.File]::WriteAllBytes($iconTarget, $iconBytes.ToArray())

$iconData = "assets/icon.png;assets"
$updateConfigData = "$updateConfigTarget;launchdock"
$arguments = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--windowed",
    "--name", "LaunchDock",
    "--icon", $iconTarget,
    "--add-data", $iconData,
    "--add-data", $updateConfigData,
    "main.py"
)

python @arguments

if ($Version) {
    $versionLabel = $Version
    if (-not $versionLabel.StartsWith("v")) {
        $versionLabel = "v$versionLabel"
    }
    $releaseDir = Join-Path $Root "dist/$versionLabel"
    $zipName = "LaunchDock-$versionLabel-windows-$channelLabel.zip"
} else {
    $releaseDir = Join-Path $Root "dist"
    $zipName = "LaunchDock-windows-$channelLabel.zip"
}

New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
$zipPath = Join-Path $releaseDir $zipName
if (Test-Path $zipPath) {
    Remove-Item $zipPath
}

$archiveCreated = $false
for ($attempt = 1; $attempt -le 5; $attempt++) {
    try {
        Start-Sleep -Seconds 2
        Compress-Archive -Path "dist/LaunchDock/*" -DestinationPath $zipPath
        $archiveCreated = $true
        break
    } catch {
        if ($attempt -eq 5) {
            throw
        }
        if (Test-Path $zipPath) {
            Remove-Item $zipPath -Force
        }
    }
}

if (-not $archiveCreated) {
    throw "Failed to create release archive."
}

Write-Host "Build completed: $zipPath"
