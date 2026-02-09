#!/usr/bin/env python3
"""
Test para verificar el sistema modular.
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, '..')

def main():
    print("🧪 VERIFICANDO SISTEMA MODULAR")
    print("=" * 50)
    
    try:
        # Test 1: Importar core
        print("🔍 Importando módulo core...")
        import core
        print("✅ Core importado exitosamente")
        
        # Test 2: Verificar disponibilidad del sistema modular
        modular_available = getattr(core, 'MODULAR_SYSTEM_AVAILABLE', False)
        print(f"📊 Sistema modular disponible: {modular_available}")
        
        # Test 3: Listar módulos disponibles
        print("\n📋 Módulos disponibles en core:")
        for attr in dir(core):
            if not attr.startswith('_'):
                print(f"  - {attr}")
        
        # Test 4: Intentar importar estructuras
        print("\n🔧 Probando importación de estructuras...")
        try:
            from core.dependency_structures import ServiceStatus
            print("✅ ServiceStatus importado:", ServiceStatus.UNKNOWN)
        except ImportError as e:
            print(f"❌ Error importando ServiceStatus: {e}")
        
        # Test 5: Verificar archivos del sistema modular
        print("\n📁 Verificando archivos del sistema modular...")
        modular_files = [
            'dependency_structures.py',
            'service_lifecycle.py', 
            'dependency_resolver.py',
            'health_monitor.py',
            'dependency_manager_modular.py'
        ]
        
        for file in modular_files:
            file_path = os.path.join('..', 'core', file)
            if os.path.exists(file_path):
                print(f"✅ {file} existe")
            else:
                print(f"❌ {file} no encontrado")
        
        print("\n🎉 Verificación completada!")
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
