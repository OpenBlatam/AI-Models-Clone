"""
🔌 METRICS INTERFACES - Contratos para Métricas y Monitoreo
==========================================================

Interfaces para sistemas de métricas, logging y monitoreo.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from ..core.entities import AnalysisResult, AnalysisError
from ..core.enums import MetricType, ErrorType


class IMetricsCollector(ABC):
    """Interface para colección de métricas."""
    
    @abstractmethod
    def record_analysis(self, result: AnalysisResult) -> None:
        """
        Registrar análisis completado.
        
        Args:
            result: Resultado del análisis
        """
        pass
    
    @abstractmethod
    def record_error(self, error: str, context: Dict[str, Any]) -> None:
        """
        Registrar error del sistema.
        
        Args:
            error: Mensaje de error
            context: Contexto del error
        """
        pass
    
    @abstractmethod
    def increment_counter(self, metric_name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Incrementar contador.
        
        Args:
            metric_name: Nombre de la métrica
            value: Valor a incrementar
            tags: Tags adicionales
        """
        pass
    
    @abstractmethod
    def record_histogram(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Registrar valor en histograma.
        
        Args:
            metric_name: Nombre de la métrica
            value: Valor a registrar
            tags: Tags adicionales
        """
        pass
    
    @abstractmethod
    def record_gauge(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Registrar gauge (valor instantáneo).
        
        Args:
            metric_name: Nombre de la métrica
            value: Valor actual
            tags: Tags adicionales
        """
        pass
    
    @abstractmethod
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de métricas.
        
        Returns:
            Resumen de todas las métricas
        """
        pass
    
    @abstractmethod
    async def get_metric_history(
        self, 
        metric_name: str, 
        time_range: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtener historial de una métrica.
        
        Args:
            metric_name: Nombre de la métrica
            time_range: Rango de tiempo (ej: "1h", "24h")
            
        Returns:
            Lista de puntos de datos históricos
        """
        pass
    
    @abstractmethod
    def reset_metrics(self) -> None:
        """Resetear todas las métricas."""
        pass


class IPerformanceMonitor(ABC):
    """Interface para monitoreo de performance."""
    
    @abstractmethod
    async def start_monitoring(self) -> None:
        """Iniciar monitoreo de performance."""
        pass
    
    @abstractmethod
    async def stop_monitoring(self) -> None:
        """Detener monitoreo de performance."""
        pass
    
    @abstractmethod
    def get_cpu_usage(self) -> float:
        """
        Obtener uso de CPU actual.
        
        Returns:
            Porcentaje de uso de CPU
        """
        pass
    
    @abstractmethod
    def get_memory_usage(self) -> Dict[str, float]:
        """
        Obtener uso de memoria.
        
        Returns:
            Diccionario con información de memoria
        """
        pass
    
    @abstractmethod
    def get_disk_usage(self) -> Dict[str, float]:
        """
        Obtener uso de disco.
        
        Returns:
            Diccionario con información de disco
        """
        pass
    
    @abstractmethod
    async def get_performance_report(self) -> Dict[str, Any]:
        """
        Obtener reporte completo de performance.
        
        Returns:
            Reporte de performance del sistema
        """
        pass


class IHealthChecker(ABC):
    """Interface para verificación de salud del sistema."""
    
    @abstractmethod
    async def check_system_health(self) -> Dict[str, Any]:
        """
        Verificar salud general del sistema.
        
        Returns:
            Estado de salud del sistema
        """
        pass
    
    @abstractmethod
    async def check_component_health(self, component_name: str) -> Dict[str, Any]:
        """
        Verificar salud de un componente específico.
        
        Args:
            component_name: Nombre del componente
            
        Returns:
            Estado de salud del componente
        """
        pass
    
    @abstractmethod
    def register_health_check(
        self, 
        component_name: str, 
        check_function: callable
    ) -> None:
        """
        Registrar función de health check para un componente.
        
        Args:
            component_name: Nombre del componente
            check_function: Función que retorna estado de salud
        """
        pass
    
    @abstractmethod
    def get_registered_checks(self) -> List[str]:
        """
        Obtener lista de health checks registrados.
        
        Returns:
            Lista de nombres de componentes
        """
        pass


class IAlertManager(ABC):
    """Interface para gestión de alertas."""
    
    @abstractmethod
    def create_alert(
        self, 
        level: str, 
        message: str, 
        component: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Crear nueva alerta.
        
        Args:
            level: Nivel de alerta (info, warning, error, critical)
            message: Mensaje de la alerta
            component: Componente que genera la alerta
            metadata: Metadatos adicionales
            
        Returns:
            ID de la alerta creada
        """
        pass
    
    @abstractmethod
    def resolve_alert(self, alert_id: str) -> bool:
        """
        Resolver una alerta.
        
        Args:
            alert_id: ID de la alerta
            
        Returns:
            True si se resolvió correctamente
        """
        pass
    
    @abstractmethod
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
        Obtener alertas activas.
        
        Returns:
            Lista de alertas activas
        """
        pass
    
    @abstractmethod
    def configure_alert_rule(
        self, 
        rule_name: str, 
        condition: str, 
        action: str
    ) -> None:
        """
        Configurar regla de alerta.
        
        Args:
            rule_name: Nombre de la regla
            condition: Condición para disparar la alerta
            action: Acción a tomar cuando se dispare
        """
        pass


class IStructuredLogger(ABC):
    """Interface para logging estructurado."""
    
    @abstractmethod
    def log_structured(
        self, 
        level: str, 
        message: str,
        extra_fields: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> None:
        """
        Log estructurado con campos adicionales.
        
        Args:
            level: Nivel de log
            message: Mensaje
            extra_fields: Campos adicionales
            request_id: ID de request para tracing
        """
        pass
    
    @abstractmethod
    def log_analysis_request(
        self,
        request_id: str,
        text_length: int,
        analysis_types: List[str],
        tier: str
    ) -> None:
        """
        Log específico para requests de análisis.
        
        Args:
            request_id: ID del request
            text_length: Longitud del texto
            analysis_types: Tipos de análisis solicitados
            tier: Tier de procesamiento
        """
        pass
    
    @abstractmethod
    def log_analysis_response(
        self,
        request_id: str,
        success: bool,
        duration_ms: float,
        cache_hit: bool,
        error: Optional[str] = None
    ) -> None:
        """
        Log específico para responses de análisis.
        
        Args:
            request_id: ID del request
            success: Si fue exitoso
            duration_ms: Duración en milisegundos
            cache_hit: Si fue cache hit
            error: Error si hubo alguno
        """
        pass
    
    @abstractmethod
    def get_log_context(self) -> Dict[str, Any]:
        """
        Obtener contexto actual de logging.
        
        Returns:
            Contexto de logging
        """
        pass
    
    @abstractmethod
    def set_log_context(self, context: Dict[str, Any]) -> None:
        """
        Establecer contexto de logging.
        
        Args:
            context: Nuevo contexto
        """
        pass


class IMetricsExporter(ABC):
    """Interface para exportación de métricas."""
    
    @abstractmethod
    async def export_metrics(
        self, 
        metrics: Dict[str, Any], 
        format_type: str = "prometheus"
    ) -> str:
        """
        Exportar métricas en formato específico.
        
        Args:
            metrics: Métricas a exportar
            format_type: Formato de exportación
            
        Returns:
            Métricas formateadas
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Obtener formatos soportados.
        
        Returns:
            Lista de formatos soportados
        """
        pass
    
    @abstractmethod
    async def send_to_external(
        self, 
        endpoint: str, 
        metrics: Dict[str, Any]
    ) -> bool:
        """
        Enviar métricas a sistema externo.
        
        Args:
            endpoint: Endpoint destino
            metrics: Métricas a enviar
            
        Returns:
            True si se envió correctamente
        """
        pass 