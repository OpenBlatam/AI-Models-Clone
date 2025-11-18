#!/usr/bin/env python3
"""
AI Search Model - Script de Inicio
Inicia el servidor backend y opcionalmente el frontend
"""

import os
import sys
import subprocess
import time
import signal
import argparse
from pathlib import Path

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        return False
    
    # Verificar dependencias principales
    required_packages = [
        'fastapi', 'uvicorn', 'sentence_transformers', 
        'scikit-learn', 'numpy', 'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Faltan dependencias: {', '.join(missing_packages)}")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def check_frontend_dependencies():
    """Verificar dependencias del frontend"""
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("⚠️  Directorio frontend no encontrado")
        return False
    
    node_modules = frontend_path / "node_modules"
    if not node_modules.exists():
        print("⚠️  Dependencias del frontend no instaladas")
        print("💡 Ejecuta: cd frontend && npm install")
        return False
    
    return True

def start_backend(host="0.0.0.0", port=8000, reload=True):
    """Iniciar el servidor backend"""
    print(f"🚀 Iniciando servidor backend en http://{host}:{port}")
    
    # Cambiar al directorio del backend
    backend_path = Path("backend")
    if not backend_path.exists():
        print("❌ Error: Directorio backend no encontrado")
        return None
    
    # Comando para iniciar uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", host,
        "--port", str(port),
        "--log-level", "info"
    ]
    
    if reload:
        cmd.append("--reload")
    
    try:
        # Iniciar proceso
        process = subprocess.Popen(
            cmd,
            cwd=backend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Mostrar logs en tiempo real
        print("📋 Logs del backend:")
        print("-" * 50)
        
        # Leer output línea por línea
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"[BACKEND] {line.strip()}")
                if "Uvicorn running on" in line:
                    print("✅ Backend iniciado correctamente")
                    break
        
        return process
        
    except Exception as e:
        print(f"❌ Error al iniciar backend: {e}")
        return None

def start_frontend(port=3000):
    """Iniciar el servidor frontend"""
    print(f"🌐 Iniciando servidor frontend en http://localhost:{port}")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("❌ Error: Directorio frontend no encontrado")
        return None
    
    try:
        # Comando para iniciar React
        cmd = ["npm", "start"]
        
        # Configurar variable de entorno para el puerto
        env = os.environ.copy()
        env["PORT"] = str(port)
        
        process = subprocess.Popen(
            cmd,
            cwd=frontend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=env
        )
        
        print("📋 Logs del frontend:")
        print("-" * 50)
        
        # Leer output línea por línea
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"[FRONTEND] {line.strip()}")
                if "Local:" in line or "webpack compiled" in line:
                    print("✅ Frontend iniciado correctamente")
                    break
        
        return process
        
    except Exception as e:
        print(f"❌ Error al iniciar frontend: {e}")
        return None

def create_env_file():
    """Crear archivo .env si no existe"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creando archivo .env...")
        
        env_content = """# AI Search Model - Configuración
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Database
DATABASE_PATH=vector_database.db
EMBEDDINGS_PATH=embeddings.pkl
BACKUP_PATH=backups

# AI Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
MAX_QUERY_LENGTH=512
MAX_CONTENT_LENGTH=100000
SNIPPET_LENGTH=200

# Search Configuration
DEFAULT_SEARCH_LIMIT=10
MAX_SEARCH_LIMIT=100
SIMILARITY_THRESHOLD=0.1
SEMANTIC_WEIGHT=0.7
KEYWORD_WEIGHT=0.3

# Logging
LOG_LEVEL=INFO
LOG_FILE=

# CORS
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true

# Security
API_KEY_REQUIRED=false
API_KEY=
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Cache
ENABLE_CACHE=true
CACHE_TTL=3600

# Document Processing
SUPPORTED_DOCUMENT_TYPES=["text", "markdown", "html", "json", "pdf"]
BATCH_SIZE=100

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
"""
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Archivo .env creado")
    else:
        print("✅ Archivo .env ya existe")

def signal_handler(signum, frame):
    """Manejar señales de interrupción"""
    print("\n🛑 Deteniendo servidores...")
    sys.exit(0)

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="AI Search Model - Script de Inicio")
    parser.add_argument("--backend-only", action="store_true", help="Iniciar solo el backend")
    parser.add_argument("--frontend-only", action="store_true", help="Iniciar solo el frontend")
    parser.add_argument("--host", default="0.0.0.0", help="Host del backend (default: 0.0.0.0)")
    parser.add_argument("--backend-port", type=int, default=8000, help="Puerto del backend (default: 8000)")
    parser.add_argument("--frontend-port", type=int, default=3000, help="Puerto del frontend (default: 3000)")
    parser.add_argument("--no-reload", action="store_true", help="Desactivar reload del backend")
    parser.add_argument("--skip-deps", action="store_true", help="Saltar verificación de dependencias")
    
    args = parser.parse_args()
    
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🤖 AI Search Model - Iniciando Sistema")
    print("=" * 50)
    
    # Crear archivo .env si no existe
    create_env_file()
    
    # Verificar dependencias
    if not args.skip_deps:
        if not check_dependencies():
            return 1
    
    processes = []
    
    try:
        # Iniciar backend
        if not args.frontend_only:
            backend_process = start_backend(
                host=args.host,
                port=args.backend_port,
                reload=not args.no_reload
            )
            if backend_process:
                processes.append(backend_process)
            else:
                print("❌ No se pudo iniciar el backend")
                return 1
        
        # Iniciar frontend
        if not args.backend_only:
            if check_frontend_dependencies():
                frontend_process = start_frontend(port=args.frontend_port)
                if frontend_process:
                    processes.append(frontend_process)
                else:
                    print("❌ No se pudo iniciar el frontend")
            else:
                print("⚠️  Saltando frontend por dependencias faltantes")
        
        # Mostrar información de acceso
        print("\n" + "=" * 50)
        print("🎉 Sistema iniciado correctamente!")
        print("=" * 50)
        
        if not args.frontend_only:
            print(f"🔗 Backend API: http://{args.host}:{args.backend_port}")
            print(f"📚 API Docs: http://{args.host}:{args.backend_port}/docs")
            print(f"❤️  Health Check: http://{args.host}:{args.backend_port}/health")
        
        if not args.backend_only and check_frontend_dependencies():
            print(f"🌐 Frontend: http://localhost:{args.frontend_port}")
        
        print("\n💡 Presiona Ctrl+C para detener todos los servidores")
        print("=" * 50)
        
        # Mantener procesos ejecutándose
        while True:
            time.sleep(1)
            
            # Verificar que los procesos sigan ejecutándose
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    print(f"⚠️  Proceso {i+1} terminó inesperadamente")
                    processes.pop(i)
                    break
            
            if not processes:
                print("❌ Todos los procesos han terminado")
                break
    
    except KeyboardInterrupt:
        print("\n🛑 Interrumpido por el usuario")
    
    finally:
        # Terminar todos los procesos
        for process in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        print("✅ Todos los servidores detenidos")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())



























