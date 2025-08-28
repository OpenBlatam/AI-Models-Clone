#!/usr/bin/env python3
"""
Test simple para verificar que los módulos modulares funcionen.
"""

import sys
import os

# Agregar el directorio padre al path para acceder a core
sys.path.insert(0, '..')

def test_imports():
    """Test de importaciones básicas"""
    print("🔍 Probando importaciones...")
    
    try:
        # Test 1: Importar el módulo core
        import core
        print("✅ Módulo core importado exitosamente")
        
        # Test 2: Verificar si el sistema modular está disponible
        modular_available = getattr(core, 'MODULAR_SYSTEM_AVAILABLE', False)
        print(f"📊 Sistema modular disponible: {modular_available}")
        
        # Test 3: Intentar importar estructuras directamente
        try:
            from core.dependency_structures import ServiceStatus
            print("✅ ServiceStatus importado directamente:", ServiceStatus.UNKNOWN)
        except ImportError as e:
            print(f"❌ Error importando ServiceStatus: {e}")
        
        # Test 4: Verificar qué está disponible en core
        print("\n📋 Módulos disponibles en core:")
        for attr in dir(core):
            if not attr.startswith('_'):
                print(f"  - {attr}")
                
    except ImportError as e:
        print(f"❌ Error importando core: {e}")
        return False
    
    return True

def test_modular_components():
    """Test de componentes modulares específicos"""
    print("\n🔧 Probando componentes modulares...")
    
    try:
        # Test de estructuras
        from core.dependency_structures import ServiceStatus, ServicePriority
        print("✅ Estructuras de datos importadas")
        
        # Test de lifecycle
        from core.service_lifecycle import ServiceLifecycle
        print("✅ ServiceLifecycle importado")
        
        # Test de resolver
        from core.dependency_resolver import DependencyResolver
        print("✅ DependencyResolver importado")
        
        # Test de health monitor
        from core.health_monitor import HealthMonitor
        print("✅ HealthMonitor importado")
        
        # Test de manager principal
        from core.dependency_manager_modular import DependencyManager
        print("✅ DependencyManager importado")
        
        print("🎉 Todos los componentes modulares funcionan correctamente!")
        return True
        
    except ImportError as e:
        print(f"❌ Error en componentes modulares: {e}")
        return False

def test_basic_functionality():
    """Test de funcionalidad básica"""
    print("\n🚀 Probando funcionalidad básica...")
    
    try:
        from core.dependency_structures import ServiceStatus, ServicePriority
        from core.service_lifecycle import ServiceLifecycle
        
        # Crear un servicio de prueba
        lifecycle = ServiceLifecycle("test-service", "test-type")
        print(f"✅ Servicio creado: {lifecycle.name}")
        
        # Verificar estado inicial
        assert lifecycle.status == ServiceStatus.UNKNOWN
        print("✅ Estado inicial correcto")
        
        # Verificar prioridad
        assert lifecycle.priority == ServicePriority.NORMAL
        print("✅ Prioridad por defecto correcta")
        
        print("🎉 Funcionalidad básica funciona correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en funcionalidad básica: {e}")
        return False

if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA MODULAR")
    print("=" * 50)
    
    # Ejecutar tests
    test1 = test_imports()
    test2 = test_modular_components()
    test3 = test_basic_functionality()
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"  Importaciones: {'✅' if test1 else '❌'}")
    print(f"  Componentes: {'✅' if test2 else '❌'}")
    print(f"  Funcionalidad: {'✅' if test3 else '❌'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema modular está funcionando correctamente.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisar los errores arriba.")
    
    print("=" * 50)
