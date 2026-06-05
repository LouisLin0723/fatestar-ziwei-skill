<#
.SYNOPSIS
  FateStar Ziwei CLI — Zi Wei Dou Shu (紫微斗数) charting + 郑大钱 AI reading.

  chart     GET  /api/ziwei              (free, anonymous)
  transits  GET  /api/ziwei?transits=1   (free)
  reading   POST /api/ziwei/reading       (paid, needs FSFSKey key)
  doc       offline interface spec

  No external modules. Works on PowerShell 5.1+ and 7+.
#>

$ErrorActionPreference = "Stop"
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

function Load-Env {
    # Priority: --api_key > .env file > environment variable > anonymous.
    foreach ($envPath in @((Join-Path $PSScriptRoot ".env"), (Join-Path $PSScriptRoot "..\.env"))) {
        if (Test-Path $envPath) {
            foreach ($line in (Get-Content $envPath -Encoding UTF8)) {
                $line = $line.Trim()
                if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) { continue }
                $idx = $line.IndexOf("=")
                $key = $line.Substring(0, $idx).Trim().TrimStart([char]0xFEFF)
                $val = $line.Substring($idx + 1).Trim().Trim('"').Trim("'").Trim()
                if ($key -and $val) { [Environment]::SetEnvironmentVariable($key, $val) }
            }
        }
    }
}
Load-Env

# BEGIN GENERATED:CONSTANTS
$DEFAULT_API_BASE = "https://www.fatestar.top"
$CHART_PATH = "/api/ziwei"
$READING_PATH = "/api/ziwei/reading"
# END GENERATED:CONSTANTS

function Get-ApiBase {
    $b = $env:FATESTAR_API_BASE
    if (-not $b) { $b = $DEFAULT_API_BASE }
    return $b.TrimEnd("/")
}

function Build-BirthParams($a) {
    $q = [ordered]@{
        year = $a["year"]; month = $a["month"]; day = $a["day"]; hour = $a["hour"];
        gender = $a["gender"]
        calendarType = $(if ($a["calendar"]) { $a["calendar"] } else { "solar" })
    }
    if ($a.Contains("minute")) { $q["minute"] = $a["minute"] }
    if ($a["leap"]) { $q["isLeapMonth"] = "true" }
    if ($a.Contains("longitude")) { $q["longitude"] = $a["longitude"] }
    if ($a.Contains("tz")) { $q["timezoneOffset"] = $a["tz"] }
    return $q
}

function To-QueryString($q) {
    ($q.GetEnumerator() | ForEach-Object {
        "$($_.Key)=" + [uri]::EscapeDataString([string]$_.Value)
    }) -join "&"
}

function Invoke-Api {
    param([string]$Method, [string]$Url, [string]$Body, [string]$ApiKey)
    $req = [System.Net.HttpWebRequest]::Create($Url)
    $req.Method = $Method
    $req.Accept = "application/json"
    $req.Timeout = 40000
    if ($ApiKey) { $req.Headers.Add("Authorization", "Bearer $ApiKey") }
    if ($Method -eq "POST") {
        $req.ContentType = "application/json"
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Body)
        $req.ContentLength = $bytes.Length
        $rs = $req.GetRequestStream(); $rs.Write($bytes, 0, $bytes.Length); $rs.Close()
    }
    $resp = $null
    try {
        $resp = $req.GetResponse()
    } catch [System.Net.WebException] {
        if ($_.Exception.Response) { $resp = $_.Exception.Response }
        else { [Console]::Error.WriteLine("Connection Error: unable to reach $(Get-ApiBase) ($($_.Exception.Message))"); exit 1 }
    }
    $status = [int]$resp.StatusCode
    $reader = New-Object System.IO.StreamReader($resp.GetResponseStream(), [System.Text.Encoding]::UTF8)
    $raw = $reader.ReadToEnd(); $reader.Close(); $resp.Close()
    return @{ status = $status; raw = $raw }
}

function Err-From($raw, $status) {
    $code = "HTTP_$status"; $msg = $raw
    try { $b = $raw | ConvertFrom-Json; if ($b.error) { $code = $b.error.code; $msg = $b.error.message } } catch {}
    [Console]::Error.WriteLine("API Error [$code]: $msg")
}

function Cmd-Chart($a) {
    $url = (Get-ApiBase) + $CHART_PATH + "?" + (To-QueryString (Build-BirthParams $a))
    $r = Invoke-Api "GET" $url $null $null
    if ($r.status -ne 200) { Err-From $r.raw $r.status; exit 1 }
    Write-Output $r.raw
}

function Cmd-Transits($a) {
    $q = Build-BirthParams $a
    $q["transits"] = "1"
    if ($a.Contains("target-year")) { $q["targetYear"] = $a["target-year"] }
    if ($a.Contains("target-month")) { $q["targetMonth"] = $a["target-month"] }
    if ($a.Contains("target-day")) { $q["targetDay"] = $a["target-day"] }
    if ($a.Contains("target-hour")) { $q["targetHour"] = $a["target-hour"] }
    $url = (Get-ApiBase) + $CHART_PATH + "?" + (To-QueryString $q)
    $r = Invoke-Api "GET" $url $null $null
    if ($r.status -ne 200) { Err-From $r.raw $r.status; exit 1 }
    Write-Output $r.raw
}

