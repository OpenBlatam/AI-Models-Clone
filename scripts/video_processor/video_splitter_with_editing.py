"""
Video Splitter with Editing
===========================
Divide videos en clips y aplica efectos de edición en un solo paso.
"""

import subprocess
import logging
import math
from pathlib import Path
from typing import Optional, Dict, Any
import imageio_ffmpeg

from .video_info import VideoInfoExtractor
from .video_editor import VideoEditor

logger = logging.getLogger(__name__)


class VideoSplitterWithEditing:
    """Divide videos en clips y aplica efectos de edición."""
    
    def __init__(
        self,
        clip_duration: float = 7.0,
        editing_config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializar splitter con edición.
        
        Args:
            clip_duration: Duración de cada clip en segundos
            editing_config: Configuración de efectos de edición
        """
        self.clip_duration = clip_duration
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        self.info_extractor = VideoInfoExtractor()
        self.editor = VideoEditor(config=editing_config)
    
    def split_video_with_editing(
        self,
        video_path: str,
        output_dir: Optional[Path] = None,
        output_prefix: Optional[str] = None
    ) -> int:
        """
        Divide un video en clips y aplica efectos de edición.
        
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
            
            # Obtener información del video
            video_info = self.info_extractor.get_video_info(str(video_path))
            if video_info.get('width') and video_info.get('height'):
                logger.info(
                    f"  Resolución: {video_info.get('width')}x{video_info.get('height')}"
                )
            if video_info.get('fps'):
                logger.info(f"  FPS: {video_info.get('fps')}")
            
            # Calcular número de clips necesarios
            num_clips = math.ceil(duration / self.clip_duration)
            logger.info(
                f"  Se crearán {num_clips} clip(s) de {self.clip_duration} segundos con edición"
            )
            logger.info("  Efectos aplicados: fade in/out, brillo, contraste, saturación, nitidez")
            
            suffix = video_path_obj.suffix
            clips_created = 0
            
            # Crear cada clip con edición
            for i in range(num_clips):
                start_time = i * self.clip_duration
                clip_duration = min(self.clip_duration, duration - start_time)
                
                if clip_duration <= 0:
                    break
                
                # Nombre del archivo de salida
                output_path = output_dir / f"{output_prefix}_edited_part{i+1:03d}_{int(self.clip_duration)}s{suffix}"
                
                logger.info(
                    f"  Creando clip {i+1}/{num_clips}: "
                    f"{start_time:.2f}s - {start_time + clip_duration:.2f}s"
                )
                
                # Construir filtros de ffmpeg
                video_filters = self.editor.build_filters(clip_duration)
                
                # Ajustar velocidad si es necesario
                speed = self.editor.config.get('speed', 1.0)
                
                # Comando base de ffmpeg
                cmd = [
                    self.ffmpeg_path,
                    '-i', str(video_path),
                    '-ss', str(start_time),
                    '-t', str(clip_duration),
                ]
                
                # Ajustar velocidad del video si es necesario
                if speed != 1.0:
                    if video_filters:
                        video_filters = f"{video_filters},setpts=PTS/{speed}"
                    else:
                        video_filters = f"setpts=PTS/{speed}"
                    # Ajustar audio también
                    cmd.extend(['-af', f"atempo={speed}"])
                
                # Aplicar filtros de video si existen
                if video_filters:
                    cmd.extend(['-vf', video_filters])
                
                # Codecs y calidad
                cmd.extend([
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    '-avoid_negative_ts', 'make_zero',
                    '-y',
                    str(output_path)
                ])
                
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    clips_created += 1
                    logger.info(f"    ✓ Clip editado guardado: {output_path.name}")
                except subprocess.CalledProcessError as e:
                    logger.error(
                        f"    ✗ Error creando clip {i+1}: "
                        f"{e.stderr[:200] if e.stderr else str(e)}"
                    )
                    continue
            
            logger.info(
                f"  ✓ Video procesado: {clips_created}/{num_clips} clips creados con edición"
            )
            return clips_created
            
        except Exception as e:
            logger.error(f"Error procesando {video_path}: {str(e)}")
            return 0




