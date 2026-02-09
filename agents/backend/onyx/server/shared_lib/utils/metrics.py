"""
Advanced Metrics Collection
===========================

Sistema de métricas avanzado con múltiples backends.
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Tipos de métricas"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Métrica individual"""
    name: str
    value: float
    metric_type: MetricType
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class MetricsCollector:
    """
    Colector de métricas avanzado
    
    Ejemplo:
        metrics = MetricsCollector()
        
        # Counter
        metrics.increment("requests_total", labels={"method": "GET"})
        
        # Gauge
        metrics.set_gauge("active_connections", 42)
        
        # Histogram
        metrics.observe("request_duration_seconds", 0.5)
        
        # Timer context
        async with metrics.timer("operation_duration"):
            await do_operation()
    """
    
    def __init__(self, service_name: str = "service"):
        self.service_name = service_name
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.gauges: Dict[str, float] = {}
        self.counters: Dict[str, int] = defaultdict(int)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = asyncio.Lock()
        self._exporters: List[Callable] = []
    
    def register_exporter(self, exporter: Callable):
        """Registra exporter para métricas"""
        self._exporters.append(exporter)
    
    async def _export(self, metric: Metric):
        """Exporta métrica a todos los exporters"""
        for exporter in self._exporters:
            try:
                if asyncio.iscoroutinefunction(exporter):
                    await exporter(metric)
                else:
                    exporter(metric)
            except Exception as e:
                logger.error(f"Error exporting metric: {e}")
    
    def increment(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ):
        """Incrementa un counter"""
        async def _increment():
            async with self._lock:
                key = f"{name}:{labels or {}}"
                self.counters[key] += int(value)
                
                metric = Metric(
                    name=name,
                    value=value,
                    metric_type=MetricType.COUNTER,
                    labels=labels or {}
                )
                self.metrics[name].append(metric)
                await self._export(metric)
        
        asyncio.create_task(_increment())
    
    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Establece un gauge"""
        async def _set_gauge():
            async with self._lock:
                key = f"{name}:{labels or {}}"
                self.gauges[key] = value
                
                metric = Metric(
                    name=name,
                    value=value,
                    metric_type=MetricType.GAUGE,
                    labels=labels or {}
                )
                self.metrics[name].append(metric)
                await self._export(metric)
        
        asyncio.create_task(_set_gauge())
    
    def observe(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Observa un valor para histogram"""
        async def _observe():
            async with self._lock:
                key = f"{name}:{labels or {}}"
                self.histograms[key].append(value)
                
                metric = Metric(
                    name=name,
                    value=value,
                    metric_type=MetricType.HISTOGRAM,
                    labels=labels or {}
                )
                self.metrics[name].append(metric)
                await self._export(metric)
        
        asyncio.create_task(_observe())
    
    class Timer:
        """Context manager para medir tiempo"""
        
        def __init__(self, collector: 'MetricsCollector', name: str, labels: Optional[Dict] = None):
            self.collector = collector
            self.name = name
            self.labels = labels
            self.start_time: Optional[float] = None
        
        async def __aenter__(self):
            self.start_time = time.time()
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if self.start_time:
                duration = time.time() - self.start_time
                self.collector.observe(self.name, duration, self.labels)
            return False
    
    def timer(self, name: str, labels: Optional[Dict[str, str]] = None) -> Timer:
        """Crea un timer context manager"""
        return self.Timer(self, name, labels)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtiene todas las métricas"""
        return {
            "service": self.service_name,
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                k: {
                    "count": len(v),
                    "sum": sum(v),
                    "avg": sum(v) / len(v) if v else 0,
                    "min": min(v) if v else 0,
                    "max": max(v) if v else 0
                }
                for k, v in self.histograms.items()
            }
        }


# Instancia global
default_metrics = MetricsCollector()




