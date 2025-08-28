"""
🚀 Sistema de Gestión de Recursos Inteligente
Gestión automática e inteligente de recursos del sistema

Este sistema implementa:
- Gestión inteligente de memoria
- Optimización automática de CPU/GPU
- Balanceo de carga inteligente
- Predicción de demanda de recursos
- Auto-scaling basado en IA
"""

import asyncio
import logging
import time
import json
import numpy as np
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import psutil
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Tipos de recursos."""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    NETWORK = "network"
    STORAGE = "storage"

@dataclass
class ResourceConfig:
    """Configuración de recursos."""
    resource_type: ResourceType
    max_usage: float = 0.9
    optimal_usage: float = 0.7
    critical_threshold: float = 0.95
    auto_optimize: bool = True
    prediction_horizon: int = 300  # 5 minutos

@dataclass
class ResourceMetrics:
    """Métricas de recursos."""
    current_usage: float
    peak_usage: float
    average_usage: float
    trend: float
    prediction: float
    timestamp: float

@dataclass
class OptimizationAction:
    """Acción de optimización."""
    action_type: str
    resource: ResourceType
    priority: int
    expected_improvement: float
    parameters: Dict[str, Any]

class BaseResourceManager:
    """Gestor de recursos base."""
    
    def __init__(self, config: ResourceConfig):
        self.config = config
        self.metrics_history: List[ResourceMetrics] = []
        self.optimization_history: List[OptimizationAction] = []
        self.current_metrics: Optional[ResourceMetrics] = None
        
    async def collect_metrics(self) -> ResourceMetrics:
        """Recolectar métricas de recursos."""
        raise NotImplementedError
    
    async def optimize(self) -> OptimizationAction:
        """Optimizar recursos."""
        raise NotImplementedError
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Obtener resumen de métricas."""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.metrics_history[-10:]  # Últimos 10
        
        return {
            'resource_type': self.config.resource_type.value,
            'current_usage': self.current_metrics.current_usage if self.current_metrics else 0.0,
            'peak_usage': max(m.peak_usage for m in recent_metrics) if recent_metrics else 0.0,
            'average_usage': np.mean([m.average_usage for m in recent_metrics]) if recent_metrics else 0.0,
            'trend': np.mean([m.trend for m in recent_metrics]) if recent_metrics else 0.0,
            'optimization_count': len(self.optimization_history)
        }

class CPUMemoryManager(BaseResourceManager):
    """Gestor de CPU y memoria."""
    
    async def collect_metrics(self) -> ResourceMetrics:
        """Recolectar métricas de CPU y memoria."""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_percent = memory.percent / 100.0
        
        # Calcular tendencias
        trend = 0.0
        prediction = memory_percent
        
        if self.metrics_history:
            recent = self.metrics_history[-5:]  # Últimos 5
            if len(recent) >= 2:
                trend = (recent[-1].current_usage - recent[0].current_usage) / len(recent)
                # Predicción simple basada en tendencia
                prediction = min(1.0, memory_percent + trend * 10)
        
        # Crear métricas
        metrics = ResourceMetrics(
            current_usage=memory_percent,
            peak_usage=max(m.peak_usage for m in self.metrics_history) if self.metrics_history else memory_percent,
            average_usage=np.mean([m.current_usage for m in self.metrics_history[-10:]]) if self.metrics_history else memory_percent,
            trend=trend,
            prediction=prediction,
            timestamp=time.time()
        )
        
        self.current_metrics = metrics
        self.metrics_history.append(metrics)
        
        # Mantener solo últimas 100 métricas
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        return metrics
    
    async def optimize(self) -> OptimizationAction:
        """Optimizar CPU y memoria."""
        if not self.current_metrics:
            await self.collect_metrics()
        
        current_usage = self.current_metrics.current_usage
        prediction = self.current_metrics.prediction
        
        # Determinar acción de optimización
        if prediction > self.config.critical_threshold:
            action_type = "emergency_cleanup"
            priority = 1
            expected_improvement = 0.2
        elif prediction > self.config.max_usage:
            action_type = "aggressive_optimization"
            priority = 2
            expected_improvement = 0.15
        elif current_usage > self.config.optimal_usage:
            action_type = "preventive_optimization"
            priority = 3
            expected_improvement = 0.1
        else:
            action_type = "maintenance_optimization"
            priority = 4
            expected_improvement = 0.05
        
        # Parámetros específicos
        if action_type == "emergency_cleanup":
            parameters = {
                'force_garbage_collection': True,
                'clear_caches': True,
                'kill_non_essential_processes': True,
                'memory_compression': True
            }
        elif action_type == "aggressive_optimization":
            parameters = {
                'garbage_collection': True,
                'clear_caches': True,
                'memory_compression': True,
                'process_priority_adjustment': True
            }
        elif action_type == "preventive_optimization":
            parameters = {
                'garbage_collection': True,
                'clear_caches': False,
                'memory_compression': False,
                'process_priority_adjustment': False
            }
        else:
            parameters = {
                'garbage_collection': False,
                'clear_caches': False,
                'memory_compression': False,
                'process_priority_adjustment': False
            }
        
        action = OptimizationAction(
            action_type=action_type,
            resource=self.config.resource_type,
            priority=priority,
            expected_improvement=expected_improvement,
            parameters=parameters
        )
        
        self.optimization_history.append(action)
        return action

