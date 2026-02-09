#!/usr/bin/env python3
"""
Deployment Performance Monitor
Tracks and analyzes deployment performance metrics
"""

import time
import logging
import psutil
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json


logger = logging.getLogger(__name__)


@dataclass
class PerformanceSnapshot:
    """Performance snapshot at a point in time"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_sent_mb: float
    network_recv_mb: float
    docker_containers: int
    docker_images: int


class DeploymentPerformanceMonitor:
    """Monitors deployment performance"""
    
    def __init__(self, metrics_file: str = '/var/lib/deployment-performance/metrics.json'):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.snapshots: List[PerformanceSnapshot] = []
        self.deployment_metrics: List[Dict[str, Any]] = []
    
    def take_snapshot(self) -> PerformanceSnapshot:
        """Take a performance snapshot"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Docker metrics
            docker_containers = self._count_docker_containers()
            docker_images = self._count_docker_images()
            
            snapshot = PerformanceSnapshot(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 ** 2),
                memory_available_mb=memory.available / (1024 ** 2),
                disk_usage_percent=disk.percent,
                disk_free_gb=disk.free / (1024 ** 3),
                network_sent_mb=network.bytes_sent / (1024 ** 2),
                network_recv_mb=network.bytes_recv / (1024 ** 2),
                docker_containers=docker_containers,
                docker_images=docker_images
            )
            
            self.snapshots.append(snapshot)
            
            # Keep only last 1000 snapshots
            if len(self.snapshots) > 1000:
                self.snapshots = self.snapshots[-1000:]
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to take performance snapshot: {e}")
            return None
    
    def _count_docker_containers(self) -> int:
        """Count running Docker containers"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '-q'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return len([line for line in result.stdout.strip().split('\n') if line])
        except Exception:
            pass
        return 0
    
    def _count_docker_images(self) -> int:
        """Count Docker images"""
        try:
            result = subprocess.run(
                ['docker', 'images', '-q'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return len([line for line in result.stdout.strip().split('\n') if line])
        except Exception:
            pass
        return 0
    
    def monitor_deployment(self, deployment_id: str, duration: float) -> Dict[str, Any]:
        """Monitor a deployment and return metrics"""
        start_snapshot = self.snapshots[-1] if self.snapshots else self.take_snapshot()
        
        # Take snapshots during deployment
        snapshots_during = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            snapshot = self.take_snapshot()
            if snapshot:
                snapshots_during.append(snapshot)
            time.sleep(1)  # Snapshot every second
        
        end_snapshot = self.take_snapshot()
        
        # Calculate metrics
        if snapshots_during:
            max_cpu = max(s.cpu_percent for s in snapshots_during)
            max_memory = max(s.memory_percent for s in snapshots_during)
            avg_cpu = sum(s.cpu_percent for s in snapshots_during) / len(snapshots_during)
            avg_memory = sum(s.memory_percent for s in snapshots_during) / len(snapshots_during)
        else:
            max_cpu = max_memory = avg_cpu = avg_memory = 0
        
        metrics = {
            'deployment_id': deployment_id,
            'duration': duration,
            'start_time': datetime.fromtimestamp(start_snapshot.timestamp).isoformat() if start_snapshot else None,
            'end_time': datetime.fromtimestamp(end_snapshot.timestamp).isoformat() if end_snapshot else None,
            'max_cpu_percent': max_cpu,
            'max_memory_percent': max_memory,
            'avg_cpu_percent': avg_cpu,
            'avg_memory_percent': avg_memory,
            'snapshots_count': len(snapshots_during),
            'docker_containers_start': start_snapshot.docker_containers if start_snapshot else 0,
            'docker_containers_end': end_snapshot.docker_containers if end_snapshot else 0,
            'disk_free_gb_start': start_snapshot.disk_free_gb if start_snapshot else 0,
            'disk_free_gb_end': end_snapshot.disk_free_gb if end_snapshot else 0
        }
        
        self.deployment_metrics.append(metrics)
        self._save_metrics()
        
        return metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.snapshots:
            return {}
        
        recent_snapshots = self.snapshots[-100:]  # Last 100 snapshots
        
        return {
            'current': {
                'cpu_percent': recent_snapshots[-1].cpu_percent if recent_snapshots else 0,
                'memory_percent': recent_snapshots[-1].memory_percent if recent_snapshots else 0,
                'disk_free_gb': recent_snapshots[-1].disk_free_gb if recent_snapshots else 0,
                'docker_containers': recent_snapshots[-1].docker_containers if recent_snapshots else 0
            },
            'averages': {
                'cpu_percent': sum(s.cpu_percent for s in recent_snapshots) / len(recent_snapshots) if recent_snapshots else 0,
                'memory_percent': sum(s.memory_percent for s in recent_snapshots) / len(recent_snapshots) if recent_snapshots else 0
            },
            'max': {
                'cpu_percent': max(s.cpu_percent for s in recent_snapshots) if recent_snapshots else 0,
                'memory_percent': max(s.memory_percent for s in recent_snapshots) if recent_snapshots else 0
            }
        }
    
    def _save_metrics(self):
        """Save metrics to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump({
                    'deployment_metrics': self.deployment_metrics[-100:],  # Keep last 100
                    'last_snapshot': asdict(self.snapshots[-1]) if self.snapshots else None
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
