"""
Manifest Loader - Cargador de manifiestos desde archivos
=========================================================
"""

import json
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Any

from .models import ResourceManifest
from .registry import ManifestRegistry

logger = logging.getLogger(__name__)


class ManifestLoader:
    """
    Cargador de manifests desde archivos JSON/YAML
    
    Soporta:
    - Archivos individuales
    - Directorios con múltiples archivos
    - Validación automática con Pydantic
    """
    
    @staticmethod
    def load_from_file(file_path: str) -> ResourceManifest:
        """
        Carga un manifest desde un archivo
        
        Args:
            file_path: Ruta al archivo (JSON o YAML)
            
        Returns:
            ResourceManifest cargado y validado
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Manifest file not found: {file_path}")
        
        with open(path, "r", encoding="utf-8") as f:
            if path.suffix.lower() in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
            elif path.suffix.lower() == ".json":
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
        
        try:
            manifest = ResourceManifest.from_dict(data)
            logger.info(f"Loaded manifest: {manifest.resource_id}")
            return manifest
        except Exception as e:
            logger.error(f"Error loading manifest from {file_path}: {e}")
            raise
    
    @staticmethod
    def load_from_directory(directory: str, pattern: str = "*.{json,yaml,yml}") -> List[ResourceManifest]:
        """
        Carga múltiples manifests desde un directorio
        
        Args:
            directory: Directorio con archivos de manifest
            pattern: Patrón de búsqueda (default: *.json, *.yaml, *.yml)
            
        Returns:
            Lista de ResourceManifest cargados
        """
        dir_path = Path(directory)
        
        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"Directory not found: {directory}")
        
        manifests = []
        for file_path in dir_path.glob(pattern):
            try:
                manifest = ManifestLoader.load_from_file(str(file_path))
                manifests.append(manifest)
            except Exception as e:
                logger.warning(f"Skipping {file_path}: {e}")
        
        logger.info(f"Loaded {len(manifests)} manifests from {directory}")
        return manifests
    
    @staticmethod
    def load_from_dict(data: Dict[str, Any]) -> ResourceManifest:
        """
        Carga un manifest desde un diccionario
        
        Args:
            data: Diccionario con datos del manifest
            
        Returns:
            ResourceManifest
        """
        return ResourceManifest.from_dict(data)
    
    @staticmethod
    def load_from_json(json_str: str) -> ResourceManifest:
        """
        Carga un manifest desde JSON string
        
        Args:
            json_str: String JSON
            
        Returns:
            ResourceManifest
        """
        return ResourceManifest.from_json(json_str)
    
    @staticmethod
    def register_from_file(registry: ManifestRegistry, file_path: str):
        """
        Carga y registra un manifest desde archivo
        
        Args:
            registry: Registry donde registrar
            file_path: Ruta al archivo
        """
        manifest = ManifestLoader.load_from_file(file_path)
        registry.register(manifest)
    
    @staticmethod
    def register_from_directory(registry: ManifestRegistry, directory: str):
        """
        Carga y registra múltiples manifests desde directorio
        
        Args:
            registry: Registry donde registrar
            directory: Directorio con archivos
        """
        manifests = ManifestLoader.load_from_directory(directory)
        for manifest in manifests:
            registry.register(manifest)