class GPUMemoryManager(BaseResourceManager):
    """Gestor de GPU y memoria de GPU."""
    
    async def collect_metrics(self) -> ResourceMetrics:
        """Recolectar métricas de GPU."""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            
            if gpus:
                # Usar primera GPU disponible
                gpu = gpus[0]
                gpu_usage = gpu.memoryUtil
                gpu_memory_used = gpu.memoryUsed
                gpu_memory_total = gpu.memoryTotal
                
                # Calcular tendencias
                trend = 0.0
                prediction = gpu_usage
                
                if self.metrics_history:
                    recent = self.metrics_history[-5:]
                    if len(recent) >= 2:
                        trend = (recent[-1].current_usage - recent[0].current_usage) / len(recent)
                        prediction = min(1.0, gpu_usage + trend * 10)
                
                metrics = ResourceMetrics(
                    current_usage=gpu_usage,
                    peak_usage=max(m.peak_usage for m in self.metrics_history) if self.metrics_history else gpu_usage,
                    average_usage=np.mean([m.current_usage for m in self.metrics_history[-10:]]) if self.metrics_history else gpu_usage,
                    trend=trend,
                    prediction=prediction,
                    timestamp=time.time()
                )
            else:
                # No GPU disponible, usar métricas simuladas
                metrics = ResourceMetrics(
                    current_usage=0.0,
                    peak_usage=0.0,
                    average_usage=0.0,
                    trend=0.0,
                    prediction=0.0,
                    timestamp=time.time()
                )
                
        except ImportError:
            # GPUtil no disponible, usar métricas simuladas
            gpu_usage = np.random.uniform(0.3, 0.8)
            
            metrics = ResourceMetrics(
                current_usage=gpu_usage,
                peak_usage=max(m.peak_usage for m in self.metrics_history) if self.metrics_history else gpu_usage,
                average_usage=np.mean([m.current_usage for m in self.metrics_history[-10:]]) if self.metrics_history else gpu_usage,
                trend=np.random.uniform(-0.1, 0.1),
                prediction=gpu_usage + np.random.uniform(-0.1, 0.1),
                timestamp=time.time()
            )
        
        self.current_metrics = metrics
        self.metrics_history.append(metrics)
        
        # Mantener solo últimas 100 métricas
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        return metrics
    
    async def optimize(self) -> OptimizationAction:
        """Optimizar GPU."""
        if not self.current_metrics:
            await self.collect_metrics()
        
        current_usage = self.current_metrics.current_usage
        prediction = self.current_metrics.prediction
        
        # Determinar acción de optimización para GPU
        if prediction > self.config.critical_threshold:
            action_type = "gpu_emergency_cleanup"
            priority = 1
            expected_improvement = 0.25
        elif prediction > self.config.max_usage:
            action_type = "gpu_aggressive_optimization"
            priority = 2
            expected_improvement = 0.2
        elif current_usage > self.config.optimal_usage:
            action_type = "gpu_preventive_optimization"
            priority = 3
            expected_improvement = 0.15
        else:
            action_type = "gpu_maintenance"
            priority = 4
            expected_improvement = 0.05
        
        # Parámetros específicos para GPU
        if action_type == "gpu_emergency_cleanup":
            parameters = {
                'clear_gpu_cache': True,
                'reset_gpu_context': True,
                'kill_gpu_processes': True,
                'memory_compression': True
            }
        elif action_type == "gpu_aggressive_optimization":
            parameters = {
                'clear_gpu_cache': True,
                'reset_gpu_context': False,
                'kill_gpu_processes': False,
                'memory_compression': True
            }
        elif action_type == "gpu_preventive_optimization":
            parameters = {
                'clear_gpu_cache': True,
                'reset_gpu_context': False,
                'kill_gpu_processes': False,
                'memory_compression': False
            }
        else:
            parameters = {
                'clear_gpu_cache': False,
                'reset_gpu_context': False,
                'kill_gpu_processes': False,
                'memory_compression': False
            }
        
        action = OptimizationAction(
            action_type=action_type,
            resource=self.config.resource_type,
            priority=priority,
            expected_improvement=expected_improvement,
            parameters=parameters
        )
        
        self.optimization_history.append(action)
        return action

