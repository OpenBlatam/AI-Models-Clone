"""
Video Composer
==============
Composición de videos usando MoviePy.
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image

try:
    from moviepy.editor import (
        ImageClip, concatenate_videoclips, CompositeVideoClip,
        ColorClip, AudioFileClip, TextClip
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class VideoComposer:
    """Compositor de videos."""
    
    def __init__(
        self,
        resolution: Tuple[int, int] = (1080, 1920),
        fps: int = 30,
        codec: str = 'libx264',
        preset: str = 'medium',
        bitrate: str = '8000k'
    ):
        """
        Inicializar compositor de videos.
        
        Args:
            resolution: Resolución del video (ancho, alto)
            fps: Frames por segundo
            codec: Codec de video
            preset: Preset de codificación
            bitrate: Bitrate del video
        """
        if not MOVIEPY_AVAILABLE:
            raise ImportError("moviepy no está disponible. Instala con: pip install moviepy")
        
        self.resolution = resolution
        self.fps = fps
        self.codec = codec
        self.preset = preset
        self.bitrate = bitrate
    
    def create_clip_from_image(
        self,
        image_path: Path,
        duration: float
    ):
        """
        Crear clip de video desde una imagen.
        
        Args:
            image_path: Ruta a la imagen
            duration: Duración del clip
        
        Returns:
            ImageClip
        """
        clip = ImageClip(str(image_path), duration=duration)
        clip = clip.resize(self.resolution)
        return clip
    
    def create_clip_from_frames(
        self,
        frames: List[Image.Image],
        temp_dir: Path
    ):
        """
        Crear clip de video desde frames.
        
        Args:
            frames: Lista de frames (imágenes PIL)
            temp_dir: Directorio temporal para guardar frames
        
        Returns:
            VideoClip concatenado
        """
        clips = []
        
        for i, frame in enumerate(frames):
            frame_path = temp_dir / f"temp_frame_{i:06d}.jpg"
            frame.save(frame_path, quality=95)
            
            clip = ImageClip(str(frame_path), duration=1/self.fps)
            clips.append(clip)
        
        # Concatenar clips
        video_clip = concatenate_videoclips(clips, method="compose")
        
        # Limpiar frames temporales
        for frame_path in temp_dir.glob("temp_frame_*.jpg"):
            frame_path.unlink()
        
        return video_clip
    
    def apply_fade(
        self,
        clip,
        fade_in: float = 0.3,
        fade_out: float = 0.3
    ):
        """
        Aplicar fade in/out a un clip.
        
        Args:
            clip: VideoClip
            fade_in: Duración de fade in
            fade_out: Duración de fade out
        
        Returns:
            Clip con fade aplicado
        """
        if fade_in > 0:
            clip = clip.fadein(fade_in)
        if fade_out > 0:
            clip = clip.fadeout(fade_out)
        return clip
    
    def write_video(
        self,
        clip,
        output_path: Path,
        audio: bool = False
    ) -> bool:
        """
        Escribir video a archivo.
        
        Args:
            clip: VideoClip a escribir
            output_path: Ruta de salida
            audio: Si True, incluir audio
        
        Returns:
            True si se escribió exitosamente
        """
        try:
            clip.write_videofile(
                str(output_path),
                fps=self.fps,
                codec=self.codec,
                preset=self.preset,
                bitrate=self.bitrate,
                audio=audio,
                logger=None
            )
            return True
        except Exception as e:
            logger.error(f"Error escribiendo video: {e}")
            return False
    
    def concatenate_clips(
        self,
        clips: List,
        method: str = "compose"
    ):
        """
        Concatenar múltiples clips.
        
        Args:
            clips: Lista de clips
            method: Método de concatenación
        
        Returns:
            Clip concatenado
        """
        return concatenate_videoclips(clips, method=method)







