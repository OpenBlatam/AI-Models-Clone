#!/usr/bin/env python3
"""
Deployment Cache Manager
Manages caching of Docker images and build artifacts
"""

import os
import json
import hashlib
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class DeploymentCache:
    """Manages deployment caching"""
    
    def __init__(self, cache_dir: str = '/var/cache/deployment'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / 'metadata.json'
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'images': {},
            'builds': {},
            'last_cleanup': None
        }
    
    def _save_metadata(self) -> None:
        """Save cache metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")
    
    def get_cache_key(self, content: str) -> str:
        """Generate cache key from content"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def cache_docker_image(self, image_name: str, tag: str, image_id: str) -> None:
        """Cache Docker image metadata"""
        key = f"{image_name}:{tag}"
        self.metadata['images'][key] = {
            'image_id': image_id,
            'cached_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat()
        }
        self._save_metadata()
        logger.info(f"Cached Docker image: {key}")
    
    def get_cached_image(self, image_name: str, tag: str) -> Optional[str]:
        """Get cached Docker image ID"""
        key = f"{image_name}:{tag}"
        if key in self.metadata['images']:
            self.metadata['images'][key]['last_used'] = datetime.now().isoformat()
            self._save_metadata()
            return self.metadata['images'][key]['image_id']
        return None
    
    def cache_build_artifact(self, artifact_path: str, cache_key: str) -> None:
        """Cache build artifact"""
        self.metadata['builds'][cache_key] = {
            'path': artifact_path,
            'cached_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat()
        }
        self._save_metadata()
    
    def get_cached_artifact(self, cache_key: str) -> Optional[str]:
        """Get cached build artifact path"""
        if cache_key in self.metadata['builds']:
            artifact_info = self.metadata['builds'][cache_key]
            artifact_path = Path(artifact_info['path'])
            if artifact_path.exists():
                artifact_info['last_used'] = datetime.now().isoformat()
                self._save_metadata()
                return str(artifact_path)
        return None
    
    def cleanup_old_cache(self, max_age_days: int = 7) -> int:
        """Clean up old cache entries"""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        removed = 0
        
        # Clean up images
        for key, info in list(self.metadata['images'].items()):
            last_used = datetime.fromisoformat(info['last_used'])
            if last_used < cutoff_date:
                del self.metadata['images'][key]
                removed += 1
        
        # Clean up builds
        for key, info in list(self.metadata['builds'].items()):
            last_used = datetime.fromisoformat(info['last_used'])
            if last_used < cutoff_date:
                artifact_path = Path(info['path'])
                if artifact_path.exists():
                    try:
                        artifact_path.unlink()
                    except:
                        pass
                del self.metadata['builds'][key]
                removed += 1
        
        self.metadata['last_cleanup'] = datetime.now().isoformat()
        self._save_metadata()
        
        logger.info(f"Cleaned up {removed} old cache entries")
        return removed
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'total_images': len(self.metadata['images']),
            'total_builds': len(self.metadata['builds']),
            'cache_dir': str(self.cache_dir),
            'last_cleanup': self.metadata.get('last_cleanup'),
            'cache_size': self._get_cache_size()
        }
    
    def _get_cache_size(self) -> int:
        """Get total cache size in bytes"""
        total_size = 0
        try:
            for path in self.cache_dir.rglob('*'):
                if path.is_file():
                    total_size += path.stat().st_size
        except:
            pass
        return total_size
