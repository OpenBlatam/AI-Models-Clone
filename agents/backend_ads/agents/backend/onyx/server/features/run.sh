#!/bin/bash
set -e

echo "🚀 Starting Onyx Ultra Production..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker not found"
    exit 1
fi

# Environment setup
export DB_PASSWORD=${DB_PASSWORD:-$(openssl rand -base64 32)}
export ENVIRONMENT=${ENVIRONMENT:-production}
export WORKERS=${WORKERS:-32}

log_info "Environment: $ENVIRONMENT"
log_info "Workers: $WORKERS"

# Start ultra-optimized stack
case "${1:-up}" in
    "build")
        log_info "Building ultra-optimized images..."
        docker-compose -f docker-compose.ultra.yml build --no-cache
        ;;
    "up")
        log_info "Starting ultra-optimized stack..."
        docker-compose -f docker-compose.ultra.yml up -d
        
        # Wait for health check
        log_info "Waiting for services..."
        sleep 10
        
        # Check health
        if curl -f http://localhost/health > /dev/null 2>&1; then
            log_info "✅ Onyx Ultra is running!"
            echo ""
            echo "📊 Access:"
            echo "   • Application: http://localhost"
            echo "   • Health: http://localhost/health"
            echo "   • Status: http://localhost/status"
            echo "   • Benchmark: http://localhost/api/benchmark"
            echo ""
            echo "🔧 Management:"
            echo "   • Logs: docker-compose -f docker-compose.ultra.yml logs -f"
            echo "   • Stop: ./run.sh down"
            echo "   • Scale: docker-compose -f docker-compose.ultra.yml up -d --scale onyx-ultra=N"
        else
            log_error "Health check failed"
            exit 1
        fi
        ;;
    "down")
        log_info "Stopping services..."
        docker-compose -f docker-compose.ultra.yml down
        ;;
    "logs")
        docker-compose -f docker-compose.ultra.yml logs -f
        ;;
    "test")
        log_info "Running performance test..."
        curl -s http://localhost/api/benchmark?iterations=50000 | jq .
        ;;
    *)
        echo "Usage: $0 {build|up|down|logs|test}"
        exit 1
        ;;
esac 