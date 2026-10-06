Param([switch]$Headless, [switch]$BackendOnly)
# davinci-resolve-mcp launcher (fleet standard shape)
# Backend :10843 (api_app) + frontend :10842. Clears port zombies, waits for
# backend health before opening the UI.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$BackendPort = 10843
$FrontendPort = 10842

# --- Port zombie clearing (backend) ---
$zombie = Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique
foreach ($procId in $zombie) {
  try { Stop-Process -Id $procId -Force -ErrorAction Stop; Write-Host "Cleared port zombie PID $procId" } catch {}
}

# --- Backend (uvicorn api_app, hidden window) ---
$Uv = 'C:\Users\sandr\.local\bin\uv.exe'
$backend = Start-Process -FilePath $Uv -ArgumentList 'run', 'uvicorn',
  'davinci_resolve_mcp.server:api_app', '--host', '127.0.0.1', '--port', "$BackendPort" `
  -WindowStyle Hidden -PassThru

# --- Backend readiness: TCP poll, 30 x 1s (no fixed sleep) ---
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
  try {
    $r = Invoke-WebRequest "http://127.0.0.1:$BackendPort/api/v1/health" -UseBasicParsing -TimeoutSec 2
    if ($r.StatusCode -eq 200) { $ready = $true; break }
  } catch { Start-Sleep -Seconds 1 }
}
if (-not $ready) {
  Write-Host "Backend did not answer /api/v1/health on :$BackendPort within 30s" -ForegroundColor Red
  exit 1
}
Write-Host "Backend ready on :$BackendPort" -ForegroundColor Green

if ($BackendOnly) { exit 0 }

# --- Frontend ---
Set-Location (Join-Path $PSScriptRoot 'web_sota')
if ($Headless) {
  npm run dev -- --host 127.0.0.1 --port $FrontendPort
} else {
  Start-Process -FilePath 'npm' -ArgumentList 'run', 'dev', '--', '--host', '127.0.0.1', '--port', "$FrontendPort"
  Start-Sleep -Seconds 3
  Start-Process "http://127.0.0.1:$FrontendPort"
}
