#!/usr/bin/env python3
"""
Auto-Scaling Manager
Manages automatic scaling based on deployment metrics
"""

import logging
import subprocess
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class ScalingTrigger(Enum):
    """Scaling trigger types"""
    CPU_THRESHOLD = "cpu_threshold"
    MEMORY_THRESHOLD = "memory_threshold"
    REQUEST_RATE = "request_rate"
    DEPLOYMENT_COUNT = "deployment_count"
    CUSTOM_METRIC = "custom_metric"


@dataclass
class ScalingPolicy:
    """Auto-scaling policy"""
    name: str
    trigger: ScalingTrigger
    threshold: float
    scale_up_instances: int = 1
    scale_down_instances: int = 1
    min_instances: int = 1
    max_instances: int = 10
    cooldown_seconds: int = 300
    enabled: bool = True


class AutoScalingManager:
    """Manages auto-scaling based on metrics"""
    
    def __init__(self, policies: Optional[List[ScalingPolicy]] = None):
        self.policies = policies or []
        self.last_scaling_action: Optional[datetime] = None
        self.scaling_history: List[Dict[str, Any]] = []
    
    def evaluate_scaling(self, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate if scaling is needed based on metrics"""
        for policy in self.policies:
            if not policy.enabled:
                continue
            
            # Check cooldown
            if self.last_scaling_action:
                elapsed = (datetime.now() - self.last_scaling_action).total_seconds()
                if elapsed < policy.cooldown_seconds:
                    continue
            
            should_scale = False
            scale_direction = None
            
            if policy.trigger == ScalingTrigger.CPU_THRESHOLD:
                cpu_usage = metrics.get('cpu_percent', 0)
                if cpu_usage > policy.threshold:
                    should_scale = True
                    scale_direction = 'up'
                elif cpu_usage < (policy.threshold * 0.5):
                    should_scale = True
                    scale_direction = 'down'
            
            elif policy.trigger == ScalingTrigger.MEMORY_THRESHOLD:
                memory_usage = metrics.get('memory_percent', 0)
                if memory_usage > policy.threshold:
                    should_scale = True
                    scale_direction = 'up'
                elif memory_usage < (policy.threshold * 0.5):
                    should_scale = True
                    scale_direction = 'down'
            
            if should_scale:
                return {
                    'policy': policy.name,
                    'direction': scale_direction,
                    'instances': policy.scale_up_instances if scale_direction == 'up' else -policy.scale_down_instances,
                    'reason': f"{policy.trigger.value} threshold exceeded"
                }
        
        return None
    
    def scale_instances(self, action: Dict[str, Any]) -> bool:
        """Scale instances based on action"""
        try:
            direction = action['direction']
            instances = action['instances']
            
            # Use AWS CLI or Terraform to scale
            # This is simplified - actual implementation would use boto3 or Terraform
            logger.info(f"Scaling {direction}: {instances} instances")
            
            # Record scaling action
            self.last_scaling_action = datetime.now()
            self.scaling_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'success': True
            })
            
            return True
        except Exception as e:
            logger.error(f"Scaling failed: {e}")
            self.scaling_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'success': False,
                'error': str(e)
            })
            return False
    
    def get_scaling_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get scaling history"""
        return self.scaling_history[-limit:]
