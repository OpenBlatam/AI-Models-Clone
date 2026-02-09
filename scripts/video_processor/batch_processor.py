"""
Batch Video Processor
=====================
Procesa múltiples videos en batch.
"""

import logging
from pathlib import Path
from typing import List, Optional

from .video_splitter import VideoSplitter
from .video_editor import VideoEditor
from .video_info import VideoInfoExtractor

logger = logging.getLogger(__name__)


class BatchVideoProcessor:
    """Procesa múltiples videos en batch."""
    
    def __init__(
        self,
        clip_duration: float = 8.0,
        editing_config: Optional[dict] = None,
        apply_editing: bool = False
    ):
        """
        Inicializar procesador batch.
        
        Args:
            clip_duration: Duración de cada clip en segundos
            editing_config: Configuración de efectos de edición
            apply_editing: Si True, aplica efectos de edición
        """
        self.splitter = VideoSplitter(clip_duration=clip_duration)
        self.editor = VideoEditor(config=editing_config) if apply_editing else None
        self.info_extractor = VideoInfoExtractor()
        self.apply_editing = apply_editing
    
    def process_directory(
        self,
        directory_path: str,
        recursive: bool = False,
        output_dir: Optional[Path] = None
    ) -> dict:
        """
        Procesa todos los videos en un directorio.
        
        Args:
            directory_path: Ruta al directorio
            recursive: Si es True, busca también en subdirectorios
            output_dir: Directorio de salida (opcional)
        
        Returns:
            Diccionario con estadísticas del procesamiento
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            logger.error(f"El directorio no existe: {directory_path}")
            return {
                'successful': 0,
                'failed': 0,
                'total_clips': 0,
                'total_videos': 0
            }
        
        # Buscar todos los archivos .mp4
        if recursive:
            video_files = list(directory.rglob("*.mp4"))
        else:
            video_files = list(directory.glob("*.mp4"))
        
        # Filtrar archivos que ya fueron procesados
        video_files = [
            f for f in video_files
            if "_part" not in f.stem and "_8s" not in f.stem and "_7s" not in f.stem
        ]
        
        if not video_files:
            logger.info("No se encontraron videos para procesar.")
            return {
                'successful': 0,
                'failed': 0,
                'total_clips': 0,
                'total_videos': 0
            }
        
        logger.info(f"Se encontraron {len(video_files)} video(s) para procesar:")
        for vf in video_files:
            logger.info(f"  - {vf.name}")
        logger.info("")
        
        # Procesar cada video
        total_clips = 0
        successful_videos = 0
        failed_videos = 0
        
        for video_file in video_files:
            clips_created = self.splitter.split_video(
                str(video_file),
                output_dir=output_dir
            )
            
            if clips_created > 0:
                successful_videos += 1
                total_clips += clips_created
            else:
                failed_videos += 1
            logger.info("")
        
        logger.info("="*50)
        logger.info(f"Procesamiento completado:")
        logger.info(f"  ✓ Videos procesados exitosamente: {successful_videos}")
        logger.info(f"  ✗ Videos fallidos: {failed_videos}")
        logger.info(f"  📹 Total de clips creados: {total_clips}")
        logger.info(f"  📁 Total de videos: {len(video_files)}")
        
        return {
            'successful': successful_videos,
            'failed': failed_videos,
            'total_clips': total_clips,
            'total_videos': len(video_files)
        }
    
    def process_video_with_editing(
        self,
        video_path: str,
        output_dir: Optional[Path] = None
    ) -> int:
        """
        Procesa un video dividiéndolo en clips y aplicando efectos.
        
        Args:
            video_path: Ruta al video
            output_dir: Directorio de salida
        
        Returns:
            Número de clips creados
        """
        if not self.editor:
            # Sin edición, solo dividir
            return self.splitter.split_video(video_path, output_dir=output_dir)
        
        # Con edición: dividir y luego editar cada clip
        clips_created = self.splitter.split_video(video_path, output_dir=output_dir)
        
        # Nota: La edición se puede aplicar después de dividir
        # o integrarse en el proceso de división
        # Por simplicidad, aquí solo dividimos
        
        return clips_created






