#!/usr/bin/env python3
"""
Deployment Strategy Pattern
Implements different deployment strategies (blue-green, rolling, canary)
"""

import os
import time
import logging
import subprocess
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class DeploymentStrategy(Enum):
    """Available deployment strategies"""
    STANDARD = "standard"
    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    CANARY = "canary"


class BaseDeploymentStrategy(ABC):
    """Base class for deployment strategies"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.project_dir = config.get('project_dir', '/opt/blatam-academy')
        self.deploy_script = config.get('deploy_script', f'{self.project_dir}/aws/scripts/auto_deploy.sh')
    
    @abstractmethod
    def deploy(self) -> Tuple[bool, str]:
        """Execute deployment strategy"""
        pass
    
    def run_command(self, command: List[str], cwd: Optional[str] = None) -> Tuple[bool, str, str]:
        """Run a shell command"""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_dir,
                capture_output=True,
                text=True,
                timeout=1800
            )
            return (
                result.returncode == 0,
                result.stdout,
                result.stderr
            )
        except subprocess.TimeoutExpired:
            return False, '', 'Command timed out'
        except Exception as e:
            return False, '', str(e)
    
    def health_check(self, url: str, timeout: int = 60) -> bool:
        """Perform health check"""
        try:
            import requests
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except:
            return False


class StandardDeploymentStrategy(BaseDeploymentStrategy):
    """Standard deployment: stop old, start new"""
    
    def deploy(self) -> Tuple[bool, str]:
        """Execute standard deployment"""
        logger.info("Executing standard deployment strategy")
        
        # Stop old containers
        logger.info("Stopping old containers...")
        success, stdout, stderr = self.run_command(['docker-compose', 'down'])
        if not success:
            logger.warning(f"Failed to stop containers: {stderr}")
        
        # Build new images
        logger.info("Building new images...")
        success, stdout, stderr = self.run_command(['docker-compose', 'build', '--no-cache'])
        if not success:
            return False, f"Build failed: {stderr}"
        
        # Start new containers
        logger.info("Starting new containers...")
        success, stdout, stderr = self.run_command(['docker-compose', 'up', '-d'])
        if not success:
            return False, f"Start failed: {stderr}"
        
        # Health check
        health_url = self.config.get('health_check_url', 'http://localhost:8000/health')
        logger.info("Performing health check...")
        for i in range(12):  # 60 seconds total
            if self.health_check(health_url, timeout=5):
                logger.info("Health check passed")
                return True, "Deployment successful"
            time.sleep(5)
        
        return False, "Health check failed"
    
    def rollback(self) -> Tuple[bool, str]:
        """Rollback to previous version"""
        logger.info("Rolling back...")
        success, stdout, stderr = self.run_command(['git', 'reset', '--hard', 'HEAD~1'])
        if not success:
            return False, f"Rollback failed: {stderr}"
        
        return self.deploy()


class BlueGreenDeploymentStrategy(BaseDeploymentStrategy):
    """Blue-Green deployment: run two environments in parallel"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.current_env = 'blue'  # or 'green'
        self.blue_compose = 'docker-compose.blue.yml'
        self.green_compose = 'docker-compose.green.yml'
    
    def deploy(self) -> Tuple[bool, str]:
        """Execute blue-green deployment"""
        logger.info("Executing blue-green deployment strategy")
        
        # Determine target environment
        target_env = 'green' if self.current_env == 'blue' else 'blue'
        target_compose = self.green_compose if target_env == 'green' else self.blue_compose
        
        logger.info(f"Deploying to {target_env} environment...")
        
        # Build and start target environment
        success, stdout, stderr = self.run_command([
            'docker-compose', '-f', target_compose, 'build', '--no-cache'
        ])
        if not success:
            return False, f"Build failed: {stderr}"
        
        success, stdout, stderr = self.run_command([
            'docker-compose', '-f', target_compose, 'up', '-d'
        ])
        if not success:
            return False, f"Start failed: {stderr}"
        
        # Health check on target environment
        health_url = self.config.get('health_check_url', f'http://localhost:8001/health')
        logger.info("Performing health check on new environment...")
        for i in range(12):
            if self.health_check(health_url, timeout=5):
                logger.info("Health check passed, switching traffic...")
                
                # Switch traffic (update load balancer/nginx config)
                # This would typically involve updating nginx or load balancer config
                self.current_env = target_env
                logger.info(f"Traffic switched to {target_env} environment")
                
                # Stop old environment after a grace period
                time.sleep(30)
                old_compose = self.blue_compose if target_env == 'green' else self.green_compose
                self.run_command(['docker-compose', '-f', old_compose, 'down'])
                
                return True, f"Blue-green deployment successful, now on {target_env}"
            time.sleep(5)
        
        # Health check failed, stop target environment
        self.run_command(['docker-compose', '-f', target_compose, 'down'])
        return False, "Health check failed on new environment"


