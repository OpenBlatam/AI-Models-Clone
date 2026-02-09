"""
Health monitoring module for services.
Handles health checks, metrics collection, and alerting.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from .dependency_structures import ServiceStatus, ServiceHealth, ServiceMetrics


@dataclass
class HealthCheck:
    """Health check configuration and results"""
    service_name: str
    check_type: str
    interval: float = 30.0  # seconds
    timeout: float = 10.0   # seconds
    last_check: Optional[datetime] = None
    last_result: Optional[bool] = None
    consecutive_failures: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert information"""
    service_name: str
    alert_type: str
    message: str
    severity: str = "warning"
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class HealthMonitor:
    """Monitors the health of all services"""
    
    def __init__(self):
        self.health_checks: Dict[str, List[HealthCheck]] = {}
        self.service_health: Dict[str, ServiceHealth] = {}
        self.service_metrics: Dict[str, ServiceMetrics] = {}
        self.alerts: List[Alert] = []
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        
        # Alert thresholds
        self.failure_threshold = 3
        self.health_score_threshold = 70.0
        
        # Callbacks
        self._on_alert: Optional[Callable] = None
        self._on_health_change: Optional[Callable] = None
    
    def add_health_check(
        self,
        service_name: str,
        check_type: str,
        check_function: Callable,
        interval: float = 30.0,
        timeout: float = 10.0
    ) -> None:
        """Add a health check for a service"""
        if service_name not in self.health_checks:
            self.health_checks[service_name] = []
        
        health_check = HealthCheck(
            service_name=service_name,
            check_type=check_type,
            interval=interval,
            timeout=timeout
        )
        
        # Store the check function in metadata
        health_check.metadata["check_function"] = check_function
        self.health_checks[service_name].append(health_check)
    
    def remove_health_check(self, service_name: str, check_type: str) -> None:
        """Remove a health check"""
        if service_name in self.health_checks:
            self.health_checks[service_name] = [
                check for check in self.health_checks[service_name]
                if check.check_type != check_type
            ]
    
    def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """Get health information for a service"""
        return self.service_health.get(service_name)
    
    def get_service_metrics(self, service_name: str) -> Optional[ServiceMetrics]:
        """Get metrics for a service"""
        return self.service_metrics.get(service_name)
    
    def update_service_status(self, service_name: str, status: ServiceStatus) -> None:
        """Update the status of a service"""
        if service_name not in self.service_health:
            self.service_health[service_name] = ServiceHealth(
                service_name=service_name,
                status=status
            )
        else:
            self.service_health[service_name].status = status
            self.service_health[service_name].last_check = datetime.now()
        
        # Trigger health change callback
        if self._on_health_change:
            self._on_health_change(service_name, status)
    
    def update_service_metrics(
        self,
        service_name: str,
        response_time: Optional[float] = None,
        throughput: Optional[float] = None,
        error_rate: Optional[float] = None
    ) -> None:
        """Update metrics for a service"""
        if service_name not in self.service_metrics:
            self.service_metrics[service_name] = ServiceMetrics(service_name=service_name)
        
        metrics = self.service_metrics[service_name]
        
        if response_time is not None:
            metrics.response_time = response_time
        
        if throughput is not None:
            metrics.throughput = throughput
        
        if error_rate is not None:
            metrics.error_rate = error_rate
        
        metrics.last_updated = datetime.now()
        
        # Update availability based on error rate
        if error_rate is not None:
            metrics.availability = max(0.0, 100.0 - error_rate)
    
    async def run_health_check(self, health_check: HealthCheck) -> bool:
        """Run a single health check"""
        try:
            check_function = health_check.metadata["check_function"]
            
            # Run the check with timeout
            result = await asyncio.wait_for(
                check_function(health_check.service_name),
                timeout=health_check.timeout
            )
            
            health_check.last_result = bool(result)
            health_check.last_check = datetime.now()
            
            if result:
                health_check.consecutive_failures = 0
            else:
                health_check.consecutive_failures += 1
            
            return bool(result)
            
        except asyncio.TimeoutError:
            health_check.last_result = False
            health_check.consecutive_failures += 1
            health_check.last_check = datetime.now()
            return False
            
        except Exception as e:
            health_check.last_result = False
            health_check.consecutive_failures += 1
            health_check.last_check = datetime.now()
            return False
    
    async def run_all_health_checks(self) -> None:
        """Run all health checks for all services"""
        for service_name, checks in self.health_checks.items():
            for check in checks:
                # Check if it's time to run this check
                if (check.last_check is None or
                    datetime.now() - check.last_check > timedelta(seconds=check.interval)):
                    
                    result = await self.run_health_check(check)
                    
                    # Update service health based on check results
                    if check.consecutive_failures >= self.failure_threshold:
                        self.update_service_status(service_name, ServiceStatus.ERROR)
                        
                        # Create alert
                        alert = Alert(
                            service_name=service_name,
                            alert_type="health_check_failure",
                            message=f"Health check '{check.check_type}' failed {check.consecutive_failures} times",
                            severity="critical"
                        )
                        self.alerts.append(alert)
                        
                        # Trigger alert callback
                        if self._on_alert:
                            self._on_alert(alert)
    
    async def start_monitoring(self) -> None:
        """Start the health monitoring loop"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        
        async def monitoring_loop():
            while self.is_monitoring:
                try:
                    await self.run_all_health_checks()
                    await asyncio.sleep(10)  # Check every 10 seconds
                except Exception as e:
                    # Log error but continue monitoring
                    print(f"Health monitoring error: {e}")
                    await asyncio.sleep(30)  # Wait longer on error
        
        self.monitoring_task = asyncio.create_task(monitoring_loop())
    
    async def stop_monitoring(self) -> None:
        """Stop the health monitoring loop"""
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        total_services = len(self.service_health)
        healthy_services = sum(
            1 for health in self.service_health.values()
            if health.status in [ServiceStatus.RUNNING, ServiceStatus.STARTING]
        )
        
        health_percentage = (healthy_services / total_services * 100) if total_services > 0 else 0
        
        return {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "unhealthy_services": total_services - healthy_services,
            "health_percentage": health_percentage,
            "active_alerts": len([a for a in self.alerts if not a.acknowledged]),
            "timestamp": datetime.now().isoformat()
        }
    
    def acknowledge_alert(self, alert_index: int) -> None:
        """Acknowledge an alert"""
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index].acknowledged = True
    
    def clear_old_alerts(self, days: int = 7) -> None:
        """Clear alerts older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        self.alerts = [
            alert for alert in self.alerts
            if alert.timestamp > cutoff
        ]
    
    def on_alert(self, callback: Callable) -> None:
        """Register callback for alerts"""
        self._on_alert = callback
    
    def on_health_change(self, callback: Callable) -> None:
        """Register callback for health changes"""
        self._on_health_change = callback
