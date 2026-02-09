"""
Sistema de Optimización de Recursos con IA v4.7
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema implementa optimización inteligente de recursos, asignación dinámica
y estrategias de IA para maximizar la eficiencia del sistema.
"""

import asyncio
import time
import json
import logging
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Tipos de recursos"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"
    COMPUTE = "compute"

class OptimizationStrategy(Enum):
    """Estrategias de optimización"""
    LOAD_BALANCING = "load_balancing"
    AUTO_SCALING = "auto_scaling"
    RESOURCE_POOLING = "resource_pooling"
    PREDICTIVE_ALLOCATION = "predictive_allocation"
    ADAPTIVE_SCHEDULING = "adaptive_scheduling"

class ResourceStatus(Enum):
    """Estados de los recursos"""
    AVAILABLE = "available"
    IN_USE = "in_use"
    OVERLOADED = "overloaded"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class ResourceMetrics:
    """Métricas de recursos"""
    resource_id: str
    resource_type: ResourceType
    current_usage: float
    capacity: float
    utilization_rate: float
    performance_score: float
    last_updated: datetime
    health_status: ResourceStatus

@dataclass
class OptimizationRequest:
    """Solicitud de optimización"""
    request_id: str
    resource_type: ResourceType
    required_capacity: float
    priority: int
    deadline: datetime
    constraints: Dict[str, Any]
    timestamp: datetime

@dataclass
class OptimizationResult:
    """Resultado de optimización"""
    request_id: str
    success: bool
    allocated_resources: List[str]
    optimization_score: float
    execution_time: float
    recommendations: List[str]
    timestamp: datetime

@dataclass
class ResourcePool:
    """Pool de recursos"""
    pool_id: str
    pool_type: ResourceType
    total_capacity: float
    available_capacity: float
    allocated_resources: Dict[str, float]
    performance_history: List[float]
    optimization_metrics: Dict[str, float]

