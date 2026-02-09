"""
Verificador de Dependencias - Face Swap Modules
================================================
Verifica que todas las dependencias estén instaladas correctamente.
"""

import sys
from typing import Dict, List, Tuple


def check_dependency(package_name: str, import_name: str = None) -> Tuple[bool, str]:
    """
    Verifica si una dependencia está instalada.
    
    Returns:
        (installed, version_info)
    """
    if import_name is None:
        import_name = package_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        return True, version
    except ImportError:
        return False, None


def main():
    """Función principal."""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE DEPENDENCIAS")
    print("=" * 60)
    print()
    
    # Dependencias requeridas
    required = {
        "opencv-python": "cv2",
        "numpy": "numpy",
    }
    
    # Dependencias opcionales
    optional = {
        "mediapipe": "mediapipe",
        "face-alignment": "face_alignment",
        "insightface": "insightface",
        "retinaface": "retinaface",
    }
    
    # Optimizaciones
    optimizations = {
        "numba": "numba",
    }
    
    # Avanzadas
    advanced = {
        "scikit-image": "skimage",
        "scipy": "scipy",
        "kornia": "kornia",
    }
    
    all_ok = True
    
    # Verificar requeridas
    print("🔴 Dependencias Requeridas:")
    for package, import_name in required.items():
        installed, version = check_dependency(package, import_name)
        if installed:
            print(f"  ✓ {package:20s} v{version}")
        else:
            print(f"  ✗ {package:20s} NO INSTALADO")
            all_ok = False
    print()
    
    # Verificar opcionales
    print("🟡 Dependencias Opcionales:")
    optional_count = 0
    for package, import_name in optional.items():
        installed, version = check_dependency(package, import_name)
        if installed:
            print(f"  ✓ {package:20s} v{version}")
            optional_count += 1
        else:
            print(f"  ⚠ {package:20s} no instalado")
    print(f"  Instaladas: {optional_count}/{len(optional)}")
    print()
    
    # Verificar optimizaciones
    print("⚡ Optimizaciones:")
    for package, import_name in optimizations.items():
        installed, version = check_dependency(package, import_name)
        if installed:
            print(f"  ✓ {package:20s} v{version} (optimizaciones activas)")
        else:
            print(f"  ⚠ {package:20s} no instalado (sin optimizaciones)")
    print()
    
    # Verificar avanzadas
    print("🎨 Dependencias Avanzadas:")
    advanced_count = 0
    for package, import_name in advanced.items():
        installed, version = check_dependency(package, import_name)
        if installed:
            print(f"  ✓ {package:20s} v{version}")
            advanced_count += 1
        else:
            print(f"  ⚠ {package:20s} no instalado")
    print(f"  Instaladas: {advanced_count}/{len(advanced)}")
    print()
    
    # Resumen
    print("=" * 60)
    if all_ok:
        print("✅ Todas las dependencias requeridas están instaladas")
    else:
        print("❌ Faltan dependencias requeridas")
        print("   Ejecutar: python setup.py")
    print("=" * 60)


if __name__ == '__main__':
    main()








