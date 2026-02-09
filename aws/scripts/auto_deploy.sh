#!/bin/bash

###############################################################################
# Auto-Deployment Script for EC2
# This script runs on EC2 instance to automatically deploy updates from GitHub
# It can be triggered via webhook, cron, or manually
###############################################################################

set -euo pipefail

# Configuration
PROJECT_NAME="${PROJECT_NAME:-blatam-academy}"
PROJECT_DIR="/opt/${PROJECT_NAME}"
GITHUB_REPO="${GITHUB_REPO:-}"
GITHUB_BRANCH="${GITHUB_BRANCH:-main}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
LOG_FILE="/var/log/${PROJECT_NAME}-deploy.log"
LOCK_FILE="/tmp/${PROJECT_NAME}-deploy.lock"
HEALTH_CHECK_URL="http://localhost:8000/health"
HEALTH_CHECK_TIMEOUT=60

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

###############################################################################
# Logging Functions
###############################################################################

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "${LOG_FILE}"
}

log_info() {
    log "INFO" "${GREEN}${@}${NC}"
}

log_warn() {
    log "WARN" "${YELLOW}${@}${NC}"
}

log_error() {
    log "ERROR" "${RED}${@}${NC}"
}

log_debug() {
    log "DEBUG" "${BLUE}${@}${NC}"
}

###############################################################################
# Lock Management
###############################################################################

acquire_lock() {
    if [ -f "${LOCK_FILE}" ]; then
        local pid=$(cat "${LOCK_FILE}")
        if ps -p "${pid}" > /dev/null 2>&1; then
            log_warn "Deployment already in progress (PID: ${pid})"
            return 1
        else
            log_warn "Stale lock file found, removing..."
            rm -f "${LOCK_FILE}"
        fi
    fi
    
    echo $$ > "${LOCK_FILE}"
    log_info "Lock acquired (PID: $$)"
    return 0
}

release_lock() {
    if [ -f "${LOCK_FILE}" ]; then
        rm -f "${LOCK_FILE}"
        log_info "Lock released"
    fi
}

cleanup() {
    release_lock
    log_info "Deployment script completed"
}

trap cleanup EXIT INT TERM

###############################################################################
# Validation Functions
###############################################################################

validate_prerequisites() {
    log_info "Validating prerequisites..."
    
    local errors=0
    
    # Check if project directory exists
    if [ ! -d "${PROJECT_DIR}" ]; then
        log_error "Project directory not found: ${PROJECT_DIR}"
        errors=$((errors + 1))
    fi
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        errors=$((errors + 1))
    elif ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        errors=$((errors + 1))
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        errors=$((errors + 1))
    fi
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed"
        errors=$((errors + 1))
    fi
    
    if [ $errors -gt 0 ]; then
        log_error "Prerequisites validation failed"
        return 1
    fi
    
    log_info "Prerequisites validated successfully"
    return 0
}

###############################################################################
# Git Operations
###############################################################################

setup_git_repo() {
    log_info "Setting up Git repository..."
    
    cd "${PROJECT_DIR}"
    
    # Initialize git if not already a repository
    if [ ! -d ".git" ]; then
        log_info "Initializing Git repository..."
        git init
        
        if [ -n "${GITHUB_REPO}" ]; then
            git remote add origin "https://github.com/${GITHUB_REPO}.git" || \
            git remote set-url origin "https://github.com/${GITHUB_REPO}.git"
        fi
    fi
    
    # Configure git if token is provided
    if [ -n "${GITHUB_TOKEN}" ]; then
        git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
    fi
    
    # Fetch latest changes
    log_info "Fetching latest changes from ${GITHUB_BRANCH}..."
    git fetch origin "${GITHUB_BRANCH}" || {
        log_error "Failed to fetch from GitHub"
        return 1
    }
}

pull_latest_code() {
    log_info "Pulling latest code from GitHub..."
    
    cd "${PROJECT_DIR}"
    
    # Get current commit
    local current_commit=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    log_info "Current commit: ${current_commit}"
    
    # Pull latest changes
    git fetch origin "${GITHUB_BRANCH}"
    git reset --hard "origin/${GITHUB_BRANCH}"
    git clean -fd
    
    # Get new commit
    local new_commit=$(git rev-parse HEAD)
    log_info "New commit: ${new_commit}"
    
    if [ "${current_commit}" == "${new_commit}" ]; then
        log_info "No new changes detected"
        return 1
    fi
    
    log_info "Code updated successfully"
    return 0
}

