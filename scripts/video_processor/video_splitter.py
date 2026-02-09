"""
Video Splitter
==============
Divide videos en clips de duración específica.
"""

import subprocess
import logging
import math
from pathlib import Path
from typing import Optional
import imageio_ffmpeg

from .video_info import VideoInfoExtractor

logger = logging.getLogger(__name__)


class VideoSplitter:
    """Divide videos en clips."""
    
    def __init__(self, clip_duration: float = 8.0):
        """
        Inicializar splitter.
        
        Args:
            clip_duration: Duración de cada clip en segundos
        """
        self.clip_duration = clip_duration
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        self.info_extractor = VideoInfoExtractor()
    
    def split_video(
        self,
        video_path: str,
        output_dir: Optional[Path] = None,
        output_prefix: Optional[str] = None
    ) -> int:
        """
        Divide un video en clips.
        
        Args:
            video_path: Ruta al video original
            output_dir: Directorio de salida (si es None, usa el mismo del video)
            output_prefix: Prefijo para archivos de salida (si es None, usa el nombre del video)
        
        Returns:
            Número de clips creados exitosamente, 0 si hubo error
        """
        try:
            video_path_obj = Path(video_path)
            if not video_path_obj.exists():
                logger.error(f"El archivo no existe: {video_path}")
                return 0
            
            if output_dir is None:
                output_dir = video_path_obj.parent
            
            if output_prefix is None:
                output_prefix = video_path_obj.stem
            
            logger.info(f"Procesando: {video_path}")
            
            # Obtener la duración del video
            duration = self.info_extractor.get_duration(str(video_path))
            if duration <= 0:
                logger.error("  No se pudo obtener la duración del video")
                return 0
            
            logger.info(f"  Duración original: {duration:.2f} segundos")
            
            # Calcular número de clips necesarios
            num_clips = math.ceil(duration / self.clip_duration)
            logger.info(f"  Se crearán {num_clips} clip(s) de {self.clip_duration} segundos")
            
            suffix = video_path_obj.suffix
            clips_created = 0
            
            # Crear cada clip
            for i in range(num_clips):
                start_time = i * self.clip_duration
                clip_duration = min(self.clip_duration, duration - start_time)
                
                if clip_duration <= 0:
                    break
                
                # Nombre del archivo de salida
                output_path = output_dir / f"{output_prefix}_part{i+1:03d}_{int(self.clip_duration)}s{suffix}"
                
                logger.info(
                    f"  Creando clip {i+1}/{num_clips}: "
                    f"{start_time:.2f}s - {start_time + clip_duration:.2f}s"
                )
                
                # Comando ffmpeg para extraer el segmento
                cmd = [
                    self.ffmpeg_path,
                    '-i', str(video_path),
                    '-ss', str(start_time),
                    '-t', str(clip_duration),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'medium',
                    '-avoid_negative_ts', 'make_zero',
                    '-y',
                    str(output_path)
                ]
                
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    clips_created += 1
                    logger.info(f"    ✓ Clip guardado: {output_path.name}")
                except subprocess.CalledProcessError as e:
                    logger.error(f"    ✗ Error creando clip {i+1}: {e.stderr[:200]}")
                    continue
            
            logger.info(f"  ✓ Video procesado: {clips_created}/{num_clips} clips creados")
            return clips_created
            
        except Exception as e:
            logger.error(f"Error procesando {video_path}: {str(e)}")
            return 0






