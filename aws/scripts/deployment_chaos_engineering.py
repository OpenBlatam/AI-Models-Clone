#!/usr/bin/env python3
"""
Chaos Engineering
Implements chaos engineering experiments for resilience testing
"""

import time
import logging
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class ChaosExperimentType(Enum):
    """Types of chaos experiments"""
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    NETWORK_LATENCY = "network_latency"
    NETWORK_PACKET_LOSS = "network_packet_loss"
    CONTAINER_KILL = "container_kill"
    DISK_FILL = "disk_fill"


@dataclass
class ChaosExperiment:
    """Chaos experiment definition"""
    name: str
    experiment_type: ChaosExperimentType
    duration: int  # seconds
    intensity: int = 50  # 0-100
    enabled: bool = False
    target: Optional[str] = None  # container name, etc.


class ChaosEngineer:
    """Manages chaos engineering experiments"""
    
    def __init__(self):
        self.active_experiments: List[ChaosExperiment] = []
        self.experiment_history: List[Dict[str, Any]] = []
    
    def run_experiment(self, experiment: ChaosExperiment) -> Dict[str, Any]:
        """Run a chaos experiment"""
        if not experiment.enabled:
            logger.warning(f"Experiment {experiment.name} is not enabled")
            return {'success': False, 'error': 'Experiment not enabled'}
        
        logger.info(f"Starting chaos experiment: {experiment.name} ({experiment.experiment_type.value})")
        
        start_time = time.time()
        result = {'success': False, 'error': None}
        
        try:
            if experiment.experiment_type == ChaosExperimentType.CPU_STRESS:
                result = self._cpu_stress(experiment)
            elif experiment.experiment_type == ChaosExperimentType.MEMORY_STRESS:
                result = self._memory_stress(experiment)
            elif experiment.experiment_type == ChaosExperimentType.NETWORK_LATENCY:
                result = self._network_latency(experiment)
            elif experiment.experiment_type == ChaosExperimentType.CONTAINER_KILL:
                result = self._container_kill(experiment)
            else:
                result = {'success': False, 'error': 'Unsupported experiment type'}
            
            duration = time.time() - start_time
            
            experiment_record = {
                'name': experiment.name,
                'type': experiment.experiment_type.value,
                'duration': duration,
                'intensity': experiment.intensity,
                'success': result['success'],
                'timestamp': datetime.now().isoformat()
            }
            
            self.experiment_history.append(experiment_record)
            
            if result['success']:
                logger.info(f"Chaos experiment {experiment.name} completed successfully")
            else:
                logger.error(f"Chaos experiment {experiment.name} failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Chaos experiment {experiment.name} raised exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def _cpu_stress(self, experiment: ChaosExperiment) -> Dict[str, Any]:
        """CPU stress test"""
        try:
            # Use stress-ng if available, otherwise skip
            cpu_count = int(experiment.intensity / 100 * 4)  # Max 4 CPUs
            if cpu_count < 1:
                cpu_count = 1
            
            subprocess.Popen(
                ['stress-ng', '--cpu', str(cpu_count), '--timeout', str(experiment.duration)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return {'success': True}
        except FileNotFoundError:
            logger.warning("stress-ng not found, skipping CPU stress")
            return {'success': False, 'error': 'stress-ng not installed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _memory_stress(self, experiment: ChaosExperiment) -> Dict[str, Any]:
        """Memory stress test"""
        try:
            # Allocate memory based on intensity
            import psutil
            available_memory = psutil.virtual_memory().available
            memory_to_use = int(available_memory * (experiment.intensity / 100))
            
            subprocess.Popen(
                ['stress-ng', '--vm', '1', '--vm-bytes', f'{memory_to_use}', '--timeout', str(experiment.duration)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return {'success': True}
        except FileNotFoundError:
            logger.warning("stress-ng not found, skipping memory stress")
            return {'success': False, 'error': 'stress-ng not installed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _network_latency(self, experiment: ChaosExperiment) -> Dict[str, Any]:
        """Add network latency"""
        try:
            # Use tc (traffic control) if available
            latency_ms = int(experiment.intensity / 100 * 100)  # Max 100ms
            subprocess.run(
                ['tc', 'qdisc', 'add', 'dev', 'eth0', 'root', 'netem', 'delay', f'{latency_ms}ms'],
                check=True,
                timeout=10
            )
            
            # Wait for duration
            time.sleep(experiment.duration)
            
            # Remove latency
            subprocess.run(
                ['tc', 'qdisc', 'del', 'dev', 'eth0', 'root'],
                timeout=10
            )
            return {'success': True}
        except FileNotFoundError:
            logger.warning("tc not found, skipping network latency")
            return {'success': False, 'error': 'tc not available'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _container_kill(self, experiment: ChaosExperiment) -> Dict[str, Any]:
        """Kill a container"""
        try:
            if experiment.target:
                subprocess.run(
                    ['docker', 'kill', experiment.target],
                    check=True,
                    timeout=10
                )
                logger.info(f"Killed container: {experiment.target}")
                return {'success': True}
            else:
                return {'success': False, 'error': 'No target container specified'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_experiment_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get experiment history"""
        return self.experiment_history[-limit:]
