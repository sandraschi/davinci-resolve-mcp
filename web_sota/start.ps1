# Start SOTA webapp: backend on 10843, then Vite on 10842.
# Run from repo root: .\web_sota\start.ps1   OR from web_sota: .\start.ps1
$BackendPort = 10843
$FrontendPort = 10842
$ApiHealth = "http://127.0.0.1:$BackendPort/api/v1/health"
$MaxWaitSec = 30

if (Test-Path (Join-Path $PSScriptRoot "package.json")) {
    $WebSotaRoot = $PSScriptRoot
    $RepoRoot = Split-Path -Parent $WebSotaRoot
} else {
    $RepoRoot = $PSScriptRoot
    $WebSotaRoot = Join-Path $RepoRoot "web_sota"
}

function Stop-PortProcess {
    param([int]$Port)
    $conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($conn) {
        $procId = $conn.OwningProcess | Select-Object -First 1 -Unique
        if ($procId) {
            Write-Host "Stopping process on port $Port (PID: $procId)"
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
        }
    }
}

Write-Host "Checking for port squatters on $FrontendPort and $BackendPort..."
Stop-PortProcess -Port $BackendPort
Stop-PortProcess -Port $FrontendPort

# Prefer .venv\python.exe -m ... so we do not run `uv sync` (which replaces Scripts\davinci-resolve-mcp.exe).
# That step fails with Windows error 32 if Cursor/MCP or another instance still loads that .exe.
$venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
Write-Host "Starting Python backend on port $BackendPort ..."
if (Test-Path $venvPython) {
    $backendProc = Start-Process -FilePath $venvPython `
        -ArgumentList "-m", "davinci_resolve_mcp.run_api", "--port", "$BackendPort", "--host", "127.0.0.1" `
        -WorkingDirectory $RepoRoot -PassThru -NoNewWindow
} else {
    $env:UV_NO_SYNC = "1"
    $backendProc = Start-Process -FilePath "uv" `
        -ArgumentList "run", "python", "-m", "davinci_resolve_mcp.run_api", "--port", "$BackendPort", "--host", "127.0.0.1" `
        -WorkingDirectory $RepoRoot -PassThru -NoNewWindow
}
$env:PORT = "$BackendPort"
$env:HOST = "127.0.0.1"

$waited = 0
$BackendStarted = $false
while ($waited -lt $MaxWaitSec) {
    try {
        $r = Invoke-WebRequest -Uri $ApiHealth -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($r.StatusCode -eq 200) {
            $BackendStarted = $true
            Write-Host "Backend ready at $ApiHealth"
            break
        }
    } catch {
        if (-not $backendProc.HasExited) { Start-Sleep -Seconds 2 }
        $waited += 2
    }
}
if (-not $BackendStarted) {
    Write-Host "WARNING: Backend did not respond at $ApiHealth within ${MaxWaitSec}s. Frontend may see proxy errors."
}

# 4b. Launch background task to open browser once frontend is ready (Auto-opened by Antigravity)
$frontendUrl = "http://127.0.0.1:$FrontendPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
Set-Location $WebSotaRoot
npm run dev
