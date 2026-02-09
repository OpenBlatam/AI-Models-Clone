#!/usr/bin/env python3
"""
Dependency Manager
Manages and validates dependencies for deployments
"""

import logging
import json
import subprocess
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class Dependency:
    """Dependency definition"""
    name: str
    version: str
    type: str  # 'python', 'node', 'system', 'docker'
    required: bool = True
    source: Optional[str] = None


class DependencyManager:
    """Manages deployment dependencies"""
    
    def __init__(self, project_dir: str = '/opt/blatam-academy'):
        self.project_dir = Path(project_dir)
        self.dependencies: List[Dependency] = []
        self.dependency_graph: Dict[str, Set[str]] = {}
    
    def load_python_dependencies(self) -> List[Dependency]:
        """Load Python dependencies from requirements.txt"""
        dependencies = []
        requirements_file = self.project_dir / 'requirements.txt'
        
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Parse requirement line
                            if '==' in line:
                                name, version = line.split('==', 1)
                            elif '>=' in line:
                                name, version = line.split('>=', 1)
                            else:
                                name = line
                                version = 'latest'
                            
                            dependencies.append(Dependency(
                                name=name.strip(),
                                version=version.strip(),
                                type='python'
                            ))
            except Exception as e:
                logger.error(f"Failed to load Python dependencies: {e}")
        
        return dependencies
    
    def check_dependency_versions(self) -> Dict[str, Any]:
        """Check if dependencies are up to date"""
        results = {
            'outdated': [],
            'vulnerable': [],
            'missing': [],
            'checked_at': datetime.now().isoformat()
        }
        
        # Check Python dependencies
        python_deps = self.load_python_dependencies()
        for dep in python_deps:
            if dep.type == 'python':
                # Use pip list to check installed versions
                try:
                    result = subprocess.run(
                        ['pip', 'show', dep.name],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode != 0:
                        results['missing'].append({
                            'name': dep.name,
                            'type': dep.type,
                            'required_version': dep.version
                        })
                except Exception as e:
                    logger.warning(f"Failed to check {dep.name}: {e}")
        
        return results
    
    def validate_dependencies(self) -> bool:
        """Validate all dependencies are available"""
        results = self.check_dependency_versions()
        
        if results['missing']:
            logger.error(f"Missing dependencies: {len(results['missing'])}")
            for dep in results['missing']:
                logger.error(f"  - {dep['name']} ({dep['type']})")
            return False
        
        if results['vulnerable']:
            logger.warning(f"Vulnerable dependencies: {len(results['vulnerable'])}")
            for dep in results['vulnerable']:
                logger.warning(f"  - {dep['name']}")
        
        return True
    
    def install_missing_dependencies(self) -> bool:
        """Install missing dependencies"""
        results = self.check_dependency_versions()
        
        if not results['missing']:
            return True
        
        try:
            requirements_file = self.project_dir / 'requirements.txt'
            if requirements_file.exists():
                subprocess.run(
                    ['pip', 'install', '-r', str(requirements_file)],
                    check=True,
                    timeout=600
                )
                logger.info("Missing dependencies installed")
                return True
        except Exception as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
        
        return False
    
    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build dependency graph"""
        graph = {}
        
        python_deps = self.load_python_dependencies()
        for dep in python_deps:
            if dep.name not in graph:
                graph[dep.name] = set()
            
            if dep.source:
                if dep.source not in graph:
                    graph[dep.source] = set()
                graph[dep.source].add(dep.name)
        
        self.dependency_graph = graph
        return graph
