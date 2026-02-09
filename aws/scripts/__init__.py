"""
AWS Deployment Scripts Package
Comprehensive deployment automation system for EC2
"""

__version__ = "1.0.0"
__author__ = "Blatam Academy"

# Core modules
from .config import DeploymentConfig
from .utils import run_command, check_git_updates, get_git_commit_hash

# Deployment modules
from .deployment_strategy import (
    DeploymentStrategy,
    DeploymentStrategyFactory,
    StandardDeploymentStrategy,
    BlueGreenDeploymentStrategy,
    RollingDeploymentStrategy,
    CanaryDeploymentStrategy
)

from .deployment_validator import DeploymentValidator, ValidationResult
from .deployment_cache import DeploymentCache
from .deployment_monitor import DeploymentMonitor
from .deployment_metrics import DeploymentMetrics
from .deployment_notifier import DeploymentNotifier
from .deployment_retry import RetryHandler, RetryConfig, RetryStrategy
from .deployment_queue import DeploymentQueue, DeploymentRequest
from .deployment_scheduler import DeploymentScheduler, ScheduleRule
from .deployment_optimizer import DeploymentOptimizer
from .health_checker import HealthChecker
from .backup_manager import BackupManager
from .webhook_listener import WebhookHandler, SecurityManager, DeploymentManager

__all__ = [
    # Core
    'DeploymentConfig',
    'run_command',
    'check_git_updates',
    'get_git_commit_hash',
    
    # Strategies
    'DeploymentStrategy',
    'DeploymentStrategyFactory',
    'StandardDeploymentStrategy',
    'BlueGreenDeploymentStrategy',
    'RollingDeploymentStrategy',
    'CanaryDeploymentStrategy',
    
    # Services
    'DeploymentValidator',
    'ValidationResult',
    'DeploymentCache',
    'DeploymentMonitor',
    'DeploymentMetrics',
    'DeploymentNotifier',
    'DeploymentQueue',
    'DeploymentRequest',
    'DeploymentScheduler',
    'ScheduleRule',
    'DeploymentOptimizer',
    'HealthChecker',
    'BackupManager',
    
    # Retry
    'RetryHandler',
    'RetryConfig',
    'RetryStrategy',
    
    # Circuit Breaker
    'CircuitBreaker',
    'CircuitBreakerConfig',
    'CircuitState',
    
    # Tracing
    'DeploymentTracer',
    'TraceSpan',
    
    # Performance
    'DeploymentPerformanceMonitor',
    'PerformanceSnapshot',
    
    # Rollback
    'AutomaticRollbackManager',
    'RollbackPolicy',
    
    # Feature Flags
    'FeatureFlagsManager',
    'FeatureFlag',
    'FeatureFlagType',
    
    # Security
    'SecurityScanner',
    'SecurityIssue',
    
    # Cost Optimization
    'CostOptimizer',
    'CostRecommendation',
    
    # Chaos Engineering
    'ChaosEngineer',
    'ChaosExperiment',
    'ChaosExperimentType',
    
    # Compliance
    'ComplianceChecker',
    'ComplianceStandard',
    'ComplianceCheck',
    
    # Approval
    'ApprovalWorkflow',
    'ApprovalRequest',
    'ApprovalStatus',
    
    # Webhook
    'WebhookHandler',
    'SecurityManager',
    'DeploymentManager',
    
    # Factory & Orchestrator
    'DeploymentComponentFactory',
    'ComponentConfig',
    'DeploymentOrchestrator',
    
    # Constants
    'DeploymentStatus',
    'DeploymentStrategyType',
    'HealthCheckStatus',
    'NotificationChannel',
    
    # Exceptions
    'DeploymentError',
    'DeploymentValidationError',
    'DeploymentSecurityError',
    'DeploymentComplianceError',
    'DeploymentApprovalError',
    'DeploymentTimeoutError',
    'DeploymentRollbackError',
    'DeploymentStrategyError',
    'DeploymentHealthCheckError',
    'DeploymentConfigurationError',
]
