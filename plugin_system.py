"""
Sistema de Plugins para Extensibilidad Modular
Permite cargar dinámicamente plugins para extender funcionalidad del sistema
"""

import asyncio
import importlib
import importlib.util
import inspect
import json
import logging
import os
import sys
import time
import yaml
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Type, Union
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PluginType(Enum):
    """Tipos de plugins disponibles."""
    OPTIMIZATION = "optimization"
    MONITORING = "monitoring"
    CONFIGURATION = "configuration"
    GRADIENT_ACCUMULATION = "gradient_accumulation"
    MEMORY_MANAGEMENT = "memory_management"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    ALERTING = "alerting"
    METRICS_STORAGE = "metrics_storage"
    CUSTOM = "custom"

class PluginStatus(Enum):
    """Estados de los plugins."""
    DISCOVERED = "discovered"
    LOADED = "loaded"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"
    UNLOADED = "unloaded"

@dataclass
class PluginMetadata:
    """Metadatos del plugin."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    entry_point: str = "main"
    config_schema: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

@dataclass
class PluginInfo:
    """Información completa del plugin."""
    metadata: PluginMetadata
    status: PluginStatus
    file_path: str
    load_time: Optional[float] = None
    error_message: Optional[str] = None
    instance: Optional[Any] = None
    config: Dict[str, Any] = field(default_factory=dict)

class BasePlugin(ABC):
    """Clase base para todos los plugins."""
    
    def __init__(self, metadata: PluginMetadata, config: Dict[str, Any] = None):
        self.metadata = metadata
        self.config = config or {}
        self.status = PluginStatus.LOADED
        self.initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Inicializar el plugin."""
        pass
    
    @abstractmethod
    async def start(self) -> bool:
        """Iniciar el plugin."""
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """Detener el plugin."""
        pass
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Ejecutar funcionalidad principal del plugin."""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del plugin."""
        return {
            'name': self.metadata.name,
            'version': self.metadata.version,
            'status': self.status.value,
            'initialized': self.initialized,
            'config': self.config
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """Actualizar configuración del plugin."""
        self.config.update(new_config)
        logger.info(f"Configuración actualizada para plugin {self.metadata.name}")

class OptimizationPlugin(BasePlugin):
    """Plugin base para optimizaciones."""
    
    async def initialize(self) -> bool:
        """Inicializar plugin de optimización."""
        try:
            # Verificar dependencias
            if not await self._check_dependencies():
                return False
            
            # Configurar optimizaciones
            await self._setup_optimizations()
            
            self.initialized = True
            self.status = PluginStatus.ACTIVE
            logger.info(f"Plugin de optimización {self.metadata.name} inicializado")
            return True
            
        except Exception as e:
            self.status = PluginStatus.ERROR
            logger.error(f"Error inicializando plugin {self.metadata.name}: {e}")
            return False
    
    async def start(self) -> bool:
        """Iniciar plugin de optimización."""
        if not self.initialized:
            logger.warning(f"Plugin {self.metadata.name} no está inicializado")
            return False
        
        try:
            self.status = PluginStatus.ACTIVE
            logger.info(f"Plugin de optimización {self.metadata.name} iniciado")
            return True
            
        except Exception as e:
            self.status = PluginStatus.ERROR
            logger.error(f"Error iniciando plugin {self.metadata.name}: {e}")
            return False
    
    async def stop(self) -> bool:
        """Detener plugin de optimización."""
        try:
            self.status = PluginStatus.DISABLED
            logger.info(f"Plugin de optimización {self.metadata.name} detenido")
            return True
            
        except Exception as e:
            logger.error(f"Error deteniendo plugin {self.metadata.name}: {e}")
            return False
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar optimización."""
        if not self.initialized or self.status != PluginStatus.ACTIVE:
            raise RuntimeError(f"Plugin {self.metadata.name} no está activo")
        
        return await self._apply_optimization(context)
    
    async def _check_dependencies(self) -> bool:
        """Verificar dependencias del plugin."""
        # Implementación base - plugins pueden sobrescribir
        return True
    
    async def _setup_optimizations(self):
        """Configurar optimizaciones del plugin."""
        # Implementación base - plugins pueden sobrescribir
        pass
    
    async def _apply_optimization(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Aplicar optimización específica del plugin."""
        # Implementación base - plugins pueden sobrescribir
        return {
            'plugin_name': self.metadata.name,
            'optimization_applied': False,
            'message': 'Método base - debe ser implementado por el plugin'
        }

class MonitoringPlugin(BasePlugin):
    """Plugin base para monitoreo."""
    
    async def initialize(self) -> bool:
        """Inicializar plugin de monitoreo."""
        try:
            # Verificar dependencias
            if not await self._check_dependencies():
                return False
            
            # Configurar métricas
            await self._setup_metrics()
            
            self.initialized = True
            self.status = PluginStatus.ACTIVE
            logger.info(f"Plugin de monitoreo {self.metadata.name} inicializado")
            return True
            
        except Exception as e:
            self.status = PluginStatus.ERROR
            logger.error(f"Error inicializando plugin {self.metadata.name}: {e}")
            return False
    
    async def start(self) -> bool:
        """Iniciar plugin de monitoreo."""
        if not self.initialized:
            logger.warning(f"Plugin {self.metadata.name} no está inicializado")
            return False
        
        try:
            self.status = PluginStatus.ACTIVE
            logger.info(f"Plugin de monitoreo {self.metadata.name} iniciado")
            return True
            
        except Exception as e:
            self.status = PluginStatus.ERROR
            logger.error(f"Error iniciando plugin {self.metadata.name}: {e}")
            return False
    
    async def stop(self) -> bool:
        """Detener plugin de monitoreo."""
        try:
            self.status = PluginStatus.DISABLED
            logger.info(f"Plugin de monitoreo {self.metadata.name} detenido")
            return True
            
        except Exception as e:
            logger.error(f"Error deteniendo plugin {self.metadata.name}: {e}")
            return False
    
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Ejecutar funcionalidad de monitoreo."""
        if not self.initialized or self.status != PluginStatus.ACTIVE:
            raise RuntimeError(f"Plugin {self.metadata.name} no está activo")
        
        return await self._collect_metrics(*args, **kwargs)
    
    async def _check_dependencies(self) -> bool:
        """Verificar dependencias del plugin."""
        return True
    
    async def _setup_metrics(self):
        """Configurar métricas del plugin."""
        pass
    
    async def _collect_metrics(self, *args, **kwargs) -> Dict[str, Any]:
        """Recolectar métricas específicas del plugin."""
        return {
            'plugin_name': self.metadata.name,
            'metrics_collected': False,
            'message': 'Método base - debe ser implementado por el plugin'
        }

class PluginManager:
    """Gestor principal de plugins."""
    
    def __init__(self, plugins_directory: str = "plugins"):
        self.plugins_directory = Path(plugins_directory)
        self.plugins: Dict[str, PluginInfo] = {}
        self.plugin_classes: Dict[str, Type[BasePlugin]] = {}
        self.loaded_modules: Dict[str, Any] = {}
        self.file_watcher: Optional[Observer] = None
        self.running = False
        
        # Crear directorio de plugins si no existe
        self.plugins_directory.mkdir(exist_ok=True)
        
        # Configurar watcher de archivos
        self._setup_file_watcher()
    
    def _setup_file_watcher(self):
        """Configurar observador de archivos para hot reload."""
        try:
            self.file_watcher = Observer()
            event_handler = PluginFileHandler(self)
            self.file_watcher.schedule(event_handler, str(self.plugins_directory), recursive=True)
            logger.info("✅ Observador de archivos de plugins configurado")
        except Exception as e:
            logger.warning(f"No se pudo configurar observador de archivos: {e}")
    
    async def start(self):
        """Iniciar gestor de plugins."""
        if self.running:
            return
        
        logger.info("🚀 Iniciando gestor de plugins...")
        
        # Iniciar observador de archivos
        if self.file_watcher:
            self.file_watcher.start()
        
        # Descubrir plugins existentes
        await self.discover_plugins()
        
        # Cargar plugins válidos
        await self.load_discovered_plugins()
        
        self.running = True
        logger.info("✅ Gestor de plugins iniciado")
    
    async def stop(self):
        """Detener gestor de plugins."""
        if not self.running:
            return
        
        logger.info("🛑 Deteniendo gestor de plugins...")
        
        # Detener todos los plugins
        for plugin_info in self.plugins.values():
            if plugin_info.instance and plugin_info.status == PluginStatus.ACTIVE:
                await plugin_info.instance.stop()
        
        # Detener observador de archivos
        if self.file_watcher:
            self.file_watcher.stop()
            self.file_watcher.join()
        
        self.running = False
        logger.info("✅ Gestor de plugins detenido")
    
    async def discover_plugins(self):
        """Descubrir plugins en el directorio."""
        logger.info(f"🔍 Descubriendo plugins en {self.plugins_directory}")
        
        discovered_count = 0
        
        for plugin_file in self.plugins_directory.rglob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
            
            try:
                plugin_name = plugin_file.stem
                
                # Verificar si ya está descubierto
                if plugin_name in self.plugins:
                    continue
                
                # Leer metadatos del plugin
                metadata = await self._read_plugin_metadata(plugin_file)
                
                if metadata:
                    plugin_info = PluginInfo(
                        metadata=metadata,
                        status=PluginStatus.DISCOVERED,
                        file_path=str(plugin_file)
                    )
                    
                    self.plugins[plugin_name] = plugin_info
                    discovered_count += 1
                    
                    logger.info(f"🔍 Plugin descubierto: {metadata.name} v{metadata.version}")
                
            except Exception as e:
                logger.warning(f"Error descubriendo plugin {plugin_file.name}: {e}")
        
        logger.info(f"✅ {discovered_count} plugins descubiertos")
    
    async def _read_plugin_metadata(self, plugin_file: Path) -> Optional[PluginMetadata]:
        """Leer metadatos del plugin desde el archivo."""
        try:
            # Intentar leer desde comentarios especiales
            metadata = await self._extract_metadata_from_comments(plugin_file)
            
            if metadata:
                return metadata
            
            # Intentar leer desde archivo de configuración
            config_file = plugin_file.with_suffix('.yaml')
            if config_file.exists():
                metadata = await self._read_metadata_from_config(config_file)
                if metadata:
                    return metadata
            
            # Crear metadatos por defecto
            return PluginMetadata(
                name=plugin_file.stem,
                version="1.0.0",
                description=f"Plugin {plugin_file.stem}",
                author="Unknown",
                plugin_type=PluginType.CUSTOM
            )
            
        except Exception as e:
            logger.warning(f"Error leyendo metadatos de {plugin_file.name}: {e}")
            return None
    
    async def _extract_metadata_from_comments(self, plugin_file: Path) -> Optional[PluginMetadata]:
        """Extraer metadatos desde comentarios del código."""
        try:
            with open(plugin_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar comentarios especiales
            lines = content.split('\n')
            metadata = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('# PLUGIN_NAME:'):
                    metadata['name'] = line.split(':', 1)[1].strip()
                elif line.startswith('# PLUGIN_VERSION:'):
                    metadata['version'] = line.split(':', 1)[1].strip()
                elif line.startswith('# PLUGIN_DESCRIPTION:'):
                    metadata['description'] = line.split(':', 1)[1].strip()
                elif line.startswith('# PLUGIN_AUTHOR:'):
                    metadata['author'] = line.split(':', 1)[1].strip()
                elif line.startswith('# PLUGIN_TYPE:'):
                    plugin_type_str = line.split(':', 1)[1].strip()
                    try:
                        metadata['plugin_type'] = PluginType(plugin_type_str)
                    except ValueError:
                        metadata['plugin_type'] = PluginType.CUSTOM
            
            if metadata:
                return PluginMetadata(
                    name=metadata.get('name', plugin_file.stem),
                    version=metadata.get('version', '1.0.0'),
                    description=metadata.get('description', f'Plugin {plugin_file.stem}'),
                    author=metadata.get('author', 'Unknown'),
                    plugin_type=metadata.get('plugin_type', PluginType.CUSTOM)
                )
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extrayendo metadatos de comentarios: {e}")
            return None
    
    async def _read_metadata_from_config(self, config_file: Path) -> Optional[PluginMetadata]:
        """Leer metadatos desde archivo de configuración."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if 'metadata' in config_data:
                metadata_data = config_data['metadata']
                return PluginMetadata(
                    name=metadata_data.get('name', config_file.stem),
                    version=metadata_data.get('version', '1.0.0'),
                    description=metadata_data.get('description', f'Plugin {config_file.stem}'),
                    author=metadata_data.get('author', 'Unknown'),
                    plugin_type=PluginType(metadata_data.get('plugin_type', 'custom')),
                    dependencies=metadata_data.get('dependencies', []),
                    requirements=metadata_data.get('requirements', []),
                    entry_point=metadata_data.get('entry_point', 'main'),
                    config_schema=metadata_data.get('config_schema', {}),
                    tags=metadata_data.get('tags', [])
                )
            
            return None
            
        except Exception as e:
            logger.debug(f"Error leyendo metadatos de configuración: {e}")
            return None
    
    async def load_discovered_plugins(self):
        """Cargar plugins descubiertos."""
        logger.info("📦 Cargando plugins descubiertos...")
        
        loaded_count = 0
        
        for plugin_name, plugin_info in self.plugins.items():
            if plugin_info.status == PluginStatus.DISCOVERED:
                try:
                    if await self.load_plugin(plugin_name):
                        loaded_count += 1
                except Exception as e:
                    logger.error(f"Error cargando plugin {plugin_name}: {e}")
                    plugin_info.status = PluginStatus.ERROR
                    plugin_info.error_message = str(e)
        
        logger.info(f"✅ {loaded_count} plugins cargados")
    
    async def load_plugin(self, plugin_name: str) -> bool:
        """Cargar un plugin específico."""
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin {plugin_name} no encontrado")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        try:
            # Cargar módulo
            module = await self._load_plugin_module(plugin_info.file_path)
            if not module:
                return False
            
            # Buscar clase del plugin
            plugin_class = await self._find_plugin_class(module, plugin_info.metadata.plugin_type)
            if not plugin_class:
                return False
            
            # Crear instancia del plugin
            plugin_instance = await self._create_plugin_instance(plugin_class, plugin_info)
            if not plugin_instance:
                return False
            
            # Inicializar plugin
            if await plugin_instance.initialize():
                plugin_info.instance = plugin_instance
                plugin_info.status = PluginStatus.LOADED
                plugin_info.load_time = time.time()
                
                # Iniciar plugin si el gestor está ejecutándose
                if self.running:
                    await plugin_instance.start()
                    plugin_info.status = PluginStatus.ACTIVE
                
                logger.info(f"✅ Plugin {plugin_name} cargado exitosamente")
                return True
            else:
                plugin_info.status = PluginStatus.ERROR
                plugin_info.error_message = "Error en inicialización"
                return False
                
        except Exception as e:
            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)
            logger.error(f"Error cargando plugin {plugin_name}: {e}")
            return False
    
    async def _load_plugin_module(self, file_path: str) -> Optional[Any]:
        """Cargar módulo del plugin."""
        try:
            # Generar nombre de módulo único
            module_name = f"plugin_{int(time.time())}_{hash(file_path)}"
            
            # Cargar especificación del módulo
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                return None
            
            # Cargar módulo
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return module
            
        except Exception as e:
            logger.error(f"Error cargando módulo del plugin: {e}")
            return None
    
    async def _find_plugin_class(self, module: Any, plugin_type: PluginType) -> Optional[Type[BasePlugin]]:
        """Encontrar clase del plugin en el módulo."""
        try:
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj != BasePlugin):
                    
                    # Verificar tipo de plugin
                    if hasattr(obj, 'metadata') and obj.metadata.plugin_type == plugin_type:
                        return obj
                    
                    # Si no tiene metadatos específicos, aceptar cualquier tipo
                    if not hasattr(obj, 'metadata'):
                        return obj
            
            return None
            
        except Exception as e:
            logger.error(f"Error buscando clase del plugin: {e}")
            return None
    
    async def _create_plugin_instance(self, plugin_class: Type[BasePlugin], plugin_info: PluginInfo) -> Optional[BasePlugin]:
        """Crear instancia del plugin."""
        try:
            # Crear instancia con metadatos y configuración
            plugin_instance = plugin_class(plugin_info.metadata, plugin_info.config)
            return plugin_instance
            
        except Exception as e:
            logger.error(f"Error creando instancia del plugin: {e}")
            return None
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Descargar un plugin."""
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin {plugin_name} no encontrado")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        try:
            # Detener plugin si está activo
            if plugin_info.instance and plugin_info.status == PluginStatus.ACTIVE:
                await plugin_info.instance.stop()
            
            # Limpiar instancia
            plugin_info.instance = None
            plugin_info.status = PluginStatus.UNLOADED
            plugin_info.load_time = None
            plugin_info.error_message = None
            
            logger.info(f"✅ Plugin {plugin_name} descargado")
            return True
            
        except Exception as e:
            logger.error(f"Error descargando plugin {plugin_name}: {e}")
            return False
    
    async def reload_plugin(self, plugin_name: str) -> bool:
        """Recargar un plugin."""
        logger.info(f"🔄 Recargando plugin {plugin_name}...")
        
        # Descargar plugin
        if not await self.unload_plugin(plugin_name):
            return False
        
        # Recargar plugin
        return await self.load_plugin(plugin_name)
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Obtener información de un plugin."""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins_info(self) -> Dict[str, PluginInfo]:
        """Obtener información de todos los plugins."""
        return self.plugins.copy()
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginInfo]:
        """Obtener plugins por tipo."""
        return [
            plugin_info for plugin_info in self.plugins.values()
            if plugin_info.metadata.plugin_type == plugin_type
        ]
    
    async def execute_plugin(self, plugin_name: str, *args, **kwargs) -> Any:
        """Ejecutar funcionalidad de un plugin."""
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin {plugin_name} no encontrado")
        
        plugin_info = self.plugins[plugin_name]
        
        if not plugin_info.instance:
            raise RuntimeError(f"Plugin {plugin_name} no está cargado")
        
        if plugin_info.status != PluginStatus.ACTIVE:
            raise RuntimeError(f"Plugin {plugin_name} no está activo")
        
        return await plugin_info.instance.execute(*args, **kwargs)

