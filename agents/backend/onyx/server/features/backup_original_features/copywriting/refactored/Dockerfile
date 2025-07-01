# Production Optimized Copywriting Service Dockerfile
# ===================================================
# Multi-stage build with performance optimizations

# ============================================================================
# Stage 1: Build Environment with Optimization Libraries
# ============================================================================
FROM python:3.11-slim as builder

# Set environment variables for optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Install system dependencies for compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    libsnappy-dev \
    liblz4-dev \
    libzstd-dev \
    libblosc-dev \
    libjemalloc-dev \
    pkg-config \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust for blake3 and other optimizations
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Create working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements_production.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir -r requirements_production.txt

# Install additional optimization libraries
RUN pip install --no-cache-dir \
    uvloop \
    orjson \
    msgspec \
    simdjson \
    numba \
    xxhash \
    blake3 \
    cramjam \
    blosc2 \
    lz4 \
    zstandard \
    polars \
    pyarrow \
    duckdb \
    hiredis \
    httptools \
    aiofiles \
    psutil

# ============================================================================
# Stage 2: Production Runtime Environment
# ============================================================================
FROM python:3.11-slim as production

# Set production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    ENVIRONMENT=production \
    DEBUG=false \
    HOST=0.0.0.0 \
    PORT=8000 \
    WORKERS=1 \
    LOG_LEVEL=INFO \
    ENABLE_JIT=true \
    CACHE_COMPRESSION=true \
    MEMORY_CACHE_SIZE=1000 \
    REDIS_CACHE_TTL=86400

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    libsnappy1v5 \
    liblz4-1 \
    libzstd1 \
    libblosc1 \
    libjemalloc2 \
    curl \
    procps \
    htop \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create application directory
WORKDIR /app

# Copy Python environment from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Create directories for logs and cache
RUN mkdir -p /app/logs /app/cache

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production startup script
COPY --chown=appuser:appuser docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Default command
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "run_production.py", "run"]

# ============================================================================
# Stage 3: Development Environment (Optional)
# ============================================================================
FROM production as development

USER root

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    pytest-benchmark \
    black \
    isort \
    flake8 \
    mypy \
    pre-commit

# Install debugging tools
RUN apt-get update && apt-get install -y \
    vim \
    nano \
    git \
    && rm -rf /var/lib/apt/lists/*

# Development environment variables
ENV DEBUG=true \
    RELOAD=true \
    LOG_LEVEL=DEBUG

USER appuser

# Development command
CMD ["python", "run_production.py", "run", "--reload-config"]

# ============================================================================
# Build Instructions
# ============================================================================

# Production build:
# docker build --target production -t copywriting-service:latest .

# Development build:
# docker build --target development -t copywriting-service:dev .

# Multi-platform build:
# docker buildx build --platform linux/amd64,linux/arm64 -t copywriting-service:latest .

# Build with optimization verification:
# docker build --target production -t copywriting-service:latest . && \
# docker run --rm copywriting-service:latest python run_production.py check 