#!/usr/bin/env python3
"""
Deployment Validator
Validates deployment configuration and environment before deployment
"""

import os
import sys
import logging
import subprocess
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation check"""
    passed: bool
    message: str
    severity: str  # 'error', 'warning', 'info'
    fix_suggestion: Optional[str] = None


class DeploymentValidator:
    """Validates deployment environment and configuration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.project_dir = Path(config.get('project_dir', '/opt/blatam-academy'))
        self.errors: List[ValidationResult] = []
        self.warnings: List[ValidationResult] = []
    
    def validate_all(self) -> Tuple[bool, List[ValidationResult]]:
        """Run all validations"""
        self.errors.clear()
        self.warnings.clear()
        
        # Run all validation checks
        self._validate_project_directory()
        self._validate_docker()
        self._validate_docker_compose()
        self._validate_disk_space()
        self._validate_memory()
        self._validate_network()
        self._validate_git_repository()
        self._validate_environment_variables()
        self._validate_permissions()
        
        all_results = self.errors + self.warnings
        return len(self.errors) == 0, all_results
    
    def _validate_project_directory(self) -> None:
        """Validate project directory exists and is accessible"""
        if not self.project_dir.exists():
            self.errors.append(ValidationResult(
                passed=False,
                message=f"Project directory does not exist: {self.project_dir}",
                severity='error',
                fix_suggestion=f"Create directory: mkdir -p {self.project_dir}"
            ))
            return
        
        if not self.project_dir.is_dir():
            self.errors.append(ValidationResult(
                passed=False,
                message=f"Project path is not a directory: {self.project_dir}",
                severity='error'
            ))
            return
        
        if not os.access(self.project_dir, os.R_OK):
            self.errors.append(ValidationResult(
                passed=False,
                message=f"Project directory is not readable: {self.project_dir}",
                severity='error',
                fix_suggestion=f"Fix permissions: chmod -R 755 {self.project_dir}"
            ))
        
        if not os.access(self.project_dir, os.W_OK):
            self.warnings.append(ValidationResult(
                passed=False,
                message=f"Project directory is not writable: {self.project_dir}",
                severity='warning',
                fix_suggestion=f"Fix permissions: chmod -R 755 {self.project_dir}"
            ))
    
    def _validate_docker(self) -> None:
        """Validate Docker installation and service"""
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                self.errors.append(ValidationResult(
                    passed=False,
                    message="Docker is not installed or not in PATH",
                    severity='error',
                    fix_suggestion="Install Docker: https://docs.docker.com/get-docker/"
                ))
                return
        except FileNotFoundError:
            self.errors.append(ValidationResult(
                passed=False,
                message="Docker command not found",
                severity='error',
                fix_suggestion="Install Docker: https://docs.docker.com/get-docker/"
            ))
            return
        except Exception as e:
            self.errors.append(ValidationResult(
                passed=False,
                message=f"Error checking Docker: {str(e)}",
                severity='error'
            ))
            return
        
        # Check if Docker daemon is running
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                self.errors.append(ValidationResult(
                    passed=False,
                    message="Docker daemon is not running",
                    severity='error',
                    fix_suggestion="Start Docker: sudo systemctl start docker"
                ))
        except Exception as e:
            self.errors.append(ValidationResult(
                passed=False,
                message=f"Error checking Docker daemon: {str(e)}",
                severity='error'
            ))
    
    def _validate_docker_compose(self) -> None:
        """Validate Docker Compose installation"""
        compose_commands = ['docker-compose', 'docker compose']
        found = False
        
        for cmd in compose_commands:
            try:
                result = subprocess.run(
                    cmd.split() + ['--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    found = True
                    break
            except:
                continue
        
        if not found:
            self.errors.append(ValidationResult(
                passed=False,
                message="Docker Compose is not installed",
                severity='error',
                fix_suggestion="Install Docker Compose: https://docs.docker.com/compose/install/"
            ))
    
    def _validate_disk_space(self, min_gb: int = 10) -> None:
        """Validate available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            free_gb = free / (1024 ** 3)
            
            if free_gb < min_gb:
                self.errors.append(ValidationResult(
                    passed=False,
                    message=f"Insufficient disk space: {free_gb:.1f}GB free (minimum: {min_gb}GB)",
                    severity='error',
                    fix_suggestion="Free up disk space or increase volume size"
                ))
            elif free_gb < min_gb * 2:
                self.warnings.append(ValidationResult(
                    passed=False,
                    message=f"Low disk space: {free_gb:.1f}GB free",
                    severity='warning',
                    fix_suggestion="Consider freeing up disk space"
                ))
        except Exception as e:
            self.warnings.append(ValidationResult(
                passed=False,
                message=f"Could not check disk space: {str(e)}",
                severity='warning'
            ))
    
    def _validate_memory(self, min_gb: int = 2) -> None:
        """Validate available memory"""
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = {}
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        meminfo[parts[0].rstrip(':')] = int(parts[1])
                
                total_kb = meminfo.get('MemTotal', 0)
                available_kb = meminfo.get('MemAvailable', meminfo.get('MemFree', 0))
                total_gb = total_kb / (1024 ** 2)
                available_gb = available_kb / (1024 ** 2)
                
                if total_gb < min_gb:
                    self.warnings.append(ValidationResult(
                        passed=False,
                        message=f"Low total memory: {total_gb:.1f}GB (recommended: {min_gb}GB+)",
                        severity='warning'
                    ))
                
                if available_gb < min_gb * 0.5:
                    self.warnings.append(ValidationResult(
                        passed=False,
                        message=f"Low available memory: {available_gb:.1f}GB",
                        severity='warning',
                        fix_suggestion="Consider stopping other services or increasing instance size"
                    ))
        except Exception as e:
            self.warnings.append(ValidationResult(
                passed=False,
                message=f"Could not check memory: {str(e)}",
                severity='warning'
            ))
    
    def _validate_network(self) -> None:
        """Validate network connectivity"""
        import socket
        
        # Check if we can resolve DNS
        try:
            socket.gethostbyname('github.com')
        except socket.gaierror:
            self.errors.append(ValidationResult(
                passed=False,
                message="Cannot resolve DNS (github.com)",
                severity='error',
                fix_suggestion="Check DNS configuration and network connectivity"
            ))
        
        # Check if we can reach GitHub
        try:
            import urllib.request
            urllib.request.urlopen('https://github.com', timeout=5)
        except Exception as e:
            self.warnings.append(ValidationResult(
                passed=False,
                message=f"Cannot reach GitHub: {str(e)}",
                severity='warning',
                fix_suggestion="Check network connectivity and firewall rules"
            ))
    
    def _validate_git_repository(self) -> None:
        """Validate Git repository"""
        git_dir = self.project_dir / '.git'
        
        if not git_dir.exists():
            self.warnings.append(ValidationResult(
                passed=False,
                message="Project directory is not a Git repository",
                severity='warning',
                fix_suggestion="Initialize Git: git init"
            ))
            return
        
        # Check if we can run git commands
        try:
            result = subprocess.run(
                ['git', 'status'],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                self.warnings.append(ValidationResult(
                    passed=False,
                    message=f"Git repository may be corrupted: {result.stderr}",
                    severity='warning'
                ))
        except Exception as e:
            self.warnings.append(ValidationResult(
                passed=False,
                message=f"Error checking Git repository: {str(e)}",
                severity='warning'
            ))
    
    def _validate_environment_variables(self) -> None:
        """Validate required environment variables"""
        required_vars = self.config.get('required_env_vars', [])
        
        for var in required_vars:
            if var not in os.environ:
                self.errors.append(ValidationResult(
                    passed=False,
                    message=f"Required environment variable not set: {var}",
                    severity='error',
                    fix_suggestion=f"Export variable: export {var}=<value>"
                ))
    
    def _validate_permissions(self) -> None:
        """Validate file permissions"""
        docker_compose_file = self.project_dir / 'aws' / 'docker-compose.yml'
        
        if docker_compose_file.exists():
            if not os.access(docker_compose_file, os.R_OK):
                self.errors.append(ValidationResult(
                    passed=False,
                    message=f"Cannot read docker-compose.yml: {docker_compose_file}",
                    severity='error',
                    fix_suggestion=f"Fix permissions: chmod 644 {docker_compose_file}"
                ))
        
        # Check if user can run docker commands
        try:
            result = subprocess.run(
                ['docker', 'ps'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0 and 'permission denied' in result.stderr.lower():
                self.errors.append(ValidationResult(
                    passed=False,
                    message="User does not have permission to run Docker commands",
                    severity='error',
                    fix_suggestion="Add user to docker group: sudo usermod -aG docker $USER"
                ))
        except:
            pass
    
    def get_summary(self) -> str:
        """Get validation summary"""
        if not self.errors and not self.warnings:
            return "All validations passed ✓"
        
        summary = []
        if self.errors:
            summary.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            summary.append(f"{len(self.warnings)} warning(s)")
        
        return ", ".join(summary)
