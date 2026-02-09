# Fix script for vibe-kanban DLL error (0xC0000135)
# This error typically indicates missing Visual C++ Redistributables

Write-Host "Fixing vibe-kanban DLL error..." -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "WARNING: This script requires administrator privileges to install Visual C++ Redistributables." -ForegroundColor Yellow
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Try installing Visual C++ Redistributables manually:" -ForegroundColor Yellow
    Write-Host "   - Visual C++ 2015-2022 Redistributable (x64): https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Yellow
    Write-Host "   - Visual C++ 2015-2022 Redistributable (x86): https://aka.ms/vs/17/release/vc_redist.x86.exe" -ForegroundColor Yellow
    exit 1
}

# Function to check if a program is installed
function Test-InstalledProgram {
    param([string]$DisplayName)
    $installed = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Where-Object { $_.DisplayName -like "*$DisplayName*" }
    return $null -ne $installed
}

# Check for Visual C++ Redistributables
Write-Host "Checking for Visual C++ Redistributables..." -ForegroundColor Cyan
$vc2015_2022_x64 = Test-InstalledProgram "Microsoft Visual C++ 2015-2022 Redistributable (x64)"
$vc2015_2022_x86 = Test-InstalledProgram "Microsoft Visual C++ 2015-2022 Redistributable (x86)"

if ($vc2015_2022_x64 -and $vc2015_2022_x86) {
    Write-Host "SUCCESS: Visual C++ Redistributables are already installed." -ForegroundColor Green
} else {
    Write-Host "ERROR: Missing Visual C++ Redistributables detected." -ForegroundColor Red
    Write-Host ""
    Write-Host "Downloading and installing Visual C++ Redistributables..." -ForegroundColor Cyan
    
    $tempDir = $env:TEMP
    $vcRedist_x64 = "$tempDir\vc_redist.x64.exe"
    $vcRedist_x86 = "$tempDir\vc_redist.x86.exe"
    
    try {
        # Download x64 version
        if (-not $vc2015_2022_x64) {
            Write-Host "Downloading Visual C++ 2015-2022 Redistributable (x64)..." -ForegroundColor Yellow
            Invoke-WebRequest -Uri "https://aka.ms/vs/17/release/vc_redist.x64.exe" -OutFile $vcRedist_x64 -UseBasicParsing
            Write-Host "Installing Visual C++ 2015-2022 Redistributable (x64)..." -ForegroundColor Yellow
            Start-Process -FilePath $vcRedist_x64 -ArgumentList "/install", "/quiet", "/norestart" -Wait -NoNewWindow
            Write-Host "SUCCESS: x64 Redistributable installed." -ForegroundColor Green
        }
        
        # Download x86 version
        if (-not $vc2015_2022_x86) {
            Write-Host "Downloading Visual C++ 2015-2022 Redistributable (x86)..." -ForegroundColor Yellow
            Invoke-WebRequest -Uri "https://aka.ms/vs/17/release/vc_redist.x86.exe" -OutFile $vcRedist_x86 -UseBasicParsing
            Write-Host "Installing Visual C++ 2015-2022 Redistributable (x86)..." -ForegroundColor Yellow
            Start-Process -FilePath $vcRedist_x86 -ArgumentList "/install", "/quiet", "/norestart" -Wait -NoNewWindow
            Write-Host "SUCCESS: x86 Redistributable installed." -ForegroundColor Green
        }
        
        # Cleanup
        if (Test-Path $vcRedist_x64) { Remove-Item $vcRedist_x64 -Force }
        if (Test-Path $vcRedist_x86) { Remove-Item $vcRedist_x86 -Force }
        
    } catch {
        Write-Host "ERROR: Error installing Redistributables: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install manually:" -ForegroundColor Yellow
        Write-Host "   - x64: https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Yellow
        Write-Host "   - x86: https://aka.ms/vs/17/release/vc_redist.x86.exe" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "Additional troubleshooting steps:" -ForegroundColor Cyan
Write-Host ""

# Clear npx cache for vibe-kanban
Write-Host "Clearing npx cache for vibe-kanban..." -ForegroundColor Yellow
$npxCache = "$env:LOCALAPPDATA\npm-cache\_npx"
if (Test-Path $npxCache) {
    $vibeKanbanCache = Get-ChildItem -Path $npxCache -Directory | Where-Object { Test-Path (Join-Path $_.FullName "node_modules\vibe-kanban") }
    if ($vibeKanbanCache) {
        Remove-Item -Path $vibeKanbanCache.FullName -Recurse -Force
        Write-Host "SUCCESS: Cleared npx cache for vibe-kanban." -ForegroundColor Green
    } else {
        Write-Host "INFO: No vibe-kanban cache found to clear." -ForegroundColor Gray
    }
} else {
    Write-Host "INFO: npx cache directory not found." -ForegroundColor Gray
}

Write-Host ""
Write-Host "SUCCESS: Fix script completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Try running vibe-kanban again:" -ForegroundColor Cyan
Write-Host "   npx vibe-kanban" -ForegroundColor White
Write-Host ""
Write-Host "If the issue persists, try:" -ForegroundColor Yellow
Write-Host "   1. Restart your computer" -ForegroundColor White
Write-Host "   2. Check Windows Event Viewer for more details" -ForegroundColor White
Write-Host "   3. Try running: npx --yes vibe-kanban" -ForegroundColor White
Write-Host "   4. Check if your antivirus is blocking the executable" -ForegroundColor White
