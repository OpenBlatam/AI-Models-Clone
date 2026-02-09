"""
Quick Test - Test Rápido de la Librería
=========================================

Test simple que verifica que la librería funciona.
"""

def test_import():
    """Test básico de import"""
    try:
        from shared_lib.middleware import setup_advanced_middleware
        print("✅ Import exitoso")
        return True
    except Exception as e:
        print(f"❌ Error en import: {e}")
        return False

def test_setup():
    """Test de setup"""
    try:
        from fastapi import FastAPI
        from shared_lib.middleware import setup_advanced_middleware
        
        app = FastAPI()
        setup_advanced_middleware(app, service_name="test", enable_opentelemetry=False)
        print("✅ Setup exitoso")
        return True
    except Exception as e:
        print(f"❌ Error en setup: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Ejecutando tests rápidos...\n")
    
    test1 = test_import()
    test2 = test_setup()
    
    print("\n" + "="*50)
    if test1 and test2:
        print("✅ Todos los tests pasaron")
        print("🚀 La librería está lista para usar")
    else:
        print("❌ Algunos tests fallaron")
        print("📝 Revisa los errores arriba")




