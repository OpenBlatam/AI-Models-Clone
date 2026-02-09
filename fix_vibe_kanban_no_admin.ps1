# Fix script for vibe-kanban DLL error (0xC0000135) - No Admin Required Version
# This version can clear cache and check system status

Write-Host "Fixing vibe-kanban DLL error (No Admin Version)..." -ForegroundColor Cyan
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
Write-Host "Checking for Visual C++ Redistributables..." -ForegroundColor Cyan

# Function to check if a program is installed
function Test-InstalledProgram {
    param([string]$DisplayName)
    try {
        $installed = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -like "*$DisplayName*" }
        return $null -ne $installed
    } catch {
        return $false
    }
}

$vc2015_2022_x64 = Test-InstalledProgram "Microsoft Visual C++ 2015-2022 Redistributable (x64)"
$vc2015_2022_x86 = Test-InstalledProgram "Microsoft Visual C++ 2015-2022 Redistributable (x86)"

if ($vc2015_2022_x64 -and $vc2015_2022_x86) {
    Write-Host "SUCCESS: Visual C++ Redistributables are installed." -ForegroundColor Green
} else {
    Write-Host "WARNING: Missing Visual C++ Redistributables detected." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To fix the DLL error, please install:" -ForegroundColor Yellow
    if (-not $vc2015_2022_x64) {
        Write-Host "   - Visual C++ 2015-2022 Redistributable (x64): https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Cyan
    }
    if (-not $vc2015_2022_x86) {
        Write-Host "   - Visual C++ 2015-2022 Redistributable (x86): https://aka.ms/vs/17/release/vc_redist.x86.exe" -ForegroundColor Cyan
    }
    Write-Host ""
    Write-Host "Or run the full fix script as Administrator:" -ForegroundColor Yellow
    Write-Host "   powershell -ExecutionPolicy Bypass -File C:\blatam-academy\fix_vibe_kanban.ps1" -ForegroundColor White
}

Write-Host ""
Write-Host "SUCCESS: Fix script completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Try running vibe-kanban again:" -ForegroundColor Cyan
Write-Host "   npx vibe-kanban" -ForegroundColor White















