#!/usr/bin/env python3
"""
Deployment Constants
Centralized constants for deployment system
"""

from enum import Enum
from pathlib import Path


class DeploymentStatus(Enum):
    """Deployment status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class DeploymentStrategyType(Enum):
    """Deployment strategy types"""
    STANDARD = "standard"
    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    CANARY = "canary"


class HealthCheckStatus(Enum):
    """Health check status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    UNKNOWN = "unknown"


class NotificationChannel(Enum):
    """Notification channels"""
    SLACK = "slack"
    DISCORD = "discord"
    WEBHOOK = "webhook"
    EMAIL = "email"


# Default paths
DEFAULT_PROJECT_DIR = Path('/opt/blatam-academy')
DEFAULT_LOG_DIR = Path('/var/log')
DEFAULT_DATA_DIR = Path('/var/lib')
DEFAULT_CACHE_DIR = Path('/var/cache')

# Log files
LOG_WEBHOOK = DEFAULT_LOG_DIR / 'github-webhook.log'
LOG_DEPLOYMENT = DEFAULT_LOG_DIR / 'blatam-academy-deploy.log'
LOG_DEPLOYMENT_CHECK = DEFAULT_LOG_DIR / 'deployment-check.log'
LOG_INTEGRATED_DEPLOYMENT = DEFAULT_LOG_DIR / 'integrated-deployment.log'

# Data directories
DATA_DEPLOYMENT_MONITOR = DEFAULT_DATA_DIR / 'deployment-monitor'
DATA_DEPLOYMENT_METRICS = DEFAULT_DATA_DIR / 'deployment-metrics'
DATA_DEPLOYMENT_QUEUE = DEFAULT_DATA_DIR / 'deployment-queue'
DATA_DEPLOYMENT_TRACING = DEFAULT_DATA_DIR / 'deployment-tracing'
DATA_DEPLOYMENT_PERFORMANCE = DEFAULT_DATA_DIR / 'deployment-performance'
DATA_DEPLOYMENT_ROLLBACK = DEFAULT_DATA_DIR / 'deployment-rollback'
DATA_FEATURE_FLAGS = DEFAULT_DATA_DIR / 'feature-flags'
DATA_DISASTER_RECOVERY = DEFAULT_DATA_DIR / 'disaster-recovery'
DATA_DEPLOYMENT_APPROVALS = DEFAULT_DATA_DIR / 'deployment-approvals'
DATA_BACKUPS = DEFAULT_DATA_DIR / 'deployment-backups'

# Cache directories
CACHE_DEPLOYMENT = DEFAULT_CACHE_DIR / 'deployment'

# Default ports
PORT_WEBHOOK = 9000
PORT_DEPLOYMENT_MONITOR = 9001
PORT_DEPLOYMENT_API = 9002

# Default timeouts (seconds)
TIMEOUT_DEPLOYMENT = 1800  # 30 minutes
TIMEOUT_HEALTH_CHECK = 60  # 1 minute
TIMEOUT_COMMAND = 300  # 5 minutes

# Default retry configuration
RETRY_MAX_ATTEMPTS = 3
RETRY_INITIAL_DELAY = 5.0
RETRY_MAX_DELAY = 60.0

# Default circuit breaker configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
CIRCUIT_BREAKER_SUCCESS_THRESHOLD = 2
CIRCUIT_BREAKER_TIMEOUT = 60

# Default scheduling
SCHEDULING_MAX_PER_HOUR = 5
SCHEDULING_MAX_PER_DAY = 20

# Default backup retention
BACKUP_RETENTION_DAYS = 30
BACKUP_MAX_COUNT = 100

# Default compliance
COMPLIANCE_MIN_SCORE = 80.0

# Default approval
APPROVAL_EXPIRES_HOURS = 24
