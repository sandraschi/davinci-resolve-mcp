# DaVinci Resolve MCP - Integration Test Runner
# This script runs integration tests for the DaVinci Resolve MCP package

param(
    [Parameter(Mandatory=$false)]
    [string]$PythonPath = "python",

    [Parameter(Mandatory=$false)]
    [switch]$DaVinciResolve,

    [Parameter(Mandatory=$false)]
    [switch]$Clean
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Function to write colored output
function Write-Colored {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Clean previous test results if requested
if ($Clean) {
    Write-Colored "Cleaning previous test results..." -Color Yellow
    if (Test-Path ".pytest_cache") {
        Remove-Item -Recurse -Force ".pytest_cache"
    }
    if (Test-Path "coverage_html") {
        Remove-Item -Recurse -Force "coverage_html"
    }
    if (Test-Path ".coverage") {
        Remove-Item ".coverage"
    }
}

# Check if DaVinci Resolve is running (if requested)
if ($DaVinciResolve) {
    Write-Colored "Checking DaVinci Resolve status..." -Color Yellow
    try {
        $resolveCheck = & $PythonPath check_resolve_running.py 2>$null
        if ($resolveCheck -match "DaVinci Resolve is running") {
            Write-Colored "✓ DaVinci Resolve is running" -Color Green
        } else {
            Write-Colored "⚠ DaVinci Resolve not detected - integration tests may fail" -Color Yellow
        }
    }
    catch {
        Write-Colored "⚠ Could not check DaVinci Resolve status" -Color Yellow
    }
}

# Run integration tests
Write-Colored "Running integration tests..." -Color Green
Write-Colored ("=" * 60) -Color White

$pytestCmd = "& $PythonPath -m pytest tests/integration/ -v --tb=short --strict-markers"

try {
    Invoke-Expression $pytestCmd
    if ($LASTEXITCODE -ne 0) {
        Write-Colored "ERROR: Integration tests failed with exit code $LASTEXITCODE" -Color Red
        exit $LASTEXITCODE
    }
}
catch {
    Write-Colored "ERROR: $_" -Color Red
    exit 1
}

Write-Colored ("=" * 60) -Color White
Write-Colored "Integration tests completed successfully!" -Color Green

# Provide guidance on what integration tests validate
Write-Colored "Integration tests validated:" -Color Cyan
Write-Colored "  • End-to-end tool workflows" -Color White
Write-Colored "  • Cross-component interactions" -Color White
Write-Colored "  • API compatibility" -Color White
Write-Colored "  • Error handling in real scenarios" -Color White
