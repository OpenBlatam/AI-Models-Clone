#!/bin/bash

###############################################################################
# EC2 User Data Script with Auto-Deploy Setup
# This script runs on EC2 instance launch to perform initial setup
# and configure automatic deployment from GitHub
#
# Features:
# - System updates and security hardening
# - Docker and Docker Compose installation
# - GitHub repository setup
# - Webhook listener service configuration
# - Automatic deployment on main branch commits
###############################################################################

set -euo pipefail

# Log all output
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

###############################################################################
# Configuration
###############################################################################

PROJECT_NAME="${project_name:-blatam-academy}"
ENVIRONMENT="${environment:-production}"
GITHUB_REPO="${github_repo:-}"
GITHUB_BRANCH="${github_branch:-main}"
GITHUB_TOKEN="${github_token:-}"
WEBHOOK_SECRET="${webhook_secret:-}"
PROJECT_DIR="/opt/${PROJECT_NAME}"
WEBHOOK_PORT=9000

###############################################################################
# Logging Functions
###############################################################################

log_info() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR] $1" >&2
}

log_warn() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [WARN] $1"
}

###############################################################################
# System Setup Functions
###############################################################################

update_system() {
    log_info "Updating system packages..."
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -y
    apt-get upgrade -y
}

install_essential_packages() {
    log_info "Installing essential packages..."
    apt-get install -y \
        curl \
        wget \
        git \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        build-essential \
        python3-pip \
        python3-venv \
        python3-dev \
        htop \
        net-tools \
        vim \
        jq \
        ufw \
        nginx \
        supervisor \
        openssl \
        certbot \
        python3-certbot-nginx
}

configure_firewall() {
    log_info "Configuring firewall..."
    ufw --force enable
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow 22/tcp    # SSH
    ufw allow 80/tcp    # HTTP
    ufw allow 443/tcp   # HTTPS
    ufw allow 8000/tcp  # FastAPI app
    ufw allow ${WEBHOOK_PORT}/tcp  # Webhook listener
    log_info "Firewall configured successfully"
}

install_docker() {
    log_info "Installing Docker..."
    
    if command -v docker &> /dev/null; then
        log_info "Docker is already installed."
        return 0
    fi
    
    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    
    # Set up Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt-get update -y
    apt-get install -y \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin
    
    # Add ubuntu user to docker group
    usermod -aG docker ubuntu
    
    # Start Docker service
    systemctl enable docker
    systemctl start docker
    
    log_info "Docker installed successfully."
}

install_docker_compose() {
    log_info "Installing Docker Compose..."
    
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        log_info "Docker Compose is already installed."
        return 0
    fi
    
    # Try to use docker compose plugin first
    if docker compose version &> /dev/null; then
        log_info "Docker Compose plugin is available."
        return 0
    fi
    
    # Fallback to standalone docker-compose
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | \
        grep tag_name | cut -d '"' -f 4)
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    log_info "Docker Compose installed successfully."
}

configure_timezone() {
    log_info "Configuring timezone..."
    timedatectl set-timezone UTC
}

install_cloudwatch_agent() {
    log_info "Installing CloudWatch agent..."
    wget -q https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb \
        -O /tmp/amazon-cloudwatch-agent.deb || {
        log_warn "Failed to download CloudWatch agent, skipping..."
        return 0
    }
    dpkg -i -E /tmp/amazon-cloudwatch-agent.deb || log_warn "CloudWatch agent installation had issues"
    rm -f /tmp/amazon-cloudwatch-agent.deb
}

install_aws_cli() {
    log_info "Installing AWS CLI..."
    
    if command -v aws &> /dev/null; then
        log_info "AWS CLI is already installed."
        return 0
    fi
    
    curl -q "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" \
        -o /tmp/awscliv2.zip || {
        log_error "Failed to download AWS CLI"
        return 1
    }
    
    unzip -q /tmp/awscliv2.zip -d /tmp
    /tmp/aws/install
    rm -rf /tmp/aws /tmp/awscliv2.zip
    
    log_info "AWS CLI installed successfully."
}

