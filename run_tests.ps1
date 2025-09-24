# DaVinci Resolve MCP - PowerShell Test Runner
# This script runs the test suite for the DaVinci Resolve MCP package

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("unit", "integration", "all")]
    [string]$TestType = "all",

    [Parameter(Mandatory=$false)]
    [switch]$Coverage,

    [Parameter(Mandatory=$false)]
    [switch]$Detailed,

    [Parameter(Mandatory=$false)]
    [string]$PythonPath = "python",

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

# Function to run command and check exit code
function Invoke-CommandChecked {
    param(
        [string]$Command,
        [string]$Description
    )

    Write-Colored "Running: $Description" -Color Yellow
    Write-Colored "Command: $Command" -Color Gray

    try {
        Invoke-Expression $Command
        if ($LASTEXITCODE -ne 0) {
            Write-Colored "ERROR: Command failed with exit code $LASTEXITCODE" -Color Red
            exit $LASTEXITCODE
        }
    }
    catch {
        Write-Colored "ERROR: $_" -Color Red
        exit 1
    }
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
    if (Test-Path "test_results.xml") {
        Remove-Item "test_results.xml"
    }
}

# Check if Python is available
try {
    $pythonVersion = & $PythonPath --version 2>$null
    Write-Colored "Using Python: $pythonVersion" -Color Green
}
catch {
    Write-Colored "ERROR: Python not found at '$PythonPath'" -Color Red
    Write-Colored "Please ensure Python is installed and in PATH, or specify -PythonPath" -Color Yellow
    exit 1
}

# Build pytest command
$pytestCmd = "& $PythonPath -m pytest"

# Add test type filter
switch ($TestType) {
    "unit" {
        $pytestCmd += " tests/unit/"
        Write-Colored "Running unit tests only" -Color Cyan
    }
    "integration" {
        $pytestCmd += " tests/integration/"
        Write-Colored "Running integration tests only" -Color Cyan
    }
    "all" {
        $pytestCmd += " tests/"
        Write-Colored "Running all tests" -Color Cyan
    }
}

# Add coverage if requested
if ($Coverage) {
    $pytestCmd += " --cov=src/davinci_resolve_mcp --cov-report=html --cov-report=term --cov-fail-under=50"
    Write-Colored "Coverage reporting enabled (50% minimum)" -Color Cyan
}

# Add detailed output if requested
if ($Detailed) {
    $pytestCmd += " -v"
}

# Add other pytest options
$pytestCmd += " --tb=short --strict-markers"

# Run the tests
Write-Colored "Starting test execution..." -Color Green
Write-Colored ("=" * 60) -Color White

Invoke-CommandChecked $pytestCmd "Test Suite Execution"

Write-Colored ("=" * 60) -Color White
Write-Colored "All tests completed successfully!" -Color Green

# Show coverage report location if coverage was enabled
if ($Coverage -and (Test-Path "coverage_html")) {
    Write-Colored "Coverage report available at: $(Resolve-Path 'coverage_html/index.html')" -Color Green
}
