#!/bin/bash
# 🚀 ENTERPRISE API QUICK START
# One-command setup and deployment script

set -euo pipefail

# === CONFIGURATION ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="enterprise-api"
DEMO_PORT=8001
REDIS_PORT=6379
COMPOSE_FILE="docker/docker-compose.yml"

# === COLORS ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# === LOGGING ===
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${CYAN}[STEP]${NC} $1"; }

# === BANNER ===
print_banner() {
    echo -e "${BLUE}"
    cat << 'EOF'
🚀 ENTERPRISE API QUICK START
=============================
Advanced FastAPI with microservices patterns
EOF
    echo -e "${NC}"
}

# === HELP ===
show_help() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

COMMANDS:
    install     Install dependencies and setup environment
    dev         Start development server (with hot reload)
    demo        Start demo server
    prod        Start production server with Docker
    test        Run tests and health checks
    benchmark   Run performance benchmarks
    clean       Clean up containers and volumes
    redis       Start Redis server
    monitor     Start monitoring stack (Prometheus + Grafana)
    help        Show this help message

OPTIONS:
    --port PORT     Set custom port (default: 8001)
    --workers N     Set number of workers for production
    --env ENV       Set environment (dev/prod/test)
    --redis-url URL Set Redis URL
    --verbose       Enable verbose output

EXAMPLES:
    $0 install              # Setup everything
    $0 dev                  # Start development server
    $0 demo --port 8080     # Start demo on port 8080
    $0 prod --workers 8     # Start production with 8 workers
    $0 test                 # Run all tests
    $0 benchmark            # Performance testing
    $0 monitor              # Start monitoring dashboard
EOF
}

# === DEPENDENCY CHECKS ===
check_dependencies() {
    log_step "Checking system dependencies..."
    
    local missing_deps=()
    
    # Check Python
    if ! command -v python3 >/dev/null 2>&1; then
        missing_deps+=("python3")
    fi
    
    # Check pip
    if ! command -v pip3 >/dev/null 2>&1; then
        missing_deps+=("pip3")
    fi
    
    # Check Docker (optional)
    if ! command -v docker >/dev/null 2>&1; then
        log_warn "Docker not found - Docker features will be disabled"
    fi
    
    # Check Redis (optional)
    if ! command -v redis-server >/dev/null 2>&1; then
        log_warn "Redis not found - will use memory cache only"
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Please install them and try again"
        exit 1
    fi
    
    log_info "✅ System dependencies check passed"
}

# === INSTALLATION ===
install_dependencies() {
    log_step "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "venv" ]]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate || {
        log_error "Failed to activate virtual environment"
        exit 1
    }
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    # Install dependencies
    if [[ -f "requirements-enterprise.txt" ]]; then
        log_info "Installing enterprise requirements..."
        pip install -r requirements-enterprise.txt
    else
        log_warn "requirements-enterprise.txt not found, installing basic requirements..."
        pip install fastapi uvicorn redis prometheus-client
    fi
    
    log_info "✅ Dependencies installed successfully"
}

# === REDIS SETUP ===
start_redis() {
    log_step "Starting Redis server..."
    
    # Check if Redis is already running
    if redis-cli ping >/dev/null 2>&1; then
        log_info "✅ Redis is already running"
        return 0
    fi
    
    # Try to start Redis
    if command -v redis-server >/dev/null 2>&1; then
        log_info "Starting Redis server on port $REDIS_PORT..."
        redis-server --port $REDIS_PORT --daemonize yes
        
        # Wait for Redis to be ready
        local max_attempts=10
        local attempt=1
        
        while [[ $attempt -le $max_attempts ]]; do
            if redis-cli -p $REDIS_PORT ping >/dev/null 2>&1; then
                log_info "✅ Redis started successfully"
                return 0
            fi
            sleep 1
            ((attempt++))
        done
        
        log_error "❌ Redis failed to start"
        return 1
    else
        log_warn "Redis server not found - will use memory cache only"
        return 1
    fi
}

