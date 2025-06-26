#!/bin/bash
set -euo pipefail

# Onyx Ultra Production Runner
# Ultra-optimized deployment script with intelligent optimization detection

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Configuration
readonly APP_NAME="Onyx-Ultra"
readonly VERSION="6.0.0"
readonly DEFAULT_PORT="8000"
readonly DEFAULT_WORKERS="auto"
readonly DEFAULT_ENVIRONMENT="production"

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${CYAN}[SUCCESS]${NC} $1"
}

log_debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${PURPLE}[DEBUG]${NC} $1"
    fi
}

# Banner
show_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
 ██████╗ ███╗   ██╗██╗   ██╗██╗  ██╗    ██╗   ██╗██╗  ████████╗██████╗  █████╗ 
██╔═══██╗████╗  ██║╚██╗ ██╔╝╚██╗██╔╝    ██║   ██║██║  ╚══██╔══╝██╔══██╗██╔══██╗
██║   ██║██╔██╗ ██║ ╚████╔╝  ╚███╔╝     ██║   ██║██║     ██║   ██████╔╝███████║
██║   ██║██║╚██╗██║  ╚██╔╝   ██╔██╗     ██║   ██║██║     ██║   ██╔══██╗██╔══██║
╚██████╔╝██║ ╚████║   ██║   ██╔╝ ██╗    ╚██████╔╝███████╗██║   ██║  ██║██║  ██║
 ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝     ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
EOF
    echo -e "${NC}"
    echo -e "${GREEN}🚀 Ultra-Optimized Production Server v${VERSION}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
}

# Check system requirements
check_requirements() {
    log_info "🔍 Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_info "Python version: $python_version"
    
    # Check if we're in a virtual environment
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        log_warn "Not in a virtual environment. Consider using venv or conda."
    else
        log_info "Virtual environment: $VIRTUAL_ENV"
    fi
    
    # Check available memory
    if command -v free &> /dev/null; then
        local memory_gb=$(free -g | awk '/^Mem:/{print $2}')
        log_info "Available memory: ${memory_gb}GB"
        
        if [[ $memory_gb -lt 2 ]]; then
            log_warn "Low memory detected. Consider increasing memory for better performance."
        fi
    fi
    
    # Check CPU cores
    local cpu_cores=$(nproc 2>/dev/null || echo "unknown")
    log_info "CPU cores: $cpu_cores"
    
    log_success "✅ System requirements check completed"
}

# Detect optimization libraries
detect_optimizations() {
    log_info "🔬 Detecting optimization libraries..."
    
    local libs_found=0
    local total_libs=0
    
    # Define optimization libraries to check
    local optimization_libs=(
        "uvloop:Event loop optimization"
        "orjson:Ultra-fast JSON"
        "blake3:Fastest hashing"
        "blosc2:Multi-threaded compression"
        "polars:Ultra-fast DataFrames"
        "numba:JIT compilation"
        "psutil:System monitoring"
        "xxhash:Fast hashing"
        "lz4:Fast compression"
        "pyarrow:Columnar data"
    )
    
    echo -e "${BLUE}┌─────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│                    OPTIMIZATION LIBRARIES                  │${NC}"
    echo -e "${BLUE}├─────────────────────────────────────────────────────────────┤${NC}"
    
    for lib_info in "${optimization_libs[@]}"; do
        IFS=':' read -r lib_name lib_desc <<< "$lib_info"
        total_libs=$((total_libs + 1))
        
        if python3 -c "import $lib_name" 2>/dev/null; then
            local version=$(python3 -c "import $lib_name; print(getattr($lib_name, '__version__', 'unknown'))" 2>/dev/null)
            echo -e "${BLUE}│${NC} ${GREEN}✅${NC} ${lib_name:<12} ${version:<10} ${lib_desc:<25} ${BLUE}│${NC}"
            libs_found=$((libs_found + 1))
        else
            echo -e "${BLUE}│${NC} ${RED}❌${NC} ${lib_name:<12} ${'not found':<10} ${lib_desc:<25} ${BLUE}│${NC}"
        fi
    done
    
    echo -e "${BLUE}└─────────────────────────────────────────────────────────────┘${NC}"
    
    local optimization_percentage=$((libs_found * 100 / total_libs))
    
    if [[ $optimization_percentage -ge 80 ]]; then
        log_success "🚀 Excellent! ${libs_found}/${total_libs} optimization libraries available (${optimization_percentage}%)"
    elif [[ $optimization_percentage -ge 50 ]]; then
        log_info "⚡ Good! ${libs_found}/${total_libs} optimization libraries available (${optimization_percentage}%)"
    else
        log_warn "⚠️  Limited optimizations: ${libs_found}/${total_libs} libraries available (${optimization_percentage}%)"
        echo -e "${YELLOW}Consider installing: pip install -r requirements_ultra.txt${NC}"
    fi
    
    return $libs_found
}