class PluginFileHandler(FileSystemEventHandler):
    """Manejador de eventos de archivos para hot reload."""
    
    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager
    
    def on_created(self, event):
        """Archivo creado."""
        if not event.is_directory and event.src_path.endswith('.py'):
            logger.info(f"📁 Nuevo archivo de plugin detectado: {event.src_path}")
            asyncio.create_task(self.plugin_manager.discover_plugins())
    
    def on_modified(self, event):
        """Archivo modificado."""
        if not event.is_directory and event.src_path.endswith('.py'):
            logger.info(f"📝 Archivo de plugin modificado: {event.src_path}")
            # Extraer nombre del plugin del path
            plugin_name = Path(event.src_path).stem
            asyncio.create_task(self.plugin_manager.reload_plugin(plugin_name))
    
    def on_deleted(self, event):
        """Archivo eliminado."""
        if not event.is_directory and event.src_path.endswith('.py'):
            logger.info(f"🗑️ Archivo de plugin eliminado: {event.src_path}")
            # Extraer nombre del plugin del path
            plugin_name = Path(event.src_path).stem
            asyncio.create_task(self.plugin_manager.unload_plugin(plugin_name))

async def run_plugin_system_demo():
    """Ejecutar demostración del sistema de plugins."""
    logger.info("🎯 Iniciando demostración del sistema de plugins...")
    
    # Crear gestor de plugins
    plugin_manager = PluginManager()
    
    try:
        # Iniciar gestor
        await plugin_manager.start()
        
        # Mostrar plugins disponibles
        plugins_info = plugin_manager.get_all_plugins_info()
        logger.info(f"Plugins disponibles: {len(plugins_info)}")
        
        for name, info in plugins_info.items():
            logger.info(f"  - {name}: {info.status.value}")
        
        # Mantener sistema ejecutándose
        await asyncio.sleep(10)
        
    finally:
        # Detener gestor
        await plugin_manager.stop()
    
    logger.info("✅ Demostración del sistema de plugins completada")

if __name__ == "__main__":
    # Ejecutar demostración
    asyncio.run(run_plugin_system_demo())
