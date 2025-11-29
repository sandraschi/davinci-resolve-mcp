#!/usr/bin/env pwsh
# Auto-generated fix script for davinci-resolve-mcp
# Generated: 2025-10-25_23-56-29
# Issues to fix: 3

param([switch]$DryRun = $false)

Write-Host '🔧 Fixing Repository Standards...' -ForegroundColor Cyan
if ($DryRun) { Write-Host '🔍 DRY RUN MODE' -ForegroundColor Yellow }

$centralDocs = 'D:\Dev\repos\mcp-central-docs'

# Fix: Create assets/icon.svg

# Fix: Create .github/workflows/release.yml from central docs template
if (-not (Test-Path '.github/workflows/release.yml')) {
    if (Test-Path "$centralDocs/templates/.github/workflows/release.yml") {
        Copy-Item "$centralDocs/templates/.github/workflows/release.yml" '.github/workflows/release.yml' -Force
        Write-Host '  ✅ Copied: .github/workflows/release.yml' -ForegroundColor Green
    }
}

# Fix: Create .github/workflows/ci.yml from central docs template
if (-not (Test-Path '.github/workflows/ci.yml')) {
    if (Test-Path "$centralDocs/templates/.github/workflows/ci.yml") {
        Copy-Item "$centralDocs/templates/.github/workflows/ci.yml" '.github/workflows/ci.yml' -Force
        Write-Host '  ✅ Copied: .github/workflows/ci.yml' -ForegroundColor Green
    }
}

Write-Host '✅ Fix script complete!' -ForegroundColor Green