# Install dependencies
install_dependencies() {
    log_info "📦 Installing dependencies..."
    
    if [[ -f "requirements_ultra.txt" ]]; then
        log_info "Installing ultra-optimized requirements..."
        pip install -r requirements_ultra.txt --upgrade
    elif [[ -f "requirements.txt" ]]; then
        log_info "Installing standard requirements..."
        pip install -r requirements.txt --upgrade
    else
        log_warn "No requirements file found. Installing minimal dependencies..."
        pip install fastapi uvicorn[standard] structlog prometheus-client
    fi
    
    log_success "✅ Dependencies installed"
}

# Calculate optimal settings
calculate_optimal_settings() {
    log_info "🧮 Calculating optimal settings..."
    
    local cpu_cores=$(nproc 2>/dev/null || echo "4")
    local memory_gb=$(free -g 2>/dev/null | awk '/^Mem:/{print $2}' || echo "4")
    
    # Calculate workers (CPU cores * 2, but max 32)
    local optimal_workers=$((cpu_cores * 2))
    if [[ $optimal_workers -gt 32 ]]; then
        optimal_workers=32
    fi
    
    # Calculate max connections
    local max_connections=$((cpu_cores * 1000))
    if [[ $max_connections -gt 10000 ]]; then
        max_connections=10000
    fi
    
    # Memory limit (80% of available)
    local memory_limit_mb=$((memory_gb * 1024 * 80 / 100))
    
    log_info "Optimal settings:"
    log_info "  • Workers: $optimal_workers"
    log_info "  • Max connections: $max_connections"
    log_info "  • Memory limit: ${memory_limit_mb}MB"
    
    # Export settings
    export WORKERS=${WORKERS:-$optimal_workers}
    export MAX_CONNECTIONS=${MAX_CONNECTIONS:-$max_connections}
    export MAX_MEMORY_MB=${MAX_MEMORY_MB:-$memory_limit_mb}
}

# Start application
start_application() {
    local app_file="${1:-main_ultra.py}"
    local port="${PORT:-$DEFAULT_PORT}"
    local environment="${ENVIRONMENT:-$DEFAULT_ENVIRONMENT}"
    
    log_info "🚀 Starting $APP_NAME..."
    log_info "Configuration:"
    log_info "  • Application: $app_file"
    log_info "  • Port: $port"
    log_info "  • Environment: $environment"
    log_info "  • Workers: ${WORKERS:-auto}"
    log_info "  • Debug: ${DEBUG:-false}"
    
    # Set environment variables
    export APP_NAME="$APP_NAME"
    export VERSION="$VERSION"
    export ENVIRONMENT="$environment"
    export PORT="$port"
    export HOST="${HOST:-0.0.0.0}"
    
    # Start the application
    if [[ "$app_file" == "main_ultra.py" ]] && [[ -f "$app_file" ]]; then
        log_info "Starting ultra-optimized application..."
        python3 "$app_file"
    elif [[ -f "ultra_prod.py" ]]; then
        log_info "Starting ultra production application..."
        python3 ultra_prod.py
    elif [[ -f "prod.py" ]]; then
        log_info "Starting production application..."
        python3 prod.py
    else
        log_error "No suitable application file found!"
        exit 1
    fi
}

