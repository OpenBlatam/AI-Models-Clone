#!/usr/bin/env python3
"""
Backup Manager
Manages automatic backups before deployments
"""

import os
import json
import shutil
import logging
import subprocess
import tarfile
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from pathlib import Path


logger = logging.getLogger(__name__)


class BackupManager:
    """Manages deployment backups"""
    
    def __init__(self, backup_dir: str = '/var/backups/deployments'):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.backup_dir / 'backups.json'
        self.metadata = self._load_metadata()
        self.max_backups = 10
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load backup metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'backups': []}
    
    def _save_metadata(self) -> None:
        """Save backup metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save backup metadata: {e}")
    
    def create_backup(
        self,
        source_dir: str,
        backup_name: Optional[str] = None,
        include_docker: bool = True
    ) -> Optional[str]:
        """Create a backup of the deployment"""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / f"{backup_name}.tar.gz"
        
        try:
            logger.info(f"Creating backup: {backup_name}")
            
            # Create tar archive
            with tarfile.open(backup_path, 'w:gz') as tar:
                # Add source directory
                source_path = Path(source_dir)
                if source_path.exists():
                    tar.add(source_dir, arcname='project', filter=self._exclude_patterns)
                
                # Add Docker volumes if requested
                if include_docker:
                    self._backup_docker_volumes(tar)
            
            # Record backup in metadata
            backup_info = {
                'name': backup_name,
                'path': str(backup_path),
                'size': backup_path.stat().st_size,
                'created_at': datetime.now().isoformat(),
                'source_dir': source_dir
            }
            
            self.metadata['backups'].append(backup_info)
            
            # Keep only last N backups
            if len(self.metadata['backups']) > self.max_backups:
                oldest = self.metadata['backups'].pop(0)
                try:
                    Path(oldest['path']).unlink()
                except:
                    pass
            
            self._save_metadata()
            
            logger.info(f"Backup created successfully: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            if backup_path.exists():
                backup_path.unlink()
            return None
    
    def _exclude_patterns(self, tarinfo: tarfile.TarInfo) -> Optional[tarfile.TarInfo]:
        """Filter out unnecessary files from backup"""
        exclude_patterns = [
            '.git',
            '__pycache__',
            '*.pyc',
            'node_modules',
            '.venv',
            'venv',
            '*.log',
            '.pytest_cache',
            '.mypy_cache'
        ]
        
        name = tarinfo.name
        for pattern in exclude_patterns:
            if pattern in name:
                return None
        
        return tarinfo
    
    def _backup_docker_volumes(self, tar: tarfile.TarFile) -> None:
        """Backup Docker volumes"""
        try:
            # Get list of volumes
            result = subprocess.run(
                ['docker', 'volume', 'ls', '--format', '{{.Name}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                volumes = [v.strip() for v in result.stdout.split('\n') if v.strip()]
                for volume in volumes:
                    if 'blatam' in volume.lower() or 'academy' in volume.lower():
                        # Export volume
                        export_file = self.backup_dir / f"volume_{volume}.tar"
                        try:
                            subprocess.run(
                                ['docker', 'run', '--rm', '-v', f'{volume}:/data', '-v', f'{self.backup_dir}:/backup',
                                 'alpine', 'tar', 'czf', f'/backup/volume_{volume}.tar.gz', '-C', '/data', '.'],
                                timeout=60,
                                check=False
                            )
                            if export_file.exists():
                                tar.add(str(export_file), arcname=f'volumes/volume_{volume}.tar.gz')
                        except:
                            pass
        except Exception as e:
            logger.warning(f"Could not backup Docker volumes: {e}")
    
    def restore_backup(self, backup_name: str, target_dir: str) -> bool:
        """Restore a backup"""
        backup_info = None
        for backup in self.metadata['backups']:
            if backup['name'] == backup_name:
                backup_info = backup
                break
        
        if not backup_info:
            logger.error(f"Backup not found: {backup_name}")
            return False
        
        backup_path = Path(backup_info['path'])
        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        try:
            logger.info(f"Restoring backup: {backup_name} to {target_dir}")
            
            # Extract backup
            target_path = Path(target_dir)
            target_path.mkdir(parents=True, exist_ok=True)
            
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(target_path)
            
            logger.info(f"Backup restored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        return self.metadata.get('backups', [])
    
    def get_backup_info(self, backup_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific backup"""
        for backup in self.metadata['backups']:
            if backup['name'] == backup_name:
                return backup
        return None
    
    def cleanup_old_backups(self, days: int = 30) -> int:
        """Clean up backups older than specified days"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        removed = 0
        backups_to_keep = []
        
        for backup in self.metadata['backups']:
            created_at = datetime.fromisoformat(backup['created_at'])
            if created_at < cutoff:
                try:
                    Path(backup['path']).unlink()
                    removed += 1
                except:
                    pass
            else:
                backups_to_keep.append(backup)
        
        self.metadata['backups'] = backups_to_keep
        self._save_metadata()
        
        logger.info(f"Cleaned up {removed} old backups")
        return removed