###############################################################################
# Application Setup Functions
###############################################################################

create_project_directory() {
    log_info "Creating application directory..."
    mkdir -p "${PROJECT_DIR}"
    chown ubuntu:ubuntu "${PROJECT_DIR}"
}

setup_github_repository() {
    if [ -z "${GITHUB_REPO}" ]; then
        log_warn "GITHUB_REPO not set, skipping repository setup"
        return 0
    fi
    
    log_info "Setting up GitHub repository..."
    cd "${PROJECT_DIR}"
    
    # Clone or update repository
    if [ -d ".git" ]; then
        log_info "Repository already exists, updating..."
        git fetch origin || log_error "Failed to fetch from origin"
        git reset --hard "origin/${GITHUB_BRANCH}" || log_error "Failed to reset to branch"
    else
        log_info "Cloning repository..."
        if [ -n "${GITHUB_TOKEN}" ]; then
            git clone "https://${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git" . || {
                log_error "Failed to clone repository"
                return 1
            }
        else
            git clone "https://github.com/${GITHUB_REPO}.git" . || {
                log_error "Failed to clone repository"
                return 1
            }
        fi
        git checkout "${GITHUB_BRANCH}" || log_warn "Failed to checkout branch"
    fi
    
    # Configure git
    git config --global user.name "EC2 Deployer" || true
    git config --global user.email "deployer@${PROJECT_NAME}.local" || true
    
    if [ -n "${GITHUB_TOKEN}" ]; then
        git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/" || true
    fi
    
    log_info "GitHub repository setup completed"
}

setup_webhook_listener_service() {
    log_info "Setting up GitHub webhook listener service..."
    
    # Ensure webhook listener script exists
    local webhook_script="${PROJECT_DIR}/aws/scripts/webhook_listener.py"
    
    if [ ! -f "${webhook_script}" ]; then
        log_warn "Webhook listener script not found at ${webhook_script}"
        log_info "The script should be deployed with the repository"
        return 0
    fi
    
    # Make script executable
    chmod +x "${webhook_script}"
    
    # Create systemd service
    cat > /etc/systemd/system/github-webhook-listener.service << EOF
[Unit]
Description=GitHub Webhook Listener for Auto-Deployment
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=${PROJECT_DIR}
Environment="GITHUB_WEBHOOK_SECRET=${WEBHOOK_SECRET}"
Environment="WEBHOOK_PORT=${WEBHOOK_PORT}"
Environment="PROJECT_DIR=${PROJECT_DIR}"
Environment="DEPLOY_SCRIPT=${PROJECT_DIR}/aws/scripts/auto_deploy.sh"
Environment="TARGET_BRANCH=${GITHUB_BRANCH}"
ExecStart=/usr/bin/python3 ${webhook_script}
Restart=always
RestartSec=10
StandardOutput=append:/var/log/github-webhook.log
StandardError=append:/var/log/github-webhook.log

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable github-webhook-listener
    systemctl start github-webhook-listener || log_warn "Failed to start webhook listener service"
    
    log_info "Webhook listener service configured"
}

setup_cron_job() {
    log_info "Setting up cron job for periodic deployment checks..."
    
    # Create deployment check script
    cat > "${PROJECT_DIR}/aws/scripts/check_and_deploy.sh" << 'EOFSCRIPT'
#!/bin/bash
# Periodic check for new commits and deploy if needed

set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/blatam-academy}"
GITHUB_BRANCH="${GITHUB_BRANCH:-main}"
LOG_FILE="/var/log/deployment-check.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

cd "${PROJECT_DIR}" || exit 1

# Check for updates
git fetch origin "${GITHUB_BRANCH}" || {
    log "ERROR: Failed to fetch from origin"
    exit 1
}