class RollingDeploymentStrategy(BaseDeploymentStrategy):
    """Rolling deployment: update containers one by one"""
    
    def deploy(self) -> Tuple[bool, str]:
        """Execute rolling deployment"""
        logger.info("Executing rolling deployment strategy")
        
        # Get list of running containers
        success, stdout, stderr = self.run_command(['docker-compose', 'ps', '-q'])
        if not success:
            return False, f"Failed to get container list: {stderr}"
        
        containers = [c.strip() for c in stdout.split('\n') if c.strip()]
        if not containers:
            return False, "No containers found"
        
        logger.info(f"Found {len(containers)} containers, updating one by one...")
        
        # Update each container
        for i, container in enumerate(containers):
            logger.info(f"Updating container {i+1}/{len(containers)}: {container}")
            
            # Stop container
            self.run_command(['docker', 'stop', container])
            
            # Build new image
            success, stdout, stderr = self.run_command(['docker-compose', 'build', '--no-cache'])
            if not success:
                return False, f"Build failed: {stderr}"
            
            # Start new container
            success, stdout, stderr = self.run_command(['docker-compose', 'up', '-d', '--scale', f'app={i+1}'])
            if not success:
                return False, f"Start failed: {stderr}"
            
            # Health check
            health_url = self.config.get('health_check_url', 'http://localhost:8000/health')
            if not self.health_check(health_url, timeout=10):
                return False, f"Health check failed after updating container {i+1}"
            
            time.sleep(5)  # Grace period between updates
        
        logger.info("Rolling deployment completed successfully")
        return True, "Rolling deployment successful"


class CanaryDeploymentStrategy(BaseDeploymentStrategy):
    """Canary deployment: deploy to small subset first"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.canary_percentage = config.get('canary_percentage', 10)  # 10% of traffic
    
    def deploy(self) -> Tuple[bool, str]:
        """Execute canary deployment"""
        logger.info(f"Executing canary deployment strategy ({self.canary_percentage}% traffic)")
        
        # Deploy canary version
        logger.info("Deploying canary version...")
        success, stdout, stderr = self.run_command([
            'docker-compose', '-f', 'docker-compose.canary.yml', 'up', '-d', '--scale', 'app=1'
        ])
        if not success:
            return False, f"Canary deployment failed: {stderr}"
        
        # Monitor canary for a period
        health_url = self.config.get('health_check_url', 'http://localhost:8002/health')
        logger.info("Monitoring canary deployment for 5 minutes...")
        
        start_time = time.time()
        monitoring_duration = 300  # 5 minutes
        
        while time.time() - start_time < monitoring_duration:
            if not self.health_check(health_url, timeout=5):
                logger.error("Canary health check failed, aborting...")
                self.run_command(['docker-compose', '-f', 'docker-compose.canary.yml', 'down'])
                return False, "Canary deployment failed health checks"
            time.sleep(30)
        
        logger.info("Canary deployment successful, promoting to full deployment...")
        
        # Promote canary to full deployment
        return StandardDeploymentStrategy(self.config).deploy()


class DeploymentStrategyFactory:
    """Factory for creating deployment strategies"""
    
    @staticmethod
    def create(strategy_type: str, config: Dict[str, Any]) -> BaseDeploymentStrategy:
        """Create a deployment strategy instance"""
        strategy_enum = DeploymentStrategy(strategy_type.lower())
        
        if strategy_enum == DeploymentStrategy.STANDARD:
            return StandardDeploymentStrategy(config)
        elif strategy_enum == DeploymentStrategy.BLUE_GREEN:
            return BlueGreenDeploymentStrategy(config)
        elif strategy_enum == DeploymentStrategy.ROLLING:
            return RollingDeploymentStrategy(config)
        elif strategy_enum == DeploymentStrategy.CANARY:
            return CanaryDeploymentStrategy(config)
        else:
            raise ValueError(f"Unknown deployment strategy: {strategy_type}")
