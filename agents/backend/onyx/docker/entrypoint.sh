#!/bin/bash
# 🚀 ENTERPRISE API ENTRYPOINT SCRIPT
# Advanced startup script with health checks and environment validation

set -euo pipefail

# === ENVIRONMENT VARIABLES ===
ENVIRONMENT=${ENVIRONMENT:-production}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-4}
REDIS_URL=${REDIS_URL:-redis://localhost:6379}
LOG_LEVEL=${LOG_LEVEL:-info}

# === COLORS FOR OUTPUT ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# === LOGGING FUNCTIONS ===
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    if [[ "${LOG_LEVEL}" == "debug" ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $1"
    fi
}

# === BANNER ===
print_banner() {
    echo -e "${BLUE}"
    echo "🚀 ENTERPRISE API STARTING"
    echo "=========================="
    echo "Environment: ${ENVIRONMENT}"
    echo "Host: ${HOST}:${PORT}"
    echo "Workers: ${WORKERS}"
    echo "Log Level: ${LOG_LEVEL}"
    echo -e "${NC}"
}

# === HEALTH CHECKS ===
check_redis() {
    log_info "Checking Redis connectivity..."
    
    # Extract host and port from Redis URL
    REDIS_HOST=$(echo $REDIS_URL | sed -n 's/.*:\/\/\([^:]*\).*/\1/p')
    REDIS_PORT=$(echo $REDIS_URL | sed -n 's/.*:\([0-9]*\).*/\1/p')
    
    if [[ -z "$REDIS_PORT" ]]; then
        REDIS_PORT=6379
    fi
    
    # Try to connect to Redis
    if command -v redis-cli >/dev/null 2>&1; then
        if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping >/dev/null 2>&1; then
            log_info "✅ Redis connection successful"
            return 0
        else
            log_warn "⚠️  Redis connection failed - will use memory cache only"
            return 1
        fi
    else
        log_debug "redis-cli not available, skipping Redis check"
        return 1
    fi
}

check_environment() {
    log_info "Validating environment configuration..."
    
    # Check required environment variables for production
    if [[ "$ENVIRONMENT" == "production" ]]; then
        if [[ "${SECRET_KEY:-}" == "change-me-in-production" ]] || [[ -z "${SECRET_KEY:-}" ]]; then
            log_error "❌ SECRET_KEY must be set in production!"
            exit 1
        fi
        
        if [[ "${ALLOWED_ORIGINS:-}" == "*" ]]; then
            log_warn "⚠️  CORS origins should be restricted in production"
        fi
    fi
    
    # Check port availability
    if netstat -tln 2>/dev/null | grep -q ":${PORT} "; then
        log_error "❌ Port ${PORT} is already in use!"
        exit 1
    fi
    
    log_info "✅ Environment validation passed"
}

check_dependencies() {
    log_info "Checking Python dependencies..."
    
    # Check if FastAPI is importable
    if ! python -c "import fastapi" 2>/dev/null; then
        log_error "❌ FastAPI not found - check requirements installation"
        exit 1
    fi
    
    # Check if uvicorn is available
    if ! python -c "import uvicorn" 2>/dev/null; then
        log_error "❌ Uvicorn not found - check requirements installation"
        exit 1
    fi
    
    log_info "✅ Dependencies check passed"
}

# === WAIT FOR SERVICES ===
wait_for_redis() {
    if [[ "${WAIT_FOR_REDIS:-false}" == "true" ]]; then
        log_info "Waiting for Redis to be ready..."
        
        local max_attempts=30
        local attempt=1
        
        while [[ $attempt -le $max_attempts ]]; do
            if check_redis; then
                log_info "✅ Redis is ready"
                return 0
            fi
            
            log_debug "Redis not ready, attempt $attempt/$max_attempts"
            sleep 2
            ((attempt++))
        done
        
        log_error "❌ Redis is not available after $max_attempts attempts"
        exit 1
    fi
}

# === INITIALIZATION ===
initialize_app() {
    log_info "Initializing application..."
    
    # Create necessary directories
    mkdir -p /app/logs /app/tmp
    
    # Set proper permissions
    if [[ -w /app/logs ]]; then
        log_debug "Log directory is writable"
    else
        log_warn "⚠️  Log directory is not writable"
    fi
    
    # Run any initialization scripts
    if [[ -f "/app/init.py" ]]; then
        log_info "Running initialization script..."
        python /app/init.py
    fi
    
    log_info "✅ Application initialized"
}

# === SIGNAL HANDLERS ===
cleanup() {
    log_info "🛑 Received shutdown signal, cleaning up..."
    
    # Kill any background processes
    if [[ -n "${APP_PID:-}" ]]; then
        kill -TERM "$APP_PID" 2>/dev/null || true
        wait "$APP_PID" 2>/dev/null || true
    fi
    
    log_info "✅ Cleanup completed"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# === MAIN EXECUTION ===
main() {
    print_banner
    
    # Pre-flight checks
    check_environment
    check_dependencies
    check_redis
    wait_for_redis
    initialize_app
    
    log_info "🚀 Starting Enterprise API..."
    
    # Determine startup command based on environment
    case "$ENVIRONMENT" in
        "development")
            log_info "Starting in development mode with hot reload..."
            exec uvicorn enterprise_demo:app \
                --host "$HOST" \
                --port "$PORT" \
                --reload \
                --log-level "$LOG_LEVEL" \
                --access-log \
                --use-colors
            ;;
            
        "testing")
            log_info "Starting in testing mode..."
            exec uvicorn enterprise_demo:app \
                --host "$HOST" \
                --port "$PORT" \
                --log-level "$LOG_LEVEL" \
                --workers 1
            ;;
            
        "production"|"staging")
            log_info "Starting in production mode with Gunicorn..."
            exec gunicorn enterprise_demo:app \
                --bind "$HOST:$PORT" \
                --workers "$WORKERS" \
                --worker-class uvicorn.workers.UvicornWorker \
                --worker-connections 1000 \
                --max-requests 1000 \
                --max-requests-jitter 100 \
                --timeout 30 \
                --keepalive 2 \
                --preload \
                --access-logfile - \
                --error-logfile - \
                --log-level "$LOG_LEVEL" \
                --capture-output \
                --enable-stdio-inheritance
            ;;
            
        *)
            log_error "❌ Unknown environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
}

# === ERROR HANDLING ===
handle_error() {
    local exit_code=$?
    log_error "❌ Script failed with exit code $exit_code"
    
    # Log system information for debugging
    log_debug "System information:"
    log_debug "- Python version: $(python --version 2>&1)"
    log_debug "- Working directory: $(pwd)"
    log_debug "- Available memory: $(free -h 2>/dev/null | head -2 | tail -1 || echo 'N/A')"
    log_debug "- Disk space: $(df -h . 2>/dev/null | tail -1 || echo 'N/A')"
    
    exit $exit_code
}

trap handle_error ERR

# === ENTRY POINT ===
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Script is being executed directly
    main "$@"
else
    # Script is being sourced
    log_debug "Entrypoint script sourced"
fi 