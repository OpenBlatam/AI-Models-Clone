"""
Pipeline Monitor
================

Sistema de monitoreo avanzado para pipelines con alertas y dashboards.
"""

import logging
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
from collections import deque

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Nivel de alerta."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PipelineAlert:
    """Alerta de pipeline."""
    pipeline_name: str
    level: AlertLevel
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineHealth:
    """Salud de un pipeline."""
    pipeline_name: str
    is_healthy: bool
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    success_rate: float = 0.0
    avg_execution_time: float = 0.0
    error_count: int = 0
    total_executions: int = 0
    issues: List[str] = field(default_factory=list)


class PipelineMonitor:
    """
    Monitor avanzado para pipelines.
    """
    
    def __init__(
        self,
        alert_thresholds: Optional[Dict[str, float]] = None,
        history_size: int = 1000
    ):
        """
        Inicializar monitor.
        
        Args:
            alert_thresholds: Umbrales para alertas
            history_size: Tamaño del historial
        """
        self.alert_thresholds = alert_thresholds or {
            'error_rate': 0.1,  # 10% de errores
            'avg_time': 60.0,  # 60 segundos promedio
            'max_time': 300.0  # 5 minutos máximo
        }
        
        self.history_size = history_size
        self.execution_history: Dict[str, deque] = {}
        self.health_status: Dict[str, PipelineHealth] = {}
        self.alerts: List[PipelineAlert] = []
        self.alert_handlers: List[Callable[[PipelineAlert], None]] = []
        self._lock = threading.Lock()
        self.monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
    
    def record_execution(
        self,
        pipeline_name: str,
        success: bool,
        execution_time: float,
        error: Optional[Exception] = None
    ) -> None:
        """
        Registrar ejecución de pipeline.
        
        Args:
            pipeline_name: Nombre del pipeline
            success: Si fue exitoso
            execution_time: Tiempo de ejecución
            error: Error si hubo
        """
        with self._lock:
            if pipeline_name not in self.execution_history:
                self.execution_history[pipeline_name] = deque(maxlen=self.history_size)
                self.health_status[pipeline_name] = PipelineHealth(
                    pipeline_name=pipeline_name,
                    is_healthy=True
                )
            
            # Registrar en historial
            self.execution_history[pipeline_name].append({
                'success': success,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'error': str(error) if error else None
            })
            
            # Actualizar salud
            health = self.health_status[pipeline_name]
            health.total_executions += 1
            
            if success:
                health.last_success = datetime.now().isoformat()
            else:
                health.last_failure = datetime.now().isoformat()
                health.error_count += 1
            
            # Calcular métricas
            recent = list(self.execution_history[pipeline_name])
            if recent:
                health.success_rate = sum(1 for e in recent if e['success']) / len(recent)
                health.avg_execution_time = sum(e['execution_time'] for e in recent) / len(recent)
            
            # Verificar salud
            self._check_health(pipeline_name, health)
    
    def _check_health(self, pipeline_name: str, health: PipelineHealth) -> None:
        """Verificar salud del pipeline."""
        issues = []
        is_healthy = True
        
        # Verificar tasa de errores
        if health.total_executions > 0:
            error_rate = health.error_count / health.total_executions
            if error_rate > self.alert_thresholds.get('error_rate', 0.1):
                issues.append(f"Alta tasa de errores: {error_rate:.2%}")
                is_healthy = False
                self._create_alert(
                    pipeline_name,
                    AlertLevel.ERROR,
                    f"Tasa de errores alta: {error_rate:.2%}"
                )
        
        # Verificar tiempo de ejecución
        if health.avg_execution_time > self.alert_thresholds.get('avg_time', 60.0):
            issues.append(f"Tiempo promedio alto: {health.avg_execution_time:.2f}s")
            self._create_alert(
                pipeline_name,
                AlertLevel.WARNING,
                f"Tiempo promedio de ejecución alto: {health.avg_execution_time:.2f}s"
            )
        
        # Verificar última ejecución
        if health.last_success:
            last_success_time = datetime.fromisoformat(health.last_success)
            if datetime.now() - last_success_time > timedelta(hours=1):
                issues.append("Sin ejecuciones exitosas recientes")
                self._create_alert(
                    pipeline_name,
                    AlertLevel.WARNING,
                    "Sin ejecuciones exitosas en la última hora"
                )
        
        health.is_healthy = is_healthy
        health.issues = issues
    
    def _create_alert(
        self,
        pipeline_name: str,
        level: AlertLevel,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Crear alerta."""
        alert = PipelineAlert(
            pipeline_name=pipeline_name,
            level=level,
            message=message,
            metadata=metadata or {}
        )
        
        self.alerts.append(alert)
        
        # Mantener solo las últimas 100 alertas
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # Ejecutar handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error en alert handler: {e}")
    
    def register_alert_handler(self, handler: Callable[[PipelineAlert], None]) -> None:
        """
        Registrar handler para alertas.
        
        Args:
            handler: Función que maneja alertas
        """
        self.alert_handlers.append(handler)
    
    def get_health(self, pipeline_name: str) -> Optional[PipelineHealth]:
        """
        Obtener salud de pipeline.
        
        Args:
            pipeline_name: Nombre del pipeline
            
        Returns:
            Salud del pipeline o None
        """
        return self.health_status.get(pipeline_name)
    
    def get_all_health(self) -> Dict[str, PipelineHealth]:
        """
        Obtener salud de todos los pipelines.
        
        Returns:
            Diccionario con salud de todos los pipelines
        """
        return self.health_status.copy()
    
    def get_recent_alerts(
        self,
        level: Optional[AlertLevel] = None,
        limit: int = 10
    ) -> List[PipelineAlert]:
        """
        Obtener alertas recientes.
        
        Args:
            level: Filtrar por nivel
            limit: Límite de resultados
            
        Returns:
            Lista de alertas
        """
        alerts = self.alerts
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        return alerts[-limit:]
    
    def get_statistics(self, pipeline_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtener estadísticas.
        
        Args:
            pipeline_name: Filtrar por pipeline (None para todos)
            
        Returns:
            Diccionario con estadísticas
        """
        if pipeline_name:
            if pipeline_name not in self.execution_history:
                return {}
            
            history = list(self.execution_history[pipeline_name])
            health = self.health_status.get(pipeline_name)
            
            return {
                'pipeline_name': pipeline_name,
                'total_executions': len(history),
                'success_rate': health.success_rate if health else 0.0,
                'avg_execution_time': health.avg_execution_time if health else 0.0,
                'is_healthy': health.is_healthy if health else False,
                'recent_executions': history[-10:]  # Últimas 10
            }
        else:
            # Estadísticas globales
            total_executions = sum(len(h) for h in self.execution_history.values())
            healthy_count = sum(1 for h in self.health_status.values() if h.is_healthy)
            
            return {
                'total_pipelines': len(self.execution_history),
                'healthy_pipelines': healthy_count,
                'total_executions': total_executions,
                'recent_alerts': len([a for a in self.alerts if a.timestamp > (datetime.now() - timedelta(hours=1)).isoformat()])
            }
    
    def start_monitoring(self, interval: float = 60.0) -> None:
        """
        Iniciar monitoreo periódico.
        
        Args:
            interval: Intervalo en segundos
        """
        if self.monitoring:
            return
        
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    self._monitor_all()
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Error en monitoreo: {e}")
                    time.sleep(interval)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Monitoreo iniciado")
    
    def stop_monitoring(self) -> None:
        """Detener monitoreo."""
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        logger.info("Monitoreo detenido")
    
    def _monitor_all(self) -> None:
        """Monitorear todos los pipelines."""
        for pipeline_name, health in self.health_status.items():
            self._check_health(pipeline_name, health)


# Instancia global del monitor
_global_monitor: Optional[PipelineMonitor] = None


def get_monitor(
    alert_thresholds: Optional[Dict[str, float]] = None
) -> PipelineMonitor:
    """
    Obtener instancia global del monitor.
    
    Args:
        alert_thresholds: Umbrales para alertas (solo se usa en la primera llamada)
        
    Returns:
        Instancia del monitor
    """
    global _global_monitor
    
    if _global_monitor is None:
        _global_monitor = PipelineMonitor(alert_thresholds)
    
    return _global_monitor

