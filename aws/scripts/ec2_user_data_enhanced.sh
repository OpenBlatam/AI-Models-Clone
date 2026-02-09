#!/bin/bash

###############################################################################
# Enhanced EC2 User Data Script
# This script runs on EC2 instance launch to perform initial setup
# Includes automatic GitHub integration for deployments
###############################################################################

set -euo pipefail

# Log all output
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

PROJECT_NAME="${project_name:-blatam-academy}"
ENVIRONMENT="${environment:-production}"
GITHUB_REPO="${github_repo:-}"
GITHUB_BRANCH="${github_branch:-main}"

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
# System Update
###############################################################################

log_info "Starting EC2 instance initialization..."
log_info "Project: ${PROJECT_NAME}"
log_info "Environment: ${ENVIRONMENT}"

log_info "Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get upgrade -y

###############################################################################
# Install Essential Packages
###############################################################################

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
    fail2ban \
    logrotate \
    supervisor

###############################################################################
# Configure Firewall
###############################################################################

log_info "Configuring firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # FastAPI (if needed)

###############################################################################
# Install Docker
###############################################################################

log_info "Installing Docker..."
if ! command -v docker &> /dev/null; then
    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    
    # Set up Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Add ubuntu user to docker group
    usermod -aG docker ubuntu
    
    # Start Docker service
    systemctl enable docker
    systemctl start docker
    
    log_success "Docker installed successfully."
else
    log_info "Docker is already installed."
fi

###############################################################################
# Install Docker Compose (standalone)
###############################################################################

log_info "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    log_success "Docker Compose installed successfully."
else
    log_info "Docker Compose is already installed."
fi

###############################################################################
# Install Node.js and npm (if needed for frontend)
###############################################################################

log_info "Installing Node.js..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    log_success "Node.js installed successfully."
else
    log_info "Node.js is already installed."
fi

###############################################################################
# Configure Timezone
###############################################################################

log_info "Configuring timezone..."
timedatectl set-timezone UTC

###############################################################################
# Install CloudWatch Agent
###############################################################################

log_info "Installing CloudWatch agent..."
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb -O /tmp/amazon-cloudwatch-agent.deb
dpkg -i -E /tmp/amazon-cloudwatch-agent.deb || true
rm /tmp/amazon-cloudwatch-agent.deb

# Configure CloudWatch agent
mkdir -p /opt/aws/amazon-cloudwatch-agent/etc
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json <<EOF
{
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/user-data.log",
                        "log_group_name": "/aws/ec2/${PROJECT_NAME}/user-data",
                        "log_stream_name": "{instance_id}"
                    },
                    {
                        "file_path": "/var/log/app-deploy.log",
                        "log_group_name": "/aws/ec2/${PROJECT_NAME}/deployment",
                        "log_stream_name": "{instance_id}"
                    },
                    {
                        "file_path": "/var/log/github-deploy.log",
                        "log_group_name": "/aws/ec2/${PROJECT_NAME}/github-deploy",
                        "log_stream_name": "{instance_id}"
                    }
                ]
            }
        }
    },
    "metrics": {
        "namespace": "${PROJECT_NAME}/${ENVIRONMENT}",
        "metrics_collected": {
            "cpu": {
                "measurement": [
                    "cpu_usage_idle",
                    "cpu_usage_iowait",
                    "cpu_usage_user",
                    "cpu_usage_system"
                ],
                "totalcpu": false
            },
            "disk": {
                "measurement": [
                    "used_percent"
                ],
                "resources": [
                    "*"
                ]
            },
            "diskio": {
                "measurement": [
                    "io_time"
                ],
                "resources": [
                    "*"
                ]
            },
            "mem": {
                "measurement": [
                    "mem_used_percent"
                ]
            }
        }
    }
}
EOF

systemctl enable amazon-cloudwatch-agent
systemctl start amazon-cloudwatch-agent || true

###############################################################################
# Create Application Directory
###############################################################################

log_info "Creating application directory..."
APP_DIR="/opt/${PROJECT_NAME}"
mkdir -p "${APP_DIR}"
chown ubuntu:ubuntu "${APP_DIR}"

