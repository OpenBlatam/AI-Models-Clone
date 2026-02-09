# Multi-stage Dockerfile for FastAPI Application
# Optimized for production deployment on EC2

# ============================================================================
# Stage 1: Base Image
# ============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# ============================================================================
# Stage 2: Dependencies
# ============================================================================
FROM base as dependencies

# Copy requirements file
COPY requirements.txt* /app/
COPY pyproject.toml* /app/
COPY setup.py* /app/

# Install Python dependencies
RUN if [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    elif [ -f pyproject.toml ]; then \
        pip install --no-cache-dir -e .; \
    else \
        pip install --no-cache-dir \
            fastapi==0.104.1 \
            uvicorn[standard]==0.24.0 \
            pydantic==2.5.0 \
            python-multipart==0.0.6 \
            python-jose[cryptography]==3.3.0 \
            passlib[bcrypt]==1.7.4 \
            sqlalchemy==2.0.23 \
            alembic==1.12.1 \
            redis==5.0.1 \
            celery==5.3.4 \
            prometheus-client==0.19.0 \
            structlog==23.2.0; \
    fi

# ============================================================================
# Stage 3: Production
# ============================================================================
FROM dependencies as production

# Copy application code
COPY . /app/

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]



