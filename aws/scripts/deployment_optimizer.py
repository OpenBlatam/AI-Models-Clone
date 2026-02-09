#!/usr/bin/env python3
"""
Deployment Optimizer
Optimizes deployment process for better performance
"""

import os
import logging
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path


logger = logging.getLogger(__name__)


class DeploymentOptimizer:
    """Optimizes deployment process"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.project_dir = Path(config.get('project_dir', '/opt/blatam-academy'))
    
    def optimize_docker_build(self) -> Dict[str, Any]:
        """Optimize Docker build process"""
        optimizations = {
            'use_build_cache': True,
            'parallel_builds': True,
            'layer_caching': True,
            'multi_stage': True
        }
        
        # Check if Dockerfile supports optimizations
        dockerfile = self.project_dir / 'aws' / 'Dockerfile'
        if dockerfile.exists():
            content = dockerfile.read_text()
            optimizations['multi_stage'] = 'FROM' in content and content.count('FROM') > 1
            optimizations['layer_caching'] = 'COPY requirements.txt' in content or 'COPY pyproject.toml' in content
        
        return optimizations
    
    def optimize_git_operations(self) -> Dict[str, Any]:
        """Optimize Git operations"""
        optimizations = {
            'shallow_clone': True,
            'single_branch': True,
            'depth': 1
        }
        
        return optimizations
    
    def cleanup_resources(self) -> Tuple[int, int]:
        """Clean up Docker resources"""
        cleaned_images = 0
        cleaned_containers = 0
        
        try:
            # Remove stopped containers
            result = subprocess.run(
                ['docker', 'container', 'prune', '-f'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                # Parse output to get count
                cleaned_containers = 1  # Simplified
            
            # Remove unused images
            result = subprocess.run(
                ['docker', 'image', 'prune', '-f'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                cleaned_images = 1  # Simplified
            
        except Exception as e:
            logger.warning(f"Failed to cleanup resources: {e}")
        
        return cleaned_images, cleaned_containers
    
    def optimize_disk_usage(self) -> Dict[str, Any]:
        """Optimize disk usage"""
        optimizations = {}
        
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            free_gb = free / (1024 ** 3)
            
            optimizations['free_space_gb'] = free_gb
            optimizations['cleanup_recommended'] = free_gb < 10
            
            if optimizations['cleanup_recommended']:
                # Perform cleanup
                cleaned_images, cleaned_containers = self.cleanup_resources()
                optimizations['cleaned_images'] = cleaned_images
                optimizations['cleaned_containers'] = cleaned_containers
                
        except Exception as e:
            logger.warning(f"Failed to optimize disk usage: {e}")
        
        return optimizations
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations"""
        recommendations = []
        
        # Check Docker build optimizations
        build_opts = self.optimize_docker_build()
        if not build_opts['multi_stage']:
            recommendations.append("Consider using multi-stage Docker builds")
        if not build_opts['layer_caching']:
            recommendations.append("Optimize Dockerfile for better layer caching")
        
        # Check disk space
        disk_opts = self.optimize_disk_usage()
        if disk_opts.get('cleanup_recommended'):
            recommendations.append("Low disk space - consider cleanup")
        
        return recommendations
