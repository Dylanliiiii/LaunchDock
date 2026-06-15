param(
    [Parameter(Mandatory = $true)]
    [string]$TagName,

    [Parameter(Mandatory = $true)]
    [string]$Title,

    [string]$Body = "",

    [string]$BodyFile = "",

    [string]$TargetCommitish = "main",

    [string]$Slug = "DylanLIIIII/LaunchDock",

    [string]$CnbUser = "cnb",

    [string]$CnbToken = $env:CNB_TOKEN,

    [string[]]$Assets = @()
)

$ErrorActionPreference = "Stop"

if (-not $CnbToken) {
    throw "缺少 CNB token。请通过 -CnbToken 或环境变量 CNB_TOKEN 传入。"
}

if ($BodyFile) {
    $Body = Get-Content -Path $BodyFile -Raw -Encoding UTF8
}

$ApiBase = "https://api.cnb.cool"
$AuthPair = "${CnbUser}:${CnbToken}"
$AuthValue = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($AuthPair))
$Headers = @{
    Authorization = "Basic $AuthValue"
    Accept = "application/json"
}

function ConvertTo-CnbJson {
    param([hashtable]$Data)
    return ($Data | ConvertTo-Json -Depth 10)
}

function Invoke-CnbJson {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("Get", "Post", "Patch", "Delete")]
        [string]$Method,

        [Parameter(Mandatory = $true)]
        [string]$Path,

        [hashtable]$Data = $null,

        [switch]$AllowNotFound
    )

    $uri = "$ApiBase/$Path"
    try {
        if ($Data) {
            return Invoke-RestMethod -Method $Method -Uri $uri -Headers $Headers -ContentType "application/json; charset=utf-8" -Body (ConvertTo-CnbJson $Data)
        }
        return Invoke-RestMethod -Method $Method -Uri $uri -Headers $Headers
    }
    catch {
        $response = $_.Exception.Response
        if ($AllowNotFound -and $response -and [int]$response.StatusCode -eq 404) {
            return $null
        }
        throw
    }
}

function Get-ResultValue {
    param($Response)
    if (-not $Response) {
        return $null
    }
    if ($Response.PSObject.Properties.Name -contains "result") {
        return $Response.result
    }
    return $Response
}

function Get-CnbRelease {
    param([string]$Tag)
    $encodedTag = [uri]::EscapeDataString($Tag)
    $response = Invoke-CnbJson -Method Get -Path "$Slug/-/releases/tags/$encodedTag" -AllowNotFound
    $result = Get-ResultValue $response
    if (-not $result) {
        return $null
    }
    if ($result.PSObject.Properties.Name -contains "release") {
        return $result.release
    }
    return $result
}

function New-CnbRelease {
    $payload = @{
        tag_name = $TagName
        target_commitish = $TargetCommitish
        title = $Title
        body = $Body
        is_prerelease = $false
        make_latest = "true"
        is_draft = $false
    }
    $response = Invoke-CnbJson -Method Post -Path "$Slug/-/releases" -Data $payload
    $result = Get-ResultValue $response
    if ($result.PSObject.Properties.Name -contains "release") {
        return $result.release
    }
    return $result
}

function Update-CnbRelease {
    param($Release)
    if (-not $Release.id) {
        return
    }
    $payload = @{
        title = $Title
        body = $Body
        is_prerelease = $false
        make_latest = "true"
        is_draft = $false
    }
    Invoke-CnbJson -Method Patch -Path "$Slug/-/releases/$($Release.id)" -Data $payload | Out-Null
}

function Get-CurlCommand {
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if (-not $curl) {
        $curl = Get-Command curl -ErrorAction Stop
    }
    return $curl.Source
}

function Upload-CnbReleaseAsset {
    param(
        [Parameter(Mandatory = $true)]
        $Release,

        [Parameter(Mandatory = $true)]
        [string]$AssetPath
    )

    if (-not (Test-Path -LiteralPath $AssetPath)) {
        throw "附件不存在：$AssetPath"
    }
    if (-not $Release.id) {
        throw "CNB Release 缺少 id，无法上传附件。"
    }

    $file = Get-Item -LiteralPath $AssetPath
    $fileName = $file.Name
    $existingAssets = @($Release.assets)
    if ($existingAssets | Where-Object { $_.name -eq $fileName }) {
        Write-Output "CNB 附件已存在，跳过：$fileName"
        return
    }

    $contentType = "application/octet-stream"
    if ($file.Extension -eq ".zip") {
        $contentType = "application/zip"
    }

    $preparePayload = @{
        name = $fileName
        size = $file.Length
        content_type = $contentType
    }
    $encodedTag = [uri]::EscapeDataString($TagName)
    $prepareResponse = Invoke-CnbJson -Method Post -Path "$Slug/-/upload/releases/$encodedTag" -Data $preparePayload
    $prepareResult = Get-ResultValue $prepareResponse
    if (-not $prepareResult.uploadUrl -and -not $prepareResult.upload_url) {
        throw "CNB 未返回附件上传地址：$fileName"
    }

    $uploadUrl = if ($prepareResult.uploadUrl) { $prepareResult.uploadUrl } else { $prepareResult.upload_url }
    $assetPathOnCnb = $prepareResult.path

    $curl = Get-CurlCommand
    $curlOutput = & $curl -sS -u "${CnbUser}:${CnbToken}" -X POST -F "file=@$($file.FullName)" $uploadUrl
    if ($LASTEXITCODE -ne 0) {
        throw "上传附件失败：$fileName"
    }

    $uploadResult = $null
    if ($curlOutput) {
        try {
            $uploadResult = $curlOutput | ConvertFrom-Json
        }
        catch {
            $uploadResult = $null
        }
    }

    $token = ""
    if ($uploadResult -and ($uploadResult.PSObject.Properties.Name -contains "token")) {
        $token = $uploadResult.token
    }
    elseif ($prepareResult.PSObject.Properties.Name -contains "token") {
        $token = $prepareResult.token
    }

    if (-not $assetPathOnCnb -and $uploadResult -and ($uploadResult.PSObject.Properties.Name -contains "path")) {
        $assetPathOnCnb = $uploadResult.path
    }

    $assetPayload = @{
        content_type = $contentType
        name = $fileName
        path = $assetPathOnCnb
        size_in_byte = $file.Length
        token = $token
    }
    Invoke-CnbJson -Method Post -Path "$Slug/-/releases/$($Release.id)/assets" -Data $assetPayload | Out-Null
    Write-Output "CNB 附件已上传：$fileName"
}

$release = Get-CnbRelease -Tag $TagName
if (-not $release) {
    Write-Output "CNB Release 不存在，正在创建：$TagName"
    $release = New-CnbRelease
}
else {
    Write-Output "CNB Release 已存在，正在更新：$TagName"
    Update-CnbRelease -Release $release
    $release = Get-CnbRelease -Tag $TagName
}

foreach ($asset in $Assets) {
    Upload-CnbReleaseAsset -Release $release -AssetPath $asset
    $release = Get-CnbRelease -Tag $TagName
}

Write-Output "CNB Release 同步完成：https://cnb.cool/$Slug/-/releases/tag/$TagName"
