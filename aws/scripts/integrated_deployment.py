#!/usr/bin/env python3
"""
Integrated Deployment System
Orchestrates deployment with monitoring, health checks, and notifications
Refactored with factory pattern and separated concerns
"""

import os
import sys
import logging
from typing import Optional, Tuple
from pathlib import Path

# Import core modules
try:
    from config import DeploymentConfig
    from utils import check_git_updates
    from deployment_factory import DeploymentComponentFactory, ComponentConfig
    from deployment_orchestrator import DeploymentOrchestrator
    from deployment_exceptions import DeploymentError
except ImportError as e:
    print(f"Warning: Could not import core modules: {e}", file=sys.stderr)
    DeploymentConfig = None
    DeploymentComponentFactory = None
    ComponentConfig = None
    DeploymentOrchestrator = None
    DeploymentError = None
    check_git_updates = None


logger = logging.getLogger(__name__)


class IntegratedDeployment:
    """Orchestrates complete deployment process"""
    
    def __init__(self, config: any):
        self.config = config
        self.strategy_type = os.environ.get('DEPLOYMENT_STRATEGY', 'standard')
        setattr(config, 'strategy_type', self.strategy_type)
        
        # Initialize component factory
        if DeploymentComponentFactory:
            self.factory = DeploymentComponentFactory(config)
            self.components = self._initialize_components()
        else:
            self.factory = None
            self.components = {}
        
        # Initialize orchestrator
        if DeploymentOrchestrator:
            self.orchestrator = DeploymentOrchestrator(self.components, config)
        else:
            self.orchestrator = None
    
    def _initialize_components(self) -> dict:
        """Initialize all deployment components using factory"""
        components = {}
        
        # Get base config dict
        config_dict = self.factory._get_config_dict()
        
        # Core components
        components['health_checker'] = self.factory.create_health_checker(
            ComponentConfig(enabled=True, config=config_dict)
        )
        
        components['notifier'] = self.factory.create_notifier(
            ComponentConfig(enabled=True)
        )
        
        components['monitor'] = self.factory.create_monitor(
            ComponentConfig(enabled=True)
        )
        
        components['validator'] = self.factory.create_validator(
            ComponentConfig(enabled=True, config=config_dict)
        )
        
        components['cache'] = self.factory.create_cache(
            ComponentConfig(enabled=True)
        )
        
        components['metrics'] = self.factory.create_metrics(
            ComponentConfig(enabled=True)
        )
        
        components['backup_manager'] = self.factory.create_backup_manager(
            ComponentConfig(enabled=True)
        )
        
        # Advanced components
        components['retry_handler'] = self.factory.create_retry_handler(
            ComponentConfig(enabled=True)
        )
        
        components['deployment_queue'] = self.factory.create_queue(
            ComponentConfig(enabled=True)
        )
        
        components['scheduler'] = self.factory.create_scheduler(
            ComponentConfig(enabled=True)
        )
        
        components['optimizer'] = self.factory.create_optimizer(
            ComponentConfig(enabled=True, config=config_dict)
        )
        
        components['circuit_breaker'] = self.factory.create_circuit_breaker(
            ComponentConfig(enabled=True)
        )
        
        components['tracer'] = self.factory.create_tracer(
            ComponentConfig(enabled=True)
        )
        
        components['performance_monitor'] = self.factory.create_performance_monitor(
            ComponentConfig(enabled=True)
        )
        
        components['rollback_manager'] = self.factory.create_rollback_manager(
            ComponentConfig(enabled=True),
            backup_manager=components.get('backup_manager'),
            health_checker=components.get('health_checker')
        )
        
        # Enterprise components
        components['feature_flags'] = self.factory.create_feature_flags(
            ComponentConfig(enabled=True)
        )
        
        components['security_scanner'] = self.factory.create_security_scanner(
            ComponentConfig(enabled=True)
        )
        
        components['cost_optimizer'] = self.factory.create_cost_optimizer(
            ComponentConfig(enabled=True)
        )
        
        components['compliance_checker'] = self.factory.create_compliance_checker(
            ComponentConfig(enabled=True)
        )
        
        components['approval_workflow'] = self.factory.create_approval_workflow(
            ComponentConfig(enabled=True)
        )
        
        # Deployment strategy
        components['strategy'] = self.factory.create_deployment_strategy(
            self.strategy_type,
            ComponentConfig(enabled=True, config=config_dict)
        )
        
        return components
    
    def get_current_commit(self) -> Optional[str]:
        """Get current commit hash"""
        from utils import get_git_commit_hash
        if get_git_commit_hash and self.config:
            return get_git_commit_hash(self.config.project_dir)
        return None
    
    def check_for_updates(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """Check if there are updates available"""
        if check_git_updates and self.config:
            return check_git_updates(self.config.project_dir, self.config.github_branch)
        return False, None, None
    
    def deploy(self) -> Tuple[bool, str]:
        """Execute deployment using orchestrator"""
        if self.orchestrator:
            return self.orchestrator.deploy()
        else:
            logger.error("DeploymentOrchestrator not available")
            return False, "Orchestrator not initialized"
    
    def run(self) -> int:
        """Run complete deployment process"""
        try:
            success, message = self.deploy()
            
            if success:
                logger.info("Deployment completed successfully")
                return 0
            else:
                logger.error(f"Deployment failed: {message}")
                return 1
                
        except DeploymentError as e:
            logger.error(f"Deployment error: {e}")
            return 1
        except Exception as e:
            logger.error(f"Unexpected deployment error: {e}", exc_info=True)
            return 1


def main():
    """Main function"""
    # Setup logging
    log_file = os.environ.get('LOG_FILE', '/var/log/integrated-deployment.log')
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Initialize configuration
    if DeploymentConfig:
        try:
            config = DeploymentConfig.from_env()
            errors = config.validate()
            if errors:
                logger.error("Configuration errors:")
                for error in errors:
                    logger.error(f"  - {error}")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
    else:
        # Fallback
        from dataclasses import dataclass
        
        @dataclass
        class FallbackConfig:
            deploy_script: str = os.environ.get('DEPLOY_SCRIPT', '/opt/blatam-academy/aws/scripts/auto_deploy.sh')
            project_dir: str = os.environ.get('PROJECT_DIR', '/opt/blatam-academy')
            github_branch: str = os.environ.get('GITHUB_BRANCH', 'main')
            project_name: str = os.environ.get('PROJECT_NAME', 'blatam-academy')
            deployment_timeout: int = int(os.environ.get('DEPLOYMENT_TIMEOUT', 1800))
            health_check_url: str = os.environ.get('HEALTH_CHECK_URL', 'http://localhost:8000/health')
            health_check_timeout: int = int(os.environ.get('HEALTH_CHECK_TIMEOUT', 60))
        
        config = FallbackConfig()
    
    # Run deployment
    deployment = IntegratedDeployment(config)
    sys.exit(deployment.run())


if __name__ == '__main__':
    main()