# Create backup directory
mkdir -p "/opt/${PROJECT_NAME}-backups"
chown ubuntu:ubuntu "/opt/${PROJECT_NAME}-backups"

###############################################################################
# Setup GitHub Integration
###############################################################################

if [ -n "${GITHUB_REPO}" ]; then
    log_info "Setting up GitHub integration..."
    log_info "Repository: ${GITHUB_REPO}"
    log_info "Branch: ${GITHUB_BRANCH}"
    
    cd "${APP_DIR}"
    
    # Clone repository (using HTTPS - can be configured to use SSH key)
    # Note: For private repos, you'll need to configure GitHub token or SSH key
    if [ ! -d ".git" ]; then
        log_info "Cloning repository..."
        # Use GitHub token if available from AWS Secrets Manager
        # For now, using public repo or configure SSH key
        git clone "https://github.com/${GITHUB_REPO}.git" . || {
            log_error "Failed to clone repository. Configure GitHub access."
        }
    fi
    
    # Checkout specified branch
    if [ -d ".git" ]; then
        git fetch origin
        git checkout "${GITHUB_BRANCH}" || git checkout -b "${GITHUB_BRANCH}" "origin/${GITHUB_BRANCH}"
        log_success "Repository setup complete"
    fi
fi

###############################################################################
# Install AWS CLI
###############################################################################

log_info "Installing AWS CLI..."
if ! command -v aws &> /dev/null; then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscliv2.zip
    unzip -q /tmp/awscliv2.zip -d /tmp
    /tmp/aws/install
    rm -rf /tmp/aws /tmp/awscliv2.zip
    log_success "AWS CLI installed successfully."
else
    log_info "AWS CLI is already installed."
fi

###############################################################################
# Setup Automatic Security Updates
###############################################################################

log_info "Configuring automatic security updates..."
apt-get install -y unattended-upgrades
cat > /etc/apt/apt.conf.d/50unattended-upgrades <<EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}-security";
    "\${distro_id}ESMApps:\${distro_codename}-apps-security";
    "\${distro_id}ESM:\${distro_codename}-infra-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

cat > /etc/apt/apt.conf.d/20auto-upgrades <<EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Download-Upgradeable-Packages "1";
EOF

###############################################################################
# Setup Fail2Ban
###############################################################################

log_info "Configuring Fail2Ban..."
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
EOF

systemctl enable fail2ban
systemctl start fail2ban

###############################################################################
# Setup Log Rotation
###############################################################################

log_info "Configuring log rotation..."
cat > /etc/logrotate.d/${PROJECT_NAME} <<EOF
/var/log/app-deploy.log
/var/log/github-deploy.log
/opt/${PROJECT_NAME}/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 ubuntu ubuntu
}
EOF

###############################################################################
# Make deployment script executable
###############################################################################

if [ -f "${APP_DIR}/aws/scripts/deploy_app.sh" ]; then
    chmod +x "${APP_DIR}/aws/scripts/deploy_app.sh"
    log_info "Deployment script is ready"
fi

###############################################################################
# Initial Application Deployment
###############################################################################

if [ -f "${APP_DIR}/aws/scripts/deploy_app.sh" ]; then
    log_info "Running initial application deployment..."
    cd "${APP_DIR}"
    sudo -u ubuntu bash aws/scripts/deploy_app.sh || {
        log_error "Initial deployment failed, but continuing..."
    }
fi

###############################################################################
# Final Steps
###############################################################################

log_success "EC2 instance initialization completed successfully!"
log_info "Project: ${PROJECT_NAME}"
log_info "Environment: ${ENVIRONMENT}"
log_info "Application directory: ${APP_DIR}"
log_info "Instance is ready for use."

# Create a marker file to indicate initialization is complete
touch /opt/.ec2-initialized
echo "Initialized at: $(date)" > /opt/.ec2-initialized
echo "Project: ${PROJECT_NAME}" >> /opt/.ec2-initialized
echo "Environment: ${ENVIRONMENT}" >> /opt/.ec2-initialized