###############################################################################
# Docker Operations
###############################################################################

build_docker_images() {
    log_info "Building Docker images..."
    
    cd "${PROJECT_DIR}"
    
    # Determine docker-compose command
    local compose_cmd="docker-compose"
    if ! command -v docker-compose &> /dev/null; then
        compose_cmd="docker compose"
    fi
    
    # Build images
    ${compose_cmd} build --no-cache || {
        log_error "Failed to build Docker images"
        return 1
    }
    
    log_info "Docker images built successfully"
}

stop_containers() {
    log_info "Stopping existing containers..."
    
    cd "${PROJECT_DIR}"
    
    local compose_cmd="docker-compose"
    if ! command -v docker-compose &> /dev/null; then
        compose_cmd="docker compose"
    fi
    
    ${compose_cmd} down --remove-orphans || {
        log_warn "Some containers may not have stopped cleanly"
    }
    
    log_info "Containers stopped"
}

start_containers() {
    log_info "Starting containers..."
    
    cd "${PROJECT_DIR}"
    
    local compose_cmd="docker-compose"
    if ! command -v docker-compose &> /dev/null; then
        compose_cmd="docker compose"
    fi
    
    ${compose_cmd} up -d || {
        log_error "Failed to start containers"
        return 1
    }
    
    log_info "Containers started successfully"
}

###############################################################################
# Health Check
###############################################################################

health_check() {
    log_info "Performing health check..."
    
    local attempts=0
    local max_attempts=$((HEALTH_CHECK_TIMEOUT / 5))
    
    while [ $attempts -lt $max_attempts ]; do
        if curl -f -s "${HEALTH_CHECK_URL}" > /dev/null 2>&1; then
            log_info "Health check passed!"
            return 0
        fi
        
        attempts=$((attempts + 1))
        log_debug "Health check attempt ${attempts}/${max_attempts} failed, retrying..."
        sleep 5
    done
    
    log_error "Health check failed after ${max_attempts} attempts"
    return 1
}

###############################################################################
# Rollback
###############################################################################

rollback() {
    log_warn "Rolling back to previous version..."
    
    cd "${PROJECT_DIR}"
    
    # Get previous commit
    local previous_commit=$(git rev-parse HEAD~1 2>/dev/null || echo "")
    
    if [ -z "${previous_commit}" ]; then
        log_error "Cannot rollback: no previous commit found"
        return 1
    fi
    
    # Checkout previous commit
    git reset --hard "${previous_commit}"
    
    # Rebuild and restart
    build_docker_images
    stop_containers
    start_containers
    
    # Health check
    if health_check; then
        log_info "Rollback successful"
        return 0
    else
        log_error "Rollback failed health check"
        return 1
    fi
}

###############################################################################
# Main Deployment Function
###############################################################################

deploy() {
    log_info "Starting deployment process..."
    log_info "Project: ${PROJECT_NAME}"
    log_info "Directory: ${PROJECT_DIR}"
    log_info "Branch: ${GITHUB_BRANCH}"
    
    # Acquire lock
    if ! acquire_lock; then
        log_error "Could not acquire lock. Another deployment may be in progress."
        exit 1
    fi
    
    # Validate prerequisites
    if ! validate_prerequisites; then
        log_error "Prerequisites validation failed"
        exit 1
    fi
    
    # Setup git repository
    setup_git_repo
    
    # Pull latest code
    if ! pull_latest_code; then
        log_info "No changes detected. Skipping deployment."
        exit 0
    fi
    
    # Build Docker images
    if ! build_docker_images; then
        log_error "Failed to build Docker images"
        exit 1
    fi
    
    # Stop containers
    stop_containers
    
    # Start containers
    if ! start_containers; then
        log_error "Failed to start containers. Attempting rollback..."
        rollback || exit 1
        exit 1
    fi
    
    # Health check
    if ! health_check; then
        log_error "Health check failed. Attempting rollback..."
        rollback || exit 1
        exit 1
    fi
    
    log_info "Deployment completed successfully!"
    
    # Clean up old Docker images
    log_info "Cleaning up old Docker images..."
    docker image prune -f > /dev/null 2>&1 || true
}

###############################################################################
# Script Entry Point
###############################################################################

main() {
    case "${1:-deploy}" in
        deploy)
            deploy
            ;;
        rollback)
            rollback
            ;;
        health-check)
            health_check
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|health-check}"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"



