# HeyGen AI Advanced Features v2.2 - Cleanup and Branch Creation Script
# Run this script when disk space is available to create the feature branch

Write-Host "🚀 HeyGen AI Advanced Features v2.2 - Cleanup and Branch Creation" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green

# Step 1: Clean up disk space
Write-Host "`n📁 Step 1: Cleaning up disk space..." -ForegroundColor Yellow

$directoriesToRemove = @(
    ".venv",
    "node_modules", 
    "cache_directory",
    "test-results",
    "playwright-report"
)

foreach ($dir in $directoriesToRemove) {
    if (Test-Path $dir) {
        Write-Host "Removing $dir..." -ForegroundColor Cyan
        Remove-Item -Recurse -Force $dir -ErrorAction SilentlyContinue
        if (-not (Test-Path $dir)) {
            Write-Host "✅ $dir removed successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to remove $dir" -ForegroundColor Red
        }
    } else {
        Write-Host "ℹ️  $dir not found, skipping..." -ForegroundColor Gray
    }
}

# Clean up temporary files
Write-Host "`n🧹 Cleaning up temporary files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Filter "*.json" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*report*" -or $_.Name -like "*optimization*" } | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "*.log" -Recurse -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "✅ Disk cleanup completed" -ForegroundColor Green

# Step 2: Check git status
Write-Host "`n📋 Step 2: Checking git status..." -ForegroundColor Yellow
git status --porcelain | Measure-Object | ForEach-Object { Write-Host "Found $($_.Count) modified files" -ForegroundColor Cyan }

# Step 3: Create new branch
Write-Host "`n🌿 Step 3: Creating feature branch..." -ForegroundColor Yellow
$branchName = "feature/advanced-heygen-ai-v2.2"

try {
    git checkout -b $branchName
    Write-Host "✅ Branch '$branchName' created successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create branch: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Add HeyGen AI files
Write-Host "`n📦 Step 4: Adding HeyGen AI files..." -ForegroundColor Yellow
try {
    git add agents/backend/onyx/server/features/heygen_ai/
    Write-Host "✅ HeyGen AI files added to staging" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to add files: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 5: Commit changes
Write-Host "`n💾 Step 5: Committing changes..." -ForegroundColor Yellow
$commitMessage = @"
feat: Add advanced HeyGen AI features v2.2

- Advanced Model Manager with load balancing and auto-scaling
- Performance Optimizer with automatic resource management  
- Advanced Security Manager with threat detection and encryption
- Real-time Analytics with live monitoring and dashboards
- Advanced Error Recovery with self-healing capabilities
- Enhanced requirements and comprehensive documentation
- Production-ready demo with performance testing

This update transforms HeyGen AI into an enterprise-grade platform
with advanced monitoring, security, and performance optimization.
"@

try {
    git commit -m $commitMessage
    Write-Host "✅ Changes committed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to commit: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 6: Push to remote
Write-Host "`n🚀 Step 6: Pushing to remote repository..." -ForegroundColor Yellow
try {
    git push origin $branchName
    Write-Host "✅ Branch pushed to remote successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to push: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 You may need to set up remote tracking or check your git credentials" -ForegroundColor Yellow
    exit 1
}

# Success message
Write-Host "`n🎉 SUCCESS! HeyGen AI Advanced Features v2.2 branch created!" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "Branch: $branchName" -ForegroundColor Cyan
Write-Host "Remote: origin/$branchName" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create a pull request from $branchName to main" -ForegroundColor White
Write-Host "2. Add detailed description of new features" -ForegroundColor White
Write-Host "3. Request code review from team members" -ForegroundColor White
Write-Host "4. Run tests and performance benchmarks" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "📚 Documentation: README_ADVANCED_FEATURES.md" -ForegroundColor Cyan
Write-Host "🎬 Demo: run_advanced_demo_v2.py" -ForegroundColor Cyan
Write-Host "📋 Summary: BRANCH_CREATION_SUMMARY.md" -ForegroundColor Cyan

