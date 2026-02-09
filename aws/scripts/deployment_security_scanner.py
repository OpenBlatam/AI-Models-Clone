#!/usr/bin/env python3
"""
Security Scanner
Scans deployments for security vulnerabilities
"""

import subprocess
import logging
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class SecurityIssue:
    """Security issue found"""
    severity: str  # critical, high, medium, low
    type: str  # vulnerability, misconfiguration, secret
    description: str
    file: Optional[str] = None
    line: Optional[int] = None
    recommendation: Optional[str] = None


class SecurityScanner:
    """Scans deployments for security issues"""
    
    def __init__(self, project_dir: str = '/opt/blatam-academy'):
        self.project_dir = Path(project_dir)
        self.issues: List[SecurityIssue] = []
    
    def scan_dockerfile(self) -> List[SecurityIssue]:
        """Scan Dockerfile for security issues"""
        issues = []
        dockerfile = self.project_dir / 'aws' / 'Dockerfile'
        
        if not dockerfile.exists():
            return issues
        
        try:
            content = dockerfile.read_text()
            
            # Check for root user
            if 'USER root' in content and 'USER appuser' not in content:
                issues.append(SecurityIssue(
                    severity='high',
                    type='misconfiguration',
                    description='Dockerfile runs as root user',
                    file=str(dockerfile),
                    recommendation='Add USER appuser after creating appuser'
                ))
            
            # Check for exposed secrets
            if 'password' in content.lower() or 'secret' in content.lower():
                issues.append(SecurityIssue(
                    severity='critical',
                    type='secret',
                    description='Potential secrets in Dockerfile',
                    file=str(dockerfile),
                    recommendation='Use environment variables or secrets management'
                ))
            
            # Check for latest tags
            if ':latest' in content:
                issues.append(SecurityIssue(
                    severity='medium',
                    type='misconfiguration',
                    description='Using :latest tag (not pinned)',
                    file=str(dockerfile),
                    recommendation='Use specific version tags'
                ))
            
        except Exception as e:
            logger.error(f"Failed to scan Dockerfile: {e}")
        
        return issues
    
    def scan_dependencies(self) -> List[SecurityIssue]:
        """Scan dependencies for known vulnerabilities"""
        issues = []
        
        # Check requirements.txt
        requirements_file = self.project_dir / 'requirements.txt'
        if requirements_file.exists():
            try:
                # Use safety or similar tool if available
                result = subprocess.run(
                    ['safety', 'check', '--json'],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    try:
                        vulnerabilities = json.loads(result.stdout)
                        for vuln in vulnerabilities:
                            issues.append(SecurityIssue(
                                severity=vuln.get('severity', 'medium'),
                                type='vulnerability',
                                description=f"Vulnerability in {vuln.get('package', 'unknown')}: {vuln.get('vulnerability', '')}",
                                recommendation=vuln.get('recommendation', 'Update package')
                            ))
                    except:
                        pass
            except FileNotFoundError:
                logger.warning("safety tool not found, skipping dependency scan")
            except Exception as e:
                logger.error(f"Failed to scan dependencies: {e}")
        
        return issues
    
    def scan_secrets(self) -> List[SecurityIssue]:
        """Scan for exposed secrets"""
        issues = []
        
        # Common secret patterns
        secret_patterns = [
            (r'password\s*=\s*["\']([^"\']+)["\']', 'password'),
            (r'api_key\s*=\s*["\']([^"\']+)["\']', 'API key'),
            (r'secret\s*=\s*["\']([^"\']+)["\']', 'secret'),
            (r'aws_access_key_id\s*=\s*["\']([^"\']+)["\']', 'AWS access key'),
        ]
        
        try:
            import re
            for file_path in self.project_dir.rglob('*.py'):
                if 'venv' in str(file_path) or '.git' in str(file_path):
                    continue
                
                try:
                    content = file_path.read_text()
                    for pattern, secret_type in secret_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            issues.append(SecurityIssue(
                                severity='critical',
                                type='secret',
                                description=f'Potential {secret_type} exposed in code',
                                file=str(file_path),
                                line=line_num,
                                recommendation='Move to environment variables or secrets manager'
                            ))
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Failed to scan for secrets: {e}")
        
        return issues
    
    def scan_all(self) -> Dict[str, Any]:
        """Run all security scans"""
        logger.info("Starting security scan...")
        
        all_issues = []
        all_issues.extend(self.scan_dockerfile())
        all_issues.extend(self.scan_dependencies())
        all_issues.extend(self.scan_secrets())
        
        self.issues = all_issues
        
        # Count by severity
        severity_counts = {
            'critical': len([i for i in all_issues if i.severity == 'critical']),
            'high': len([i for i in all_issues if i.severity == 'high']),
            'medium': len([i for i in all_issues if i.severity == 'medium']),
            'low': len([i for i in all_issues if i.severity == 'low'])
        }
        
        return {
            'total_issues': len(all_issues),
            'severity_counts': severity_counts,
            'issues': [
                {
                    'severity': issue.severity,
                    'type': issue.type,
                    'description': issue.description,
                    'file': issue.file,
                    'line': issue.line,
                    'recommendation': issue.recommendation
                }
                for issue in all_issues
            ],
            'scan_time': datetime.now().isoformat()
        }
    
    def should_block_deployment(self, max_critical: int = 0, max_high: int = 0) -> bool:
        """Determine if deployment should be blocked"""
        critical_count = len([i for i in self.issues if i.severity == 'critical'])
        high_count = len([i for i in self.issues if i.severity == 'high'])
        
        return critical_count > max_critical or high_count > max_high
