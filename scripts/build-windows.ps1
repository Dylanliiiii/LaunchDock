param(
    [string]$Version = ""
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

$addData = "assets/icon.png;assets"
$arguments = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--windowed",
    "--name", "LaunchDock",
    "--icon", $iconTarget,
    "--add-data", $addData,
    "main.py"
)

python @arguments

if ($Version) {
    $zipName = "LaunchDock-$Version-windows.zip"
} else {
    $zipName = "LaunchDock-windows.zip"
}

$zipPath = Join-Path $Root "dist/$zipName"
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
