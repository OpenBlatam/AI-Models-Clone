# Script para instalar Python en Windows
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Instalador de Python para Robot Movement AI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Python ya está instalado
$pythonInstalled = $false
$pythonCheck = python --version 2>&1
if ($pythonCheck -match "Python") {
    Write-Host "✓ Python ya está instalado: $pythonCheck" -ForegroundColor Green
    $pythonInstalled = $true
}

if ($pythonInstalled) {
    Write-Host ""
    Write-Host "Python está listo para usar!" -ForegroundColor Green
    exit 0
}

Write-Host "Python no está instalado. Intentando instalar..." -ForegroundColor Yellow
Write-Host ""

# Opción 1: Intentar con winget (Windows Package Manager)
Write-Host "Opción 1: Intentando instalar con winget..." -ForegroundColor Cyan
$wingetResult = $false
$wingetCheck = winget --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ winget está disponible" -ForegroundColor Green
    Write-Host "Instalando Python 3.11..." -ForegroundColor Yellow
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Python instalado exitosamente con winget!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Por favor, cierra y vuelve a abrir la terminal para usar Python." -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "✗ La instalación con winget falló" -ForegroundColor Red
    }
} else {
    Write-Host "✗ winget no está disponible" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Instalación Manual Requerida" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opciones para instalar Python:" -ForegroundColor Yellow
Write-Host ""
Write-Host "OPCIÓN 1 - Microsoft Store (Más fácil):" -ForegroundColor Green
Write-Host "  1. Abre Microsoft Store"
Write-Host "  2. Busca 'Python 3.11' o 'Python 3.12'"
Write-Host "  3. Haz clic en 'Obtener' o 'Instalar'"
Write-Host ""
Write-Host "OPCIÓN 2 - Descarga directa:" -ForegroundColor Green
Write-Host "  1. Ve a: https://www.python.org/downloads/"
Write-Host "  2. Descarga Python 3.11 o 3.12 (Windows installer 64-bit)"
Write-Host "  3. Ejecuta el instalador"
Write-Host "  4. IMPORTANTE: Marca 'Add Python to PATH' durante la instalación"
Write-Host ""
Write-Host "OPCIÓN 3 - Usar el comando de Windows:" -ForegroundColor Green
Write-Host "  Ejecuta este comando en PowerShell:"
Write-Host "  python" -ForegroundColor Cyan
Write-Host "  (Esto abrirá Microsoft Store para instalar Python)"
Write-Host ""
Write-Host "Después de instalar, cierra y vuelve a abrir esta terminal." -ForegroundColor Yellow
Write-Host ""

# Intentar abrir Microsoft Store
$response = Read-Host "¿Quieres abrir Microsoft Store ahora? (S/N)"
if ($response -eq "S" -or $response -eq "s" -or $response -eq "Y" -or $response -eq "y") {
    Start-Process "ms-windows-store://pdp/?ProductId=9NRWMJP3717K"
    Write-Host "Microsoft Store abierto. Busca 'Python 3.11' e instálalo." -ForegroundColor Green
}
