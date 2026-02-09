#!/usr/bin/env python3
"""
Deployment Component Factory
Centralized factory for creating deployment components
"""

import os
import logging
from typing import Dict, Any, Optional, Type
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class ComponentConfig:
    """Configuration for component initialization"""
    enabled: bool = True
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


class DeploymentComponentFactory:
    """Factory for creating deployment components"""
    
    def __init__(self, base_config: Any):
        self.base_config = base_config
        self.project_dir = getattr(base_config, 'project_dir', '/opt/blatam-academy')
        self._component_cache: Dict[str, Any] = {}
    
    def _get_config_dict(self) -> Dict[str, Any]:
        """Get base configuration dictionary"""
        return {
            'health_check_url': getattr(self.base_config, 'health_check_url', 'http://localhost:8000/health'),
            'health_check_timeout': getattr(self.base_config, 'health_check_timeout', 60),
            'project_dir': self.project_dir,
            'deploy_script': getattr(
                self.base_config,
                'deploy_script',
                f'{self.project_dir}/aws/scripts/auto_deploy.sh'
            )
        }
    
    def create_health_checker(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create HealthChecker instance"""
        if not component_config.enabled:
            return None
        
        try:
            from health_checker import HealthChecker
            return HealthChecker(component_config.config or self._get_config_dict())
        except ImportError as e:
            logger.warning(f"HealthChecker not available: {e}")
            return None
    
    def create_notifier(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create DeploymentNotifier instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_notifier import DeploymentNotifier
            config = component_config.config or {
                'slack_webhook': os.environ.get('SLACK_WEBHOOK_URL'),
                'discord_webhook': os.environ.get('DISCORD_WEBHOOK_URL'),
                'webhook_urls': {}
            }
            return DeploymentNotifier(config)
        except ImportError as e:
            logger.warning(f"DeploymentNotifier not available: {e}")
            return None
    
    def create_monitor(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create DeploymentMonitor instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_monitor import DeploymentMonitor
            return DeploymentMonitor()
        except ImportError as e:
            logger.warning(f"DeploymentMonitor not available: {e}")
            return None
    
    def create_validator(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create DeploymentValidator instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_validator import DeploymentValidator
            return DeploymentValidator(component_config.config or self._get_config_dict())
        except ImportError as e:
            logger.warning(f"DeploymentValidator not available: {e}")
            return None
    
    def create_cache(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create DeploymentCache instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_cache import DeploymentCache
            return DeploymentCache()
        except ImportError as e:
            logger.warning(f"DeploymentCache not available: {e}")
            return None
    
    def create_metrics(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create DeploymentMetrics instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_metrics import DeploymentMetrics
            return DeploymentMetrics()
        except ImportError as e:
            logger.warning(f"DeploymentMetrics not available: {e}")
            return None
    
    def create_backup_manager(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create BackupManager instance"""
        if not component_config.enabled:
            return None
        
        try:
            from backup_manager import BackupManager
            return BackupManager()
        except ImportError as e:
            logger.warning(f"BackupManager not available: {e}")
            return None
    
    def create_retry_handler(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create RetryHandler instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_retry import RetryHandler, RetryConfig, RetryStrategy
            retry_config = RetryConfig(
                max_attempts=int(os.environ.get('DEPLOYMENT_MAX_RETRIES', 3)),
                initial_delay=float(os.environ.get('DEPLOYMENT_RETRY_DELAY', 5.0)),
                strategy=RetryStrategy.EXPONENTIAL
            )
            return RetryHandler(retry_config)
        except ImportError as e:
            logger.warning(f"RetryHandler not available: {e}")
            return None
    
    def create_queue(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create DeploymentQueue instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_queue import DeploymentQueue
            return DeploymentQueue()
        except ImportError as e:
            logger.warning(f"DeploymentQueue not available: {e}")
            return None
    
    def create_scheduler(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create DeploymentScheduler instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_scheduler import DeploymentScheduler, ScheduleRule
            schedule_rules = ScheduleRule(
                enabled=os.environ.get('DEPLOYMENT_SCHEDULING_ENABLED', 'false').lower() == 'true',
                allowed_hours=self._parse_hours(os.environ.get('DEPLOYMENT_ALLOWED_HOURS', '')),
                max_deployments_per_hour=int(os.environ.get('DEPLOYMENT_MAX_PER_HOUR', 5)),
                max_deployments_per_day=int(os.environ.get('DEPLOYMENT_MAX_PER_DAY', 20))
            )
            return DeploymentScheduler(schedule_rules)
        except ImportError as e:
            logger.warning(f"DeploymentScheduler not available: {e}")
            return None
    
    def create_optimizer(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create DeploymentOptimizer instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_optimizer import DeploymentOptimizer
            return DeploymentOptimizer(component_config.config or self._get_config_dict())
        except ImportError as e:
            logger.warning(f"DeploymentOptimizer not available: {e}")
            return None
    
    def create_circuit_breaker(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create CircuitBreaker instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_circuit_breaker import CircuitBreaker, CircuitBreakerConfig
            circuit_config = CircuitBreakerConfig(
                failure_threshold=int(os.environ.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5)),
                success_threshold=int(os.environ.get('CIRCUIT_BREAKER_SUCCESS_THRESHOLD', 2)),
                timeout_seconds=int(os.environ.get('CIRCUIT_BREAKER_TIMEOUT', 60))
            )
            return CircuitBreaker(circuit_config)
        except ImportError as e:
            logger.warning(f"CircuitBreaker not available: {e}")
            return None
    
    def create_tracer(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create DeploymentTracer instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_tracing import DeploymentTracer
            return DeploymentTracer()
        except ImportError as e:
            logger.warning(f"DeploymentTracer not available: {e}")
            return None
    
    def create_performance_monitor(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create DeploymentPerformanceMonitor instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_performance import DeploymentPerformanceMonitor
            monitor = DeploymentPerformanceMonitor()
            monitor.take_snapshot()  # Initial snapshot
            return monitor
        except ImportError as e:
            logger.warning(f"DeploymentPerformanceMonitor not available: {e}")
            return None
    
    def create_rollback_manager(
        self,
        component_config: ComponentConfig,
        backup_manager: Optional[Any] = None,
        health_checker: Optional[Any] = None
    ) -> Optional[Any]:
        """Create AutomaticRollbackManager instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_rollback_auto import AutomaticRollbackManager, RollbackPolicy
            rollback_policy = RollbackPolicy(
                enabled=os.environ.get('AUTO_ROLLBACK_ENABLED', 'true').lower() == 'true',
                auto_rollback_on_failure=os.environ.get('AUTO_ROLLBACK_ON_FAILURE', 'true').lower() == 'true'
            )
            return AutomaticRollbackManager(rollback_policy, backup_manager, health_checker)
        except ImportError as e:
            logger.warning(f"AutomaticRollbackManager not available: {e}")
            return None
    
    def create_feature_flags(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create FeatureFlagsManager instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_feature_flags import FeatureFlagsManager
            return FeatureFlagsManager()
        except ImportError as e:
            logger.warning(f"FeatureFlagsManager not available: {e}")
            return None
    
    def create_security_scanner(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create SecurityScanner instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_security_scanner import SecurityScanner
            return SecurityScanner(self.project_dir)
        except ImportError as e:
            logger.warning(f"SecurityScanner not available: {e}")
            return None
    
    def create_cost_optimizer(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create CostOptimizer instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_cost_optimizer import CostOptimizer
            return CostOptimizer(self.project_dir)
        except ImportError as e:
            logger.warning(f"CostOptimizer not available: {e}")
            return None
    
    def create_compliance_checker(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create ComplianceChecker instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_compliance import ComplianceChecker
            return ComplianceChecker(self.project_dir)
        except ImportError as e:
            logger.warning(f"ComplianceChecker not available: {e}")
            return None
    
    def create_approval_workflow(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create ApprovalWorkflow instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_approval import ApprovalWorkflow
            return ApprovalWorkflow()
        except ImportError as e:
            logger.warning(f"ApprovalWorkflow not available: {e}")
            return None
    
    def create_deployment_strategy(
        self,
        strategy_type: str,
        component_config: ComponentConfig
    ) -> Optional[Any]:
        """Create DeploymentStrategy instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_strategy import DeploymentStrategyFactory
            config_dict = component_config.config or self._get_config_dict()
            return DeploymentStrategyFactory.create(strategy_type, config_dict)
        except ImportError as e:
            logger.warning(f"DeploymentStrategyFactory not available: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create deployment strategy: {e}")
            return None
    
    def create_autoscaling_manager(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create AutoScalingManager instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_autoscaling import AutoScalingManager
            return AutoScalingManager()
        except ImportError as e:
            logger.warning(f"AutoScalingManager not available: {e}")
            return None
    
    def create_dependency_manager(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create DependencyManager instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_dependency_manager import DependencyManager
            return DependencyManager(self.project_dir)
        except ImportError as e:
            logger.warning(f"DependencyManager not available: {e}")
            return None
    
    def create_blueprint_manager(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create BlueprintManager instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_blueprint import BlueprintManager
            return BlueprintManager()
        except ImportError as e:
            logger.warning(f"BlueprintManager not available: {e}")
            return None
    
    def create_event_stream(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create EventStream instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_events import EventStream
            return EventStream()
        except ImportError as e:
            logger.warning(f"EventStream not available: {e}")
            return None
    
    def create_benchmark(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create DeploymentBenchmark instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_benchmark import DeploymentBenchmark
            return DeploymentBenchmark()
        except ImportError as e:
            logger.warning(f"DeploymentBenchmark not available: {e}")
            return None
    
    def create_resource_tagger(self, component_config: ComponentConfig) -> Optional[Any]:
        """Create ResourceTagger instance"""
        if not component_config.enabled:
            return None
        
        try:
            from deployment_resource_tagger import ResourceTagger
            return ResourceTagger()
        except ImportError as e:
            logger.warning(f"ResourceTagger not available: {e}")
            return None
    
    def _parse_hours(self, hours_str: str) -> Optional[list]:
        """Parse allowed hours from string"""
        if not hours_str:
            return None
        
        hours = []
        for part in hours_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                hours.extend(range(start, end + 1))
            else:
                hours.append(int(part))
        
        return sorted(set(hours)) if hours else None
