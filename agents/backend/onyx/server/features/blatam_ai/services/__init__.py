"""
🔧 BLATAM AI SERVICES MODULE v5.0.0
===================================

Servicios modulares especializados:
- 🏢 Enterprise Processing Service
- 🎯 Optimization Service  
- 📊 Monitoring Service
- 🔄 Event Service
- 📝 Logging Service
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# 🔧 SERVICE REGISTRY
# =============================================================================

class BlatamServiceRegistry:
    """Registro modular de servicios."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._service_types: Dict[str, str] = {}
        self._initialized = False
    
    def register_service(self, name: str, service: Any, service_type: str = "generic"):
        """Registra un servicio."""
        self._services[name] = service
        self._service_types[name] = service_type
        logger.info(f"🔧 Service registered: {name} ({service_type})")
    
    def get_service(self, name: str) -> Optional[Any]:
        """Obtiene un servicio."""
        return self._services.get(name)
    
    def get_services_by_type(self, service_type: str) -> Dict[str, Any]:
        """Obtiene servicios por tipo."""
        return {
            name: service for name, service in self._services.items()
            if self._service_types.get(name) == service_type
        }
    
    def get_available_services(self) -> List[str]:
        """Lista servicios disponibles."""
        return list(self._services.keys())
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Health check de todos los servicios."""
        health_results = {}
        
        for name, service in self._services.items():
            try:
                if hasattr(service, 'health_check'):
                    health_results[name] = await service.health_check()
                else:
                    health_results[name] = {'status': 'healthy', 'type': 'no_health_check'}
            except Exception as e:
                health_results[name] = {'status': 'error', 'error': str(e)}
        
        return health_results

# =============================================================================
# 🏢 ENTERPRISE PROCESSING SERVICE
# =============================================================================

class EnterpriseProcessingService:
    """Servicio de procesamiento empresarial."""
    
    def __init__(self, speed_engine=None, nlp_engine=None):
        self.speed_engine = speed_engine
        self.nlp_engine = nlp_engine
        self.stats = {'total_processed': 0, 'success_count': 0}
    
    async def process_data(self, data: Any, user_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Procesa datos empresariales."""
        try:
            self.stats['total_processed'] += 1
            
            # Use speed engine if available
            if self.speed_engine and hasattr(self.speed_engine, 'ultra_fast_call'):
                result = await self.speed_engine.ultra_fast_call(self._process_core, data, user_id, **kwargs)
            else:
                result = await self._process_core(data, user_id, **kwargs)
            
            self.stats['success_count'] += 1
            return result
            
        except Exception as e:
            logger.error(f"Enterprise processing error: {e}")
            return {'error': str(e), 'success': False}
    
    async def _process_core(self, data: Any, user_id: Optional[str], **kwargs) -> Dict[str, Any]:
        """Procesamiento core."""
        return {
            'processed_data': data,
            'user_id': user_id,
            'service': 'enterprise_processing',
            'success': True
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check del servicio."""
        return {
            'status': 'healthy',
            'service_type': 'enterprise_processing',
            'stats': self.stats
        }

# =============================================================================
# 🎯 OPTIMIZATION SERVICE
# =============================================================================

class OptimizationService:
    """Servicio de optimización."""
    
    def __init__(self):
        self.optimization_history = []
    
    async def optimize_component(self, component: Any, strategy: str = "balanced") -> Dict[str, Any]:
        """Optimiza un componente."""
        try:
            if hasattr(component, 'optimize'):
                result = await component.optimize(strategy, {})
                self.optimization_history.append({
                    'component': type(component).__name__,
                    'strategy': strategy,
                    'result': result
                })
                return result
            else:
                return {'status': 'not_optimizable'}
        except Exception as e:
            return {'error': str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check del servicio."""
        return {
            'status': 'healthy',
            'service_type': 'optimization',
            'optimizations_performed': len(self.optimization_history)
        }

# =============================================================================
# 📊 MONITORING SERVICE
# =============================================================================

class MonitoringService:
    """Servicio de monitoreo."""
    
    def __init__(self):
        self.metrics_history = []
        self.alerts = []
    
    async def collect_metrics(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Recolecta métricas de componentes."""
        metrics = {}
        
        for name, component in components.items():
            try:
                if hasattr(component, 'get_stats'):
                    metrics[name] = component.get_stats()
                else:
                    metrics[name] = {'status': 'no_stats_available'}
            except Exception as e:
                metrics[name] = {'error': str(e)}
        
        self.metrics_history.append(metrics)
        
        # Keep only last 1000 metrics
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check del servicio."""
        return {
            'status': 'healthy',
            'service_type': 'monitoring',
            'metrics_collected': len(self.metrics_history),
            'alerts_active': len(self.alerts)
        }

# =============================================================================
# 🏭 SERVICE FACTORY
# =============================================================================

async def create_service_layer(service_container) -> BlatamServiceRegistry:
    """Factory para crear capa de servicios."""
    registry = BlatamServiceRegistry()
    
    # Get engines from container
    speed_engine = service_container.get_service('speed_engine') if hasattr(service_container, 'get_service') else None
    nlp_engine = service_container.get_service('nlp_engine') if hasattr(service_container, 'get_service') else None
    
    # Create and register services
    enterprise_service = EnterpriseProcessingService(speed_engine, nlp_engine)
    registry.register_service('enterprise_processing', enterprise_service, 'processing')
    
    optimization_service = OptimizationService()
    registry.register_service('optimization', optimization_service, 'optimization')
    
    monitoring_service = MonitoringService()
    registry.register_service('monitoring', monitoring_service, 'monitoring')
    
    logger.info("🔧 Service layer created with enterprise, optimization, and monitoring services")
    return registry

# =============================================================================
# 🌟 EXPORTS
# =============================================================================

__all__ = [
    "BlatamServiceRegistry",
    "EnterpriseProcessingService", 
    "OptimizationService",
    "MonitoringService",
    "create_service_layer"
] 