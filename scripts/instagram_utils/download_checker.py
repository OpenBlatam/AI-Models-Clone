"""
Instagram Download Checker
==========================
Verifica y analiza descargas de Instagram.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image

logger = logging.getLogger(__name__)


class InstagramDownloadChecker:
    """Verifica y analiza descargas de Instagram."""
    
    def __init__(self, base_dir: str = "instagram_downloads"):
        """
        Inicializar checker.
        
        Args:
            base_dir: Directorio base de descargas
        """
        self.base_dir = Path(base_dir)
    
    def check_profile_downloads(
        self,
        profile_name: str,
        image_extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Verifica las descargas de un perfil específico.
        
        Args:
            profile_name: Nombre del perfil
            image_extensions: Extensiones de imagen a verificar
        
        Returns:
            Diccionario con información del perfil
        """
        if image_extensions is None:
            image_extensions = ['.jpg', '.jpeg', '.png']
        
        profile_dir = self.base_dir / profile_name
        
        if not profile_dir.exists():
            return {
                'profile': profile_name,
                'exists': False,
                'images': 0,
                'json_files': 0,
                'total_size_mb': 0.0,
                'resolutions': [],
                'max_resolution': None
            }
        
        # Buscar archivos
        image_files = []
        json_files = []
        
        for ext in image_extensions:
            image_files.extend(profile_dir.glob(f"*{ext}"))
            image_files.extend(profile_dir.glob(f"*{ext.upper()}"))
        
        json_files = list(profile_dir.glob("*.json"))
        
        # Calcular tamaño total
        total_size = sum(os.path.getsize(f) for f in image_files) / (1024 * 1024)
        
        # Obtener resoluciones
        resolutions = []
        max_resolution = None
        max_area = 0
        
        for img_file in image_files:
            try:
                img = Image.open(img_file)
                size = img.size
                resolutions.append(size)
                area = size[0] * size[1]
                if area > max_area:
                    max_area = area
                    max_resolution = size
            except Exception as e:
                logger.warning(f"Error al leer {img_file.name}: {e}")
        
        return {
            'profile': profile_name,
            'exists': True,
            'images': len(image_files),
            'json_files': len(json_files),
            'total_size_mb': total_size,
            'resolutions': list(set(resolutions)),
            'max_resolution': max_resolution
        }
    
    def check_all_profiles(
        self,
        profile_names: List[str],
        image_extensions: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Verifica las descargas de múltiples perfiles.
        
        Args:
            profile_names: Lista de nombres de perfiles
            image_extensions: Extensiones de imagen a verificar
        
        Returns:
            Diccionario con información de cada perfil
        """
        results = {}
        
        for profile in profile_names:
            results[profile] = self.check_profile_downloads(profile, image_extensions)
        
        return results
    
    def print_summary(self, results: Dict[str, Dict[str, Any]]) -> None:
        """
        Imprime un resumen de los resultados.
        
        Args:
            results: Resultados de check_all_profiles
        """
        logger.info("=" * 60)
        logger.info("RESUMEN DE DESCARGA DE IMÁGENES")
        logger.info("=" * 60)
        
        for profile, data in results.items():
            logger.info(f"\n@{profile}:")
            if data['exists']:
                logger.info(f"  - Imágenes: {data['images']}")
                logger.info(f"  - Archivos JSON: {data['json_files']}")
                logger.info(f"  - Tamaño total: {data['total_size_mb']:.2f} MB")
                if data['resolutions']:
                    logger.info(f"  - Resoluciones únicas: {len(data['resolutions'])}")
                    if data['max_resolution']:
                        logger.info(f"  - Resolución máxima: {data['max_resolution']}")
            else:
                logger.warning(f"  - ERROR: No se pudo descargar (perfil no encontrado o bloqueado)")
        
        logger.info("\n" + "=" * 60)






