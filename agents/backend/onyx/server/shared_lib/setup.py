"""
Setup script para la librería compartida
==========================================

Este script ayuda a configurar y verificar la librería compartida.
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    required_packages = [
        "fastapi",
        "opentelemetry",
        "jose",
        "passlib",
        "pika",
        "kafka",
        "redis",
        "celery",
        "boto3",
        "elasticsearch",
        "pymemcache",
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Dependencias faltantes: {', '.join(missing)}")
        print("Instala con: pip install -r shared_lib/requirements.txt")
        return False
    else:
        print("✅ Todas las dependencias están instaladas")
        return True

def verify_structure():
    """Verifica la estructura de la librería"""
    required_dirs = [
        "middleware",
        "security",
        "workers",
        "messaging",
        "gateway",
        "service_mesh",
        "database",
        "search",
        "cache",
        "security_owasp",
        "serverless",
        "logging",
        "discovery",
        "inter_service",
    ]
    
    base_path = Path(__file__).parent
    missing = []
    
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if not dir_path.exists():
            missing.append(dir_name)
    
    if missing:
        print(f"⚠️  Directorios faltantes: {', '.join(missing)}")
        print("Algunos módulos pueden no estar disponibles")
        return False
    else:
        print("✅ Estructura de directorios correcta")
        return True

def main():
    """Función principal"""
    print("🔍 Verificando librería compartida...\n")
    
    structure_ok = verify_structure()
    deps_ok = check_dependencies()
    
    print("\n" + "="*50)
    if structure_ok and deps_ok:
        print("✅ La librería está lista para usar")
        return 0
    else:
        print("⚠️  La librería necesita configuración adicional")
        return 1

if __name__ == "__main__":
    sys.exit(main())




