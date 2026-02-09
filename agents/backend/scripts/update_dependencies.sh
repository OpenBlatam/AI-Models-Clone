#!/bin/bash

# Dependency Update Script for Blatam Academy Backend
# This script safely updates dependencies with testing and rollback capabilities

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REQUIREMENTS_DIR="$PROJECT_ROOT/requirements"
BACKUP_DIR="$PROJECT_ROOT/backups"
LOG_FILE="$PROJECT_ROOT/logs/dependency_update.log"
DATE=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Create necessary directories
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Function to backup requirements files
backup_requirements() {
    log "Creating backup of current requirements..."
    
    BACKUP_PATH="$BACKUP_DIR/requirements_backup_$DATE"
    mkdir -p "$BACKUP_PATH"
    
    for req_file in "$REQUIREMENTS_DIR"/*.txt; do
        if [ -f "$req_file" ]; then
            cp "$req_file" "$BACKUP_PATH/"
            log "Backed up $(basename "$req_file")"
        fi
    done
    
    echo "$BACKUP_PATH"
}

# Function to check if safety is installed
check_safety() {
    if ! command -v safety &> /dev/null; then
        warning "Safety is not installed. Installing..."
        pip install safety
    fi
}

# Function to check for vulnerabilities
check_vulnerabilities() {
    log "Checking for vulnerabilities in current dependencies..."
    
    if command -v safety &> /dev/null; then
        safety check -r "$REQUIREMENTS_DIR/default.txt" || {
            warning "Vulnerabilities found in current dependencies"
            return 1
        }
        success "No vulnerabilities found in current dependencies"
    else
        warning "Safety not available, skipping vulnerability check"
    fi
}

# Function to update a specific requirements file
update_requirements_file() {
    local req_file="$1"
    local update_type="$2"  # "patch", "minor", "major"
    
    log "Updating $req_file ($update_type updates)..."
    
    # Create temporary file
    local temp_file=$(mktemp)
    
    # Read current requirements and update versions
    while IFS= read -r line; do
        if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "$line" ]]; then
            # Comment or empty line, keep as is
            echo "$line" >> "$temp_file"
        elif [[ "$line" =~ ^[[:space:]]*-r ]]; then
            # Include directive, keep as is
            echo "$line" >> "$temp_file"
        elif [[ "$line" =~ ^([^=]+)==([0-9]+)\.([0-9]+)\.([0-9]+) ]]; then
            # Versioned requirement
            package="${BASH_REMATCH[1]}"
            major="${BASH_REMATCH[2]}"
            minor="${BASH_REMATCH[3]}"
            patch="${BASH_REMATCH[4]}"
            
            case "$update_type" in
                "patch")
                    # Update patch version only
                    new_version="$major.$minor.$((patch + 1))"
                    ;;
                "minor")
                    # Update minor version
                    new_version="$major.$((minor + 1)).0"
                    ;;
                "major")
                    # Update major version (be more conservative)
                    new_version="$((major + 1)).0.0"
                    ;;
                *)
                    error "Invalid update type: $update_type"
                    return 1
                    ;;
            esac
            
            echo "$package==$new_version" >> "$temp_file"
            log "Updated $package to $new_version"
        else
            # Other format, keep as is
            echo "$line" >> "$temp_file"
        fi
    done < "$req_file"
    
    # Replace original file
    mv "$temp_file" "$req_file"
    success "Updated $req_file"
}

# Function to install and test dependencies
install_and_test() {
    log "Installing updated dependencies..."
    
    # Install production dependencies
    pip install -r "$REQUIREMENTS_DIR/default.txt" || {
        error "Failed to install production dependencies"
        return 1
    }
    
    # Install all dependencies for testing
    pip install -r "$REQUIREMENTS_DIR/combined.txt" || {
        error "Failed to install all dependencies"
        return 1
    }
    
    # Run tests if available
    if [ -d "$PROJECT_ROOT/tests" ]; then
        log "Running tests..."
        cd "$PROJECT_ROOT"
        python -m pytest tests/ -v --tb=short || {
            error "Tests failed after dependency update"
            return 1
        }
        success "All tests passed"
    else
        warning "No tests directory found, skipping tests"
    fi
}

# Function to rollback changes
rollback() {
    local backup_path="$1"
    
    error "Rolling back to backup: $backup_path"
    
    for req_file in "$backup_path"/*.txt; do
        if [ -f "$req_file" ]; then
            filename=$(basename "$req_file")
            cp "$req_file" "$REQUIREMENTS_DIR/$filename"
            log "Restored $filename"
        fi
    done
    
    success "Rollback completed"
}

# Function to generate dependency report
generate_report() {
    log "Generating dependency analysis report..."
    
    cd "$PROJECT_ROOT"
    python scripts/dependency_analyzer.py . --output "dependency_report_$DATE.md" || {
        warning "Failed to generate dependency report"
    }
}

# Main update function
update_dependencies() {
    local update_type="${1:-patch}"  # Default to patch updates
    local files_to_update="${2:-default.txt}"  # Default to production dependencies
    
    log "Starting dependency update process..."
    log "Update type: $update_type"
    log "Files to update: $files_to_update"
    
    # Check prerequisites
    check_safety
    
    # Check current vulnerabilities
    check_vulnerabilities || {
        warning "Proceeding despite vulnerabilities..."
    }
    
    # Create backup
    local backup_path=$(backup_requirements)
    log "Backup created at: $backup_path"
    
    # Update specified files
    IFS=',' read -ra FILES <<< "$files_to_update"
    for file in "${FILES[@]}"; do
        file_path="$REQUIREMENTS_DIR/$file"
        if [ -f "$file_path" ]; then
            update_requirements_file "$file_path" "$update_type" || {
                error "Failed to update $file"
                rollback "$backup_path"
                exit 1
            }
        else
            error "Requirements file not found: $file_path"
            rollback "$backup_path"
            exit 1
        fi
    done
    
    # Install and test
    install_and_test || {
        error "Installation or testing failed"
        rollback "$backup_path"
        exit 1
    }
    
    # Generate report
    generate_report
    
    success "Dependency update completed successfully!"
    log "Backup available at: $backup_path"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE       Update type: patch, minor, major (default: patch)"
    echo "  -f, --files FILES     Comma-separated list of files to update (default: default.txt)"
    echo "  -c, --check-only      Only check for vulnerabilities, don't update"
    echo "  -r, --report-only     Only generate dependency report"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Update production dependencies (patch)"
    echo "  $0 -t minor                          # Update production dependencies (minor)"
    echo "  $0 -f default.txt,dev.txt            # Update specific files"
    echo "  $0 -c                                # Check vulnerabilities only"
    echo "  $0 -r                                # Generate report only"
}

# Parse command line arguments
CHECK_ONLY=false
REPORT_ONLY=false
UPDATE_TYPE="patch"
FILES_TO_UPDATE="default.txt"

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            UPDATE_TYPE="$2"
            shift 2
            ;;
        -f|--files)
            FILES_TO_UPDATE="$2"
            shift 2
            ;;
        -c|--check-only)
            CHECK_ONLY=true
            shift
            ;;
        -r|--report-only)
            REPORT_ONLY=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate update type
if [[ ! "$UPDATE_TYPE" =~ ^(patch|minor|major)$ ]]; then
    error "Invalid update type: $UPDATE_TYPE. Must be patch, minor, or major."
    exit 1
fi

# Main execution
if [ "$CHECK_ONLY" = true ]; then
    log "Running vulnerability check only..."
    check_safety
    check_vulnerabilities
elif [ "$REPORT_ONLY" = true ]; then
    log "Generating dependency report only..."
    generate_report
else
    update_dependencies "$UPDATE_TYPE" "$FILES_TO_UPDATE"
fi

success "Script completed successfully!" 