#!/bin/bash

###############################################################################
# Application Deployment Script
# This script is executed on EC2 instance to deploy/update the application
# Called automatically by GitHub Actions or manually
###############################################################################

set -euo pipefail

# Log all output
exec > >(tee /var/log/app-deploy.log|logger -t app-deploy -s 2>/dev/console) 2>&1

PROJECT_NAME="blatam-academy"
APP_DIR="/opt/${PROJECT_NAME}"
ENVIRONMENT="${ENVIRONMENT:-production}"

log_info() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR] $1" >&2
}

log_success() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [SUCCESS] $1"
}

###############################################################################
# Pre-deployment checks
###############################################################################

log_info "Starting application deployment..."
log_info "Project: ${PROJECT_NAME}"
log_info "Environment: ${ENVIRONMENT}"
log_info "Application directory: ${APP_DIR}"

# Check if application directory exists
if [ ! -d "${APP_DIR}" ]; then
    log_error "Application directory ${APP_DIR} does not exist!"
    exit 1
fi

cd "${APP_DIR}"

# Check if git repository
if [ ! -d ".git" ]; then
    log_error "Not a git repository!"
    exit 1
fi

###############################################################################
# Backup current deployment
###############################################################################

log_info "Creating backup of current deployment..."
BACKUP_DIR="/opt/${PROJECT_NAME}-backups"
mkdir -p "${BACKUP_DIR}"
BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"

