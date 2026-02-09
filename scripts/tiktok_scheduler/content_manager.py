"""
Content Manager
===============
Manejo centralizado de contenido (videos e imágenes).
"""

import json
import logging
from pathlib import Path
from typing import List, Optional

from .config import Config

logger = logging.getLogger(__name__)


class ContentManager:
    """Gestor de contenido para posts."""
    
    def __init__(self, use_videos: Optional[bool] = None):
        """
        Inicializar gestor de contenido.
        
        Args:
            use_videos: Si True, prioriza videos. Si None, usa Config.USE_VIDEOS
        """
        self.use_videos = use_videos if use_videos is not None else Config.USE_VIDEOS
        self.content_dir = Config.CONTENT_DIR
        self.videos_dir = Config.VIDEOS_DIR
    
    def get_content_files(self) -> List[Path]:
        """
        Obtener lista de archivos de contenido (videos o imágenes).
        
        Returns:
            Lista de paths a archivos de contenido
        """
        if self.use_videos:
            # Buscar videos generados con IA
            if self.videos_dir.exists():
                video_files = list(self.videos_dir.glob('*.mp4')) + list(self.videos_dir.glob('*.MP4'))
                if video_files:
                    logger.info(f"Encontrados {len(video_files)} videos en {self.videos_dir}")
                    return sorted(video_files)
                else:
                    logger.warning(f"No se encontraron videos en {self.videos_dir}, buscando imágenes...")
            else:
                logger.warning(f"Directorio de videos no existe: {self.videos_dir}, buscando imágenes...")
        
        # Fallback a imágenes
        if not self.content_dir.exists():
            logger.error(f"Directorio de contenido no existe: {self.content_dir}")
            return []
        
        image_files = (
            list(self.content_dir.glob('*.jpg')) +
            list(self.content_dir.glob('*.jpeg')) +
            list(self.content_dir.glob('*.png'))
        )
        logger.info(f"Encontradas {len(image_files)} imágenes en {self.content_dir}")
        return sorted(image_files)
    
    def get_caption_from_json(self, content_path: Path) -> str:
        """
        Obtener caption del archivo JSON asociado.
        
        Args:
            content_path: Path al archivo de contenido
        
        Returns:
            Caption del contenido o default
        """
        # Para videos, buscar JSON en content_dir
        if content_path.suffix.lower() in ['.mp4', '.mov', '.avi']:
            # Buscar JSON con el mismo nombre base
            for json_file in self.content_dir.glob('*.json'):
                if json_file.stem in content_path.stem or content_path.stem.replace('_ai', '').replace('_video', '') in json_file.stem:
                    return self._read_caption_from_json(json_file)
            return "✨ Nuevo video"
        else:
            # Para imágenes, buscar JSON con mismo nombre
            json_path = content_path.with_suffix('.json')
            return self._read_caption_from_json(json_path)
    
    def _read_caption_from_json(self, json_path: Path) -> str:
        """
        Leer caption de un archivo JSON.
        
        Args:
            json_path: Path al archivo JSON
        
        Returns:
            Caption extraído o default
        """
        if not json_path.exists():
            return "✨ Nuevo post"
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                caption = data.get('node', {}).get('edge_media_to_caption', {}).get('edges', [])
                if caption and len(caption) > 0:
                    text = caption[0].get('node', {}).get('text', '')
                    return text[:150]  # TikTok limita a 150 caracteres
        except Exception as e:
            logger.error(f"Error leyendo JSON {json_path}: {e}")
        
        return "✨ Nuevo post"
    
    def get_content_type(self, content_path: Path) -> str:
        """
        Determinar tipo de contenido.
        
        Args:
            content_path: Path al archivo
        
        Returns:
            'video' o 'image'
        """
        if content_path.suffix.lower() in ['.mp4', '.mov', '.avi']:
            return 'video'
        return 'image'
    
    def get_content_statistics(self) -> dict:
        """
        Obtener estadísticas de contenido disponible.
        
        Returns:
            Diccionario con estadísticas
        """
        files = self.get_content_files()
        videos = [f for f in files if self.get_content_type(f) == 'video']
        images = [f for f in files if self.get_content_type(f) == 'image']
        
        return {
            'total': len(files),
            'videos': len(videos),
            'images': len(images),
            'using_videos': self.use_videos
        }