# === DEVELOPMENT SERVER ===
start_dev() {
    local port=${1:-$DEMO_PORT}
    
    log_step "Starting development server on port $port..."
    
    # Activate virtual environment
    source venv/bin/activate 2>/dev/null || {
        log_error "Virtual environment not found. Run '$0 install' first."
        exit 1
    }
    
    # Start Redis if available
    start_redis || true
    
    # Start development server
    export ENVIRONMENT=development
    export PORT=$port
    export LOG_LEVEL=debug
    
    log_info "🚀 Starting FastAPI development server..."
    log_info "📍 URL: http://localhost:$port"
    log_info "📚 Docs: http://localhost:$port/docs"
    log_info "🏥 Health: http://localhost:$port/health"
    log_info "📊 Stats: http://localhost:$port/stats"
    
    if [[ -f "enterprise_demo.py" ]]; then
        uvicorn enterprise_demo:app --host 0.0.0.0 --port $port --reload --log-level debug
    else
        log_error "enterprise_demo.py not found!"
        exit 1
    fi
}

# === DEMO SERVER ===
start_demo() {
    local port=${1:-$DEMO_PORT}
    
    log_step "Starting demo server on port $port..."
    
    # Activate virtual environment
    source venv/bin/activate 2>/dev/null || {
        log_error "Virtual environment not found. Run '$0 install' first."
        exit 1
    }
    
    # Start Redis if available
    start_redis || true
    
    # Start demo server
    export ENVIRONMENT=demo
    export PORT=$port
    
    log_info "🚀 Starting Enterprise API Demo..."
    log_info "📍 URL: http://localhost:$port"
    log_info "📚 API Docs: http://localhost:$port/docs"
    log_info "🏥 Health Check: http://localhost:$port/health"
    log_info "📊 Statistics: http://localhost:$port/stats"
    log_info "⚡ Cached Endpoint: http://localhost:$port/api/cached"
    log_info "🔄 Circuit Breaker: http://localhost:$port/api/protected"
    
    if [[ -f "enterprise_demo.py" ]]; then
        python enterprise_demo.py
    else
        log_error "enterprise_demo.py not found!"
        exit 1
    fi
}

# === PRODUCTION SERVER ===
start_production() {
    local workers=${1:-4}
    
    log_step "Starting production server with $workers workers..."
    
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker is required for production deployment"
        exit 1
    fi
    
    # Build Docker image
    log_info "Building Docker image..."
    docker build -f docker/Dockerfile.enterprise -t $PROJECT_NAME:latest .
    
    # Start production container
    log_info "Starting production container..."
    docker run -d \
        --name $PROJECT_NAME \
        --restart unless-stopped \
        -p 8000:8000 \
        -e ENVIRONMENT=production \
        -e WORKERS=$workers \
        -e REDIS_URL=redis://host.docker.internal:6379 \
        $PROJECT_NAME:latest
    
    log_info "✅ Production server started"
    log_info "📍 URL: http://localhost:8000"
    log_info "🐳 Container: $PROJECT_NAME"
    
    # Show logs
    log_info "Showing container logs (Ctrl+C to exit)..."
    docker logs -f $PROJECT_NAME
}

# === TESTING ===
run_tests() {
    log_step "Running tests and health checks..."
    
    # Activate virtual environment
    source venv/bin/activate 2>/dev/null || {
        log_error "Virtual environment not found. Run '$0 install' first."
        exit 1
    }
    
    # Start test server in background
    export ENVIRONMENT=testing
    export PORT=8999
    
    log_info "Starting test server..."
    python enterprise_demo.py &
    local test_pid=$!
    
    # Wait for server to start
    sleep 3
    
    # Run health checks
    log_info "Running health checks..."
    
    # Test root endpoint
    if curl -s http://localhost:8999/ | jq . >/dev/null 2>&1; then
        log_info "✅ Root endpoint test passed"
    else
        log_error "❌ Root endpoint test failed"
    fi
    
    # Test health endpoint
    if curl -s http://localhost:8999/health | jq . >/dev/null 2>&1; then
        log_info "✅ Health endpoint test passed"
    else
        log_error "❌ Health endpoint test failed"
    fi
    
    # Test cached endpoint
    if curl -s http://localhost:8999/api/cached | jq . >/dev/null 2>&1; then
        log_info "✅ Cached endpoint test passed"
    else
        log_error "❌ Cached endpoint test failed"
    fi
    
    # Kill test server
    kill $test_pid 2>/dev/null || true
    
    log_info "✅ Tests completed"
}

