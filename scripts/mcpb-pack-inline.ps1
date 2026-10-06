#Requires -Version 5.1
<#
  mcpb-pack-inline.ps1 — MCPB fresh-stage for davinci-resolve-mcp.
  Wipes mcpb/src/ and recopies src/ so the bundle never ships a stale twin,
  validates manifest.json, then packs via the MCPB CLI when available.
  Final packing is also possible via the Anthropic DXT desktop app
  (validate, then pack — never init/publish).
#>
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Stage = Join-Path $RepoRoot 'mcpb\src'

if (Test-Path $Stage) { Remove-Item -Recurse -Force $Stage }
New-Item -ItemType Directory -Force -Path $Stage | Out-Null
Copy-Item (Join-Path $RepoRoot 'src\*') $Stage -Recurse -Force
Write-Host "Staged fresh copy: src/ -> mcpb/src/" -ForegroundColor Green

$manifest = Get-Content (Join-Path $RepoRoot 'manifest.json') -Raw | ConvertFrom-Json
Write-Host ("manifest: {0} v{1} main={2}" -f $manifest.name, $manifest.version, $manifest.main)

$packCmd = Get-Command 'mcpb' -ErrorAction SilentlyContinue
if ($null -eq $packCmd) {
  Write-Host 'Staging done. No `mcpb` CLI on PATH — finish with the DXT desktop app (validate, then pack).' -ForegroundColor Yellow
  exit 0
}
& mcpb pack $RepoRoot
