# Setup script for Instagram Captions API Documentation System
# This script helps set up the Python environment and install dependencies

Write-Host "========================================" -ForegroundColor Green
Write-Host "Instagram Captions API Documentation Setup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not available"
    }
} catch {
    Write-Host "Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing Python, run this script again" -ForegroundColor Yellow
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""

# Check if pip is available
try {
    $pipVersion = pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "pip found: $pipVersion" -ForegroundColor Green
    } else {
        throw "pip not available"
    }
} catch {
    Write-Host "pip is not available" -ForegroundColor Red
    Write-Host "Please ensure pip is installed with Python" -ForegroundColor Yellow
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""

# Install required dependencies
Write-Host "Installing required dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install dependencies"
    }
} catch {
    Write-Host "Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""
Write-Host "Dependencies installed successfully!" -ForegroundColor Green
Write-Host ""

# Test the documentation system
Write-Host "Testing the documentation system..." -ForegroundColor Yellow
try {
    python test_docs.py
    if ($LASTEXITCODE -ne 0) {
        throw "Tests failed"
    }
} catch {
    Write-Host ""
    Write-Host "Tests failed. Please check the error messages above." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now use the documentation system:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Generate Instagram API docs:" -ForegroundColor Cyan
Write-Host "   python generate_docs.py" -ForegroundColor White
Write-Host ""
Write-Host "2. Use the CLI interface:" -ForegroundColor Cyan
Write-Host "   python cli.py --help" -ForegroundColor White
Write-Host ""
Write-Host "3. Run tests:" -ForegroundColor Cyan
Write-Host "   python test_docs.py" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to continue"






