import torch
import time
import psutil
import GPUtil
from typing import Dict, List, Optional, Any, Tuple
import logging
import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict, deque
import threading
from datetime import datetime
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """
    Real-time performance monitoring for GPU, memory, and training metrics
    """
    
    def __init__(self, 
                 monitor_interval: float = 1.0,
                 history_size: int = 1000,
                 save_metrics: bool = True,
                 metrics_dir: str = "metrics"):
        
        self.monitor_interval = monitor_interval
        self.history_size = history_size
        self.save_metrics = save_metrics
        self.metrics_dir = Path(metrics_dir)
        
        # Create metrics directory
        if self.save_metrics:
            self.metrics_dir.mkdir(exist_ok=True)
        
        # Initialize monitoring
        self.monitoring = False
        self.monitor_thread = None
        
        # Metrics storage
        self.metrics = defaultdict(lambda: deque(maxlen=history_size))
        self.timestamps = deque(maxlen=history_size)
        
        # Performance thresholds
        self.thresholds = {
            'gpu_memory_usage': 0.9,  # 90%
            'gpu_temperature': 85,     # 85°C
            'cpu_usage': 0.95,         # 95%
            'memory_usage': 0.9        # 90%
        }
        
        # Alert system
        self.alerts = []
        self.alert_callbacks = []
        
        logger.info("PerformanceMonitor initialized")
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        if self.monitoring:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._collect_metrics()
                self._check_thresholds()
                time.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitor_interval)
    
    def _collect_metrics(self):
        """Collect current performance metrics"""
        timestamp = time.time()
        self.timestamps.append(timestamp)
        
        # GPU metrics
        if torch.cuda.is_available():
            gpu_metrics = self._get_gpu_metrics()
            for key, value in gpu_metrics.items():
                self.metrics[key].append(value)
        
        # CPU and system metrics
        system_metrics = self._get_system_metrics()
        for key, value in system_metrics.items():
            self.metrics[key].append(value)
        
        # PyTorch specific metrics
        pytorch_metrics = self._get_pytorch_metrics()
        for key, value in pytorch_metrics.items():
            self.metrics[key].append(value)
    
    def _get_gpu_metrics(self) -> Dict[str, float]:
        """Get GPU performance metrics"""
        metrics = {}
        
        try:
            # Get GPU info using GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Monitor first GPU
                
                metrics['gpu_memory_usage'] = gpu.memoryUtil
                metrics['gpu_memory_used'] = gpu.memoryUsed / 1024  # GB
                metrics['gpu_memory_total'] = gpu.memoryTotal / 1024  # GB
                metrics['gpu_temperature'] = gpu.temperature
                metrics['gpu_load'] = gpu.load
                
                # PyTorch GPU memory
                if torch.cuda.is_available():
                    metrics['pytorch_gpu_memory_allocated'] = torch.cuda.memory_allocated() / 1e9
                    metrics['pytorch_gpu_memory_reserved'] = torch.cuda.memory_reserved() / 1e9
                    metrics['pytorch_gpu_memory_cached'] = torch.cuda.memory_reserved() / 1e9
                    
                    # Memory fragmentation
                    metrics['gpu_memory_fragmentation'] = (
                        torch.cuda.memory_reserved() - torch.cuda.memory_allocated()
                    ) / torch.cuda.memory_reserved()
        
        except Exception as e:
            logger.warning(f"Failed to get GPU metrics: {e}")
            metrics = {key: 0.0 for key in [
                'gpu_memory_usage', 'gpu_memory_used', 'gpu_memory_total',
                'gpu_temperature', 'gpu_load', 'pytorch_gpu_memory_allocated',
                'pytorch_gpu_memory_reserved', 'pytorch_gpu_memory_cached',
                'gpu_memory_fragmentation'
            ]}
        
        return metrics
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Get system performance metrics"""
        metrics = {}
        
        try:
            # CPU metrics
            metrics['cpu_usage'] = psutil.cpu_percent(interval=0.1) / 100
            metrics['cpu_count'] = psutil.cpu_count()
            metrics['cpu_freq'] = psutil.cpu_freq().current / 1000  # GHz
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics['memory_usage'] = memory.percent / 100
            metrics['memory_used'] = memory.used / 1e9  # GB
            metrics['memory_total'] = memory.total / 1e9  # GB
            metrics['memory_available'] = memory.available / 1e9  # GB
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            metrics['disk_usage'] = disk.percent / 100
            metrics['disk_free'] = disk.free / 1e9  # GB
            
            # Network metrics
            network = psutil.net_io_counters()
            metrics['network_bytes_sent'] = network.bytes_sent / 1e6  # MB
            metrics['network_bytes_recv'] = network.bytes_recv / 1e6  # MB
        
        except Exception as e:
            logger.warning(f"Failed to get system metrics: {e}")
            metrics = {key: 0.0 for key in [
                'cpu_usage', 'cpu_count', 'cpu_freq', 'memory_usage',
                'memory_used', 'memory_total', 'memory_available',
                'disk_usage', 'disk_free', 'network_bytes_sent', 'network_bytes_recv'
            ]}
        
        return metrics
    
    def _get_pytorch_metrics(self) -> Dict[str, float]:
        """Get PyTorch specific metrics"""
        metrics = {}
        
        try:
            if torch.cuda.is_available():
                # CUDA memory info
                metrics['cuda_memory_allocated'] = torch.cuda.memory_allocated() / 1e9
                metrics['cuda_memory_reserved'] = torch.cuda.memory_reserved() / 1e9
                metrics['cuda_memory_cached'] = torch.cuda.memory_reserved() / 1e9
                
                # CUDA device properties
                device_props = torch.cuda.get_device_properties(0)
                metrics['cuda_compute_capability'] = f"{device_props.major}.{device_props.minor}"
                metrics['cuda_multi_processor_count'] = device_props.multi_processor_count
                
                # Memory fragmentation
                if torch.cuda.memory_reserved() > 0:
                    metrics['cuda_memory_fragmentation'] = (
                        torch.cuda.memory_reserved() - torch.cuda.memory_allocated()
                    ) / torch.cuda.memory_reserved()
                else:
                    metrics['cuda_memory_fragmentation'] = 0.0
            else:
                metrics = {key: 0.0 for key in [
                    'cuda_memory_allocated', 'cuda_memory_reserved', 'cuda_memory_cached',
                    'cuda_memory_fragmentation'
                ]}
        
        except Exception as e:
            logger.warning(f"Failed to get PyTorch metrics: {e}")
            metrics = {key: 0.0 for key in [
                'cuda_memory_allocated', 'cuda_memory_reserved', 'cuda_memory_cached',
                'cuda_memory_fragmentation'
            ]}
        
        return metrics
    
    def _check_thresholds(self):
        """Check if any metrics exceed thresholds"""
        for metric_name, threshold in self.thresholds.items():
            if metric_name in self.metrics and self.metrics[metric_name]:
                current_value = self.metrics[metric_name][-1]
                
                if current_value > threshold:
                    alert = {
                        'timestamp': time.time(),
                        'metric': metric_name,
                        'value': current_value,
                        'threshold': threshold,
                        'severity': 'high' if current_value > threshold * 1.2 else 'medium'
                    }
                    
                    self.alerts.append(alert)
                    self._trigger_alerts(alert)
    
    def _trigger_alerts(self, alert: Dict[str, Any]):
        """Trigger alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def add_alert_callback(self, callback):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
    
    def get_current_metrics(self) -> Dict[str, float]:
        """Get current metric values"""
        current_metrics = {}
        for metric_name, values in self.metrics.items():
            if values:
                current_metrics[metric_name] = values[-1]
        return current_metrics
    
    def get_metric_history(self, metric_name: str) -> List[float]:
        """Get history for specific metric"""
        return list(self.metrics[metric_name])
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary statistics for all metrics"""
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                values_list = list(values)
                summary[metric_name] = {
                    'current': values_list[-1],
                    'min': min(values_list),
                    'max': max(values_list),
                    'mean': np.mean(values_list),
                    'std': np.std(values_list)
                }
        
        return summary
    
    def plot_metrics(self, 
                    metric_names: Optional[List[str]] = None,
                    save_path: Optional[str] = None,
                    show_plot: bool = True):
        """Plot metric history"""
        if not metric_names:
            metric_names = list(self.metrics.keys())
        
        fig, axes = plt.subplots(len(metric_names), 1, figsize=(12, 4 * len(metric_names)))
        if len(metric_names) == 1:
            axes = [axes]
        
        timestamps = list(self.timestamps)
        
        for i, metric_name in enumerate(metric_names):
            if metric_name in self.metrics and self.metrics[metric_name]:
                values = list(self.metrics[metric_name])
                
                axes[i].plot(timestamps, values, label=metric_name)
                axes[i].set_title(f"{metric_name} over time")
                axes[i].set_ylabel(metric_name)
                axes[i].grid(True)
                
                # Add threshold line if available
                if metric_name in self.thresholds:
                    threshold = self.thresholds[metric_name]
                    axes[i].axhline(y=threshold, color='r', linestyle='--', 
                                  label=f'Threshold: {threshold}')
                    axes[i].legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Metrics plot saved to {save_path}")
        
        if show_plot:
            plt.show()
    
    def save_metrics(self, filename: Optional[str] = None):
        """Save metrics to JSON file"""
        if not self.save_metrics:
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.json"
        
        filepath = self.metrics_dir / filename
        
        metrics_data = {
            'timestamps': list(self.timestamps),
            'metrics': {name: list(values) for name, values in self.metrics.items()},
            'summary': self.get_metrics_summary(),
            'alerts': self.alerts
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        logger.info(f"Metrics saved to {filepath}")
    
    def clear_metrics(self):
        """Clear all metrics and history"""
        for metric_name in self.metrics:
            self.metrics[metric_name].clear()
        self.timestamps.clear()
        self.alerts.clear()
        logger.info("All metrics cleared")
    
    def optimize_memory(self):
        """Optimize memory usage"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        gc.collect()
        logger.info("Memory optimization completed")

