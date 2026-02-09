"""
Video Trimmer
=============
Recorta videos a una duración específica.
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional
import imageio_ffmpeg

from .video_info import VideoInfoExtractor

logger = logging.getLogger(__name__)


class VideoTrimmer:
    """Recorta videos a una duración específica."""
    
    def __init__(self, use_moviepy: bool = False):
        """
        Inicializar trimmer.
        
        Args:
            use_moviepy: Si True, usa moviepy en lugar de ffmpeg
        """
        self.use_moviepy = use_moviepy
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        self.info_extractor = VideoInfoExtractor()
        
        if use_moviepy:
            try:
                from moviepy import VideoFileClip
                self.VideoFileClip = VideoFileClip
                self.moviepy_available = True
            except ImportError:
                try:
                    from moviepy.editor import VideoFileClip
                    self.VideoFileClip = VideoFileClip
                    self.moviepy_available = True
                except ImportError:
                    self.moviepy_available = False
                    logger.warning("MoviePy no disponible, usando ffmpeg")
                    self.use_moviepy = False
        else:
            self.moviepy_available = False
    
    def trim_video_ffmpeg(
        self,
        input_path: Path,
        output_path: Path,
        duration: float = 30.0
    ) -> bool:
        """
        Recorta un video usando ffmpeg.
        
        Args:
            input_path: Ruta del video de entrada
            output_path: Ruta del video de salida
            duration: Duración en segundos
        
        Returns:
            True si fue exitoso
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", str(input_path),
                "-t", str(duration),
                "-c", "copy",
                "-avoid_negative_ts", "make_zero",
                "-y",
                str(output_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error al recortar video: {e.stderr[:200]}")
            return False
        except Exception as e:
            logger.error(f"Error al recortar video: {str(e)}")
            return False
    
    def trim_video_moviepy(
        self,
        input_path: Path,
        output_path: Path,
        duration: float = 30.0
    ) -> bool:
        """
        Recorta un video usando moviepy.
        
        Args:
            input_path: Ruta del video de entrada
            output_path: Ruta del video de salida
            duration: Duración en segundos
        
        Returns:
            True si fue exitoso
        """
        if not self.moviepy_available:
            logger.error("MoviePy no disponible")
            return False
        
        try:
            video = self.VideoFileClip(str(input_path))
            video_duration = video.duration
            trim_duration = min(duration, video_duration)
            
            trimmed_video = video.subclip(0, trim_duration)
            
            trimmed_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                logger=None
            )
            
            trimmed_video.close()
            video.close()
            
            return True
        except Exception as e:
            logger.error(f"Error al recortar video: {e}")
            return False
    
    def trim_video(
        self,
        input_path: Path,
        output_path: Path,
        duration: float = 30.0
    ) -> bool:
        """
        Recorta un video a la duración especificada.
        
        Args:
            input_path: Ruta del video de entrada
            output_path: Ruta del video de salida
            duration: Duración en segundos
        
        Returns:
            True si fue exitoso
        """
        if self.use_moviepy and self.moviepy_available:
            return self.trim_video_moviepy(input_path, output_path, duration)
        else:
            return self.trim_video_ffmpeg(input_path, output_path, duration)
    
    def trim_directory(
        self,
        input_directory: str,
        output_directory: Optional[str] = None,
        duration: float = 30.0,
        video_extensions: Optional[list] = None
    ) -> dict:
        """
        Recorta todos los videos en un directorio.
        
        Args:
            input_directory: Directorio con videos de entrada
            output_directory: Directorio para videos de salida (si es None, sobrescribe)
            duration: Duración objetivo en segundos
            video_extensions: Extensiones de video a procesar
        
        Returns:
            Diccionario con estadísticas
        """
        if video_extensions is None:
            video_extensions = ['.mp4', '.MP4', '.mov', '.MOV', '.avi', '.AVI', '.mkv', '.MKV']
        
        input_dir = Path(input_directory)
        if not input_dir.exists():
            logger.error(f"El directorio no existe: {input_directory}")
            return {
                'successful': 0,
                'failed': 0,
                'total': 0
            }
        
        # Buscar archivos de video
        video_files = []
        for ext in video_extensions:
            video_files.extend(input_dir.glob(f"*{ext}"))
        
        video_files = sorted(video_files)
        
        if not video_files:
            logger.info("No se encontraron videos para procesar.")
            return {
                'successful': 0,
                'failed': 0,
                'total': 0
            }
        
        logger.info(f"Se encontraron {len(video_files)} video(s) para recortar")
        
        successful = 0
        failed = 0
        
        for video_file in video_files:
            # Determinar ruta de salida
            if output_directory:
                output_dir = Path(output_directory)
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"{video_file.stem}_trimmed{video_file.suffix}"
            else:
                output_path = video_file.parent / f"{video_file.stem}_trimmed{video_file.suffix}"
            
            logger.info(f"Recortando: {video_file.name}")
            
            # Obtener duración del video
            video_duration = self.info_extractor.get_duration(str(video_file))
            if video_duration > 0:
                logger.info(f"  Duración original: {video_duration:.2f}s")
                trim_duration = min(duration, video_duration)
                logger.info(f"  Recortando a: {trim_duration:.2f}s")
            else:
                trim_duration = duration
            
            # Recortar video
            if self.trim_video(video_file, output_path, trim_duration):
                successful += 1
                logger.info(f"  ✓ Video recortado: {output_path.name}")
            else:
                failed += 1
                logger.error(f"  ✗ Error recortando: {video_file.name}")
        
        logger.info("="*50)
        logger.info(f"Procesamiento completado:")
        logger.info(f"  ✓ Videos recortados exitosamente: {successful}")
        logger.info(f"  ✗ Videos fallidos: {failed}")
        logger.info(f"  📁 Total de videos: {len(video_files)}")
        
        return {
            'successful': successful,
            'failed': failed,
            'total': len(video_files)
        }