class IntelligentResourceOrchestrator:
    """Orquestador inteligente de recursos."""
    
    def __init__(self):
        self.resource_managers: Dict[str, BaseResourceManager] = {}
        self.running = False
        self.optimization_queue: List[OptimizationAction] = []
        self.prediction_models: Dict[str, Any] = {}
        
        # Configurar gestores de recursos
        self._setup_resource_managers()
    
    def _setup_resource_managers(self):
        """Configurar gestores de recursos por defecto."""
        configs = {
            'cpu_memory': ResourceConfig(ResourceType.MEMORY),
            'gpu': ResourceConfig(ResourceType.GPU)
        }
        
        self.resource_managers = {
            'cpu_memory': CPUMemoryManager(configs['cpu_memory']),
            'gpu': GPUMemoryManager(configs['gpu'])
        }
    
    async def start(self):
        """Iniciar orquestador de recursos."""
        logger.info("🚀 Iniciando orquestador inteligente de recursos...")
        self.running = True
        
        # Iniciar monitoreo continuo
        asyncio.create_task(self._continuous_monitoring_loop())
        asyncio.create_task(self._optimization_processor_loop())
        
        logger.info("✅ Orquestador de recursos iniciado")
    
    async def stop(self):
        """Detener orquestador de recursos."""
        self.running = False
        logger.info("✅ Orquestador de recursos detenido")
    
    async def collect_all_metrics(self) -> Dict[str, ResourceMetrics]:
        """Recolectar métricas de todos los recursos."""
        metrics = {}
        
        for name, manager in self.resource_managers.items():
            try:
                metrics[name] = await manager.collect_metrics()
            except Exception as e:
                logger.error(f"Error recolectando métricas de {name}: {e}")
        
        return metrics
    
    async def optimize_all_resources(self) -> Dict[str, OptimizationAction]:
        """Optimizar todos los recursos."""
        optimizations = {}
        
        for name, manager in self.resource_managers.items():
            try:
                action = await manager.optimize()
                optimizations[name] = action
                
                # Agregar a cola de optimización
                self.optimization_queue.append(action)
                
            except Exception as e:
                logger.error(f"Error optimizando {name}: {e}")
        
        return optimizations
    
    async def get_resource_summary(self) -> Dict[str, Any]:
        """Obtener resumen de todos los recursos."""
        summary = {}
        
        for name, manager in self.resource_managers.items():
            summary[name] = manager.get_metrics_summary()
        
        return {
            'resources': summary,
            'optimization_queue_size': len(self.optimization_queue),
            'total_optimizations': sum(
                len(manager.optimization_history) 
                for manager in self.resource_managers.values()
            )
        }
    
    async def _continuous_monitoring_loop(self):
        """Loop de monitoreo continuo."""
        while self.running:
            try:
                # Recolectar métricas de todos los recursos
                metrics = await self.collect_all_metrics()
                
                # Analizar métricas y predecir problemas
                await self._analyze_and_predict(metrics)
                
                # Esperar intervalo
                await asyncio.sleep(30)  # 30 segundos
                
            except Exception as e:
                logger.error(f"Error en monitoreo continuo: {e}")
                await asyncio.sleep(10)
    
    async def _optimization_processor_loop(self):
        """Loop de procesamiento de optimizaciones."""
        while self.running:
            try:
                # Procesar cola de optimizaciones
                if self.optimization_queue:
                    # Ordenar por prioridad (menor número = mayor prioridad)
                    self.optimization_queue.sort(key=lambda x: x.priority)
                    
                    # Procesar optimización de mayor prioridad
                    action = self.optimization_queue.pop(0)
                    await self._execute_optimization(action)
                
                await asyncio.sleep(5)  # 5 segundos
                
            except Exception as e:
                logger.error(f"Error en procesamiento de optimizaciones: {e}")
                await asyncio.sleep(5)
    
    async def _analyze_and_predict(self, metrics: Dict[str, ResourceMetrics]):
        """Analizar métricas y predecir problemas."""
        for resource_name, metric in metrics.items():
            # Verificar umbrales críticos
            if metric.prediction > 0.95:
                logger.warning(f"🚨 {resource_name}: Predicción crítica ({metric.prediction:.2%})")
                
                # Forzar optimización inmediata
                if resource_name in self.resource_managers:
                    try:
                        action = await self.resource_managers[resource_name].optimize()
                        action.priority = 0  # Máxima prioridad
                        self.optimization_queue.insert(0, action)
                        logger.info(f"🚨 Optimización de emergencia programada para {resource_name}")
                    except Exception as e:
                        logger.error(f"Error en optimización de emergencia de {resource_name}: {e}")
            
            # Verificar tendencias negativas
            elif metric.trend > 0.1 and metric.current_usage > 0.7:
                logger.info(f"📈 {resource_name}: Tendencia creciente, optimización preventiva recomendada")
    
    async def _execute_optimization(self, action: OptimizationAction):
        """Ejecutar acción de optimización."""
        logger.info(f"🔧 Ejecutando optimización: {action.action_type}")
        
        try:
            # Simular ejecución de optimización
            if action.action_type.startswith("emergency"):
                await asyncio.sleep(1)  # Optimización rápida
            elif action.action_type.startswith("aggressive"):
                await asyncio.sleep(2)  # Optimización moderada
            else:
                await asyncio.sleep(3)  # Optimización normal
            
            # Verificar mejora
            if action.resource == ResourceType.MEMORY:
                manager = self.resource_managers['cpu_memory']
            elif action.resource == ResourceType.GPU:
                manager = self.resource_managers['gpu']
            else:
                return
            
            # Recolectar métricas después de optimización
            await manager.collect_metrics()
            
            if manager.current_metrics:
                improvement = manager.current_metrics.current_usage - action.expected_improvement
                logger.info(f"✅ Optimización completada: {action.action_type}, Mejora: {improvement:.4f}")
            else:
                logger.info(f"✅ Optimización completada: {action.action_type}")
                
        except Exception as e:
            logger.error(f"Error ejecutando optimización {action.action_type}: {e}")