class IntelligentResourceAnalyzer:
    """Analizador inteligente de recursos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.resource_metrics: Dict[str, ResourceMetrics] = {}
        self.usage_patterns: Dict[str, List[float]] = {}
        self.performance_trends: Dict[str, List[float]] = {}
        self.anomaly_detection_enabled = config.get('anomaly_detection', True)
        
    async def start(self):
        """Iniciar el analizador"""
        logger.info("🚀 Iniciando Analizador Inteligente de Recursos")
        await self._initialize_analysis()
        
    async def _initialize_analysis(self):
        """Inicializar análisis"""
        logger.info("🔧 Configurando análisis inteligente de recursos")
        await asyncio.sleep(0.5)
        
    async def collect_resource_metrics(self, resource_id: str, metrics: ResourceMetrics) -> bool:
        """Recolectar métricas de recursos"""
        self.resource_metrics[resource_id] = metrics
        
        # Actualizar patrones de uso
        if resource_id not in self.usage_patterns:
            self.usage_patterns[resource_id] = []
        self.usage_patterns[resource_id].append(metrics.utilization_rate)
        
        # Mantener solo los últimos 100 valores
        if len(self.usage_patterns[resource_id]) > 100:
            self.usage_patterns[resource_id] = self.usage_patterns[resource_id][-100:]
            
        # Actualizar tendencias de rendimiento
        if resource_id not in self.performance_trends:
            self.performance_trends[resource_id] = []
        self.performance_trends[resource_id].append(metrics.performance_score)
        
        if len(self.performance_trends[resource_id]) > 100:
            self.performance_trends[resource_id] = self.performance_trends[resource_id][-100:]
            
        logger.info(f"📊 Métricas recolectadas para recurso {resource_id}")
        return True
        
    async def analyze_resource_health(self, resource_id: str) -> Dict[str, Any]:
        """Analizar salud del recurso"""
        if resource_id not in self.resource_metrics:
            return {}
            
        metrics = self.resource_metrics[resource_id]
        usage_pattern = self.usage_patterns.get(resource_id, [])
        performance_trend = self.performance_trends.get(resource_id, [])
        
        # Calcular métricas de salud
        health_analysis = {
            'resource_id': resource_id,
            'current_health': metrics.health_status.value,
            'utilization_trend': self._calculate_trend(usage_pattern),
            'performance_trend': self._calculate_trend(performance_trend),
            'anomaly_score': self._detect_anomalies(resource_id),
            'recommendations': self._generate_recommendations(resource_id),
            'timestamp': datetime.now().isoformat()
        }
        
        return health_analysis
        
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcular tendencia de valores"""
        if len(values) < 2:
            return "insufficient_data"
            
        recent_values = values[-10:] if len(values) >= 10 else values
        if len(recent_values) < 2:
            return "insufficient_data"
            
        # Calcular pendiente simple
        x = list(range(len(recent_values)))
        y = recent_values
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        if n * sum_x2 - sum_x ** 2 == 0:
            return "stable"
            
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
            
    def _detect_anomalies(self, resource_id: str) -> float:
        """Detectar anomalías en el recurso"""
        if not self.anomaly_detection_enabled:
            return 0.0
            
        usage_pattern = self.usage_patterns.get(resource_id, [])
        if len(usage_pattern) < 10:
            return 0.0
            
        # Detectar valores atípicos usando método estadístico simple
        values = np.array(usage_pattern)
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return 0.0
            
        # Calcular puntuación de anomalía
        anomaly_scores = np.abs((values - mean) / std)
        max_anomaly = np.max(anomaly_scores)
        
        # Normalizar a 0-1
        normalized_score = min(max_anomaly / 3.0, 1.0)  # 3 desviaciones estándar como máximo
        
        return float(normalized_score)
        
    def _generate_recommendations(self, resource_id: str) -> List[str]:
        """Generar recomendaciones para el recurso"""
        recommendations = []
        metrics = self.resource_metrics.get(resource_id)
        
        if not metrics:
            return recommendations
            
        # Recomendaciones basadas en utilización
        if metrics.utilization_rate > 0.9:
            recommendations.append("Considerar escalado horizontal")
        elif metrics.utilization_rate < 0.3:
            recommendations.append("Considerar consolidación de recursos")
            
        # Recomendaciones basadas en rendimiento
        if metrics.performance_score < 0.7:
            recommendations.append("Revisar configuración de recursos")
            
        # Recomendaciones basadas en tendencias
        usage_trend = self._calculate_trend(self.usage_patterns.get(resource_id, []))
        if usage_trend == "increasing":
            recommendations.append("Monitorear crecimiento de demanda")
            
        return recommendations

