"""
Video Editor
============
Aplica efectos de edición a videos usando ffmpeg.
"""

import subprocess
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import imageio_ffmpeg

logger = logging.getLogger(__name__)


class VideoEditor:
    """Aplica efectos de edición a videos."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializar editor.
        
        Args:
            config: Configuración de efectos de edición
        """
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        self.config = config or {
            'fade_in': 0.5,
            'fade_out': 0.5,
            'brightness': 1.0,
            'contrast': 1.0,
            'saturation': 1.0,
            'sharpness': 1.0,
            'speed': 1.0
        }
    
    def build_filters(self, clip_duration: float) -> Optional[str]:
        """
        Construye la cadena de filtros de ffmpeg.
        
        Args:
            clip_duration: Duración del clip en segundos
        
        Returns:
            Cadena de filtros de ffmpeg o None si no hay filtros
        """
        filters = []
        
        # Fade in/out
        fade_in = self.config.get('fade_in', 0)
        fade_out = self.config.get('fade_out', 0)
        
        if fade_in > 0:
            filters.append(f"fade=t=in:st=0:d={fade_in}")
        
        if fade_out > 0 and clip_duration > fade_out:
            fade_out_start = clip_duration - fade_out
            filters.append(f"fade=t=out:st={fade_out_start:.2f}:d={fade_out}")
        
        # Ajustes de color (brightness, contrast, saturation)
        brightness = self.config.get('brightness', 1.0)
        contrast = self.config.get('contrast', 1.0)
        saturation = self.config.get('saturation', 1.0)
        
        if brightness != 1.0 or contrast != 1.0 or saturation != 1.0:
            # eq = equalizer de color
            # brightness en eq va de -1.0 a 1.0, así que ajustamos
            brightness_eq = (brightness - 1.0) * 0.3  # Limitar el rango
            eq_filter = (
                f"eq=brightness={brightness_eq:.2f}:"
                f"contrast={contrast:.2f}:"
                f"saturation={saturation:.2f}"
            )
            filters.append(eq_filter)
        
        # Nitidez (unsharp)
        sharpness = self.config.get('sharpness', 1.0)
        if sharpness != 1.0:
            # Unsharp mask para nitidez
            luma_amount = (sharpness - 1.0) * 0.5
            filters.append(f"unsharp=5:5:{luma_amount:.2f}:5:5:0.0")
        
        # Combinar todos los filtros
        return ",".join(filters) if filters else None
    
    def edit_video(
        self,
        input_path: str,
        output_path: str,
        clip_duration: float
    ) -> bool:
        """
        Aplica efectos de edición a un video.
        
        Args:
            input_path: Ruta al video de entrada
            output_path: Ruta al video de salida
            clip_duration: Duración del clip
        
        Returns:
            True si se editó exitosamente
        """
        try:
            filters = self.build_filters(clip_duration)
            
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-y'
            ]
            
            if filters:
                cmd.extend(['-vf', filters])
            
            cmd.append(output_path)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error editando video: {e.stderr[:200]}")
            return False
        except Exception as e:
            logger.error(f"Error editando video: {str(e)}")
            return False






