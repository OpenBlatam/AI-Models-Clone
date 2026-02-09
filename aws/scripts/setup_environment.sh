#!/bin/bash

###############################################################################
# Environment Setup Script
# Sets up local development environment for AWS deployment
###############################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed."
        return 1
    fi
    return 0
}

main() {
    log_info "Setting up AWS deployment environment..."
    
    # Check prerequisites
    log_info "Checking prerequisites..."
    MISSING_DEPS=()
    
    check_command "aws" || MISSING_DEPS+=("aws-cli")
    check_command "terraform" || MISSING_DEPS+=("terraform")
    check_command "ansible" || MISSING_DEPS+=("ansible")
    
    if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${MISSING_DEPS[*]}"
        log_info "Install instructions:"
        for dep in "${MISSING_DEPS[@]}"; do
            case $dep in
                "aws-cli")
                    echo "  AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
                    ;;
                "terraform")
                    echo "  Terraform: https://learn.hashicorp.com/tutorials/terraform/install-cli"
                    ;;
                "ansible")
                    echo "  Ansible: pip install ansible boto3"
                    ;;
            esac
        done
        exit 1
    fi
    
    log_info "All prerequisites are installed."
    
    # Configure AWS credentials
    if [ ! -f ~/.aws/credentials ]; then
        log_info "AWS credentials not found. Please run 'aws configure'"
    else
        log_info "AWS credentials found."
    fi
    
    # Create SSH key if it doesn't exist
    if [ ! -f ~/.ssh/blatam-academy-key.pem ]; then
        log_info "SSH key not found. Creating one..."
        log_info "Please create an AWS key pair named 'blatam-academy-key' in the AWS console"
        log_info "Then download it and save to ~/.ssh/blatam-academy-key.pem"
        log_info "Set permissions: chmod 400 ~/.ssh/blatam-academy-key.pem"
    else
        log_info "SSH key found."
    fi
    
    # Install Ansible collections
    log_info "Installing Ansible collections..."
    ansible-galaxy collection install amazon.aws community.general || true
    
    log_info "Environment setup completed!"
}

main "$@"

