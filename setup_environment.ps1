# Instagram Captions API v10.0 Setup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTAGRAM CAPTIONS API v10.0 SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python is already installed" -ForegroundColor Green
        Write-Host $pythonVersion -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "✗ Python is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to continue after installing Python"
    exit 1
}

Write-Host ""
Write-Host "[2/5] Installing required packages..." -ForegroundColor Yellow
pip install fastapi uvicorn pydantic transformers torch numba orjson cachetools pyyaml

Write-Host ""
Write-Host "[3/5] Installing additional dependencies..." -ForegroundColor Yellow
pip install pytest pytest-asyncio httpx

Write-Host ""
Write-Host "[4/5] Creating virtual environment (recommended)..." -ForegroundColor Yellow
python -m venv venv
Write-Host "✓ Virtual environment created" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the virtual environment, run:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White

Write-Host ""
Write-Host "[5/5] Running basic tests..." -ForegroundColor Yellow
python test_enhanced_modules.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the API server, run:" -ForegroundColor Cyan
Write-Host "  python api_v10.py" -ForegroundColor White
Write-Host ""
Write-Host "To run tests, use:" -ForegroundColor Cyan
Write-Host "  python test_enhanced_modules.py" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue"
