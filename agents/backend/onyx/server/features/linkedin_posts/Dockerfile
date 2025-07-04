# Dockerfile Ultra Optimizado - LinkedIn Posts Production
# =====================================================

# Etapa de build - Optimizada para dependencias
FROM python:3.11-slim as builder

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements_ultra_optimized.txt .

# Instalar dependencias Python con optimizaciones
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --compile -r requirements_ultra_optimized.txt

# Etapa de producción - Ultra optimizada
FROM python:3.11-slim

# Instalar dependencias de runtime
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias Python desde builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/cache && \
    chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Variables de entorno para optimización
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV UVICORN_CMD="uvicorn optimized_core.ultra_fast_api:app --host 0.0.0.0 --port 8000 --loop asyncio --workers 4 --log-level info --access-log"

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicio ultra optimizado
CMD ["/bin/sh", "-c", "$UVICORN_CMD"] 