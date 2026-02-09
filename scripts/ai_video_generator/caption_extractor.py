"""
Caption Extractor
=================
Extracción de captions desde archivos JSON.
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class CaptionExtractor:
    """Extractor de captions desde archivos JSON."""
    
    def extract(self, image_path: Path) -> str:
        """
        Extraer caption del archivo JSON asociado.
        
        Args:
            image_path: Ruta a la imagen
        
        Returns:
            Caption extraído o string vacío
        """
        json_path = image_path.with_suffix('.json')
        
        if not json_path.exists():
            return ""
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                caption = data.get('node', {}).get('edge_media_to_caption', {}).get('edges', [])
                if caption and len(caption) > 0:
                    return caption[0].get('node', {}).get('text', '')
        except Exception as e:
            logger.error(f"Error leyendo JSON {json_path}: {e}")
        
        return ""