# === BENCHMARKING ===
run_benchmark() {
    log_step "Running performance benchmarks..."
    
    # Check for Apache Bench
    if ! command -v ab >/dev/null 2>&1; then
        log_warn "Apache Bench (ab) not found. Install apache2-utils for benchmarking."
        return 1
    fi
    
    # Start server for benchmarking
    export ENVIRONMENT=testing
    export PORT=8998
    
    log_info "Starting benchmark server..."
    python enterprise_demo.py &
    local bench_pid=$!
    
    # Wait for server to start
    sleep 3
    
    # Run benchmarks
    log_info "Running benchmark (1000 requests, 10 concurrent)..."
    ab -n 1000 -c 10 -g benchmark.dat http://localhost:8998/ || true
    
    log_info "Running cache benchmark..."
    ab -n 500 -c 5 http://localhost:8998/api/cached || true
    
    # Kill benchmark server
    kill $bench_pid 2>/dev/null || true
    
    log_info "✅ Benchmarks completed"
}

# === MONITORING ===
start_monitoring() {
    log_step "Starting monitoring stack..."
    
    if ! command -v docker-compose >/dev/null 2>&1; then
        log_error "docker-compose is required for monitoring stack"
        exit 1
    fi
    
    # Create monitoring configuration
    mkdir -p monitoring
    
    # Create Prometheus config
    cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'enterprise-api'
    static_configs:
      - targets: ['host.docker.internal:8001']
EOF
    
    # Create docker-compose for monitoring
    cat > monitoring/docker-compose.yml << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
EOF
    
    # Start monitoring stack
    cd monitoring
    docker-compose up -d
    cd ..
    
    log_info "✅ Monitoring stack started"
    log_info "📊 Prometheus: http://localhost:9090"
    log_info "📈 Grafana: http://localhost:3000 (admin/admin)"
}

# === CLEANUP ===
cleanup() {
    log_step "Cleaning up containers and volumes..."
    
    # Stop and remove containers
    docker stop $PROJECT_NAME 2>/dev/null || true
    docker rm $PROJECT_NAME 2>/dev/null || true
    
    # Clean up monitoring
    if [[ -f "monitoring/docker-compose.yml" ]]; then
        cd monitoring
        docker-compose down -v 2>/dev/null || true
        cd ..
    fi
    
    # Stop Redis if we started it
    redis-cli shutdown 2>/dev/null || true
    
    log_info "✅ Cleanup completed"
}

# === MAIN FUNCTION ===
main() {
    local command=${1:-help}
    shift || true
    
    # Parse options
    local port=$DEMO_PORT
    local workers=4
    local env="dev"
    local verbose=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --port)
                port="$2"
                shift 2
                ;;
            --workers)
                workers="$2"
                shift 2
                ;;
            --env)
                env="$2"
                shift 2
                ;;
            --verbose)
                verbose=true
                shift
                ;;
            *)
                break
                ;;
        esac
    done
    
    # Set verbose mode
    if [[ "$verbose" == "true" ]]; then
        set -x
    fi
    
    print_banner
    
    case $command in
        install)
            check_dependencies
            install_dependencies
            log_info "🎉 Installation completed! Run '$0 demo' to start."
            ;;
        dev)
            start_dev $port
            ;;
        demo)
            start_demo $port
            ;;
        prod)
            start_production $workers
            ;;
        test)
            run_tests
            ;;
        benchmark)
            run_benchmark
            ;;
        redis)
            start_redis
            ;;
        monitor)
            start_monitoring
            ;;
        clean)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# === SIGNAL HANDLING ===
cleanup_on_exit() {
    log_info "🛑 Received interrupt signal"
    cleanup
    exit 0
}

trap cleanup_on_exit SIGINT SIGTERM

# === ENTRY POINT ===
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 