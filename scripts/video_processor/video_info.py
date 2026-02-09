"""
Video Info Extractor
====================
Extrae información de videos usando ffmpeg.
"""

import subprocess
import re
import logging
from typing import Dict, Any, Optional
import imageio_ffmpeg

logger = logging.getLogger(__name__)


class VideoInfoExtractor:
    """Extrae información de videos usando ffmpeg."""
    
    def __init__(self):
        """Inicializar extractor."""
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    
    def get_duration(self, video_path: str) -> float:
        """
        Obtiene la duración de un video en segundos.
        
        Args:
            video_path: Ruta al video
        
        Returns:
            Duración en segundos, o 0 si hay error
        """
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-f', 'null',
                '-'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            # Buscar la duración en el stderr
            # Formato: Duration: HH:MM:SS.mmm
            duration_match = re.search(
                r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})',
                result.stderr
            )
            
            if duration_match:
                hours = int(duration_match.group(1))
                minutes = int(duration_match.group(2))
                seconds = int(duration_match.group(3))
                milliseconds = int(duration_match.group(4))
                total_seconds = (
                    hours * 3600 +
                    minutes * 60 +
                    seconds +
                    milliseconds / 100.0
                )
                return total_seconds
            
            return 0
        except Exception as e:
            logger.warning(f"No se pudo obtener la duración del video: {e}")
            return 0
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Obtiene información completa del video.
        
        Args:
            video_path: Ruta al video
        
        Returns:
            Diccionario con información del video
        """
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-f', 'null',
                '-'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            info = {
                'duration': self.get_duration(video_path),
                'width': None,
                'height': None,
                'fps': None,
                'bitrate': None,
                'codec': None
            }
            
            # Buscar resolución
            resolution_match = re.search(
                r'(\d+)x(\d+)',
                result.stderr
            )
            if resolution_match:
                info['width'] = int(resolution_match.group(1))
                info['height'] = int(resolution_match.group(2))
            
            # Buscar FPS
            fps_match = re.search(
                r'(\d+(?:\.\d+)?)\s*fps',
                result.stderr
            )
            if fps_match:
                info['fps'] = float(fps_match.group(1))
            
            # Buscar bitrate
            bitrate_match = re.search(
                r'bitrate:\s*(\d+)\s*kb/s',
                result.stderr
            )
            if bitrate_match:
                info['bitrate'] = int(bitrate_match.group(1))
            
            # Buscar codec
            codec_match = re.search(
                r'Video:\s*(\w+)',
                result.stderr
            )
            if codec_match:
                info['codec'] = codec_match.group(1)
            
            return info
        except Exception as e:
            logger.warning(f"No se pudo obtener información del video: {e}")
            return {
                'duration': 0,
                'width': None,
                'height': None,
                'fps': None,
                'bitrate': None,
                'codec': None
            }






