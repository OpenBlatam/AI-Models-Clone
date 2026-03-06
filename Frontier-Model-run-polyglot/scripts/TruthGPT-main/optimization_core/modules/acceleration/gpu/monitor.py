"""
GPU Performance Monitoring
"""
import time
import threading
import logging
import numpy as np
import torch
from typing import Dict, Any, List

from .config import GPUAcceleratorConfig

logger = logging.getLogger(__name__)

class GPUPerformanceMonitor:
    """Monitor GPU performance in real-time."""
    
    def __init__(self, config: GPUAcceleratorConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.monitoring = False
        self.monitor_thread = None
        self.metrics_history = []
        self.current_metrics = {}
        
        if self.config.enable_monitoring:
            self.start_monitoring()
        
        self.logger.info("✅ GPU Performance Monitor initialized")
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("📊 Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("📊 Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            metrics = self._collect_metrics()
            self.current_metrics = metrics
            self.metrics_history.append(metrics)
            
            # Keep only last 1000 entries
            if len(self.metrics_history) > 1000:
                self.metrics_history.pop(0)
            
            time.sleep(self.config.monitoring_interval)
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect GPU performance metrics."""
        metrics = {
            'timestamp': time.time(),
            'device_id': self.config.device_id
        }
        
        if torch.cuda.is_available() and self.config.device == "cuda":
            total_mem = torch.cuda.get_device_properties(self.config.device_id).total_memory
            alloc_mem = torch.cuda.memory_allocated(self.config.device_id)
            metrics.update({
                'memory_allocated': alloc_mem,
                'memory_cached': torch.cuda.memory_reserved(self.config.device_id),
                'memory_usage_percent': alloc_mem / total_mem if total_mem > 0 else 0.0,
                'utilization': 0.0,  # Would use pynvml in practice
                'temperature': 0.0,  # Would use pynvml in practice
                'power_usage': 0.0   # Would use pynvml in practice
            })
        
        return metrics
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.current_metrics.copy()
    
    def get_metrics_history(self) -> List[Dict[str, Any]]:
        """Get performance metrics history."""
        return self.metrics_history.copy()
    
    def get_average_metrics(self) -> Dict[str, Any]:
        """Get average performance metrics."""
        if not self.metrics_history:
            return {}
        
        avg_metrics = {}
        # Assumes dict keys are uniform
        for key in self.metrics_history[0].keys():
            if isinstance(self.metrics_history[0][key], (int, float)):
                values = [m[key] for m in self.metrics_history]
                avg_metrics[f'avg_{key}'] = float(np.mean(values))
                avg_metrics[f'min_{key}'] = float(np.min(values))
                avg_metrics[f'max_{key}'] = float(np.max(values))
        
        return avg_metrics
