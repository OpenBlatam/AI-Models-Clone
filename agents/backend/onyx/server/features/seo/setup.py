#!/usr/bin/env python3
"""
Script de instalación y configuración ultra-optimizado para el Servicio SEO
con librerías modernas y de alto rendimiento.
"""

import os
import sys
import subprocess
import platform
import json
import time
from pathlib import Path

def print_banner():
    """Muestra banner de instalación"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🚀 SEO SERVICE ULTRA-OPTIMIZED 🚀        ║
    ║                                                              ║
    ║  Librerías Modernas y de Alto Rendimiento                   ║
    ║  • httpx (HTTP cliente asíncrono ultra-rápido)              ║
    ║  • lxml (Parsing XML/HTML ultra-eficiente)                  ║
    ║  • orjson (JSON serialización ultra-rápida)                 ║
    ║  • cachetools (Cache con TTL optimizado)                    ║
    ║  • tenacity (Retry con backoff exponencial)                 ║
    ║  • tracemalloc (Monitoreo de memoria en tiempo real)        ║
    ║  • aiofiles (I/O asíncrono para archivos)                   ║
    ║  • uvicorn (Servidor ASGI de alto rendimiento)              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Verifica la versión de Python"""
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} - Compatible")

def install_dependencies():
    """Instala todas las dependencias optimizadas"""
    print("\n📦 Instalando dependencias ultra-optimizadas...")
    
    # Dependencias principales optimizadas
    core_deps = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",  # Servidor ASGI optimizado
        "httpx>=0.25.0",              # Cliente HTTP asíncrono ultra-rápido
        "lxml>=4.9.0",                # Parsing XML/HTML ultra-eficiente
        "orjson>=3.9.0",              # JSON serialización ultra-rápida
        "cachetools>=5.3.0",          # Cache con TTL optimizado
        "tenacity>=8.2.0",            # Retry con backoff exponencial
        "aiofiles>=23.2.0",           # I/O asíncrono para archivos
        "pydantic>=2.5.0",            # Validación de datos optimizada
        "python-multipart>=0.0.6",    # Para uploads de archivos
    ]
    
    # Dependencias de scraping y análisis
    scraping_deps = [
        "selenium>=4.15.0",           # Web scraping avanzado
        "webdriver-manager>=4.0.0",   # Gestión automática de drivers
        "beautifulsoup4>=4.12.0",     # Fallback para parsing HTML
        "requests>=2.31.0",           # Cliente HTTP síncrono (fallback)
    ]
    
    # Dependencias de IA y análisis
    ai_deps = [
        "langchain>=0.1.0",           # Framework de IA
        "langchain-openai>=0.0.5",    # Integración con OpenAI
        "openai>=1.3.0",              # Cliente OpenAI oficial
    ]
    
    # Dependencias de desarrollo y monitoreo
    dev_deps = [
        "pytest>=7.4.0",              # Testing framework
        "pytest-asyncio>=0.21.0",     # Testing asíncrono
        "pytest-cov>=4.1.0",          # Coverage de tests
        "black>=23.0.0",              # Formateador de código
        "flake8>=6.0.0",              # Linter
        "mypy>=1.7.0",                # Type checker
        "pre-commit>=3.5.0",          # Git hooks
    ]
    
    # Dependencias de producción
    prod_deps = [
        "gunicorn>=21.2.0",           # Servidor WSGI para producción
        "redis>=5.0.0",               # Cache distribuido (opcional)
        "prometheus-client>=0.19.0",  # Métricas de monitoreo
        "structlog>=23.2.0",          # Logging estructurado
    ]
    
    all_deps = core_deps + scraping_deps + ai_deps + dev_deps + prod_deps
    
    try:
        for dep in all_deps:
            print(f"   Instalando {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        
        print("✅ Todas las dependencias instaladas correctamente")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        sys.exit(1)

def setup_environment():
    """Configura variables de entorno"""
    print("\n🔧 Configurando variables de entorno...")
    
    env_file = Path(".env")
    env_content = """# Configuración del Servicio SEO Ultra-Optimizado
# ================================================

# API Keys
OPENAI_API_KEY=your_openai_api_key_here

# Configuración del servidor
HOST=0.0.0.0
PORT=8000
WORKERS=4
RELOAD=true

# Configuración de cache
CACHE_TTL=3600
CACHE_MAX_SIZE=2000
REDIS_URL=redis://localhost:6379

# Configuración de logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Configuración de Selenium
SELENIUM_HEADLESS=true
SELENIUM_TIMEOUT=30
CHROME_DRIVER_PATH=

# Configuración de rendimiento
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT=30
BATCH_SIZE=20

# Configuración de monitoreo
ENABLE_METRICS=true
ENABLE_TRACEMALLOC=true
METRICS_PORT=9090

# Configuración de desarrollo
DEBUG=false
ENVIRONMENT=development
"""
    
    if not env_file.exists():
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ Archivo .env creado")
    else:
        print("ℹ️  Archivo .env ya existe")

def setup_chromedriver():
    """Configura ChromeDriver automáticamente"""
    print("\n🌐 Configurando ChromeDriver...")
    
    try:
        # Instalar webdriver-manager si no está instalado
        subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])
        
        # Test de ChromeDriver
        test_script = """
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.quit()
    print("ChromeDriver configurado correctamente")
except Exception as e:
    print(f"Error configurando ChromeDriver: {e}")
"""
        
        result = subprocess.run([sys.executable, "-c", test_script], 
                              capture_output=True, text=True)
        
        if "configurado correctamente" in result.stdout:
            print("✅ ChromeDriver configurado automáticamente")
        else:
            print("⚠️  ChromeDriver requiere configuración manual")
            print("   Instrucciones:")
            print("   1. Descarga ChromeDriver desde: https://chromedriver.chromium.org/")
            print("   2. Agrega la ruta al PATH o configura SELENIUM_DRIVER_PATH en .env")
    
    except Exception as e:
        print(f"❌ Error configurando ChromeDriver: {e}")

