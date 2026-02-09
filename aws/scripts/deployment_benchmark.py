#!/usr/bin/env python3
"""
Deployment Benchmarking
Performance benchmarking for deployments
"""

import time
import logging
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json


logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Benchmark result"""
    name: str
    duration: float
    success: bool
    metrics: Dict[str, Any] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class DeploymentBenchmark:
    """Benchmarks deployment performance"""
    
    def __init__(self, results_file: str = '/var/lib/deployment-benchmarks/results.json'):
        self.results_file = Path(results_file)
        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        self.results: List[BenchmarkResult] = []
        self._load_results()
    
    def _load_results(self):
        """Load benchmark results"""
        if self.results_file.exists():
            try:
                with open(self.results_file, 'r') as f:
                    data = json.load(f)
                    for result_data in data.get('results', []):
                        result = BenchmarkResult(**result_data)
                        self.results.append(result)
            except Exception as e:
                logger.error(f"Failed to load benchmark results: {e}")
    
    def _save_results(self):
        """Save benchmark results"""
        try:
            data = {
                'results': [
                    {
                        'name': r.name,
                        'duration': r.duration,
                        'success': r.success,
                        'metrics': r.metrics,
                        'timestamp': r.timestamp
                    }
                    for r in self.results[-100:]  # Keep last 100
                ],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.results_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save benchmark results: {e}")
    
    def benchmark_deployment(
        self,
        name: str,
        deployment_func: callable,
        *args,
        **kwargs
    ) -> BenchmarkResult:
        """Benchmark a deployment function"""
        logger.info(f"Starting benchmark: {name}")
        
        start_time = time.time()
        success = False
        metrics = {}
        
        try:
            # Execute deployment
            result = deployment_func(*args, **kwargs)
            
            if isinstance(result, tuple):
                success = result[0]
            else:
                success = bool(result)
            
            duration = time.time() - start_time
            
            # Collect metrics
            try:
                import psutil
                metrics = {
                    'cpu_percent': psutil.cpu_percent(interval=0.1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {}
                }
            except ImportError:
                pass
            
            benchmark_result = BenchmarkResult(
                name=name,
                duration=duration,
                success=success,
                metrics=metrics
            )
            
            self.results.append(benchmark_result)
            self._save_results()
            
            logger.info(f"Benchmark completed: {name} in {duration:.2f}s")
            return benchmark_result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Benchmark failed: {e}")
            
            benchmark_result = BenchmarkResult(
                name=name,
                duration=duration,
                success=False,
                metrics={'error': str(e)}
            )
            
            self.results.append(benchmark_result)
            self._save_results()
            return benchmark_result
    
    def compare_benchmarks(self, benchmark_names: List[str]) -> Dict[str, Any]:
        """Compare multiple benchmarks"""
        filtered_results = [r for r in self.results if r.name in benchmark_names]
        
        if not filtered_results:
            return {}
        
        successful = [r for r in filtered_results if r.success]
        failed = [r for r in filtered_results if not r.success]
        
        if successful:
            durations = [r.duration for r in successful]
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
        else:
            avg_duration = min_duration = max_duration = 0
        
        return {
            'total': len(filtered_results),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / len(filtered_results) * 100 if filtered_results else 0,
            'avg_duration': avg_duration,
            'min_duration': min_duration,
            'max_duration': max_duration,
            'benchmarks': [
                {
                    'name': r.name,
                    'duration': r.duration,
                    'success': r.success,
                    'timestamp': r.timestamp
                }
                for r in filtered_results
            ]
        }
    
    def get_latest_results(self, limit: int = 10) -> List[BenchmarkResult]:
        """Get latest benchmark results"""
        return self.results[-limit:]
