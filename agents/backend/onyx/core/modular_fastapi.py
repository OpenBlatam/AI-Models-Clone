from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .modular_architecture import ModuleOrchestrator, module_registry
import structlog
    import uvicorn
from typing import Any, List, Dict, Optional
import logging
"""
🚀 MODULAR FASTAPI APPLICATION
==============================

FastAPI modular que integra el sistema de módulos ultra-avanzado.
"""



logger = structlog.get_logger(__name__)

# =============================================================================
# MODULAR APPLICATION MODELS
# =============================================================================

class ModuleActionRequest(BaseModel):
    """Request para acciones de módulos."""
    action: str
    data: Dict[str, Any] = {}
    config: Optional[Dict[str, Any]] = None

class ServiceRequest(BaseModel):
    """Request para servicios."""
    service_name: str
    action: str = "process"
    data: Dict[str, Any] = {}

# =============================================================================
# MODULAR FASTAPI CLASS
# =============================================================================

class ModularFastAPI:
    """FastAPI modular con sistema de módulos."""
    
    def __init__(self, 
                 title: str = "Modular FastAPI",
                 modules_path: str = "modules",
                 config_path: str = "config"):
        
    """__init__ function."""
self.orchestrator = ModuleOrchestrator(modules_path, config_path)
        self.app = None
        
    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None, None]:
        """Gestión del ciclo de vida de la aplicación."""
        logger.info("🚀 Starting Modular FastAPI...")
        
        # Inicializar orquestador
        success = await self.orchestrator.initialize()
        if not success:
            logger.error("Failed to initialize module orchestrator")
            raise RuntimeError("Module orchestrator initialization failed")
        
        # Aplicar middleware de módulos
        self._apply_modular_middleware(app)
        
        logger.info("✅ Modular FastAPI started successfully")
        
        yield
        
        # Cleanup
        logger.info("🛑 Shutting down Modular FastAPI...")
        await self.orchestrator.shutdown()
        logger.info("✅ Modular FastAPI shutdown complete")
    
    def create_app(self) -> FastAPI:
        """Crea la aplicación FastAPI modular."""
        self.app = FastAPI(
            title="🧩 Ultra-Modular FastAPI",
            description="""
            # 🌟 ULTRA-MODULAR FASTAPI
            
            Sistema modular ultra-avanzado con:
            
            ## 🧩 Características Modulares
            - **Carga Dinámica** de módulos
            - **Sistema de Plugins** extensible
            - **Registry de Servicios** centralizado
            - **Configuración Modular** por componente
            - **Middleware Modular** con prioridades
            
            ## 🔧 Módulos Disponibles
            - **AI Services** - Generación de contenido con IA
            - **Cache System** - Cache multi-nivel (L1/L2/L3)
            - **Microservices** - Patrones de microservicios
            - **Security** - Autenticación y autorización
            - **Monitoring** - Observabilidad y métricas
            
            ## 🎯 Capacidades
            - **Hot Reload** de módulos sin reiniciar
            - **Configuración en Tiempo Real**
            - **Health Checks** por módulo
            - **Dependency Injection** automático
            - **Service Discovery** integrado
            """,
            version="1.0.0-modular",
            lifespan=self.lifespan
        )
        
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        # Agregar rutas modulares
        self._add_modular_routes()
        
        return self.app
    
    def _apply_modular_middleware(self, app: FastAPI):
        """Aplica middleware de módulos."""
        middleware_stack = module_registry.get_middleware_stack()
        
        for middleware in middleware_stack:
            @app.middleware("http")
            async def modular_middleware(request: Request, call_next):
                
    """modular_middleware function."""