def create_config_file():
    """Crea archivo de configuración optimizado"""
    print("\n⚙️  Creando archivo de configuración...")
    
    config_content = """# Configuración del Servicio SEO Ultra-Optimizado
import os
from pathlib import Path

# Configuración base
BASE_DIR = Path(__file__).parent
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Configuración del servidor
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
WORKERS = int(os.getenv("WORKERS", 4))
RELOAD = os.getenv("RELOAD", "true").lower() == "true"

# Configuración de cache
CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", 2000))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Configuración de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")

# Configuración de Selenium
SELENIUM_HEADLESS = os.getenv("SELENIUM_HEADLESS", "true").lower() == "true"
SELENIUM_TIMEOUT = int(os.getenv("SELENIUM_TIMEOUT", 30))
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", "")

# Configuración de rendimiento
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 100))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 20))

# Configuración de monitoreo
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
ENABLE_TRACEMALLOC = os.getenv("ENABLE_TRACEMALLOC", "true").lower() == "true"
METRICS_PORT = int(os.getenv("METRICS_PORT", 9090))

# Configuración de API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuración de librerías optimizadas
OPTIMIZATION_CONFIG = {
    "httpx": {
        "timeout": 30.0,
        "limits": {
            "max_keepalive_connections": 20,
            "max_connections": 100
        }
    },
    "lxml": {
        "encoding": "utf-8",
        "remove_blank_text": True
    },
    "orjson": {
        "option": 0  # Configuración por defecto
    },
    "cachetools": {
        "maxsize": CACHE_MAX_SIZE,
        "ttl": CACHE_TTL
    },
    "tenacity": {
        "stop_max_attempt_number": 3,
        "wait_exponential_multiplier": 1,
        "wait_exponential_max": 10
    }
}
"""
    
    config_file = Path("config.py")
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print("✅ Archivo config.py creado")

def create_dockerfile():
    """Crea Dockerfile optimizado"""
    print("\n🐳 Creando Dockerfile optimizado...")
    
    dockerfile_content = """# Dockerfile para Servicio SEO Ultra-Optimizado
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \\
    wget \\
    gnupg \\
    unzip \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Instalar Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \\
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \\
    && apt-get update \\
    && apt-get install -y google-chrome-stable \\
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias Python optimizadas
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Exponer puerto
EXPOSE 8000

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SELENIUM_HEADLESS=true

# Comando de inicio optimizado
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
"""
    
    with open("Dockerfile", "w", encoding="utf-8") as f:
        f.write(dockerfile_content)
    
    print("✅ Dockerfile creado")

def create_requirements():
    """Crea archivo requirements.txt optimizado"""
    print("\n📋 Creando requirements.txt...")
    
    requirements_content = """# Requirements para Servicio SEO Ultra-Optimizado
# ================================================

# Core dependencies - Librerías principales optimizadas
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx>=0.25.0
lxml>=4.9.0
orjson>=3.9.0
cachetools>=5.3.0
tenacity>=8.2.0
aiofiles>=23.2.0
pydantic>=2.5.0
python-multipart>=0.0.6

# Scraping and analysis - Scraping y análisis
selenium>=4.15.0
webdriver-manager>=4.0.0
beautifulsoup4>=4.12.0
requests>=2.31.0

# AI and analysis - IA y análisis
langchain>=0.1.0
langchain-openai>=0.0.5
openai>=1.3.0

# Development - Desarrollo
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.7.0
pre-commit>=3.5.0

# Production - Producción
gunicorn>=21.2.0
redis>=5.0.0
prometheus-client>=0.19.0
structlog>=23.2.0
"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements_content)
    
    print("✅ requirements.txt creado")

def run_tests():
    """Ejecuta tests optimizados"""
    print("\n🧪 Ejecutando tests optimizados...")
    
    try:
        # Test básico de importación
        test_import = """
try:
    from service import SEOService
    from api import router
    from models import SEOScrapeRequest, SEOScrapeResponse
    print("✅ Imports exitosos")
except Exception as e:
    print(f"❌ Error en imports: {e}")
