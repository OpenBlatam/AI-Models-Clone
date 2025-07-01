# ═══════════════════════════════════════════════════════════════
# 🚀 DOCKERFILE - NLP ENGINE MODULAR ENTERPRISE
# ═══════════════════════════════════════════════════════════════
# 
# Multi-stage build para motor NLP con Clean Architecture
# Target: Performance ultra-optimizado < 0.1ms latency

# ─────────────────────────────────────────────────────────────
# 🏗️ BUILDER STAGE - Compilación y Dependencies
# ─────────────────────────────────────────────────────────────
FROM python:3.11-slim as builder

# Variables de build optimizado
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Instalar build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /build

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias con optimizaciones
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --compile -r requirements.txt

# ─────────────────────────────────────────────────────────────
# 🚀 PRODUCTION STAGE - Runtime Optimizado  
# ─────────────────────────────────────────────────────────────
FROM python:3.11-slim as production

# Variables de entorno enterprise
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    NLP_ENVIRONMENT=production \
    NLP_LOG_LEVEL=INFO \
    NLP_MAX_WORKERS=100 \
    NLP_CACHE_SIZE=100000 \
    NLP_RATE_LIMIT=10000 \
    NLP_API_HOST=0.0.0.0 \
    NLP_API_PORT=8000 \
    NLP_PROCESSING_TIER=balanced \
    NLP_CACHE_STRATEGY=lru \
    NLP_HEALTH_CHECK_INTERVAL=30

# Labels para metadata
LABEL maintainer="Enterprise NLP Team" \
      version="1.0.0-modular" \
      description="Motor NLP Modular Enterprise con Clean Architecture" \
      architecture="amd64"

# Instalar solo runtime dependencies mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

# Crear usuario no-root para seguridad
RUN groupadd --gid 1000 nlp_group && \
    useradd --uid 1000 --gid nlp_group --create-home --shell /bin/bash nlp_user

# Crear estructura de directorios
RUN mkdir -p /app/logs /app/cache /app/tmp && \
    chown -R nlp_user:nlp_group /app && \
    chmod 755 /app

# Copiar dependencias Python desde builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Cambiar a directorio de aplicación
WORKDIR /app

# Copiar código del motor NLP modular
COPY --chown=nlp_user:nlp_group . .

# Asegurar permisos correctos
RUN chmod -R 644 /app && \
    chmod 755 /app && \
    find /app -type d -exec chmod 755 {} \; && \
    find /app -name "*.py" -exec chmod 644 {} \;

# Cambiar a usuario no-root
USER nlp_user

# Health check optimizado
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import asyncio; from nlp_engine import NLPEngine; \
                   async def check(): \
                       engine = NLPEngine(); \
                       await engine.initialize(); \
                       health = await engine.get_health_status(); \
                       exit(0 if health['status'] == 'healthy' else 1); \
                   asyncio.run(check())" || exit 1

# Exponer puerto
EXPOSE 8000

# Scripts de inicio
COPY --chown=nlp_user:nlp_group docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Punto de entrada
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Comando por defecto - demo
CMD ["demo"]

# ─────────────────────────────────────────────────────────────
# 🎯 COMANDOS DISPONIBLES:
# ─────────────────────────────────────────────────────────────
# 
# demo    - Ejecutar demo completo del sistema
# api     - Iniciar API REST en puerto 8000  
# test    - Ejecutar suite de tests
# shell   - Iniciar shell interactivo
# 
# Ejemplos:
#   docker run nlp-engine:latest demo
#   docker run -p 8000:8000 nlp-engine:latest api
#   docker run -it nlp-engine:latest shell 