LOCAL=$(git rev-parse HEAD 2>/dev/null || echo "")
REMOTE=$(git rev-parse "origin/${GITHUB_BRANCH}" 2>/dev/null || echo "")

if [ -z "$LOCAL" ] || [ -z "$REMOTE" ]; then
    log "WARN: Could not determine commit hashes"
    exit 0
fi

if [ "$LOCAL" != "$REMOTE" ]; then
    log "INFO: New commits detected (local: ${LOCAL:0:7}, remote: ${REMOTE:0:7}), triggering deployment..."
    bash "${PROJECT_DIR}/aws/scripts/auto_deploy.sh" deploy >> "${LOG_FILE}" 2>&1
else
    log "DEBUG: No new commits detected"
fi
EOFSCRIPT

    chmod +x "${PROJECT_DIR}/aws/scripts/check_and_deploy.sh"
    
    # Add cron job (check every 5 minutes)
    (crontab -l 2>/dev/null | grep -v "check_and_deploy.sh"; \
     echo "*/5 * * * * ${PROJECT_DIR}/aws/scripts/check_and_deploy.sh >> /var/log/deployment-check.log 2>&1") | \
     crontab - || log_warn "Failed to setup cron job"
    
    log_info "Cron job configured to check for updates every 5 minutes"
}

configure_automatic_security_updates() {
    log_info "Configuring automatic security updates..."
    apt-get install -y unattended-upgrades || log_warn "Failed to install unattended-upgrades"
    
    cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF

    log_info "Automatic security updates configured"
}

run_initial_deployment() {
    local deploy_script="${PROJECT_DIR}/aws/scripts/auto_deploy.sh"
    
    if [ ! -f "${deploy_script}" ]; then
        log_warn "Deploy script not found, skipping initial deployment"
        return 0
    fi
    
    log_info "Running initial deployment..."
    chmod +x "${deploy_script}"
    
    cd "${PROJECT_DIR}"
    export GITHUB_BRANCH="${GITHUB_BRANCH}"
    export GITHUB_REPO="${GITHUB_REPO}"
    export GITHUB_TOKEN="${GITHUB_TOKEN}"
    export PROJECT_NAME="${PROJECT_NAME}"
    export PROJECT_DIR="${PROJECT_DIR}"
    
    bash "${deploy_script}" deploy || {
        log_error "Initial deployment failed"
        return 1
    }
    
    log_info "Initial deployment completed"
}

###############################################################################
# Main Execution
###############################################################################

main() {
    log_info "=========================================="
    log_info "Starting EC2 User Data Script"
    log_info "Project: ${PROJECT_NAME}"
    log_info "Environment: ${ENVIRONMENT}"
    log_info "=========================================="
    
    # System setup
    update_system
    install_essential_packages
    configure_firewall
    install_docker
    install_docker_compose
    configure_timezone
    install_cloudwatch_agent
    install_aws_cli
    
    # Application setup
    create_project_directory
    setup_github_repository
    setup_webhook_listener_service
    setup_cron_job
    configure_automatic_security_updates
    
    # Initial deployment (if repository was set up)
    if [ -n "${GITHUB_REPO}" ]; then
        run_initial_deployment
    fi
    
    # Summary
    log_info "=========================================="
    log_info "User Data Script Completed Successfully"
    log_info "=========================================="
    log_info "Services configured:"
    log_info "  - Docker: $(docker --version 2>/dev/null || echo 'Not available')"
    log_info "  - Docker Compose: $(docker-compose --version 2>/dev/null || docker compose version 2>/dev/null || echo 'Not available')"
    log_info "  - GitHub Webhook Listener: Running on port ${WEBHOOK_PORT}"
    log_info "  - Cron Job: Checking for updates every 5 minutes"
    log_info "  - GitHub Repository: ${GITHUB_REPO:-Not configured}"
    log_info "  - Branch: ${GITHUB_BRANCH}"
    log_info "=========================================="
}

# Run main function
main "$@"