function Cmd-Reading($a) {
    $question = ([string]$a["question"]).Trim()
    if (-not $question) { [Console]::Error.WriteLine("Error: --question is required for reading."); exit 1 }
    $apiKey = $a["api_key"]
    if (-not $apiKey) { $apiKey = $env:FATESTAR_API_KEY }
    if (-not $apiKey) {
        [Console]::Error.WriteLine("郑大钱解读需要 FSFSKey key (尚未配置)。")
        [Console]::Error.WriteLine("请到 https://www.fatestar.top 注册免费会员 → 做新手任务领积分 →")
        [Console]::Error.WriteLine("开发者中心创建 FSFSKey key → 写进 .env (FATESTAR_API_KEY=) 或用 --api_key 传入。")
        [Console]::Error.WriteLine("在此之前可用 ``chart`` 免费排盘, 再自行解读。")
        exit 2
    }
    $bodyObj = Build-BirthParams $a
    $bodyObj["question"] = $question
    $body = $bodyObj | ConvertTo-Json -Compress
    $r = Invoke-Api "POST" ((Get-ApiBase) + $READING_PATH) $body $apiKey
    if ($r.status -eq 200) {
        $d = $null
        try { $d = ($r.raw | ConvertFrom-Json).data } catch {}
        if (-not $d -or -not $d.reading) { [Console]::Error.WriteLine("郑大钱解读失败: 空回复 (未扣费), 请重试。"); exit 1 }
        Write-Output $d.reading
        [Console]::Error.WriteLine("`n---`n[积分] 本次扣除 $($d.creditsUsed), 剩余 $($d.balanceAfter)")
        return
    }
    if ($r.status -eq 401) {
        [Console]::Error.WriteLine("Key 无效或已吊销 (401)。请到 https://www.fatestar.top 开发者中心确认或重新申请 FSFSKey key。")
    } elseif ($r.status -eq 402) {
        $need = $null; $have = $null
        try { $e = ($r.raw | ConvertFrom-Json).error; $need = $e.need; $have = $e.have } catch {}
        [Console]::Error.WriteLine("积分不足 (402, 需 $need / 有 $have), 未扣费。")
        [Console]::Error.WriteLine("请到 https://www.fatestar.top 充值, 或等北京时间 21:00 免费重置 (每日 3 积分)。")
        [Console]::Error.WriteLine("现在可改用 ``chart`` 拿命盘数据 + 自行解读兜底。")
    } else {
        Err-From $r.raw $r.status
    }
    exit 1
}

# BEGIN GENERATED:DOC_SPEC
function Render-Doc {
    $shared = Join-Path $PSScriptRoot "shared"
    $tpl = Get-Content (Join-Path $shared "doc_spec.md") -Raw -Encoding UTF8
    $tpl = $tpl.Replace("{{LANG_NAME}}", "PowerShell")
    $tpl = $tpl.Replace("{{LANG_CODEBLOCK}}", "powershell")
    $tpl = $tpl.Replace("{{LANG_INVOKE}}", "powershell -ExecutionPolicy Bypass -File scripts/ziwei_cli.ps1")
    return $tpl
}
# END GENERATED:DOC_SPEC

function Parse-Args($arr) {
    $h = @{}
    $boolFlags = @("leap")
    for ($i = 0; $i -lt $arr.Count; $i++) {
        $tok = [string]$arr[$i]
        if (-not $tok.StartsWith("--")) { continue }
        $key = $tok.Substring(2)
        if ($boolFlags -contains $key) { $h[$key] = $true; continue }
        $next = if ($i + 1 -lt $arr.Count) { [string]$arr[$i + 1] } else { $null }
        if ($null -eq $next -or $next.StartsWith("--")) { $h[$key] = $true }
        else { $h[$key] = $next; $i++ }
    }
    return $h
}

function Require-Birth($a) {
    foreach ($k in @("year", "month", "day", "hour", "gender")) {
        if (-not $a.Contains($k)) { [Console]::Error.WriteLine("Error: --$k is required."); exit 1 }
    }
    if (@("male", "female") -notcontains $a["gender"]) { [Console]::Error.WriteLine("Error: --gender must be male or female."); exit 1 }
    if ($a["calendar"] -and (@("solar", "lunar") -notcontains $a["calendar"])) { [Console]::Error.WriteLine("Error: --calendar must be solar or lunar."); exit 1 }
}

$command = if ($args.Count -ge 1) { [string]$args[0] } else { $null }
$rest = if ($args.Count -ge 2) { $args[1..($args.Count - 1)] } else { @() }
$parsed = Parse-Args $rest

switch ($command) {
    "chart" { Require-Birth $parsed; Cmd-Chart $parsed }
    "transits" { Require-Birth $parsed; Cmd-Transits $parsed }
    "reading" { Require-Birth $parsed; Cmd-Reading $parsed }
    "doc" { Write-Output (Render-Doc) }
    $null { Write-Output (Render-Doc) }
    default { [Console]::Error.WriteLine("Unknown command: $command. Use one of: chart, transits, reading, doc."); exit 1 }
}
