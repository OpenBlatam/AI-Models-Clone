# 🚀 **DOCKERFILE OPTIMIZADO PARA SISTEMA DE GESTIÓN DE RECURSOS INTELIGENTE**
# Multi-stage build para máxima optimización y seguridad

# ============================================================================
# 🏗️ **STAGE 1: BASE IMAGE CON CUDA**
# ============================================================================
FROM nvidia/cuda:12.1-devel-ubuntu22.04 AS base

# Configurar variables de entorno
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-distutils \
    python3-pip \
    git \
    curl \
    wget \
    build-essential \
    cmake \
    pkg-config \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    libxft-dev \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    gfortran \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    libqtgui4 \
    libqtwebkit4 \
    libqt4-test \
    python3-pyqt5 \
    libgtk-3-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg8-dev \
    libjpeg-turbo8-dev \
    libtiff5-dev \
    libjasper-dev \
    libdc1394-22-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-bad1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    gstreamer1.0-x \
    gstreamer1.0-alsa \
    gstreamer1.0-gl \
    gstreamer1.0-gtk3 \
    gstreamer1.0-qt5 \
    gstreamer1.0-pulseaudio \
    && rm -rf /var/lib/apt/lists/*

# Crear enlace simbólico para python
RUN ln -s /usr/bin/python3.11 /usr/bin/python

# Actualizar pip
RUN python -m pip install --upgrade pip setuptools wheel

# ============================================================================
# 🔧 **STAGE 2: DEVELOPMENT ENVIRONMENT**
# ============================================================================
FROM base AS development

# Instalar dependencias de desarrollo
COPY requirements_optimized.txt /tmp/requirements_optimized.txt
RUN pip install -r /tmp/requirements_optimized.txt

# Instalar dependencias de desarrollo adicionales
RUN pip install \
    jupyter \
    jupyterlab \
    ipython \
    ipykernel \
    notebook \
    pytest-benchmark \
    pytest-xdist \
    pytest-mock \
    pytest-cov \
    coverage \
    pre-commit \
    tox \
    sphinx \
    sphinx-rtd-theme \
    myst-parser \
    sphinx-autodoc-typehints

# Configurar Jupyter
RUN python -m ipykernel install --user --name=resource-manager --display-name="Resource Manager"

# ============================================================================
# 🚀 **STAGE 3: PRODUCTION ENVIRONMENT**
# ============================================================================
FROM base AS production

# Instalar solo dependencias de producción
COPY requirements_optimized.txt /tmp/requirements_optimized.txt
RUN pip install --no-cache-dir -r /tmp/requirements_optimized.txt

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Crear directorio de trabajo
WORKDIR /app

# Copiar código de la aplicación
COPY intelligent_resource_manager.py /app/
COPY resource_manager_demo.py /app/
COPY resource_config.yaml /app/
COPY test_intelligent_resource_manager.py /app/

# Cambiar propietario de archivos
RUN chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto para Gradio
EXPOSE 7860

# Variables de entorno para producción
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860
ENV GRADIO_SHARE=False

# Comando por defecto
CMD ["python", "resource_manager_demo.py"]

# ============================================================================
# 🧪 **STAGE 4: TESTING ENVIRONMENT**
# ============================================================================
FROM development AS testing

# Copiar código de la aplicación
COPY . /app/
WORKDIR /app

# Configurar variables de entorno para testing
ENV PYTHONPATH=/app
ENV TESTING=True

# Comando para ejecutar tests
CMD ["python", "-m", "pytest", "test_intelligent_resource_manager.py", "-v"]

# ============================================================================
# 📊 **STAGE 5: MONITORING ENVIRONMENT**
# ============================================================================
FROM production AS monitoring

# Instalar herramientas de monitoreo adicionales
RUN pip install \
    prometheus-client \
    structlog \
    sentry-sdk \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-instrumentation-fastapi \
    opentelemetry-instrumentation-requests

# Copiar configuración de monitoreo
COPY resource_config.yaml /app/

# Exponer puerto para métricas
EXPOSE 9090

# Comando para monitoreo
CMD ["python", "intelligent_resource_manager.py"]

# ============================================================================
# 🔬 **STAGE 6: PROFILING ENVIRONMENT**
# ============================================================================
FROM development AS profiling

# Instalar herramientas de profiling
RUN pip install \
    memory-profiler \
    line-profiler \
    py-spy \
    pyinstrument \
    scalene \
    pyroscope-io

# Copiar código de la aplicación
COPY . /app/
WORKDIR /app

# Comando para profiling
CMD ["python", "-m", "pyinstrument", "intelligent_resource_manager.py"]

# ============================================================================
# 🐳 **STAGE 7: DOCKER COMPOSE ENVIRONMENT**
# ============================================================================
FROM production AS compose

# Instalar dependencias para Docker Compose
RUN pip install \
    docker \
    kubernetes \
    redis \
    celery

# Copiar scripts de Docker Compose
COPY docker-compose.yml /app/
COPY docker-entrypoint.sh /app/

# Hacer ejecutable el script de entrada
RUN chmod +x /app/docker-entrypoint.sh

# Script de entrada
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# ============================================================================
# 🚨 **NOTAS IMPORTANTES**
# ============================================================================
# Para usar GPU: docker run --gpus all -p 7860:7860 intelligent-resource-manager
# Para desarrollo: docker run -it -p 7860:7860 -v $(pwd):/app intelligent-resource-manager:dev
# Para testing: docker run intelligent-resource-manager:test
# Para monitoreo: docker run -p 9090:9090 intelligent-resource-manager:monitoring
# Para profiling: docker run intelligent-resource-manager:profiling
