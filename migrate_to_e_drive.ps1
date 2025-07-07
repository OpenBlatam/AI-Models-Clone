# Migration Script: C to E Drive (10GB Project)
# This script migrates the blatam-academy project from C: to E: drive

param(
    [string]$SourcePath = "C:\Users\USER\blatam-academy",
    [string]$DestinationPath = "E:\blatam-academy",
    [switch]$DryRun = $false,
    [switch]$SkipBackup = $false
)

# Set error action preference
$ErrorActionPreference = "Continue"

# Function to write colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Function to format file size
function Format-FileSize {
    param([long]$Size)
    if ($Size -gt 1GB) {
        return "{0:N2} GB" -f ($Size / 1GB)
    } elseif ($Size -gt 1MB) {
        return "{0:N2} MB" -f ($Size / 1MB)
    } elseif ($Size -gt 1KB) {
        return "{0:N2} KB" -f ($Size / 1KB)
    } else {
        return "$Size bytes"
    }
}

# Function to calculate directory size
function Get-DirectorySize {
    param([string]$Path)
    try {
        $size = (Get-ChildItem -Path $Path -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        return $size
    } catch {
        return 0
    }
}

# Function to create backup
function Create-Backup {
    param([string]$SourcePath, [string]$BackupPath)
    Write-ColorOutput "Creating backup at: $BackupPath" "Yellow"
    
    try {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupName = "blatam-academy_backup_$timestamp"
        $fullBackupPath = Join-Path $BackupPath $backupName
        
        if (!(Test-Path $BackupPath)) {
            New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
        }
        
        Write-ColorOutput "Starting backup process..." "Yellow"
        robocopy $SourcePath $fullBackupPath /MIR /R:3 /W:10 /MT:8 /LOG:"$BackupPath\backup_log.txt" /TEE
        
        if ($LASTEXITCODE -le 7) {
            Write-ColorOutput "Backup completed successfully!" "Green"
            return $fullBackupPath
        } else {
            Write-ColorOutput "Backup completed with warnings (Exit code: $LASTEXITCODE)" "Yellow"
            return $fullBackupPath
        }
    } catch {
        Write-ColorOutput "Backup failed: $($_.Exception.Message)" "Red"
        return $null
    }
}

# Main migration function
function Start-Migration {
    Write-ColorOutput "=== BLATAM ACADEMY MIGRATION SCRIPT ===" "Cyan"
    Write-ColorOutput "Source: $SourcePath" "White"
    Write-ColorOutput "Destination: $DestinationPath" "White"
    Write-ColorOutput "Dry Run: $DryRun" "White"
    Write-ColorOutput "=====================================" "Cyan"
    
    # Check if source exists
    if (!(Test-Path $SourcePath)) {
        Write-ColorOutput "ERROR: Source path does not exist: $SourcePath" "Red"
        exit 1
    }
    
    # Check destination drive space
    $driveE = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq "E:" }
    if ($driveE) {
        $freeSpaceGB = [math]::Round($driveE.FreeSpace / 1GB, 2)
        Write-ColorOutput "Drive E free space: $freeSpaceGB GB" "Green"
        
        if ($freeSpaceGB -lt 15) {
            Write-ColorOutput "WARNING: Less than 15GB free space on drive E!" "Yellow"
            $continue = Read-Host "Do you want to continue? (y/N)"
            if ($continue -ne "y" -and $continue -ne "Y") {
                Write-ColorOutput "Migration cancelled by user." "Yellow"
                exit 0
            }
        }
    } else {
        Write-ColorOutput "ERROR: Drive E not found!" "Red"
        exit 1
    }
    
    # Calculate source size
    Write-ColorOutput "Calculating source directory size..." "Yellow"
    $sourceSize = Get-DirectorySize -Path $SourcePath
    $sourceSizeFormatted = Format-FileSize -Size $sourceSize
    Write-ColorOutput "Source size: $sourceSizeFormatted" "Green"
    
    # Create backup if not skipped
    $backupPath = $null
    if (!$SkipBackup -and !$DryRun) {
        $backupDrive = "E:\backups"
        $backupPath = Create-Backup -SourcePath $SourcePath -BackupPath $backupDrive
        if (!$backupPath) {
            Write-ColorOutput "ERROR: Backup failed. Migration aborted." "Red"
            exit 1
        }
    }
    
    # Perform migration
    if ($DryRun) {
        Write-ColorOutput "=== DRY RUN MODE ===" "Yellow"
        Write-ColorOutput "This is a simulation. No files will be moved." "Yellow"
        
        # Simulate the migration process
        Write-ColorOutput "Would copy from: $SourcePath" "White"
        Write-ColorOutput "Would copy to: $DestinationPath" "White"
        Write-ColorOutput "Total size to migrate: $sourceSizeFormatted" "White"
        
        # Show what would be copied
        $files = Get-ChildItem -Path $SourcePath -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object
        Write-ColorOutput "Total files and directories: $($files.Count)" "White"
        
    } else {
        Write-ColorOutput "Starting migration process..." "Green"
        
        # Create destination directory
        if (!(Test-Path $DestinationPath)) {
            New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null
            Write-ColorOutput "Created destination directory: $DestinationPath" "Green"
        }
        
        # Use robocopy for efficient copying
        Write-ColorOutput "Copying files using robocopy..." "Yellow"
        $logFile = "E:\migration_log.txt"
        
        robocopy $SourcePath $DestinationPath /MIR /R:3 /W:10 /MT:8 /LOG:$logFile /TEE /NP
        
        $exitCode = $LASTEXITCODE
        
        # Check robocopy exit codes
        if ($exitCode -le 7) {
            Write-ColorOutput "Migration completed successfully!" "Green"
            
            # Verify migration
            Write-ColorOutput "Verifying migration..." "Yellow"
            $destSize = Get-DirectorySize -Path $DestinationPath
            $destSizeFormatted = Format-FileSize -Size $destSize
            
            Write-ColorOutput "Source size: $sourceSizeFormatted" "White"
            Write-ColorOutput "Destination size: $destSizeFormatted" "White"
            
            if ($destSize -eq $sourceSize) {
                Write-ColorOutput "Size verification: PASSED" "Green"
            } else {
                Write-ColorOutput "Size verification: FAILED - Sizes don't match!" "Red"
            }
            
            # Create migration summary
            $summary = @"
=== MIGRATION SUMMARY ===
Date: $(Get-Date)
Source: $SourcePath
Destination: $DestinationPath
Source Size: $sourceSizeFormatted
Destination Size: $destSizeFormatted
Backup Location: $backupPath
Log File: $logFile
Exit Code: $exitCode
Status: $(if ($exitCode -le 7) { "SUCCESS" } else { "WARNINGS" })
"@
            
            $summary | Out-File -FilePath "E:\migration_summary.txt" -Encoding UTF8
            Write-ColorOutput "Migration summary saved to: E:\migration_summary.txt" "Green"
            
        } else {
            Write-ColorOutput "Migration completed with errors (Exit code: $exitCode)" "Red"
            Write-ColorOutput "Check log file: $logFile" "Yellow"
        }
    }
    
    Write-ColorOutput "=== MIGRATION PROCESS COMPLETED ===" "Cyan"
}

# Execute migration
try {
    Start-Migration
} catch {
    Write-ColorOutput "FATAL ERROR: $($_.Exception.Message)" "Red"
    Write-ColorOutput "Stack trace: $($_.ScriptStackTrace)" "Red"
    exit 1
} 