if [ -d "${APP_DIR}" ]; then
    tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" -C "${APP_DIR}" . 2>/dev/null || true
    log_info "Backup created: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
    
    # Keep only last 5 backups
    ls -t "${BACKUP_DIR}"/*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
fi

###############################################################################
# Update application code
###############################################################################

log_info "Updating application code from Git..."

# Fetch latest changes
git fetch origin

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
log_info "Current branch: ${CURRENT_BRANCH}"

# Pull latest changes
git pull origin "${CURRENT_BRANCH}" || {
    log_error "Failed to pull latest changes"
    exit 1
}

# Get current commit
CURRENT_COMMIT=$(git rev-parse HEAD)
log_info "Deployed commit: ${CURRENT_COMMIT}"

###############################################################################
# Install/Update Python dependencies
###############################################################################

if [ -f "requirements.txt" ]; then
    log_info "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip --quiet
    
    # Install dependencies
    pip install -r requirements.txt --quiet
    
    log_success "Python dependencies installed"
fi

# Install backend-specific dependencies if they exist
if [ -f "agents/backend/onyx/server/requirements.txt" ]; then
    log_info "Installing backend dependencies..."
    pip install -r agents/backend/onyx/server/requirements.txt --quiet
fi

###############################################################################
# Setup environment variables
###############################################################################

log_info "Setting up environment variables..."

# Create .env file from example if it doesn't exist
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    log_info "Creating .env file from .env.example..."
    cp .env.example .env
fi

# Load environment variables from AWS Systems Manager Parameter Store (if configured)
if command -v aws &> /dev/null; then
    log_info "Loading environment variables from AWS Parameter Store..."
    
    # Try to get parameters (this will fail silently if not configured)
    aws ssm get-parameters-by-path \
        --path "/${PROJECT_NAME}/${ENVIRONMENT}/" \
        --recursive \
        --with-decryption \
        --query 'Parameters[*].[Name,Value]' \
        --output text 2>/dev/null | \
    while read name value; do
        key=$(basename "$name")
        echo "export ${key}=${value}" >> "${APP_DIR}/.env.aws"
    done || true
    
    if [ -f "${APP_DIR}/.env.aws" ]; then
        source "${APP_DIR}/.env.aws"
        log_info "Loaded environment variables from AWS"
    fi
fi

###############################################################################
# Build and deploy FastAPI application
###############################################################################

# Check if this is a FastAPI application
if [ -f "agents/backend/onyx/server/main.py" ] || [ -f "api/main.py" ]; then
    log_info "Detected FastAPI application, setting up..."
    
    # Find main.py
    if [ -f "agents/backend/onyx/server/main.py" ]; then
        APP_MAIN="agents/backend/onyx/server/main.py"
        APP_DIR_REL="agents/backend/onyx/server"
    elif [ -f "api/main.py" ]; then
        APP_MAIN="api/main.py"
        APP_DIR_REL="api"
    fi
    
    log_info "FastAPI application found: ${APP_MAIN}"
    
    # Create systemd service if it doesn't exist
    SYSTEMD_SERVICE="/etc/systemd/system/${PROJECT_NAME}.service"
    if [ ! -f "${SYSTEMD_SERVICE}" ]; then
        log_info "Creating systemd service..."
        
        cat > "${SYSTEMD_SERVICE}" <<EOF
[Unit]
Description=Blatam Academy FastAPI Application
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=${APP_DIR}/${APP_DIR_REL}
Environment="PATH=${APP_DIR}/venv/bin"
ExecStart=${APP_DIR}/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
        
        systemctl daemon-reload
        systemctl enable "${PROJECT_NAME}.service"
        log_success "Systemd service created"
    fi
    
    # Restart service
    log_info "Restarting application service..."
    systemctl restart "${PROJECT_NAME}.service"
    
    # Wait for service to start
    sleep 5
    
    # Check service status
    if systemctl is-active --quiet "${PROJECT_NAME}.service"; then
        log_success "Application service is running"
    else
        log_error "Application service failed to start"
        systemctl status "${PROJECT_NAME}.service" || true
        exit 1
    fi
fi

###############################################################################
# Docker Compose deployment (alternative)
###############################################################################

if [ -f "docker-compose.yml" ] || [ -f "aws/docker-compose.yml" ]; then
    log_info "Detected Docker Compose configuration..."
    
    COMPOSE_FILE="docker-compose.yml"
    [ -f "aws/docker-compose.yml" ] && COMPOSE_FILE="aws/docker-compose.yml"
    
    log_info "Using Docker Compose file: ${COMPOSE_FILE}"
    
    # Pull latest images
    docker-compose -f "${COMPOSE_FILE}" pull || true
    
    # Rebuild and restart services
    docker-compose -f "${COMPOSE_FILE}" up -d --build
    
    log_success "Docker Compose services restarted"
fi

###############################################################################
# Run database migrations (if applicable)
###############################################################################

if [ -f "alembic.ini" ] || [ -d "migrations" ]; then
    log_info "Running database migrations..."
    
    if [ -f "venv/bin/alembic" ]; then
        source venv/bin/activate
        alembic upgrade head || log_error "Migration failed (non-critical)"
    fi
fi

###############################################################################
# Health check
###############################################################################

log_info "Performing health check..."

# Wait a bit for services to be ready
sleep 5

# Check if application is responding
HEALTH_ENDPOINTS=("http://localhost:8000/health" "http://localhost/health" "http://localhost:8000/")
HEALTH_OK=false

for endpoint in "${HEALTH_ENDPOINTS[@]}"; do
    if curl -f -s --max-time 5 "${endpoint}" > /dev/null 2>&1; then
        log_success "Health check passed: ${endpoint}"
        HEALTH_OK=true
        break
    fi
done

if [ "$HEALTH_OK" = false ]; then
    log_error "Health check failed - application may not be responding"
    # Don't exit with error as the service might still be starting
fi

###############################################################################
# Cleanup
###############################################################################

log_info "Cleaning up..."

# Remove old Python cache
find "${APP_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${APP_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true

# Remove old logs (keep last 7 days)
find /var/log -name "*${PROJECT_NAME}*" -type f -mtime +7 -delete 2>/dev/null || true

###############################################################################
# Deployment complete
###############################################################################

log_success "Deployment completed successfully!"
log_info "Commit: ${CURRENT_COMMIT}"
log_info "Branch: ${CURRENT_BRANCH}"
log_info "Time: $(date)"

# Send notification (optional - can integrate with SNS, Slack, etc.)
# aws sns publish --topic-arn "arn:aws:sns:..." --message "Deployment completed" || true

exit 0