class TrainingMetricsTracker:
    """
    Track training-specific metrics
    """
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.training_metrics = defaultdict(lambda: deque(maxlen=1000))
        self.epoch_metrics = defaultdict(list)
        self.current_epoch = 0
        
        # Register with performance monitor
        self.monitor.add_alert_callback(self._training_alert_callback)
    
    def start_epoch(self, epoch: int):
        """Start tracking new epoch"""
        self.current_epoch = epoch
        logger.info(f"Starting epoch {epoch}")
    
    def log_training_step(self, 
                         step: int,
                         loss: float,
                         learning_rate: float,
                         batch_size: int,
                         **kwargs):
        """Log training step metrics"""
        timestamp = time.time()
        
        self.training_metrics['step'].append(step)
        self.training_metrics['loss'].append(loss)
        self.training_metrics['learning_rate'].append(learning_rate)
        self.training_metrics['batch_size'].append(batch_size)
        self.training_metrics['timestamp'].append(timestamp)
        
        # Log additional metrics
        for key, value in kwargs.items():
            self.training_metrics[key].append(value)
    
    def log_validation_step(self, 
                           step: int,
                           val_loss: float,
                           **kwargs):
        """Log validation step metrics"""
        timestamp = time.time()
        
        self.training_metrics['val_step'].append(step)
        self.training_metrics['val_loss'].append(val_loss)
        self.training_metrics['val_timestamp'].append(timestamp)
        
        # Log additional validation metrics
        for key, value in kwargs.items():
            self.training_metrics[f'val_{key}'].append(value)
    
    def end_epoch(self, epoch_metrics: Dict[str, float]):
        """End epoch and store epoch-level metrics"""
        self.epoch_metrics['epoch'].append(self.current_epoch)
        
        for key, value in epoch_metrics.items():
            self.epoch_metrics[key].append(value)
        
        logger.info(f"Epoch {self.current_epoch} completed: {epoch_metrics}")
    
    def _training_alert_callback(self, alert: Dict[str, Any]):
        """Handle performance alerts during training"""
        if alert['metric'] in ['gpu_memory_usage', 'gpu_temperature']:
            logger.warning(f"Training performance alert: {alert}")
            
            # Suggest actions
            if alert['metric'] == 'gpu_memory_usage' and alert['value'] > 0.9:
                logger.info("Consider reducing batch size or using gradient accumulation")
            elif alert['metric'] == 'gpu_temperature' and alert['value'] > 85:
                logger.info("Consider reducing GPU load or improving cooling")
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get training metrics summary"""
        summary = {}
        
        for metric_name, values in self.training_metrics.items():
            if values:
                values_list = list(values)
                summary[metric_name] = {
                    'current': values_list[-1],
                    'min': min(values_list),
                    'max': max(values_list),
                    'mean': np.mean(values_list),
                    'std': np.std(values_list)
                }
        
        return summary
    
    def plot_training_metrics(self, save_path: Optional[str] = None):
        """Plot training metrics"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()
        
        # Loss plot
        if 'loss' in self.training_metrics and self.training_metrics['loss']:
            axes[0].plot(self.training_metrics['step'], self.training_metrics['loss'], 
                        label='Training Loss')
            if 'val_loss' in self.training_metrics and self.training_metrics['val_loss']:
                axes[0].plot(self.training_metrics['val_step'], self.training_metrics['val_loss'], 
                            label='Validation Loss')
            axes[0].set_title('Training and Validation Loss')
            axes[0].set_xlabel('Step')
            axes[0].set_ylabel('Loss')
            axes[0].legend()
            axes[0].grid(True)
        
        # Learning rate plot
        if 'learning_rate' in self.training_metrics and self.training_metrics['learning_rate']:
            axes[1].plot(self.training_metrics['step'], self.training_metrics['learning_rate'])
            axes[1].set_title('Learning Rate')
            axes[1].set_xlabel('Step')
            axes[1].set_ylabel('Learning Rate')
            axes[1].grid(True)
        
        # Batch size plot
        if 'batch_size' in self.training_metrics and self.training_metrics['batch_size']:
            axes[2].plot(self.training_metrics['step'], self.training_metrics['batch_size'])
            axes[2].set_title('Batch Size')
            axes[2].set_xlabel('Step')
            axes[2].set_ylabel('Batch Size')
            axes[2].grid(True)
        
        # Epoch metrics plot
        if 'epoch' in self.epoch_metrics and self.epoch_metrics['epoch']:
            for key in self.epoch_metrics:
                if key != 'epoch' and self.epoch_metrics[key]:
                    axes[3].plot(self.epoch_metrics['epoch'], self.epoch_metrics[key], 
                                label=key, marker='o')
            axes[3].set_title('Epoch Metrics')
            axes[3].set_xlabel('Epoch')
            axes[3].set_ylabel('Value')
            axes[3].legend()
            axes[3].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Training metrics plot saved to {save_path}")
        
        plt.show()

