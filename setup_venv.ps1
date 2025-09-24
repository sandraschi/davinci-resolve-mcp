# DaVinci Resolve MCP - Virtual Environment Setup Script
# This script creates and configures a Python virtual environment for the DaVinci Resolve MCP server

param(
    [string]$PythonVersion = "3.8",
    [string]$VenvName = "davinci_resolve_mcp_env",
    [switch]$InstallPackage,
    [switch]$TestInstallation
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

# Check if Python is installed
function Test-Python {
    try {
        $pythonVersion = & python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Colored "✓ Python found: $pythonVersion" -Color Green
            return $true
        }
    }
    catch {
        # Try python3
        try {
            $pythonVersion = & python3 --version 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Colored "✓ Python found: $pythonVersion" -Color Green
                return $true
            }
        }
        catch {
            Write-Colored "✗ Python not found. Please install Python $PythonVersion or later." -Color Red
            return $false
        }
    }
    return $false
}

# Create virtual environment
function New-VirtualEnvironment {
    param([string]$VenvPath)

    Write-Colored "Creating virtual environment: $VenvPath" -Color Yellow

    if (Test-Path $VenvPath) {
        Write-Colored "Virtual environment already exists. Removing..." -Color Yellow
        Remove-Item -Recurse -Force $VenvPath
    }

    try {
        & python -m venv $VenvPath
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
        Write-Colored "✓ Virtual environment created successfully" -Color Green
        return $true
    }
    catch {
        Write-Colored "✗ Failed to create virtual environment: $_" -Color Red
        return $false
    }
}

# Activate virtual environment and install dependencies
function Install-Dependencies {
    param([string]$VenvPath)

    Write-Colored "Activating virtual environment and installing dependencies..." -Color Yellow

    try {
        # Activate virtual environment
        $activateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
        if (!(Test-Path $activateScript)) {
            throw "Virtual environment activation script not found"
        }

        # Install dependencies
        $pipPath = Join-Path $VenvPath "Scripts\pip.exe"
        if (!(Test-Path $pipPath)) {
            throw "pip not found in virtual environment"
        }

        # Upgrade pip first
        Write-Colored "Upgrading pip..." -Color Yellow
        & $pipPath install --upgrade pip
        if ($LASTEXITCODE -ne 0) {
            Write-Colored "Warning: Failed to upgrade pip, continuing..." -Color Yellow
        }

        # Install the package
        if ($InstallPackage) {
            Write-Colored "Installing DaVinci Resolve MCP package..." -Color Yellow
            & $pipPath install -e .
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to install package"
            }
        } else {
            Write-Colored "Installing dependencies from requirements.txt..." -Color Yellow
            & $pipPath install -r requirements.txt
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to install dependencies"
            }
        }

        Write-Colored "✓ Dependencies installed successfully" -Color Green
        return $true
    }
    catch {
        Write-Colored "✗ Failed to install dependencies: $_" -Color Red
        return $false
    }
}

# Test installation
function Test-Installation {
    param([string]$VenvPath)

    Write-Colored "Testing installation..." -Color Yellow

    try {
        $pythonPath = Join-Path $VenvPath "Scripts\python.exe"
        if (!(Test-Path $pythonPath)) {
            throw "Python executable not found in virtual environment"
        }

        # Test basic import
        $testScript = @"
import sys
sys.path.insert(0, '.')
try:
    import davinci_resolve_mcp
    print("SUCCESS: Package imported successfully")
    print(f"Version: {davinci_resolve_mcp.__version__}")
except ImportError as e:
    print(f"FAILED: Import error - {e}")
    sys.exit(1)
"@

        $testResult = & $pythonPath -c $testScript
        if ($LASTEXITCODE -ne 0) {
            throw "Package import test failed"
        }

        Write-Colored "✓ Installation test passed" -Color Green
        Write-Colored $testResult -Color Green
        return $true
    }
    catch {
        Write-Colored "✗ Installation test failed: $_" -Color Red
        return $false
    }
}

# Main execution
function Main {
    Write-Colored "DaVinci Resolve MCP - Virtual Environment Setup" -Color Cyan
    Write-Colored "=" * 50 -Color Cyan

    # Check Python
    if (!(Test-Python)) {
        exit 1
    }

    # Create virtual environment
    $venvPath = Join-Path (Get-Location) $VenvName
    if (!(New-VirtualEnvironment -VenvPath $venvPath)) {
        exit 1
    }

    # Install dependencies
    if (!(Install-Dependencies -VenvPath $venvPath)) {
        exit 1
    }

    # Test installation if requested
    if ($TestInstallation) {
        if (!(Test-Installation -VenvPath $venvPath)) {
            exit 1
        }
    }

    # Print activation instructions
    Write-Colored "`nSetup completed successfully!" -Color Green
    Write-Colored "To activate the virtual environment, run:" -Color Cyan
    Write-Colored "    $VenvName\Scripts\Activate.ps1" -Color White
    Write-Colored "`nTo run the DaVinci Resolve MCP server:" -Color Cyan
    Write-Colored "    davinci-resolve-mcp mcp" -Color White
    Write-Colored "`nTo check the environment:" -Color Cyan
    Write-Colored "    davinci-resolve-mcp check" -Color White
}

# Run main function
Main
