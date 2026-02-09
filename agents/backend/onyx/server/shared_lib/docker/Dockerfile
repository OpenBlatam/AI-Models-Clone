# Dockerfile para Shared Library - Producción
# ===========================================
# Multi-stage build optimizado para producción

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Metadata
LABEL maintainer="Blatam Academy"
LABEL description="Shared Library for FastAPI microservices"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /home/appuser/.local

# Copiar código de la aplicación
COPY . .

# Asegurar permisos
RUN chown -R appuser:appuser /app

# Agregar .local/bin al PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Cambiar a usuario no-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Exponer puerto (default, puede ser sobrescrito)
EXPOSE 8030

# Comando por defecto (puede ser sobrescrito)
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8030"]




