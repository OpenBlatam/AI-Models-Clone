"""
🧩 MODULAR ARCHITECTURE SYSTEM
=============================

Sistema de arquitectura modular ultra-avanzado:
- Carga dinámica de módulos
- Sistema de plugins
- Registry de servicios
- Configuración modular
- Interfaces estándar
"""

import asyncio
import importlib
import inspect
import json
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Callable, Union
from functools import wraps
import logging
import structlog

logger = structlog.get_logger(__name__)

# =============================================================================
# MODULE INTERFACES
# =============================================================================

class ModuleStatus(Enum):
    """Estados de módulos."""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"

@dataclass
class ModuleMetadata:
    """Metadatos de módulo."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    optional_dependencies: List[str] = field(default_factory=list)
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    priority: int = 100  # Mayor número = mayor prioridad
    config_schema: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "dependencies": self.dependencies,
            "optional_dependencies": self.optional_dependencies,
            "category": self.category,
            "tags": self.tags,
            "priority": self.priority,
            "config_schema": self.config_schema
        }

class ModuleInterface(ABC):
    """Interfaz base para todos los módulos."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.status = ModuleStatus.UNLOADED
        self._initialized = False
    
    @property
    @abstractmethod
    def metadata(self) -> ModuleMetadata:
        """Metadatos del módulo."""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Inicializa el módulo."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """Cierra el módulo."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificación de salud del módulo."""
        return {
            "status": self.status.value,
            "initialized": self._initialized,
            "module": self.metadata.name,
            "version": self.metadata.version
        }
    
    def get_capabilities(self) -> List[str]:
        """Capacidades del módulo."""
        return []
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida configuración del módulo."""
        return True

class ServiceInterface(ABC):
    """Interfaz para servicios modulares."""
    
    @abstractmethod
    async def process(self, data: Any, **kwargs) -> Any:
        """Procesa datos."""
        pass
    
    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """Información del servicio."""
        pass

class MiddlewareInterface(ABC):
    """Interfaz para middleware modular."""
    
    @abstractmethod
    async def process_request(self, request: Any, call_next: Callable) -> Any:
        """Procesa request."""
        pass
    
    @abstractmethod
    def get_middleware_info(self) -> Dict[str, Any]:
        """Información del middleware."""
        pass

# =============================================================================
# MODULE REGISTRY
# =============================================================================

class ModuleRegistry:
    """Registry central de módulos."""
    
    def __init__(self):
        self._modules: Dict[str, ModuleInterface] = {}
        self._services: Dict[str, ServiceInterface] = {}
        self._middleware: List[MiddlewareInterface] = []
        self._dependencies: Dict[str, List[str]] = {}
        self._load_order: List[str] = []
        
    def register_module(self, module: ModuleInterface) -> bool:
        """Registra un módulo."""
        name = module.metadata.name
        
        if name in self._modules:
            logger.warning(f"Module {name} already registered")
            return False
        
        # Validar dependencias
        for dep in module.metadata.dependencies:
            if dep not in self._modules:
                logger.error(f"Missing dependency {dep} for module {name}")
                return False
        
        self._modules[name] = module
        self._dependencies[name] = module.metadata.dependencies
        
        # Calcular orden de carga
        self._calculate_load_order()
        
        logger.info(f"Module {name} registered", version=module.metadata.version)
        return True
    
    def register_service(self, name: str, service: ServiceInterface) -> bool:
        """Registra un servicio."""
        if name in self._services:
            logger.warning(f"Service {name} already registered")
            return False
        
        self._services[name] = service
        logger.info(f"Service {name} registered")
        return True
    
    def register_middleware(self, middleware: MiddlewareInterface, priority: int = 100) -> bool:
        """Registra middleware."""
        self._middleware.append((priority, middleware))
        self._middleware.sort(key=lambda x: x[0], reverse=True)
        logger.info(f"Middleware registered with priority {priority}")
        return True
    
    def get_module(self, name: str) -> Optional[ModuleInterface]:
        """Obtiene módulo por nombre."""
        return self._modules.get(name)
    
    def get_service(self, name: str) -> Optional[ServiceInterface]:
        """Obtiene servicio por nombre."""
        return self._services.get(name)
    
    def get_middleware_stack(self) -> List[MiddlewareInterface]:
        """Obtiene stack de middleware ordenado."""
        return [mw for _, mw in self._middleware]
    
    def list_modules(self) -> List[Dict[str, Any]]:
        """Lista todos los módulos."""
        return [
            {
                **module.metadata.to_dict(),
                "status": module.status.value,
                "initialized": module._initialized
            }
            for module in self._modules.values()
        ]
    
    def list_services(self) -> List[str]:
        """Lista todos los servicios."""
        return list(self._services.keys())
    
    def _calculate_load_order(self):
        """Calcula orden de carga basado en dependencias."""
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(name: str):
            if name in temp_visited:
                raise ValueError(f"Circular dependency detected: {name}")
            if name in visited:
                return
                
            temp_visited.add(name)
            
            for dep in self._dependencies.get(name, []):
                visit(dep)
            
            temp_visited.remove(name)
            visited.add(name)
            order.append(name)
        
        for module_name in self._modules.keys():
            if module_name not in visited:
                visit(module_name)
        
        self._load_order = order

# Global registry
module_registry = ModuleRegistry()

# =============================================================================
# MODULE LOADER
# =============================================================================

class DynamicModuleLoader:
    """Cargador dinámico de módulos."""
    
    def __init__(self, modules_path: str = "modules"):
        self.modules_path = Path(modules_path)
        self._loaded_modules: Dict[str, ModuleInterface] = {}
        
    async def discover_modules(self) -> List[str]:
        """Descubre módulos disponibles."""
        modules = []
        
        if not self.modules_path.exists():
            logger.warning(f"Modules path {self.modules_path} does not exist")
            return modules
        
        for item in self.modules_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                modules.append(item.name)
            elif item.suffix == ".py" and item.name != "__init__.py":
                modules.append(item.stem)
        
        logger.info(f"Discovered {len(modules)} modules", modules=modules)
        return modules
    
    async def load_module(self, module_name: str, config: Optional[Dict] = None) -> Optional[ModuleInterface]:
        """Carga un módulo dinámicamente."""
        try:
            # Importar módulo
            if self.modules_path.name not in sys.path:
                sys.path.insert(0, str(self.modules_path.parent))
            
            module_path = f"{self.modules_path.name}.{module_name}"
            imported_module = importlib.import_module(module_path)
            
            # Buscar clase que implemente ModuleInterface
            module_class = None
            for name, obj in inspect.getmembers(imported_module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, ModuleInterface) and 
                    obj is not ModuleInterface):
                    module_class = obj
                    break
            
            if not module_class:
                logger.error(f"No ModuleInterface implementation found in {module_name}")
                return None
            
            # Instanciar módulo
            module_instance = module_class(config)
            
            # Inicializar
            module_instance.status = ModuleStatus.LOADING
            if await module_instance.initialize():
                module_instance.status = ModuleStatus.LOADED
                module_instance._initialized = True
                
                # Registrar en registry
                if module_registry.register_module(module_instance):
                    self._loaded_modules[module_name] = module_instance
                    logger.info(f"Module {module_name} loaded successfully")
                    return module_instance
                else:
                    module_instance.status = ModuleStatus.ERROR
                    logger.error(f"Failed to register module {module_name}")
            else:
                module_instance.status = ModuleStatus.ERROR
                logger.error(f"Failed to initialize module {module_name}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading module {module_name}", error=str(e))
            return None
    
    async def unload_module(self, module_name: str) -> bool:
        """Descarga un módulo."""
        if module_name not in self._loaded_modules:
            return False
        
        module = self._loaded_modules[module_name]
        
        try:
            if await module.shutdown():
                module.status = ModuleStatus.UNLOADED
                module._initialized = False
                del self._loaded_modules[module_name]
                logger.info(f"Module {module_name} unloaded")
                return True
        except Exception as e:
            logger.error(f"Error unloading module {module_name}", error=str(e))
        
        return False
    
    async def reload_module(self, module_name: str, config: Optional[Dict] = None) -> Optional[ModuleInterface]:
        """Recarga un módulo."""
        await self.unload_module(module_name)
        
        # Recargar desde disco
        module_path = f"{self.modules_path.name}.{module_name}"
        if module_path in sys.modules:
            importlib.reload(sys.modules[module_path])
        
        return await self.load_module(module_name, config)
    
    def get_loaded_modules(self) -> Dict[str, ModuleInterface]:
        """Obtiene módulos cargados."""
        return self._loaded_modules.copy()

# =============================================================================
# CONFIGURATION MANAGER
# =============================================================================

class ModularConfigManager:
    """Gestor de configuración modular."""
    
    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._module_configs: Dict[str, Dict[str, Any]] = {}
        
    async def load_config(self, config_file: str = "config.json") -> bool:
        """Carga configuración principal."""
        config_file_path = self.config_path / config_file
        
        if not config_file_path.exists():
            logger.warning(f"Config file {config_file_path} does not exist")
            return False
        
        try:
            with open(config_file_path, 'r') as f:
                self._config = json.load(f)
            
            logger.info(f"Configuration loaded from {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading config", error=str(e))
            return False
    
    async def load_module_config(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Carga configuración específica de módulo."""
        config_file = self.config_path / "modules" / f"{module_name}.json"
        
        if not config_file.exists():
            # Usar configuración por defecto si existe
            default_config = self._config.get("modules", {}).get(module_name, {})
            self._module_configs[module_name] = default_config
            return default_config
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            self._module_configs[module_name] = config
            logger.info(f"Module config loaded for {module_name}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading module config for {module_name}", error=str(e))
            return None
    
    def get_config(self, key: str = None) -> Any:
        """Obtiene configuración."""
        if key is None:
            return self._config
        
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """Obtiene configuración de módulo."""
        return self._module_configs.get(module_name, {})
    
    def set_config(self, key: str, value: Any) -> None:
        """Establece configuración."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    async def save_config(self, config_file: str = "config.json") -> bool:
        """Guarda configuración."""
        config_file_path = self.config_path / config_file
        config_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_file_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            
            logger.info(f"Configuration saved to {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving config", error=str(e))
            return False

# =============================================================================
# MODULE ORCHESTRATOR
# =============================================================================

class ModuleOrchestrator:
    """Orquestador principal de módulos."""
    
    def __init__(self, 
                 modules_path: str = "modules",
                 config_path: str = "config"):
        self.loader = DynamicModuleLoader(modules_path)
        self.config_manager = ModularConfigManager(config_path)
        self.registry = module_registry
        self._active_modules: Dict[str, ModuleInterface] = {}
        
    async def initialize(self) -> bool:
        """Inicializa el orquestador."""
        try:
            # Cargar configuración
            await self.config_manager.load_config()
            
            # Descubrir módulos
            discovered_modules = await self.loader.discover_modules()
            
            # Cargar módulos habilitados
            enabled_modules = self.config_manager.get_config("modules.enabled") or []
            
            for module_name in discovered_modules:
                if not enabled_modules or module_name in enabled_modules:
                    module_config = await self.config_manager.load_module_config(module_name)
                    await self.load_module(module_name, module_config)
            
            logger.info("Module orchestrator initialized")
            return True
            
        except Exception as e:
            logger.error("Error initializing orchestrator", error=str(e))
            return False
    
    async def load_module(self, module_name: str, config: Optional[Dict] = None) -> bool:
        """Carga un módulo."""
        module = await self.loader.load_module(module_name, config)
        if module:
            self._active_modules[module_name] = module
            module.status = ModuleStatus.ACTIVE
            logger.info(f"Module {module_name} activated")
            return True
        return False
    
    async def unload_module(self, module_name: str) -> bool:
        """Descarga un módulo."""
        if module_name in self._active_modules:
            if await self.loader.unload_module(module_name):
                del self._active_modules[module_name]
                return True
        return False
    
    async def reload_module(self, module_name: str) -> bool:
        """Recarga un módulo."""
        config = self.config_manager.get_module_config(module_name)
        module = await self.loader.reload_module(module_name, config)
        if module:
            self._active_modules[module_name] = module
            module.status = ModuleStatus.ACTIVE
            return True
        return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Estado del sistema modular."""
        return {
            "active_modules": len(self._active_modules),
            "total_services": len(self.registry.list_services()),
            "middleware_count": len(self.registry.get_middleware_stack()),
            "modules": self.registry.list_modules()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificación de salud del sistema."""
        health = {
            "orchestrator": "healthy",
            "modules": {}
        }
        
        for name, module in self._active_modules.items():
            try:
                module_health = await module.health_check()
                health["modules"][name] = module_health
            except Exception as e:
                health["modules"][name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health
    
    async def shutdown(self) -> bool:
        """Cierra todos los módulos."""
        success = True
        
        for module_name in list(self._active_modules.keys()):
            if not await self.unload_module(module_name):
                success = False
        
        logger.info("Module orchestrator shutdown")
        return success

# Global orchestrator
orchestrator = ModuleOrchestrator()

# =============================================================================
# DECORATORS AND UTILITIES
# =============================================================================

def modular_service(name: str, category: str = "general"):
    """Decorador para registrar servicios modulares."""
    def decorator(cls):
        def register_service():
            service_instance = cls()
            module_registry.register_service(name, service_instance)
            logger.info(f"Service {name} registered via decorator")
        
        # Registrar automáticamente
        register_service()
        return cls
    
    return decorator

def modular_middleware(priority: int = 100):
    """Decorador para registrar middleware modular."""
    def decorator(cls):
        def register_middleware():
            middleware_instance = cls()
            module_registry.register_middleware(middleware_instance, priority)
            logger.info(f"Middleware registered via decorator with priority {priority}")
        
        # Registrar automáticamente
        register_middleware()
        return cls
    
    return decorator

# =============================================================================
# EXAMPLE MODULE BASE CLASSES
# =============================================================================

class ContentProcessorModule(ModuleInterface):
    """Módulo base para procesamiento de contenido."""
    
    async def process_content(self, content_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa contenido."""
        raise NotImplementedError

class AIServiceModule(ModuleInterface):
    """Módulo base para servicios de IA."""
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Genera contenido con IA."""
        raise NotImplementedError

class CacheModule(ModuleInterface):
    """Módulo base para cache."""
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del cache."""
        raise NotImplementedError
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Establece valor en cache."""
        raise NotImplementedError

class SecurityModule(ModuleInterface):
    """Módulo base para seguridad."""
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Autentica usuario."""
        raise NotImplementedError
    
    async def authorize(self, user: Dict[str, Any], resource: str, action: str) -> bool:
        """Autoriza acción."""
        raise NotImplementedError

if __name__ == "__main__":
    # Demo básico
    async def demo():
        print("🧩 Modular Architecture System Demo")
        
        # Inicializar orquestador
        success = await orchestrator.initialize()
        print(f"Orchestrator initialized: {success}")
        
        # Estado del sistema
        status = orchestrator.get_system_status()
        print(f"System status: {status}")
        
        # Health check
        health = await orchestrator.health_check()
        print(f"Health check: {health}")
    
    asyncio.run(demo()) 