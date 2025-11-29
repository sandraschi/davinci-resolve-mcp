# DaVinci Resolve MCP - DXT Build Script
# Builds a proper DXT package with source code included

param(
    [string]$OutputDir = "dist",
    [switch]$Validate
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "Building DaVinci Resolve MCP DXT package..." -ForegroundColor Green

# Create output directory
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# Copy source code to root level of dxt directory for packaging
Write-Host "Copying source code to dxt directory..." -ForegroundColor Yellow
# Remove any existing package directories
Get-ChildItem "dxt" -Directory | Where-Object { $_.Name -ne "assets" } | Remove-Item -Recurse -Force
# Copy source code to root level
Copy-Item -Path "src\*" -Destination "dxt\" -Recurse

if (Test-Path "requirements.txt") {
    Copy-Item "requirements.txt" "dxt/requirements.txt"
}

# Build the DXT package
Write-Host "Building DXT package..." -ForegroundColor Yellow
$packageName = "davinci-resolve-mcp-0.1.0.dxt"
$outputPath = Join-Path $OutputDir $packageName

try {
    & mcpb pack dxt $outputPath
    if ($LASTEXITCODE -ne 0) {
        throw "mcpb pack failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-Host "ERROR: Failed to build DXT package - $_" -ForegroundColor Red
    exit 1
}

# Validate the package if requested
if ($Validate) {
    Write-Host "Validating DXT package..." -ForegroundColor Yellow
    try {
        & mcpb validate $outputPath
        if ($LASTEXITCODE -ne 0) {
            throw "mcpb validate failed with exit code $LASTEXITCODE"
        }
        Write-Host "✓ DXT package validation passed" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: DXT package validation failed - $_" -ForegroundColor Red
        exit 1
    }
}

# Clean up - remove copied files
Write-Host "Cleaning up temporary files..." -ForegroundColor Yellow
Get-ChildItem "dxt" -Directory | Where-Object { $_.Name -ne "assets" } | Remove-Item -Recurse -Force
if (Test-Path "dxt/requirements.txt") {
    Remove-Item "dxt/requirements.txt"
}

# Show package info
$packageInfo = Get-Item $outputPath
$sizeMB = [math]::Round($packageInfo.Length / 1MB, 2)
Write-Host "✓ DXT package built successfully!" -ForegroundColor Green
Write-Host "  Location: $outputPath" -ForegroundColor White
Write-Host "  Size: $sizeMB MB ($($packageInfo.Length) bytes)" -ForegroundColor White
Write-Host "  Files: $(& mcpb info $outputPath | Select-String -Pattern "total files:" | ForEach-Object { $_.Line -replace ".*total files: ", "" })" -ForegroundColor White
