"""
Script de Ejecución y Verificación
====================================

Ejecuta tests y verifica que todos los módulos funcionen correctamente.
"""

import sys
import asyncio
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Verifica que todos los imports funcionen"""
    logger.info("🔍 Verificando imports...")
    
    try:
        from shared_lib.middleware import setup_advanced_middleware
        logger.info("✅ Middleware importado correctamente")
    except Exception as e:
        logger.error(f"❌ Error importando middleware: {e}")
        return False
    
    # Verificar otros módulos opcionales
    optional_modules = [
        ("security", "oauth2_security"),
        ("workers", "WorkerManager"),
        ("messaging", "MessageBrokerManager"),
        ("database", "DatabaseManager"),
    ]
    
    for module_name, class_name in optional_modules:
        try:
            __import__(f"shared_lib.{module_name}")
            logger.info(f"✅ Módulo {module_name} disponible")
        except ImportError:
            logger.warning(f"⚠️  Módulo {module_name} no disponible (opcional)")
    
    return True


def test_middleware_setup():
    """Prueba la configuración del middleware"""
    logger.info("🔍 Probando setup de middleware...")
    
    try:
        from fastapi import FastAPI
        from shared_lib.middleware import setup_advanced_middleware
        
        app = FastAPI()
        setup_advanced_middleware(
            app,
            service_name="test_service",
            enable_opentelemetry=False  # Sin OpenTelemetry para tests rápidos
        )
        
        logger.info("✅ Middleware configurado correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error configurando middleware: {e}")
        return False


async def test_async_components():
    """Prueba componentes asíncronos"""
    logger.info("🔍 Probando componentes asíncronos...")
    
    try:
        # Probar workers si están disponibles
        try:
            from shared_lib.workers import WorkerManager, WorkerType
            
            worker_manager = WorkerManager(
                worker_type=WorkerType.ASYNC,
                max_workers=2
            )
            
            await worker_manager.start()
            logger.info("✅ Workers iniciados correctamente")
            
            await worker_manager.stop()
            logger.info("✅ Workers detenidos correctamente")
        except ImportError:
            logger.warning("⚠️  Workers no disponibles (opcional)")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error en componentes asíncronos: {e}")
        return False


def test_dependencies():
    """Verifica dependencias críticas"""
    logger.info("🔍 Verificando dependencias...")
    
    critical = ["fastapi", "starlette"]
    optional = ["opentelemetry", "jose", "passlib", "pika", "celery", "boto3"]
    
    missing_critical = []
    missing_optional = []
    
    for package in critical:
        try:
            __import__(package)
        except ImportError:
            missing_critical.append(package)
    
    for package in optional:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_optional.append(package)
    
    if missing_critical:
        logger.error(f"❌ Dependencias críticas faltantes: {', '.join(missing_critical)}")
        return False
    
    if missing_optional:
        logger.warning(f"⚠️  Dependencias opcionales faltantes: {', '.join(missing_optional)}")
    
    logger.info("✅ Dependencias verificadas")
    return True


async def main():
    """Función principal"""
    logger.info("🚀 Iniciando verificación de shared_lib...\n")
    
    results = []
    
    # Test 1: Dependencias
    results.append(("Dependencias", test_dependencies()))
    
    # Test 2: Imports
    results.append(("Imports", test_imports()))
    
    # Test 3: Middleware
    results.append(("Middleware Setup", test_middleware_setup()))
    
    # Test 4: Componentes asíncronos
    results.append(("Componentes Asíncronos", await test_async_components()))
    
    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*50)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    print(f"\nTotal: {passed}/{total} tests pasados")
    
    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) fallaron")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)




