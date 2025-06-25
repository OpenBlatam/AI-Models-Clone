#!/bin/bash
set -e

# Onyx Enterprise Production Deployment Script
# Ultra-optimized deployment with zero-downtime rolling updates

echo "🚀 Starting Onyx Enterprise Deployment..."

# Configuration
PROJECT_NAME="onyx-enterprise"
IMAGE_NAME="onyx/enterprise"
VERSION=${1:-latest}
ENVIRONMENT=${2:-production}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check environment file
    if [ ! -f ".env.${ENVIRONMENT}" ]; then
        log_error "Environment file .env.${ENVIRONMENT} not found"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Build optimized Docker image
build_image() {
    log_info "Building optimized production image..."
    
    docker build \
        -f Dockerfile.production \
        -t ${IMAGE_NAME}:${VERSION} \
        -t ${IMAGE_NAME}:latest \
        --build-arg ENVIRONMENT=${ENVIRONMENT} \
        .
    
    log_success "Image built successfully"
}

# Run security scan
security_scan() {
    log_info "Running security scan..."
    
    # Install Trivy if not present
    if ! command -v trivy &> /dev/null; then
        log_warning "Trivy not found, skipping security scan"
        return
    fi
    
    trivy image --severity HIGH,CRITICAL ${IMAGE_NAME}:${VERSION}
    log_success "Security scan completed"
}

# Run tests
run_tests() {
    log_info "Running production tests..."
    
    # Run unit tests
    docker run --rm \
        -e ENVIRONMENT=testing \
        ${IMAGE_NAME}:${VERSION} \
        python -m pytest tests/ -v --cov=agents/backend_ads/agents/backend/onyx/server/features
    
    # Run performance tests
    docker run --rm \
        -e ENVIRONMENT=testing \
        ${IMAGE_NAME}:${VERSION} \
        python -m pytest tests/performance/ -v
    
    log_success "Tests passed"
}

# Deploy with zero downtime
deploy() {
    log_info "Starting zero-downtime deployment..."
    
    # Load environment variables
    export $(cat .env.${ENVIRONMENT} | xargs)
    
    # Create backup of current deployment
    if docker-compose -f docker-compose.production.yml ps | grep -q "Up"; then
        log_info "Creating backup of current deployment..."
        docker-compose -f docker-compose.production.yml exec postgres pg_dump -U onyx onyx_prod > backup_$(date +%Y%m%d_%H%M%S).sql
    fi
    
    # Pull latest images
    docker-compose -f docker-compose.production.yml pull
    
    # Start new services
    docker-compose -f docker-compose.production.yml up -d --scale onyx-enterprise=2
    
    # Wait for health check
    log_info "Waiting for health check..."
    sleep 30
    
    # Check if new instances are healthy
    HEALTHY_INSTANCES=$(docker-compose -f docker-compose.production.yml ps onyx-enterprise | grep "healthy" | wc -l)
    
    if [ "$HEALTHY_INSTANCES" -ge 1 ]; then
        log_success "New instances are healthy"
        
        # Scale down old instances
        docker-compose -f docker-compose.production.yml up -d --scale onyx-enterprise=1
        
        # Cleanup old containers
        docker-compose -f docker-compose.production.yml exec nginx nginx -s reload
        
        log_success "Deployment completed successfully"
    else
        log_error "New instances failed health check, rolling back..."
        docker-compose -f docker-compose.production.yml down
        exit 1
    fi
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Start monitoring stack
    docker-compose -f docker-compose.production.yml up -d prometheus grafana
    
    # Import Grafana dashboards
    sleep 15
    curl -X POST \
        -H "Content-Type: application/json" \
        -d @grafana/dashboards/onyx-dashboard.json \
        http://admin:${GRAFANA_PASSWORD}@localhost:3000/api/dashboards/db
    
    log_success "Monitoring setup completed"
}

# Cleanup old images
cleanup() {
    log_info "Cleaning up old images..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove old backups (keep last 7 days)
    find . -name "backup_*.sql" -type f -mtime +7 -delete
    
    log_success "Cleanup completed"
}

# Performance optimization
optimize_performance() {
    log_info "Applying performance optimizations..."
    
    # Optimize Docker daemon
    if [ -f /etc/docker/daemon.json ]; then
        log_info "Docker daemon already configured"
    else
        cat > /etc/docker/daemon.json <<EOF
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    },
    "storage-driver": "overlay2",
    "live-restore": true
}
EOF
        systemctl reload docker
    fi
    
    # Set system optimizations
    echo 'vm.max_map_count=262144' >> /etc/sysctl.conf
    echo 'fs.file-max=65536' >> /etc/sysctl.conf
    sysctl -p
    
    log_success "Performance optimizations applied"
}

# Main deployment flow
main() {
    echo "🎯 Onyx Enterprise Deployment v${VERSION} to ${ENVIRONMENT}"
    echo "=================================================="
    
    check_prerequisites
    build_image
    security_scan
    run_tests
    
    if [ "$ENVIRONMENT" = "production" ]; then
        optimize_performance
        setup_monitoring
    fi
    
    deploy
    cleanup
    
    echo "=================================================="
    log_success "🎉 Deployment completed successfully!"
    echo ""
    echo "📊 Access your application:"
    echo "   • Application: http://localhost:8000"
    echo "   • Health: http://localhost:8000/health"
    echo "   • Metrics: http://localhost:8000/metrics"
    echo "   • Grafana: http://localhost:3000 (admin/${GRAFANA_PASSWORD})"
    echo "   • Prometheus: http://localhost:9090"
    echo ""
    echo "🔧 Useful commands:"
    echo "   • View logs: docker-compose -f docker-compose.production.yml logs -f"
    echo "   • Scale app: docker-compose -f docker-compose.production.yml up -d --scale onyx-enterprise=N"
    echo "   • Update app: ./deploy.sh new-version production"
}

# Handle script arguments
case "${1:-deploy}" in
    "build")
        check_prerequisites
        build_image
        ;;
    "test")
        run_tests
        ;;
    "deploy")
        main
        ;;
    "rollback")
        log_info "Rolling back to previous version..."
        docker-compose -f docker-compose.production.yml down
        # Restore from backup logic here
        ;;
    *)
        echo "Usage: $0 {build|test|deploy|rollback} [version] [environment]"
        exit 1
        ;;
esac 