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

Write-Host "Starting Python backend on port $BackendPort ..."
$backendProc = Start-Process -FilePath "uv" -ArgumentList "run", "python", "-m", "davinci_resolve_mcp.run_api", "--port", "$BackendPort", "--host", "127.0.0.1" -WorkingDirectory $RepoRoot -PassThru -NoNewWindow
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

Write-Host "Starting Vite frontend on port $FrontendPort ..."
Set-Location $WebSotaRoot
npm run dev
