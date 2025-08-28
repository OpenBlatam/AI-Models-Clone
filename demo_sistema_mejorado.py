#!/usr/bin/env python3
"""
Demo del Sistema Modular Mejorado
Muestra las nuevas funcionalidades: plugins, métricas y configuración dinámica.
"""

import asyncio
import time
import sys
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, '.')

def print_header(title: str):
    """Imprimir un encabezado bonito"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_section(title: str):
    """Imprimir una sección"""
    print(f"\n📋 {title}")
    print("-" * 40)

async def demo_sistema_modular():
    """Demo completo del sistema modular mejorado"""
    
    print_header("SISTEMA MODULAR MEJORADO - DEMO COMPLETO")
    
    try:
        # Importar módulos del sistema
        from core.dependency_structures import ServiceStatus, ServicePriority
        from core.service_lifecycle import ServiceLifecycle
        from core.dependency_manager_modular import DependencyManager
        from core.plugin_manager import get_plugin_manager, register_hook
        from core.metrics_collector import get_metrics_collector, record_service_metric, record_global_metric
        from core.dynamic_config import get_config_manager, get_config, set_config
        
        print("✅ Todos los módulos importados exitosamente")
        
        # ============================================================================
        # 1. DEMO: Configuración Dinámica
        # ============================================================================
        
        print_section("1. CONFIGURACIÓN DINÁMICA")
        
        config_manager = get_config_manager()
        
        # Mostrar configuración actual
        print("📊 Configuración actual del sistema:")
        system_config = config_manager.get_section('system')
        if system_config:
            for key, value in system_config.data.items():
                print(f"  - {key}: {value}")
        
        # Cambiar configuración en tiempo real
        print("\n🔄 Cambiando configuración en tiempo real...")
        set_config("debug_mode", True, section="system")
        set_config("max_workers", 8, section="system")
        set_config("log_level", "DEBUG", section="system")
        
        print("✅ Configuración actualizada sin reiniciar el sistema")
        
        # ============================================================================
        # 2. DEMO: Sistema de Métricas
        # ============================================================================
        
        print_section("2. SISTEMA DE MÉTRICAS AVANZADAS")
        
        metrics_collector = get_metrics_collector()
        
        # Registrar algunas métricas de ejemplo
        print("📈 Registrando métricas de ejemplo...")
        
        record_global_metric("demo_start_time", time.time())
        record_service_metric("demo_service", "response_time", 0.15, unit="seconds")
        record_service_metric("demo_service", "requests_per_second", 42.5, unit="req/s")
        record_service_metric("demo_service", "error_rate", 0.02, unit="percentage")
        
        # Simular algunas operaciones
        for i in range(5):
            record_service_metric("demo_service", "operation_count", i + 1)
            await asyncio.sleep(0.1)
        
        # Obtener estadísticas
        print("\n📊 Estadísticas de métricas:")
        service_metrics = metrics_collector.get_service_metrics("demo_service")
        if service_metrics and 'metrics' in service_metrics:
            for metric_name, metric_data in service_metrics['metrics'].items():
                if 'statistics' in metric_data:
                    stats = metric_data['statistics']
                    print(f"  - {metric_name}: {stats.get('latest', 'N/A')} {metric_data.get('unit', '')}")
        
        # Calcular puntuación de salud
        health_score = metrics_collector.get_system_health_score()
        print(f"🏥 Puntuación de salud del sistema: {health_score:.1f}/100")
        
        # ============================================================================
        # 3. DEMO: Sistema de Plugins
        # ============================================================================
        
        print_section("3. SISTEMA DE PLUGINS")
        
        plugin_manager = get_plugin_manager()
        
        # Crear un plugin de ejemplo
        print("🔌 Creando plugin de ejemplo...")
        
        # Crear directorio de plugins si no existe
        plugins_dir = Path("plugins")
        plugins_dir.mkdir(exist_ok=True)
        
        # Crear un plugin simple
        plugin_code = '''
"""
Plugin de ejemplo para el demo
"""

__version__ = "1.0.0"
__description__ = "Plugin de demostración"
__author__ = "Sistema Modular"

def register_hooks(plugin_manager):
    """Registrar hooks del plugin"""
    plugin_manager.register_hook("service_start", on_service_start, priority=10)
    plugin_manager.register_hook("service_stop", on_service_stop, priority=5)

def on_service_start(service_name):
    """Callback cuando un servicio inicia"""
    print(f"🎉 Plugin: Servicio {service_name} ha iniciado!")
    return f"Plugin procesado: {service_name}"

def on_service_stop(service_name):
    """Callback cuando un servicio se detiene"""
    print(f"🛑 Plugin: Servicio {service_name} se ha detenido!")
    return f"Plugin procesado: {service_name}"
'''
        
        with open(plugins_dir / "demo_plugin.py", "w") as f:
            f.write(plugin_code)
        
        # Cargar el plugin
        print("📦 Cargando plugin...")
        if plugin_manager.load_plugin("demo_plugin"):
            print("✅ Plugin cargado exitosamente")
            
            # Mostrar información del plugin
            plugin_info = plugin_manager.get_plugin_info("demo_plugin")
            if plugin_info:
                print(f"  - Nombre: {plugin_info.name}")
                print(f"  - Versión: {plugin_info.version}")
                print(f"  - Descripción: {plugin_info.description}")
                print(f"  - Autor: {plugin_info.author}")
        else:
            print("❌ Error cargando plugin")
        
        # ============================================================================
        # 4. DEMO: Dependency Manager Mejorado
        # ============================================================================
        
        print_section("4. GESTOR DE DEPENDENCIAS MEJORADO")
        
        # Crear instancia del gestor
        dm = DependencyManager()
        
        # Registrar servicios de ejemplo
        print("🔧 Registrando servicios de ejemplo...")
        
        def create_database_service():
            return {"type": "database", "connection": "postgresql://localhost/db"}
        
        def create_api_service():
            return {"type": "api", "port": 8000, "host": "0.0.0.0"}
        
        def create_cache_service():
            return {"type": "cache", "backend": "redis", "ttl": 3600}
        
        dm.register_service("database", "database", create_database_service, 
                          ServicePriority.CRITICAL)
        dm.register_service("cache", "cache", create_cache_service, 
                          ServicePriority.HIGH, dependencies=["database"])
        dm.register_service("api", "api", create_api_service, 
                          ServicePriority.NORMAL, dependencies=["cache"])
        
        print("✅ Servicios registrados con dependencias")
        
        # Mostrar información de servicios
        print("\n📋 Información de servicios:")
        for service_info in dm.get_all_services():
            print(f"  - {service_info.name}: {service_info.service_type} (Prioridad: {service_info.priority.name})")
            if service_info.dependencies:
                print(f"    Dependencias: {', '.join(service_info.dependencies)}")
        
        # ============================================================================
        # 5. DEMO: Integración Completa
        # ============================================================================
        
        print_section("5. INTEGRACIÓN COMPLETA")
        
        # Simular el ciclo de vida de un servicio con todas las funcionalidades
        print("🔄 Simulando ciclo de vida completo...")
        
        # Ejecutar hooks de inicio
        print("🔌 Ejecutando hooks de inicio...")
        hook_results = await plugin_manager.execute_hooks("service_start", "demo_service")
        for result in hook_results:
            if result:
                print(f"  - Hook ejecutado: {result}")
        
        # Registrar métricas durante la operación
        print("📊 Registrando métricas durante operación...")
        for i in range(3):
            record_service_metric("demo_service", "active_connections", 10 + i)
            record_service_metric("demo_service", "memory_usage", 512 + i * 64, unit="MB")
            await asyncio.sleep(0.2)
        
        # Ejecutar hooks de parada
        print("🔌 Ejecutando hooks de parada...")
        hook_results = await plugin_manager.execute_hooks("service_stop", "demo_service")
        for result in hook_results:
            if result:
                print(f"  - Hook ejecutado: {result}")
        
        # ============================================================================
        # 6. DEMO: Exportación y Reportes
        # ============================================================================
        
        print_section("6. EXPORTACIÓN Y REPORTES")
        
        # Exportar métricas
        print("📤 Exportando métricas...")
        try:
            export_path = metrics_collector.export_metrics()
            print(f"✅ Métricas exportadas a: {export_path}")
        except Exception as e:
            print(f"⚠️ Error exportando métricas: {e}")
        
        # Exportar configuración
        print("📤 Exportando configuración...")
        try:
            config_path = config_manager.export_config("config_export.json")
            print(f"✅ Configuración exportada a: {config_path}")
        except Exception as e:
            print(f"⚠️ Error exportando configuración: {e}")
        
        # ============================================================================
        # RESUMEN FINAL
        # ============================================================================
        
        print_section("RESUMEN DEL DEMO")
        
        print("🎉 ¡Demo completado exitosamente!")
        print("\n✅ Funcionalidades demostradas:")
        print("  - ✅ Configuración dinámica con hot-reload")
        print("  - ✅ Sistema de métricas avanzadas")
        print("  - ✅ Sistema de plugins extensible")
        print("  - ✅ Gestión de dependencias mejorada")
        print("  - ✅ Integración completa de componentes")
        print("  - ✅ Exportación de datos y reportes")
        
        print(f"\n📊 Estadísticas finales:")
        print(f"  - Plugins cargados: {len(plugin_manager.list_plugins())}")
        print(f"  - Servicios registrados: {len(dm.get_all_services())}")
        print(f"  - Métricas recolectadas: {len(metrics_collector.services)}")
        print(f"  - Configuraciones activas: {len(config_manager.sections)}")
        
        print("\n🚀 El sistema modular mejorado está completamente operativo!")
        
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("💡 Asegúrate de que todos los módulos estén disponibles")
        
    except Exception as e:
        print(f"❌ Error durante el demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 INICIANDO DEMO DEL SISTEMA MODULAR MEJORADO")
    print("=" * 60)
    
    # Ejecutar el demo
    asyncio.run(demo_sistema_modular())
    
    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETADO")
    print("=" * 60)
