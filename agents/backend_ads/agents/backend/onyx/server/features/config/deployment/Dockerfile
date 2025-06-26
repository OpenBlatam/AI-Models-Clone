# Onyx Features - Production Optimized Dockerfile
# Multi-stage build for optimal image size and security

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILDPLATFORM
ARG TARGETPLATFORM
ARG BUILDX_VERSION

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic1 \
    libmagic-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app user for security
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/temp && \
    chown -R appuser:appuser /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"] 