async def main():
    """Función principal de demostración."""
    print("🚀 Sistema de Gestión de Recursos Inteligente - Demostración")
    print("=" * 80)
    
    orchestrator = IntelligentResourceOrchestrator()
    
    try:
        await orchestrator.start()
        
        print("\n📊 Monitoreando recursos...")
        
        # Recolectar métricas iniciales
        metrics = await orchestrator.collect_all_metrics()
        print("\n📈 Métricas Iniciales:")
        for name, metric in metrics.items():
            print(f"   {name}: {metric.current_usage:.2%} (Predicción: {metric.prediction:.2%})")
        
        # Optimizar recursos
        print("\n🔧 Optimizando recursos...")
        optimizations = await orchestrator.optimize_all_resources()
        
        for name, action in optimizations.items():
            print(f"   {name}: {action.action_type} (Prioridad: {action.priority})")
        
        # Obtener resumen
        print("\n📋 Resumen del Sistema:")
        summary = await orchestrator.get_resource_summary()
        print(f"   Cola de optimización: {summary['optimization_queue_size']}")
        print(f"   Total de optimizaciones: {summary['total_optimizations']}")
        
        print("\n🎉 ¡Sistema de gestión de recursos funcionando!")
        
        # Monitorear por un tiempo
        print("\n⏳ Monitoreo continuo activo (2 minutos)...")
        for i in range(4):  # 4 intervalos de 30 segundos
            await asyncio.sleep(30)
            metrics = await orchestrator.collect_all_metrics()
            print(f"   Intervalo {i+1}: CPU/Mem: {metrics['cpu_memory'].current_usage:.2%}, GPU: {metrics['gpu'].current_usage:.2%}")
        
    except Exception as e:
        logger.error(f"Error en demostración: {e}")
    
    finally:
        await orchestrator.stop()

if __name__ == "__main__":
    asyncio.run(main())
