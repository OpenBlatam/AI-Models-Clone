#!/bin/bash

###############################################################################
# Health Check Script
# Checks the health of deployed application instances
###############################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANSIBLE_DIR="${SCRIPT_DIR}/../ansible"

HEALTH_CHECK_URL="${HEALTH_CHECK_URL:-http://localhost:8000/health}"
TIMEOUT="${TIMEOUT:-10}"
RETRIES="${RETRIES:-3}"

log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

check_health() {
    local url=$1
    local timeout=$2
    local retries=$3
    
    for i in $(seq 1 $retries); do
        log_info "Health check attempt $i of $retries..."
        
        if curl -f -s --max-time $timeout "$url" > /dev/null; then
            log_info "Health check passed!"
            return 0
        fi
        
        if [ $i -lt $retries ]; then
            log_info "Health check failed. Retrying in 5 seconds..."
            sleep 5
        fi
    done
    
    log_error "Health check failed after $retries attempts."
    return 1
}

check_all_instances() {
    log_info "Checking health of all instances via Ansible..."
    
    cd "${ANSIBLE_DIR}"
    
    ansible all \
        -i inventory/ec2.ini \
        -m uri \
        -a "url=${HEALTH_CHECK_URL} method=GET return_content=yes status_code=200" \
        || {
        log_error "Health check failed for one or more instances."
        return 1
    }
    
    log_info "All instances are healthy."
}

main() {
    local check_type="${1:-local}"
    
    case $check_type in
        "local")
            log_info "Performing local health check..."
            check_health "$HEALTH_CHECK_URL" "$TIMEOUT" "$RETRIES"
            ;;
        "all")
            log_info "Performing health check on all instances..."
            check_all_instances
            ;;
        *)
            log_error "Unknown check type: $check_type"
            log_info "Usage: $0 [local|all]"
            exit 1
            ;;
    esac
}

main "$@"

