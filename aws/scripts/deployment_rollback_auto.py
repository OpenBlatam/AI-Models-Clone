#!/usr/bin/env python3
"""
Automatic Rollback Manager
Automatically rolls back failed deployments
"""

import logging
import subprocess
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json


logger = logging.getLogger(__name__)


@dataclass
class RollbackPolicy:
    """Rollback policy configuration"""
    enabled: bool = True
    auto_rollback_on_failure: bool = True
    health_check_failures_threshold: int = 3
    health_check_interval: int = 30  # seconds
    max_rollback_attempts: int = 3
    rollback_timeout: int = 600  # seconds


class AutomaticRollbackManager:
    """Manages automatic rollbacks"""
    
    def __init__(self, config: RollbackPolicy, backup_manager=None, health_checker=None):
        self.config = config
        self.backup_manager = backup_manager
        self.health_checker = health_checker
        self.rollback_history: List[Dict[str, Any]] = []
        self.history_file = Path('/var/lib/deployment-rollback/history.json')
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_history()
    
    def _load_history(self):
        """Load rollback history"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.rollback_history = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load rollback history: {e}")
                self.rollback_history = []
    
    def _save_history(self):
        """Save rollback history"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.rollback_history[-100:], f, indent=2)  # Keep last 100
        except Exception as e:
            logger.error(f"Failed to save rollback history: {e}")
    
    def should_rollback(self, deployment_result: Dict[str, Any]) -> bool:
        """Determine if rollback should be triggered"""
        if not self.config.enabled or not self.config.auto_rollback_on_failure:
            return False
        
        # Check if deployment failed
        if not deployment_result.get('success', False):
            logger.info("Deployment failed - triggering automatic rollback")
            return True
        
        # Check health after deployment
        if self.health_checker:
            health_failures = 0
            for _ in range(self.config.health_check_failures_threshold):
                results = self.health_checker.run_all_checks()
                if not self._is_healthy(results):
                    health_failures += 1
                else:
                    break  # Health check passed
        
            if health_failures >= self.config.health_check_failures_threshold:
                logger.warning(f"Health checks failed {health_failures} times - triggering rollback")
                return True
        
        return False
    
    def _is_healthy(self, health_results: Dict[str, Any]) -> bool:
        """Check if system is healthy"""
        critical_checks = ['docker', 'application', 'project_directory']
        for check_name in critical_checks:
            if check_name in health_results.get('checks', {}):
                check_result = health_results['checks'][check_name]
                if check_result.get('status') != 'pass':
                    return False
        return True
    
    def execute_rollback(self, deployment_id: str, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Execute rollback"""
        logger.info(f"Executing automatic rollback for deployment {deployment_id}")
        
        rollback_result = {
            'deployment_id': deployment_id,
            'timestamp': datetime.now().isoformat(),
            'backup_name': backup_name,
            'success': False,
            'method': None,
            'error': None
        }
        
        # Method 1: Restore from backup
        if backup_name and self.backup_manager:
            try:
                logger.info(f"Restoring from backup: {backup_name}")
                success = self.backup_manager.restore_backup(backup_name)
                if success:
                    rollback_result['success'] = True
                    rollback_result['method'] = 'backup_restore'
                    logger.info("Rollback successful via backup restore")
                    self.rollback_history.append(rollback_result)
                    self._save_history()
                    return rollback_result
            except Exception as e:
                logger.error(f"Backup restore failed: {e}")
                rollback_result['error'] = str(e)
        
        # Method 2: Docker rollback (stop new, start old)
        try:
            logger.info("Attempting Docker rollback")
            success = self._docker_rollback()
            if success:
                rollback_result['success'] = True
                rollback_result['method'] = 'docker_rollback'
                logger.info("Rollback successful via Docker")
                self.rollback_history.append(rollback_result)
                self._save_history()
                return rollback_result
        except Exception as e:
            logger.error(f"Docker rollback failed: {e}")
            rollback_result['error'] = str(e)
        
        # Method 3: Git rollback
        try:
            logger.info("Attempting Git rollback")
            success = self._git_rollback()
            if success:
                rollback_result['success'] = True
                rollback_result['method'] = 'git_rollback'
                logger.info("Rollback successful via Git")
                self.rollback_history.append(rollback_result)
                self._save_history()
                return rollback_result
        except Exception as e:
            logger.error(f"Git rollback failed: {e}")
            rollback_result['error'] = str(e)
        
        logger.error("All rollback methods failed")
        rollback_result['success'] = False
        self.rollback_history.append(rollback_result)
        self._save_history()
        return rollback_result
    
    def _docker_rollback(self) -> bool:
        """Rollback using Docker"""
        try:
            # Stop current containers
            subprocess.run(['docker-compose', 'down'], check=True, timeout=60)
            # Start previous version (if available)
            subprocess.run(['docker-compose', 'up', '-d'], check=True, timeout=120)
            return True
        except Exception as e:
            logger.error(f"Docker rollback error: {e}")
            return False
    
    def _git_rollback(self) -> bool:
        """Rollback using Git"""
        try:
            # Get previous commit
            result = subprocess.run(
                ['git', 'log', '--oneline', '-2'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                if len(commits) > 1:
                    prev_commit = commits[1].split()[0]
                    subprocess.run(['git', 'reset', '--hard', prev_commit], check=True, timeout=10)
                    return True
        except Exception as e:
            logger.error(f"Git rollback error: {e}")
        return False
    
    def get_rollback_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get rollback history"""
        return self.rollback_history[-limit:]
