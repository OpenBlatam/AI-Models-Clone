"""
Setup Script - Face Swap Modules
==================================
Script de instalación y configuración de dependencias.
"""

import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Verifica que la versión de Python sea compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Se requiere Python 3.7 o superior")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_package(package, description=""):
    """Instala un paquete usando pip."""
    try:
        print(f"📦 Instalando {package}...", end=" ")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
        print("✓")
        return True
    except subprocess.CalledProcessError:
        print("✗")
        return False


def check_package(package_name, import_name=None):
    """Verifica si un paquete está instalado."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def main():
    """Función principal de instalación."""
    print("=" * 60)
    print("🚀 INSTALACIÓN DE FACE SWAP MODULES")
    print("=" * 60)
    print()
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    print()
    print("📋 Verificando dependencias...")
    print()
    
    # Dependencias requeridas
    required = [
        ("opencv-python", "cv2"),
        ("numpy", "numpy"),
    ]
    
    # Dependencias opcionales recomendadas
    optional = [
        ("mediapipe", "mediapipe"),
        ("face-alignment", "face_alignment"),
        ("insightface", "insightface"),
    ]
    
    # Dependencias para optimizaciones
    optimization = [
        ("numba", "numba"),
    ]
    
    # Dependencias avanzadas
    advanced = [
        ("scikit-image", "skimage"),
        ("scipy", "scipy"),
    ]
    
    # Verificar e instalar requeridas
    print("🔴 Dependencias Requeridas:")
    missing_required = []
    for package, import_name in required:
        if check_package(package, import_name):
            print(f"  ✓ {package}")
        else:
            print(f"  ✗ {package} (faltante)")
            missing_required.append(package)
    
    if missing_required:
        print()
        print("📦 Instalando dependencias requeridas...")
        for package in missing_required:
            install_package(package)
    
    print()
    print("🟡 Dependencias Opcionales (Recomendadas):")
    missing_optional = []
    for package, import_name in optional:
        if check_package(package, import_name):
            print(f"  ✓ {package}")
        else:
            print(f"  ⚠ {package} (no instalado)")
            missing_optional.append(package)
    
    if missing_optional:
        print()
        response = input("¿Instalar dependencias opcionales recomendadas? (s/n): ")
        if response.lower() == 's':
            for package in missing_optional:
                install_package(package)
    
    print()
    print("⚡ Optimizaciones (Numba):")
    if check_package("numba", "numba"):
        print("  ✓ numba (optimizaciones activas)")
    else:
        print("  ⚠ numba (no instalado - sin optimizaciones)")
        response = input("¿Instalar Numba para optimizaciones? (s/n): ")
        if response.lower() == 's':
            install_package("numba")
    
    print()
    print("🎨 Dependencias Avanzadas:")
    missing_advanced = []
    for package, import_name in advanced:
        if check_package(package, import_name):
            print(f"  ✓ {package}")
        else:
            print(f"  ⚠ {package} (no instalado)")
            missing_advanced.append(package)
    
    if missing_advanced:
        print()
        response = input("¿Instalar dependencias avanzadas? (s/n): ")
        if response.lower() == 's':
            for package in missing_advanced:
                install_package(package)
    
    print()
    print("=" * 60)
    print("✅ INSTALACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("📚 Próximos pasos:")
    print("  1. Ejecutar: python validate_modules.py")
    print("  2. Ver: QUICK_START.md para comenzar")
    print("  3. Ver: README.md para documentación completa")
    print()


if __name__ == '__main__':
    main()








