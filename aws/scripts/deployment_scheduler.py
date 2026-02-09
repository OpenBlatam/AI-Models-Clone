#!/usr/bin/env python3
"""
Deployment Scheduler
Schedules deployments at optimal times
"""

import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, time as dt_time
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class ScheduleRule:
    """Schedule rule for deployments"""
    enabled: bool = True
    allowed_hours: List[int] = None  # 0-23, None = all hours
    allowed_days: List[int] = None  # 0-6 (Monday=0), None = all days
    max_deployments_per_hour: int = 5
    max_deployments_per_day: int = 20
    maintenance_window_start: Optional[dt_time] = None
    maintenance_window_end: Optional[dt_time] = None
    
    def __post_init__(self):
        if self.allowed_hours is None:
            self.allowed_hours = list(range(24))
        if self.allowed_days is None:
            self.allowed_days = list(range(7))


class DeploymentScheduler:
    """Schedules deployments based on rules"""
    
    def __init__(self, rules: Optional[ScheduleRule] = None):
        self.rules = rules or ScheduleRule()
        self.deployment_counts: Dict[str, int] = {}  # Track deployments per hour/day
    
    def can_deploy_now(self) -> Tuple[bool, str]:
        """
        Check if deployment is allowed now
        
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        now = datetime.now()
        current_hour = now.hour
        current_day = now.weekday()
        hour_key = f"{now.date()}_{current_hour}"
        day_key = str(now.date())
        
        # Check if scheduling is enabled
        if not self.rules.enabled:
            return True, "Scheduling disabled"
        
        # Check allowed hours
        if current_hour not in self.rules.allowed_hours:
            return False, f"Deployment not allowed at hour {current_hour}"
        
        # Check allowed days
        if current_day not in self.rules.allowed_days:
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            return False, f"Deployment not allowed on {day_names[current_day]}"
        
        # Check maintenance window
        if self.rules.maintenance_window_start and self.rules.maintenance_window_end:
            current_time = now.time()
            if (self.rules.maintenance_window_start <= current_time <= self.rules.maintenance_window_end):
                return False, "Currently in maintenance window"
        
        # Check deployment limits
        hour_count = self.deployment_counts.get(hour_key, 0)
        if hour_count >= self.rules.max_deployments_per_hour:
            return False, f"Max deployments per hour reached ({self.rules.max_deployments_per_hour})"
        
        day_count = sum(
            count for key, count in self.deployment_counts.items()
            if key.startswith(day_key)
        )
        if day_count >= self.rules.max_deployments_per_day:
            return False, f"Max deployments per day reached ({self.rules.max_deployments_per_day})"
        
        return True, "Deployment allowed"
    
    def record_deployment(self) -> None:
        """Record a deployment for rate limiting"""
        now = datetime.now()
        hour_key = f"{now.date()}_{now.hour}"
        self.deployment_counts[hour_key] = self.deployment_counts.get(hour_key, 0) + 1
        
        # Clean up old entries (older than 24 hours)
        cutoff = now.date()
        keys_to_remove = [
            key for key in self.deployment_counts.keys()
            if not key.startswith(str(cutoff))
        ]
        for key in keys_to_remove:
            del self.deployment_counts[key]
    
    def get_next_allowed_time(self) -> Optional[datetime]:
        """Get next time when deployment is allowed"""
        now = datetime.now()
        
        # Check next hour
        for hour_offset in range(24):
            check_time = now.replace(hour=(now.hour + hour_offset) % 24, minute=0, second=0)
            if check_time.hour in self.rules.allowed_hours:
                if check_time > now:
                    return check_time
        
        return None
