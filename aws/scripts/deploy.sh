#!/bin/bash

###############################################################################
# Deployment Script for Blatam Academy
# This script automates the deployment process to AWS EC2 instances
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TERRAFORM_DIR="${SCRIPT_DIR}/../terraform"
ANSIBLE_DIR="${SCRIPT_DIR}/../ansible"

# Default values
ENVIRONMENT="${ENVIRONMENT:-production}"
DEPLOY_INFRASTRUCTURE="${DEPLOY_INFRASTRUCTURE:-false}"
DEPLOY_APPLICATION="${DEPLOY_APPLICATION:-true}"

###############################################################################
# Helper Functions
###############################################################################

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

###############################################################################
# Validation
###############################################################################

validate_prerequisites() {
    log_info "Validating prerequisites..."
    
    check_command "aws"
    check_command "terraform"
    check_command "ansible"
    check_command "ansible-inventory"
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    
    log_info "Prerequisites validated successfully."
}

###############################################################################
# Infrastructure Deployment
###############################################################################

deploy_infrastructure() {
    if [ "${DEPLOY_INFRASTRUCTURE}" != "true" ]; then
        log_info "Skipping infrastructure deployment."
        return 0
    fi
    
    log_info "Deploying infrastructure with Terraform..."
    
    cd "${TERRAFORM_DIR}"
    
    # Initialize Terraform
    if [ ! -d ".terraform" ]; then
        log_info "Initializing Terraform..."
        terraform init
    fi
    
    # Plan deployment
    log_info "Planning Terraform deployment..."
    terraform plan -out=tfplan
    
    # Apply deployment
    log_info "Applying Terraform deployment..."
    read -p "Do you want to proceed with infrastructure deployment? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply tfplan
        log_info "Infrastructure deployed successfully."
    else
        log_warn "Infrastructure deployment cancelled."
        return 1
    fi
}

###############################################################################
# Application Deployment
###############################################################################

deploy_application() {
    if [ "${DEPLOY_APPLICATION}" != "true" ]; then
        log_info "Skipping application deployment."
        return 0
    fi
    
    log_info "Deploying application with Ansible..."
    
    cd "${ANSIBLE_DIR}"
    
    # Update EC2 inventory
    log_info "Updating EC2 inventory..."
    ansible-inventory -i inventory/ec2.ini --list > /dev/null || {
        log_error "Failed to update EC2 inventory. Check AWS credentials and filters."
        exit 1
    }
    
    # Run deployment playbook
    log_info "Running deployment playbook..."
    ansible-playbook \
        -i inventory/ec2.ini \
        playbooks/deploy.yml \
        -e "environment=${ENVIRONMENT}" \
        --ask-become-pass
    
    log_info "Application deployed successfully."
}

###############################################################################
# Health Check
###############################################################################

health_check() {
    log_info "Performing health check..."
    
    cd "${ANSIBLE_DIR}"
    
    ansible-playbook \
        -i inventory/ec2.ini \
        --tags health_check \
        playbooks/deploy.yml \
        -e "environment=${ENVIRONMENT}" || {
        log_warn "Health check failed. Please verify manually."
        return 1
    }
    
    log_info "Health check passed."
}

###############################################################################
# Main Execution
###############################################################################

main() {
    log_info "Starting deployment process for environment: ${ENVIRONMENT}"
    
    validate_prerequisites
    
    if [ "${DEPLOY_INFRASTRUCTURE}" == "true" ]; then
        deploy_infrastructure
    fi
    
    if [ "${DEPLOY_APPLICATION}" == "true" ]; then
        deploy_application
        health_check
    fi
    
    log_info "Deployment completed successfully!"
}

# Run main function
main "$@"

