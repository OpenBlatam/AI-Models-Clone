#!/usr/bin/env python3
"""
Health Checker Service
Performs comprehensive health checks on the deployment
"""

import os
import sys
import time
import logging
import subprocess
import requests
from typing import Dict, Any, List, Tuple
from pathlib import Path


logger = logging.getLogger(__name__)


class HealthChecker:
    """Performs health checks on various system components"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.health_check_url = config.get('health_check_url', 'http://localhost:8000/health')
        self.timeout = config.get('health_check_timeout', 60)
    
    def check_docker(self) -> Tuple[bool, str]:
        """Check if Docker is running"""
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, "Docker is running"
            else:
                return False, f"Docker check failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Docker check timed out"
        except FileNotFoundError:
            return False, "Docker command not found"
        except Exception as e:
            return False, f"Docker check error: {str(e)}"
    
    def check_containers(self) -> Tuple[bool, str]:
        """Check if application containers are running"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                containers = [c.strip() for c in result.stdout.split('\n') if c.strip()]
                app_containers = [c for c in containers if 'blatam-academy' in c.lower()]
                if app_containers:
                    return True, f"Found {len(app_containers)} application container(s)"
                else:
                    return False, "No application containers found"
            else:
                return False, f"Failed to list containers: {result.stderr}"
        except Exception as e:
            return False, f"Container check error: {str(e)}"
    
    def check_application_health(self) -> Tuple[bool, str]:
        """Check application health endpoint"""
        try:
            response = requests.get(
                self.health_check_url,
                timeout=10
            )
            if response.status_code == 200:
                return True, "Application health check passed"
            else:
                return False, f"Application returned status {response.status_code}"
        except requests.exceptions.Timeout:
            return False, "Application health check timed out"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to application"
        except Exception as e:
            return False, f"Application health check error: {str(e)}"
    
    def check_disk_space(self, threshold: int = 10) -> Tuple[bool, str]:
        """Check available disk space (percentage)"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            free_percent = (free / total) * 100
            
            if free_percent >= threshold:
                return True, f"Disk space: {free_percent:.1f}% free"
            else:
                return False, f"Low disk space: {free_percent:.1f}% free (threshold: {threshold}%)"
        except Exception as e:
            return False, f"Disk space check error: {str(e)}"
    
    def check_memory(self, threshold: int = 10) -> Tuple[bool, str]:
        """Check available memory (percentage)"""
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = {}
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        meminfo[parts[0].rstrip(':')] = int(parts[1])
                
                total = meminfo.get('MemTotal', 0)
                available = meminfo.get('MemAvailable', meminfo.get('MemFree', 0))
                
                if total > 0:
                    free_percent = (available / total) * 100
                    if free_percent >= threshold:
                        return True, f"Memory: {free_percent:.1f}% available"
                    else:
                        return False, f"Low memory: {free_percent:.1f}% available (threshold: {threshold}%)"
                else:
                    return False, "Cannot determine memory usage"
        except Exception as e:
            return False, f"Memory check error: {str(e)}"
    
    def check_project_directory(self) -> Tuple[bool, str]:
        """Check if project directory exists and is accessible"""
        project_dir = self.config.get('project_dir', '/opt/blatam-academy')
        path = Path(project_dir)
        
        if not path.exists():
            return False, f"Project directory does not exist: {project_dir}"
        
        if not path.is_dir():
            return False, f"Project path is not a directory: {project_dir}"
        
        if not os.access(project_dir, os.R_OK):
            return False, f"Project directory is not readable: {project_dir}"
        
        return True, f"Project directory accessible: {project_dir}"
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        checks = {
            'docker': self.check_docker(),
            'containers': self.check_containers(),
            'application': self.check_application_health(),
            'disk_space': self.check_disk_space(),
            'memory': self.check_memory(),
            'project_directory': self.check_project_directory()
        }
        
        all_passed = all(result[0] for result in checks.values())
        
        return {
            'status': 'healthy' if all_passed else 'unhealthy',
            'timestamp': time.time(),
            'checks': {
                name: {
                    'status': 'pass' if result[0] else 'fail',
                    'message': result[1]
                }
                for name, result in checks.items()
            },
            'summary': {
                'total': len(checks),
                'passed': sum(1 for r in checks.values() if r[0]),
                'failed': sum(1 for r in checks.values() if not r[0])
            }
        }


def main():
    """Main function for CLI usage"""
    import json
    
    config = {
        'health_check_url': os.environ.get('HEALTH_CHECK_URL', 'http://localhost:8000/health'),
        'health_check_timeout': int(os.environ.get('HEALTH_CHECK_TIMEOUT', 60)),
        'project_dir': os.environ.get('PROJECT_DIR', '/opt/blatam-academy')
    }
    
    checker = HealthChecker(config)
    results = checker.run_all_checks()
    
    print(json.dumps(results, indent=2))
    
    # Exit with error code if unhealthy
    if results['status'] != 'healthy':
        sys.exit(1)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    main()