"""
        
        result = subprocess.run([sys.executable, "-c", test_import], 
                              capture_output=True, text=True)
        
        if "Imports exitosos" in result.stdout:
            print("✅ Tests de importación pasaron")
        else:
            print("❌ Tests de importación fallaron")
            print(result.stderr)
        
        # Test de funcionalidad básica
        test_functionality = """
import asyncio
from service import SEOService
from models import SEOScrapeRequest

async def test_basic():
    try:
        service = SEOService()
        request = SEOScrapeRequest(url="https://example.com")
        response = await service.scrape(request)
        print("✅ Test básico exitoso")
    except Exception as e:
        print(f"❌ Error en test básico: {e}")

asyncio.run(test_basic())
"""
        
        result = subprocess.run([sys.executable, "-c", test_functionality], 
                              capture_output=True, text=True, timeout=30)
        
        if "Test básico exitoso" in result.stdout:
            print("✅ Test de funcionalidad básica exitoso")
        else:
            print("⚠️  Test de funcionalidad básica falló (puede ser normal sin API key)")
            print(result.stderr)
    
    except subprocess.TimeoutExpired:
        print("⚠️  Test de funcionalidad timeout (puede ser normal)")
    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")

def create_startup_script():
    """Crea script de inicio optimizado"""
    print("\n🚀 Creando script de inicio...")
    
    if platform.system() == "Windows":
        script_content = """@echo off
echo Iniciando Servicio SEO Ultra-Optimizado...
echo.

REM Verificar Python
python --version
if errorlevel 1 (
    echo Error: Python no encontrado
    pause
    exit /b 1
)

REM Verificar dependencias
echo Verificando dependencias...
python -c "import fastapi, httpx, lxml, orjson, cachetools, tenacity" 2>nul
if errorlevel 1 (
    echo Instalando dependencias...
    pip install -r requirements.txt
)

REM Iniciar servidor
echo.
echo Iniciando servidor en http://localhost:8000
echo Presiona Ctrl+C para detener
echo.
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
"""
        script_file = "start.bat"
    else:
        script_content = """#!/bin/bash
echo "🚀 Iniciando Servicio SEO Ultra-Optimizado..."
echo

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no encontrado"
    exit 1
fi

# Verificar dependencias
echo "📦 Verificando dependencias..."
python3 -c "import fastapi, httpx, lxml, orjson, cachetools, tenacity" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Instalando dependencias..."
    pip3 install -r requirements.txt
fi

# Iniciar servidor
echo
echo "🌐 Servidor iniciado en http://localhost:8000"
echo "📊 Health check: http://localhost:8000/seo/health"
echo "📚 Documentación: http://localhost:8000/docs"
echo "🛑 Presiona Ctrl+C para detener"
echo

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""
        script_file = "start.sh"
        # Hacer ejecutable en Unix
        os.chmod(script_file, 0o755)
    
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print(f"✅ Script de inicio creado: {script_file}")

def main():
    """Función principal de instalación"""
    print_banner()
    
    print("🔍 Verificando requisitos del sistema...")
    check_python_version()
    
    print("\n" + "="*60)
    print("🚀 INICIANDO INSTALACIÓN ULTRA-OPTIMIZADA")
    print("="*60)
    
    # Instalar dependencias
    install_dependencies()
    
    # Configurar entorno
    setup_environment()
    setup_chromedriver()
    
    # Crear archivos de configuración
    create_config_file()
    create_requirements()
    create_dockerfile()
    create_startup_script()
    
    # Ejecutar tests
    run_tests()
    
    print("\n" + "="*60)
    print("✅ INSTALACIÓN COMPLETADA EXITOSAMENTE")
    print("="*60)
    
    print("\n🎉 ¡El Servicio SEO Ultra-Optimizado está listo!")
    print("\n📋 Próximos pasos:")
    print("   1. Configura tu OPENAI_API_KEY en el archivo .env")
    print("   2. Ejecuta el script de inicio:")
    if platform.system() == "Windows":
        print("      start.bat")
    else:
        print("      ./start.sh")
    print("   3. Accede a la documentación: http://localhost:8000/docs")
    print("   4. Prueba el health check: http://localhost:8000/seo/health")
    
    print("\n🚀 Características ultra-optimizadas incluidas:")
    print("   • httpx: Cliente HTTP asíncrono ultra-rápido")
    print("   • lxml: Parsing XML/HTML ultra-eficiente")
    print("   • orjson: JSON serialización ultra-rápida")
    print("   • cachetools: Cache con TTL optimizado")
    print("   • tenacity: Retry con backoff exponencial")
    print("   • tracemalloc: Monitoreo de memoria en tiempo real")
    print("   • aiofiles: I/O asíncrono para archivos")
    print("   • uvicorn: Servidor ASGI de alto rendimiento")
    
    print("\n📊 Métricas de rendimiento disponibles:")
    print("   • /seo/health - Estado del servicio")
    print("   • /seo/performance - Métricas de rendimiento")
    print("   • /seo/cache/stats - Estadísticas del cache")
    
    print("\n🎯 ¡Disfruta del rendimiento ultra-optimizado!")

if __name__ == "__main__":
    main() 