# Example usage
if __name__ == "__main__":
    # Initialize performance monitor
    monitor = PerformanceMonitor(monitor_interval=2.0)
    
    # Initialize training tracker
    tracker = TrainingMetricsTracker(monitor)
    
    # Start monitoring
    monitor.start_monitoring()
    
    # Simulate training
    for epoch in range(3):
        tracker.start_epoch(epoch)
        
        for step in range(100):
            # Simulate training step
            loss = 1.0 / (1 + step * 0.01)
            lr = 0.001 * (0.9 ** epoch)
            
            tracker.log_training_step(
                step=step,
                loss=loss,
                learning_rate=lr,
                batch_size=32
            )
            
            if step % 20 == 0:
                tracker.log_validation_step(
                    step=step,
                    val_loss=loss * 1.1
                )
            
            time.sleep(0.01)  # Simulate processing time
        
        tracker.end_epoch({
            'avg_loss': 0.5,
            'avg_val_loss': 0.55
        })
    
    # Stop monitoring
    monitor.stop_monitoring()
    
    # Get summaries
    print("Performance Summary:", monitor.get_metrics_summary())
    print("Training Summary:", tracker.get_training_summary())
    
    # Plot metrics
    monitor.plot_metrics(['gpu_memory_usage', 'cpu_usage'])
    tracker.plot_training_metrics()
    
    # Save metrics
    monitor.save_metrics()
    
    # Cleanup
    monitor.clear_metrics()
    monitor.optimize_memory()