return await middleware.process_request(request, call_next)
    
    def _add_modular_routes(self) -> Any:
        """Agrega rutas modulares."""
        
        @self.app.get("/", tags=["🧩 Modular Root"])
        async def modular_root():
            """Root endpoint modular."""
            return {
                "🧩 system": "Ultra-Modular FastAPI",
                "version": "1.0.0",
                "architecture": "Dynamic Module System",
                "status": "🟢 OPERATIONAL",
                
                "🎯 features": [
                    "✅ Dynamic Module Loading",
                    "✅ Plugin System",
                    "✅ Service Registry",
                    "✅ Modular Configuration",
                    "✅ Hot Reload Support",
                    "✅ Health Monitoring",
                    "✅ Dependency Management"
                ],
                
                "📊 system_status": self.orchestrator.get_system_status(),
                
                "🔗 endpoints": {
                    "/modules": "Module management",
                    "/services": "Service operations", 
                    "/health": "System health",
                    "/config": "Configuration management"
                }
            }
        
        @self.app.get("/health", tags=["🏥 Health"])
        async def modular_health():
            """Health check modular."""
            health = await self.orchestrator.health_check()
            overall_status = "🟢 HEALTHY"
            
            # Verificar si algún módulo tiene problemas
            for module_health in health.get("modules", {}).values():
                if module_health.get("status") == "error":
                    overall_status = "🟡 DEGRADED"
                    break
            
            return {
                "🏥 overall_status": overall_status,
                "📊 system": health,
                "🕐 timestamp": asyncio.get_event_loop().time()
            }
        
        @self.app.get("/modules", tags=["🧩 Modules"])
        async def list_modules():
            """Lista módulos disponibles."""
            modules = module_registry.list_modules()
            return {
                "📦 modules": modules,
                "📊 summary": {
                    "total": len(modules),
                    "active": len([m for m in modules if m["status"] == "active"]),
                    "loaded": len([m for m in modules if m["status"] == "loaded"]),
                    "error": len([m for m in modules if m["status"] == "error"])
                }
            }
        
        @self.app.post("/modules/{module_name}/action", tags=["🧩 Modules"])
        async def module_action(module_name: str, request: ModuleActionRequest):
            """Ejecuta acción en módulo."""
            module = module_registry.get_module(module_name)
            if not module:
                raise HTTPException(status_code=404, detail=f"Module {module_name} not found")
            
            if request.action == "reload":
                success = await self.orchestrator.reload_module(module_name)
                return {"success": success, "action": "reload"}
            elif request.action == "health":
                health = await module.health_check()
                return {"health": health}
            elif request.action == "capabilities":
                capabilities = module.get_capabilities()
                return {"capabilities": capabilities}
            
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
        
        @self.app.get("/services", tags=["🔧 Services"])
        async def list_services():
            """Lista servicios disponibles."""
            services = module_registry.list_services()
            service_info = {}
            
            for service_name in services:
                service = module_registry.get_service(service_name)
                if service:
                    service_info[service_name] = service.get_service_info()
            
            return {
                "🔧 services": service_info,
                "📊 count": len(services)
            }
        
        @self.app.post("/services/call", tags=["🔧 Services"])
        async def call_service(request: ServiceRequest):
            """Llama a un servicio."""
            service = module_registry.get_service(request.service_name)
            if not service:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Service {request.service_name} not found"
                )
            
            try:
                result = await service.process(request.data, action=request.action)
                return {
                    "success": True,
                    "service": request.service_name,
                    "result": result
                }
            except Exception as e:
                logger.error(f"Service call failed", service=request.service_name, error=str(e))
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/system/status", tags=["📊 System"])
        async def system_status():
            """Estado completo del sistema."""
            return {
                "🎯 modular_system": self.orchestrator.get_system_status(),
                "🏥 health": await self.orchestrator.health_check(),
                "🧩 modules": module_registry.list_modules(),
                "🔧 services": module_registry.list_services(),
                "⚙️ middleware": [
                    mw.get_middleware_info() 
                    for mw in module_registry.get_middleware_stack()
                ]
            }

# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_modular_app(modules_path: str = "modules", config_path: str = "config") -> FastAPI:
    """Crea aplicación FastAPI modular."""
    modular_fastapi = ModularFastAPI(
        title="Ultra-Modular FastAPI",
        modules_path=modules_path,
        config_path=config_path
    )
    
    return modular_fastapi.create_app()

# Crear instancia por defecto
modular_app = create_modular_app(
    modules_path="agents/backend/onyx/core/modules",
    config_path="agents/backend/onyx/core/config"
)

if __name__ == "__main__":
    
    uvicorn.run(
        "modular_fastapi:modular_app",
        host="0.0.0.0",
        port=8001,  # Puerto diferente para evitar conflictos
        reload=True
    ) 