class DynamicResourceAllocator:
    """Asignador dinámico de recursos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.resource_pools: Dict[str, ResourcePool] = {}
        self.optimization_requests: List[OptimizationRequest] = []
        self.allocation_history: List[Dict[str, Any]] = []
        self.auto_scaling_enabled = config.get('auto_scaling', True)
        
    async def start(self):
        """Iniciar el asignador"""
        logger.info("🚀 Iniciando Asignador Dinámico de Recursos")
        await self._initialize_allocation()
        
    async def _initialize_allocation(self):
        """Inicializar asignación"""
        logger.info("🔧 Configurando asignación dinámica de recursos")
        await asyncio.sleep(0.5)
        
    async def create_resource_pool(self, pool_type: ResourceType, total_capacity: float) -> str:
        """Crear pool de recursos"""
        pool_id = f"pool_{pool_type.value}_{int(time.time())}"
        
        pool = ResourcePool(
            pool_id=pool_id,
            pool_type=pool_type,
            total_capacity=total_capacity,
            available_capacity=total_capacity,
            allocated_resources={},
            performance_history=[],
            optimization_metrics={}
        )
        
        self.resource_pools[pool_id] = pool
        logger.info(f"🏊 Pool de recursos creado: {pool_id} ({pool_type.value})")
        return pool_id
        
    async def request_resource_optimization(self, request: OptimizationRequest) -> str:
        """Solicitar optimización de recursos"""
        self.optimization_requests.append(request)
        logger.info(f"📋 Solicitud de optimización creada: {request.request_id}")
        return request.request_id
        
    async def optimize_resource_allocation(self, request_id: str) -> OptimizationResult:
        """Optimizar asignación de recursos"""
        request = next((req for req in self.optimization_requests if req.request_id == request_id), None)
        if not request:
            return OptimizationResult(
                request_id=request_id,
                success=False,
                allocated_resources=[],
                optimization_score=0.0,
                execution_time=0.0,
                recommendations=["Solicitud no encontrada"],
                timestamp=datetime.now()
            )
            
        start_time = time.time()
        
        # Buscar pool de recursos apropiado
        suitable_pools = [
            pool for pool in self.resource_pools.values()
            if pool.pool_type == request.resource_type
            and pool.available_capacity >= request.required_capacity
        ]
        
        if not suitable_pools:
            # Intentar auto-scaling si está habilitado
            if self.auto_scaling_enabled:
                await self._perform_auto_scaling(request.resource_type, request.required_capacity)
                suitable_pools = [
                    pool for pool in self.resource_pools.values()
                    if pool.pool_type == request.resource_type
                    and pool.available_capacity >= request.required_capacity
                ]
                
        if not suitable_pools:
            return OptimizationResult(
                request_id=request_id,
                success=False,
                allocated_resources=[],
                optimization_score=0.0,
                execution_time=time.time() - start_time,
                recommendations=["No hay recursos disponibles"],
                timestamp=datetime.now()
            )
            
        # Seleccionar el mejor pool (mayor capacidad disponible)
        best_pool = max(suitable_pools, key=lambda p: p.available_capacity)
        
        # Asignar recursos
        allocation_id = f"alloc_{request_id}_{int(time.time())}"
        best_pool.allocated_resources[allocation_id] = request.required_capacity
        best_pool.available_capacity -= request.required_capacity
        
        # Calcular puntuación de optimización
        optimization_score = self._calculate_optimization_score(best_pool, request)
        
        execution_time = time.time() - start_time
        
        result = OptimizationResult(
            request_id=request_id,
            success=True,
            allocated_resources=[allocation_id],
            optimization_score=optimization_score,
            execution_time=execution_time,
            recommendations=self._generate_optimization_recommendations(best_pool),
            timestamp=datetime.now()
        )
        
        # Registrar en historial
        self.allocation_history.append({
            'request_id': request_id,
            'pool_id': best_pool.pool_id,
            'allocation_id': allocation_id,
            'allocated_capacity': request.required_capacity,
            'optimization_score': optimization_score,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"✅ Optimización completada para {request_id}")
        return result
        
    async def _perform_auto_scaling(self, resource_type: ResourceType, required_capacity: float):
        """Realizar auto-scaling"""
        logger.info(f"🔄 Realizando auto-scaling para {resource_type.value}")
        
        # Crear nuevo pool con capacidad adicional
        new_capacity = required_capacity * 1.5  # 50% de margen
        pool_id = await self.create_resource_pool(resource_type, new_capacity)
        
        logger.info(f"🏗️ Nuevo pool creado: {pool_id} con capacidad {new_capacity}")
        
    def _calculate_optimization_score(self, pool: ResourcePool, request: OptimizationRequest) -> float:
        """Calcular puntuación de optimización"""
        # Factores para la puntuación
        utilization_factor = 1.0 - (pool.available_capacity / pool.total_capacity)
        efficiency_factor = 1.0 - (request.required_capacity / pool.total_capacity)
        performance_factor = np.mean(pool.performance_history) if pool.performance_history else 0.8
        
        # Puntuación ponderada
        score = (
            utilization_factor * 0.4 +
            efficiency_factor * 0.3 +
            performance_factor * 0.3
        )
        
        return min(max(score, 0.0), 1.0)
        
    def _generate_optimization_recommendations(self, pool: ResourcePool) -> List[str]:
        """Generar recomendaciones de optimización"""
        recommendations = []
        
        # Recomendaciones basadas en utilización
        utilization_rate = 1.0 - (pool.available_capacity / pool.total_capacity)
        if utilization_rate > 0.9:
            recommendations.append("Considerar expansión del pool")
        elif utilization_rate < 0.3:
            recommendations.append("Considerar consolidación de pools")
            
        # Recomendaciones basadas en rendimiento
        if pool.performance_history:
            avg_performance = np.mean(pool.performance_history)
            if avg_performance < 0.7:
                recommendations.append("Revisar configuración del pool")
                
        return recommendations

class PredictiveResourceManager:
    """Gestor predictivo de recursos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.prediction_models: Dict[str, Any] = {}
        self.forecast_data: Dict[str, List[float]] = {}
        self.optimization_suggestions: List[Dict[str, Any]] = []
        self.prediction_horizon = config.get('prediction_horizon', 24)  # horas
        
    async def start(self):
        """Iniciar el gestor"""
        logger.info("🚀 Iniciando Gestor Predictivo de Recursos")
        await self._initialize_prediction()
        
    async def _initialize_prediction(self):
        """Inicializar predicción"""
        logger.info("🔧 Configurando predicción de recursos")
        await asyncio.sleep(0.5)
        
    async def predict_resource_demand(self, resource_type: ResourceType, hours_ahead: int = 24) -> Dict[str, Any]:
        """Predecir demanda de recursos"""
        logger.info(f"🔮 Prediciendo demanda de {resource_type.value} para {hours_ahead} horas")
        
        # Simular predicción usando patrones históricos
        base_demand = random.uniform(0.3, 0.8)
        time_pattern = self._generate_time_pattern(hours_ahead)
        seasonal_factor = self._calculate_seasonal_factor()
        
        predictions = []
        for hour in range(hours_ahead):
            # Demanda base + patrón temporal + factor estacional + ruido
            demand = base_demand + time_pattern[hour] + seasonal_factor + random.uniform(-0.1, 0.1)
            demand = max(0.0, min(1.0, demand))  # Clamp entre 0 y 1
            predictions.append(demand)
            
        forecast_data = {
            'resource_type': resource_type.value,
            'predictions': predictions,
            'confidence_interval': [0.8, 0.95],
            'trend': self._analyze_trend(predictions),
            'peak_hours': self._find_peak_hours(predictions),
            'timestamp': datetime.now().isoformat()
        }
        
        # Almacenar predicción
        self.forecast_data[f"{resource_type.value}_forecast"] = predictions
        
        logger.info(f"✅ Predicción completada para {resource_type.value}")
        return forecast_data
        
    def _generate_time_pattern(self, hours: int) -> List[float]:
        """Generar patrón temporal"""
        pattern = []
        for hour in range(hours):
            # Patrón diario (mayor uso durante horas laborales)
            hour_of_day = hour % 24
            if 8 <= hour_of_day <= 18:  # Horas laborales
                pattern.append(random.uniform(0.1, 0.3))
            else:  # Horas no laborales
                pattern.append(random.uniform(-0.2, 0.1))
        return pattern
        
    def _calculate_seasonal_factor(self) -> float:
        """Calcular factor estacional"""
        current_month = datetime.now().month
        
        # Patrón estacional simple
        if current_month in [12, 1, 2]:  # Invierno
            return random.uniform(-0.1, 0.1)
        elif current_month in [6, 7, 8]:  # Verano
            return random.uniform(0.05, 0.15)
        else:  # Primavera/Otoño
            return random.uniform(-0.05, 0.05)
            
    def _analyze_trend(self, predictions: List[float]) -> str:
        """Analizar tendencia de predicciones"""
        if len(predictions) < 2:
            return "insufficient_data"
            
        # Calcular pendiente de la línea de tendencia
        x = list(range(len(predictions)))
        y = predictions
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        if n * sum_x2 - sum_x ** 2 == 0:
            return "stable"
            
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
            
    def _find_peak_hours(self, predictions: List[float]) -> List[int]:
        """Encontrar horas pico"""
        if len(predictions) < 3:
            return []
            
        peak_hours = []
        for i in range(1, len(predictions) - 1):
            if predictions[i] > predictions[i-1] and predictions[i] > predictions[i+1]:
                peak_hours.append(i)
                
        return peak_hours[:5]  # Retornar solo los primeros 5 picos
        
    async def generate_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Generar sugerencias de optimización"""
        suggestions = []
        
        for resource_type in ResourceType:
            forecast_key = f"{resource_type.value}_forecast"
            if forecast_key in self.forecast_data:
                predictions = self.forecast_data[forecast_key]
                
                if predictions:
                    avg_demand = np.mean(predictions)
                    peak_demand = np.max(predictions)
                    
                    if avg_demand > 0.8:
                        suggestions.append({
                            'resource_type': resource_type.value,
                            'suggestion': 'Considerar expansión de capacidad',
                            'priority': 'high',
                            'reason': f'Demanda promedio alta: {avg_demand:.2f}',
                            'timestamp': datetime.now().isoformat()
                        })
                    elif peak_demand > 0.9:
                        suggestions.append({
                            'resource_type': resource_type.value,
                            'suggestion': 'Implementar auto-scaling',
                            'priority': 'medium',
                            'reason': f'Demanda pico alta: {peak_demand:.2f}',
                            'timestamp': datetime.now().isoformat()
                        })
                        
        self.optimization_suggestions = suggestions
        return suggestions

class AIResourceOptimizationSystem:
    """Sistema principal de optimización de recursos con IA"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.resource_analyzer = IntelligentResourceAnalyzer(config)
        self.resource_allocator = DynamicResourceAllocator(config)
        self.predictive_manager = PredictiveResourceManager(config)
        
        self.system_status = "initializing"
        self.optimization_history: List[OptimizationResult] = []
        self.health_score = 1.0
        
    async def start(self):
        """Iniciar el sistema completo"""
        logger.info("🚀 INICIANDO SISTEMA DE OPTIMIZACIÓN DE RECURSOS CON IA v4.7")
        
        try:
            # Iniciar componentes
            await asyncio.gather(
                self.resource_analyzer.start(),
                self.resource_allocator.start(),
                self.predictive_manager.start()
            )
            
            # Crear pools de recursos iniciales
            await self._initialize_resource_pools()
            
            self.system_status = "running"
            logger.info("✅ Sistema de Optimización de Recursos con IA iniciado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error al iniciar el sistema: {e}")
            self.system_status = "error"
            raise
            
    async def _initialize_resource_pools(self):
        """Inicializar pools de recursos"""
        logger.info("🏗️ Inicializando pools de recursos")
        
        # Crear pools para cada tipo de recurso
        pool_configs = [
            (ResourceType.CPU, 100.0),      # 100 cores
            (ResourceType.MEMORY, 1000.0),  # 1000 GB
            (ResourceType.GPU, 50.0),       # 50 GPUs
            (ResourceType.STORAGE, 10000.0), # 10000 GB
            (ResourceType.NETWORK, 100.0)   # 100 Gbps
        ]
        
        for resource_type, capacity in pool_configs:
            await self.resource_allocator.create_resource_pool(resource_type, capacity)
            
        logger.info("✅ Pools de recursos inicializados")
        
    async def stop(self):
        """Detener el sistema"""
        logger.info("🛑 Deteniendo Sistema de Optimización de Recursos con IA")
        self.system_status = "stopped"
        
    async def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        return {
            'system_name': 'Sistema de Optimización de Recursos con IA v4.7',
            'status': self.system_status,
            'health_score': self.health_score,
            'resource_pools': len(self.resource_allocator.resource_pools),
            'active_requests': len(self.resource_allocator.optimization_requests),
            'optimization_history': len(self.optimization_history),
            'prediction_models': len(self.predictive_manager.prediction_models),
            'timestamp': datetime.now().isoformat()
        }
        
    async def run_optimization_cycle(self) -> Dict[str, Any]:
        """Ejecutar ciclo de optimización"""
        logger.info("🔄 Iniciando ciclo de optimización de recursos")
        
        # Generar predicciones para todos los tipos de recursos
        predictions = {}
        for resource_type in ResourceType:
            forecast = await self.predictive_manager.predict_resource_demand(resource_type)
            predictions[resource_type.value] = forecast
            
        # Generar sugerencias de optimización
        suggestions = await self.predictive_manager.generate_optimization_suggestions()
        
        # Simular solicitudes de optimización
        optimization_results = []
        for suggestion in suggestions[:3]:  # Procesar solo las primeras 3 sugerencias
            request = OptimizationRequest(
                request_id=f"opt_{suggestion['resource_type']}_{int(time.time())}",
                resource_type=ResourceType(suggestion['resource_type']),
                required_capacity=random.uniform(0.1, 0.3),
                priority=1 if suggestion['priority'] == 'high' else 2,
                deadline=datetime.now() + timedelta(hours=1),
                constraints={'max_cost': 1000.0},
                timestamp=datetime.now()
            )
            
            # Solicitar optimización
            await self.resource_allocator.request_resource_optimization(request)
            
            # Ejecutar optimización
            result = await self.resource_allocator.optimize_resource_allocation(request.request_id)
            optimization_results.append(result)
            
            # Almacenar en historial
            self.optimization_history.append(result)
            
        cycle_result = {
            'predictions_generated': len(predictions),
            'suggestions_generated': len(suggestions),
            'optimizations_executed': len(optimization_results),
            'successful_optimizations': len([r for r in optimization_results if r.success]),
            'average_optimization_score': np.mean([r.optimization_score for r in optimization_results]) if optimization_results else 0.0,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("✅ Ciclo de optimización completado")
        return cycle_result
        
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de rendimiento"""
        return {
            'resource_pools_count': len(self.resource_allocator.resource_pools),
            'optimization_requests': len(self.resource_allocator.optimization_requests),
            'optimization_history': len(self.optimization_history),
            'predictions_generated': len(self.predictive_manager.forecast_data),
            'optimization_suggestions': len(self.predictive_manager.optimization_suggestions),
            'system_health': self.health_score,
            'timestamp': datetime.now().isoformat()
        }

# Configuración del sistema
SYSTEM_CONFIG = {
    'anomaly_detection': True,
    'auto_scaling': True,
    'prediction_horizon': 24,
    'convergence_threshold': 0.01,
    'max_optimization_time': 300
}

async def main():
    """Función principal de demostración"""
    try:
        # Crear e iniciar el sistema
        system = AIResourceOptimizationSystem(SYSTEM_CONFIG)
        await system.start()
        
        # Ejecutar ciclo de optimización
        logger.info("🎬 DEMOSTRACIÓN DEL SISTEMA v4.7")
        
        optimization_result = await system.run_optimization_cycle()
        logger.info(f"📊 Resultado de Optimización: {optimization_result}")
        
        # Estado final del sistema
        final_status = await system.get_system_status()
        logger.info(f"📊 Estado Final: {final_status}")
        
        # Métricas de rendimiento
        performance = await system.get_performance_metrics()
        logger.info(f"📊 Rendimiento: {performance}")
        
        await system.stop()
        logger.info("✅ Demostración completada exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error en la demostración: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