# Health check
health_check() {
    local port="${PORT:-$DEFAULT_PORT}"
    local max_attempts=30
    local attempt=1
    
    log_info "🏥 Performing health check..."
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -sf "http://localhost:$port/health" > /dev/null 2>&1; then
            log_success "✅ Application is healthy!"
            
            # Get application info
            local app_info=$(curl -s "http://localhost:$port/health" | python3 -m json.tool 2>/dev/null || echo "{}")
            echo -e "${CYAN}Application Status:${NC}"
            echo "$app_info" | grep -E "(version|status|performance_score|uptime)" || true
            
            return 0
        fi
        
        log_debug "Health check attempt $attempt/$max_attempts failed"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "❌ Health check failed after $max_attempts attempts"
    return 1
}

# Performance test
performance_test() {
    local port="${PORT:-$DEFAULT_PORT}"
    
    log_info "⚡ Running performance test..."
    
    if command -v curl &> /dev/null; then
        local response=$(curl -s "http://localhost:$port/api/benchmark?iterations=50000" 2>/dev/null || echo "{}")
        
        if [[ -n "$response" ]] && [[ "$response" != "{}" ]]; then
            log_success "🎯 Performance test completed!"
            echo -e "${CYAN}Performance Results:${NC}"
            echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'benchmarks' in data:
        for name, result in data['benchmarks'].items():
            print(f'  • {name.title()}: {result.get(\"ops_per_second\", 0):.0f} ops/sec ({result.get(\"library\", \"unknown\")})')
    print(f'  • Performance Score: {data.get(\"performance_score\", 1.0):.1f}x')
except:
    pass
            " 2>/dev/null || echo "  • Test data not available"
        else
            log_warn "Performance test endpoint not available"
        fi
    else
        log_warn "curl not available for performance testing"
    fi
}

# Show usage
show_usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

COMMANDS:
    start [app]     Start the application (default: main_ultra.py)
    install         Install dependencies
    check           Check system requirements and optimizations
    test            Run performance test
    health          Check application health
    stop            Stop the application
    restart         Restart the application
    status          Show application status

OPTIONS:
    --port PORT     Set port (default: $DEFAULT_PORT)
    --workers N     Set number of workers (default: auto)
    --env ENV       Set environment (default: $DEFAULT_ENVIRONMENT)
    --debug         Enable debug mode
    --help          Show this help

EXAMPLES:
    $0 start                    # Start with auto-detection
    $0 start ultra_prod.py      # Start specific application
    $0 check                    # Check optimizations
    $0 test                     # Run performance test
    $0 --port 9000 start        # Start on custom port

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --port)
                export PORT="$2"
                shift 2
                ;;
            --workers)
                export WORKERS="$2"
                shift 2
                ;;
            --env)
                export ENVIRONMENT="$2"
                shift 2
                ;;
            --debug)
                export DEBUG="true"
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                break
                ;;
        esac
    done
}

# Main function
main() {
    parse_args "$@"
    
    local command="${1:-start}"
    local app_file="${2:-main_ultra.py}"
    
    show_banner
    
    case "$command" in
        "start")
            check_requirements
            detect_optimizations
            calculate_optimal_settings
            start_application "$app_file"
            ;;
        "install")
            install_dependencies
            ;;
        "check")
            check_requirements
            detect_optimizations
            ;;
        "test")
            performance_test
            ;;
        "health")
            health_check
            ;;
        "stop")
            log_info "🛑 Stopping application..."
            pkill -f "python.*ultra" || log_warn "No running application found"
            ;;
        "restart")
            log_info "🔄 Restarting application..."
            pkill -f "python.*ultra" || true
            sleep 2
            start_application "$app_file"
            ;;
        "status")
            health_check && performance_test
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Trap signals for graceful shutdown
trap 'log_info "🛑 Received shutdown signal"; exit 0' SIGTERM SIGINT

# Run main function
main "$@" 