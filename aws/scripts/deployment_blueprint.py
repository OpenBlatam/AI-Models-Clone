#!/usr/bin/env python3
"""
Deployment Blueprint Manager
Manages deployment blueprints/templates for reusable configurations
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class DeploymentBlueprint:
    """Deployment blueprint/template"""
    name: str
    description: str
    strategy: str = 'standard'
    environment: str = 'production'
    config: Dict[str, Any] = None
    components: List[str] = None  # List of component names to enable
    tags: Dict[str, str] = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.components is None:
            self.components = []
        if self.tags is None:
            self.tags = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()


class BlueprintManager:
    """Manages deployment blueprints"""
    
    def __init__(self, blueprints_file: str = '/var/lib/deployment-blueprints/blueprints.json'):
        self.blueprints_file = Path(blueprints_file)
        self.blueprints_file.parent.mkdir(parents=True, exist_ok=True)
        self.blueprints: Dict[str, DeploymentBlueprint] = {}
        self._load_blueprints()
    
    def _load_blueprints(self):
        """Load blueprints from file"""
        if self.blueprints_file.exists():
            try:
                with open(self.blueprints_file, 'r') as f:
                    data = json.load(f)
                    for blueprint_data in data.get('blueprints', []):
                        blueprint = DeploymentBlueprint(**blueprint_data)
                        self.blueprints[blueprint.name] = blueprint
            except Exception as e:
                logger.error(f"Failed to load blueprints: {e}")
    
    def _save_blueprints(self):
        """Save blueprints to file"""
        try:
            data = {
                'blueprints': [asdict(bp) for bp in self.blueprints.values()],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.blueprints_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save blueprints: {e}")
    
    def create_blueprint(self, blueprint: DeploymentBlueprint) -> DeploymentBlueprint:
        """Create a new blueprint"""
        blueprint.updated_at = datetime.now().isoformat()
        self.blueprints[blueprint.name] = blueprint
        self._save_blueprints()
        logger.info(f"Created blueprint: {blueprint.name}")
        return blueprint
    
    def get_blueprint(self, name: str) -> Optional[DeploymentBlueprint]:
        """Get a blueprint by name"""
        return self.blueprints.get(name)
    
    def list_blueprints(self, environment: Optional[str] = None) -> List[DeploymentBlueprint]:
        """List all blueprints, optionally filtered by environment"""
        if environment:
            return [bp for bp in self.blueprints.values() if bp.environment == environment]
        return list(self.blueprints.values())
    
    def apply_blueprint(self, name: str, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Apply a blueprint configuration"""
        blueprint = self.blueprints.get(name)
        if not blueprint:
            raise ValueError(f"Blueprint {name} not found")
        
        config = blueprint.config.copy()
        if overrides:
            config.update(overrides)
        
        return {
            'blueprint': name,
            'strategy': blueprint.strategy,
            'environment': blueprint.environment,
            'config': config,
            'components': blueprint.components,
            'tags': blueprint.tags
        }
    
    def update_blueprint(self, name: str, updates: Dict[str, Any]) -> DeploymentBlueprint:
        """Update an existing blueprint"""
        if name not in self.blueprints:
            raise ValueError(f"Blueprint {name} not found")
        
        blueprint = self.blueprints[name]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(blueprint, key):
                setattr(blueprint, key, value)
        
        blueprint.updated_at = datetime.now().isoformat()
        self._save_blueprints()
        logger.info(f"Updated blueprint: {name}")
        return blueprint
    
    def delete_blueprint(self, name: str) -> bool:
        """Delete a blueprint"""
        if name in self.blueprints:
            del self.blueprints[name]
            self._save_blueprints()
            logger.info(f"Deleted blueprint: {name}")
            return True
        return False
