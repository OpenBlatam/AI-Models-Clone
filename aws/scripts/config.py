#!/usr/bin/env python3
"""
Configuration module for AWS deployment scripts
Centralizes all configuration management
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    project_name: str
    project_dir: str
    github_repo: Optional[str]
    github_branch: str
    github_token: Optional[str]
    webhook_secret: Optional[str]
    webhook_port: int
    deploy_script: str
    log_file: str
    deployment_timeout: int
    health_check_url: str
    health_check_timeout: int
    
    @classmethod
    def from_env(cls) -> 'DeploymentConfig':
        """Create configuration from environment variables"""
        project_name = os.environ.get('PROJECT_NAME', 'blatam-academy')
        project_dir = os.environ.get('PROJECT_DIR', f'/opt/{project_name}')
        
        return cls(
            project_name=project_name,
            project_dir=project_dir,
            github_repo=os.environ.get('GITHUB_REPO'),
            github_branch=os.environ.get('GITHUB_BRANCH', 'main'),
            github_token=os.environ.get('GITHUB_TOKEN'),
            webhook_secret=os.environ.get('GITHUB_WEBHOOK_SECRET'),
            webhook_port=int(os.environ.get('WEBHOOK_PORT', 9000)),
            deploy_script=os.environ.get(
                'DEPLOY_SCRIPT',
                f'{project_dir}/aws/scripts/auto_deploy.sh'
            ),
            log_file=os.environ.get(
                'LOG_FILE',
                f'/var/log/{project_name}-deploy.log'
            ),
            deployment_timeout=int(os.environ.get('DEPLOYMENT_TIMEOUT', 1800)),
            health_check_url=os.environ.get('HEALTH_CHECK_URL', 'http://localhost:8000/health'),
            health_check_timeout=int(os.environ.get('HEALTH_CHECK_TIMEOUT', 60))
        )
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if not Path(self.project_dir).exists():
            errors.append(f"Project directory does not exist: {self.project_dir}")
        
        if not Path(self.deploy_script).exists():
            errors.append(f"Deploy script does not exist: {self.deploy_script}")
        
        if self.github_repo and not self.github_token:
            # Warning, not error - public repos don't need token
            pass
        
        return errors
    
    def is_webhook_secret_configured(self) -> bool:
        """Check if webhook secret is configured"""
        return bool(self.webhook_secret)
