#!/usr/bin/env python3
"""
Cost Optimizer
Optimizes deployment costs by analyzing resource usage
"""

import logging
import subprocess
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class CostRecommendation:
    """Cost optimization recommendation"""
    category: str  # compute, storage, network, etc.
    description: str
    potential_savings: Optional[float] = None
    priority: str = 'medium'  # high, medium, low
    action: Optional[str] = None


class CostOptimizer:
    """Optimizes deployment costs"""
    
    def __init__(self, project_dir: str = '/opt/blatam-academy'):
        self.project_dir = Path(project_dir)
        self.recommendations: List[CostRecommendation] = []
    
    def analyze_docker_resources(self) -> List[CostRecommendation]:
        """Analyze Docker resource usage"""
        recommendations = []
        
        try:
            # Check for unused images
            result = subprocess.run(
                ['docker', 'images', '--format', '{{.Repository}}:{{.Tag}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                images = [line for line in result.stdout.strip().split('\n') if line]
                if len(images) > 10:
                    recommendations.append(CostRecommendation(
                        category='storage',
                        description=f'Found {len(images)} Docker images. Consider cleaning unused images.',
                        priority='medium',
                        action='docker image prune -a'
                    ))
            
            # Check for stopped containers
            result = subprocess.run(
                ['docker', 'ps', '-a', '--filter', 'status=exited', '-q'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                stopped = [line for line in result.stdout.strip().split('\n') if line]
                if stopped:
                    recommendations.append(CostRecommendation(
                        category='compute',
                        description=f'Found {len(stopped)} stopped containers. Clean up to free resources.',
                        priority='low',
                        action='docker container prune'
                    ))
        
        except Exception as e:
            logger.error(f"Failed to analyze Docker resources: {e}")
        
        return recommendations
    
    def analyze_disk_usage(self) -> List[CostRecommendation]:
        """Analyze disk usage"""
        recommendations = []
        
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            free_gb = free / (1024 ** 3)
            usage_percent = (used / total) * 100
            
            if usage_percent > 80:
                recommendations.append(CostRecommendation(
                    category='storage',
                    description=f'Disk usage at {usage_percent:.1f}%. Consider cleanup.',
                    priority='high',
                    action='Clean up old logs, backups, and Docker resources'
                ))
            
            if free_gb < 5:
                recommendations.append(CostRecommendation(
                    category='storage',
                    description=f'Low disk space: {free_gb:.1f}GB free. Critical cleanup needed.',
                    priority='critical',
                    action='Immediate cleanup required'
                ))
        
        except Exception as e:
            logger.error(f"Failed to analyze disk usage: {e}")
        
        return recommendations
    
    def analyze_dockerfile(self) -> List[CostRecommendation]:
        """Analyze Dockerfile for cost optimizations"""
        recommendations = []
        dockerfile = self.project_dir / 'aws' / 'Dockerfile'
        
        if not dockerfile.exists():
            return recommendations
        
        try:
            content = dockerfile.read_text()
            
            # Check for multi-stage builds (cost optimization)
            if content.count('FROM') == 1:
                recommendations.append(CostRecommendation(
                    category='compute',
                    description='Consider using multi-stage builds to reduce image size',
                    priority='medium',
                    action='Implement multi-stage Dockerfile'
                ))
            
            # Check for .dockerignore
            dockerignore = self.project_dir / '.dockerignore'
            if not dockerignore.exists():
                recommendations.append(CostRecommendation(
                    category='storage',
                    description='Missing .dockerignore file. May include unnecessary files in image.',
                    priority='low',
                    action='Create .dockerignore file'
                ))
        
        except Exception as e:
            logger.error(f"Failed to analyze Dockerfile: {e}")
        
        return recommendations
    
    def analyze_all(self) -> Dict[str, Any]:
        """Run all cost optimizations"""
        logger.info("Starting cost optimization analysis...")
        
        all_recommendations = []
        all_recommendations.extend(self.analyze_docker_resources())
        all_recommendations.extend(self.analyze_disk_usage())
        all_recommendations.extend(self.analyze_dockerfile())
        
        self.recommendations = all_recommendations
        
        # Count by priority
        priority_counts = {
            'critical': len([r for r in all_recommendations if r.priority == 'critical']),
            'high': len([r for r in all_recommendations if r.priority == 'high']),
            'medium': len([r for r in all_recommendations if r.priority == 'medium']),
            'low': len([r for r in all_recommendations if r.priority == 'low'])
        }
        
        return {
            'total_recommendations': len(all_recommendations),
            'priority_counts': priority_counts,
            'recommendations': [
                {
                    'category': rec.category,
                    'description': rec.description,
                    'potential_savings': rec.potential_savings,
                    'priority': rec.priority,
                    'action': rec.action
                }
                for rec in all_recommendations
            ],
            'analysis_time': datetime.now().isoformat()
        }
    
    def get_high_priority_recommendations(self) -> List[CostRecommendation]:
        """Get high priority recommendations"""
        return [r for r in self.recommendations if r.priority in ['critical', 'high']]
