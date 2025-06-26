#!/usr/bin/env python3
"""
AUTOMATIC ADS OPTIMIZATION INSTALLER
===================================

Script para instalar automáticamente todas las librerías de optimización
necesarias para el backend de ads ultra-optimizado.
"""

import subprocess
import sys
import time

def run_command(command):
    """Ejecutar comando con manejo de errores"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout durante instalación"
    except Exception as e:
        return False, "", str(e)

def install_ads_optimizations():
    """Instalar todas las optimizaciones para ads backend"""
    
    print("🚀 ADS BACKEND OPTIMIZATION INSTALLER")
    print("="*50)
    print("Instalando librerías ultra-optimizadas para ads...")
    print()
    
    # Librerías de optimización específicas para ads
    ads_libraries = [
        ("orjson", "JSON ultra-rápido (5x faster)"),
        ("blake3", "Hash ultra-rápido (8x faster)"), 
        ("lz4", "Compresión ultra-rápida (10x faster)"),
        ("redis", "Cache distribuido para ads"),
        ("polars", "Data processing para ads analytics"),
        ("numba", "Cálculos optimizados (+15 score)"),
        ("uvloop", "Event loop ultra-rápido"),
        ("aiohttp", "HTTP client optimizado")
    ]
    
    installed = 0
    failed = 0
    
    for lib, description in ads_libraries:
        print(f"📦 Instalando {lib}... ({description})")
        
        success, stdout, stderr = run_command(f"pip install {lib}")
        
        if success:
            print(f"   ✅ {lib} instalado correctamente")
            installed += 1
        else:
            print(f"   ❌ Error instalando {lib}: {stderr}")
            failed += 1
        
        time.sleep(0.5)  # Pausa entre instalaciones
    
    print(f"\n{'='*50}")
    print(f"🎉 INSTALACIÓN COMPLETADA")
    print(f"✅ Instaladas: {installed}/{len(ads_libraries)}")
    print(f"❌ Fallidas: {failed}/{len(ads_libraries)}")
    
    if installed == len(ads_libraries):
        print(f"🔥 ¡Todas las librerías instaladas! Score esperado: 100/100")
    elif installed >= 6:
        print(f"⚡ Suficientes librerías para score 85-95/100")
    else:
        print(f"⚠️  Pocas librerías instaladas. Score estimado: {installed*15}/100")
    
    print(f"\n📊 PRÓXIMO PASO:")
    print(f"   Ejecutar: py optimized_ads_backend.py")
    print(f"   Para verificar el score de optimización")
    
    return installed, failed

if __name__ == "__main__":
    try:
        installed, failed = install_ads_optimizations()
        
        if failed == 0:
            print(f"\n🚀 Sistema listo para ads ultra-optimizados!")
            sys.exit(0)
        else:
            print(f"\n⚠️  Algunas librerías fallaron, pero el sistema funcionará")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n❌ Instalación cancelada por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error durante instalación: {e}")
        sys.exit(1) 