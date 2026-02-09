"""
Video Processor
===============
Procesamiento de lotes de imágenes para crear videos.
"""

import logging
from pathlib import Path
from typing import List, Optional

from .image_enhancer import ImageEnhancer
from .ken_burns_effect import KenBurnsEffect
from .video_composer import VideoComposer
from .caption_extractor import CaptionExtractor

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Procesador de videos en lotes."""
    
    def __init__(
        self,
        output_dir: Path,
        resolution: tuple = (1080, 1920),
        fps: int = 30,
        duration_per_image: float = 3.0
    ):
        """
        Inicializar procesador de videos.
        
        Args:
            output_dir: Directorio de salida
            resolution: Resolución del video
            fps: Frames por segundo
            duration_per_image: Duración por imagen
        """
        self.output_dir = output_dir
        self.resolution = resolution
        self.fps = fps
        self.duration_per_image = duration_per_image
        
        # Inicializar componentes
        self.image_enhancer = ImageEnhancer()
        self.ken_burns = KenBurnsEffect(resolution, fps)
        self.video_composer = VideoComposer(resolution, fps)
        self.caption_extractor = CaptionExtractor()
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_image_files(self, images_dir: Path) -> List[Path]:
        """
        Obtener lista de archivos de imagen.
        
        Args:
            images_dir: Directorio con imágenes
        
        Returns:
            Lista de paths a imágenes
        """
        image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
        images = [
            img for img in images_dir.iterdir()
            if img.is_file() and img.suffix in image_extensions
        ]
        return sorted(images, key=lambda x: x.name)
    
    def create_single_video(
        self,
        image_path: Path,
        output_path: Path,
        use_ken_burns: bool = True,
        add_fade: bool = True
    ) -> bool:
        """
        Crear video individual desde una imagen.
        
        Args:
            image_path: Ruta a la imagen
            output_path: Ruta de salida del video
            use_ken_burns: Si True, usar efecto Ken Burns
            add_fade: Si True, agregar fade in/out
        
        Returns:
            True si se creó exitosamente
        """
        try:
            logger.info(f"🎬 Creando video: {image_path.name}")
            
            # Mejorar imagen
            enhanced_img = self.image_enhancer.enhance(image_path)
            if not enhanced_img:
                logger.error(f"Error mejorando imagen: {image_path.name}")
                return False
            
            if use_ken_burns:
                # Generar parámetros aleatorios
                params = self.ken_burns.generate_random_params()
                
                # Crear frames con efecto Ken Burns
                frames = self.ken_burns.generate_frames(
                    enhanced_img,
                    self.duration_per_image,
                    **params
                )
                
                # Crear clip desde frames
                video_clip = self.video_composer.create_clip_from_frames(
                    frames,
                    self.output_dir
                )
            else:
                # Video simple sin animación
                video_clip = self.video_composer.create_clip_from_image(
                    image_path,
                    self.duration_per_image
                )
            
            # Aplicar fade
            if add_fade:
                video_clip = self.video_composer.apply_fade(video_clip)
            
            # Escribir video
            success = self.video_composer.write_video(video_clip, output_path)
            
            video_clip.close()
            
            if success:
                logger.info(f"✅ Video creado: {output_path.name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error creando video de {image_path.name}: {e}")
            return False
    
    def create_compilation_video(
        self,
        image_paths: List[Path],
        output_path: Path,
        use_ken_burns: bool = True,
        transition_duration: float = 0.5
    ) -> bool:
        """
        Crear video compilado con múltiples imágenes.
        
        Args:
            image_paths: Lista de rutas a imágenes
            output_path: Ruta de salida del video
            use_ken_burns: Si True, usar efecto Ken Burns
            transition_duration: Duración de transiciones
        
        Returns:
            True si se creó exitosamente
        """
        try:
            logger.info(f"🎬 Creando video compilado con {len(image_paths)} imágenes")
            
            clips = []
            
            for i, img_path in enumerate(image_paths):
                logger.info(f"   Procesando {i+1}/{len(image_paths)}: {img_path.name}")
                
                # Mejorar imagen
                enhanced_img = self.image_enhancer.enhance(img_path)
                if not enhanced_img:
                    continue
                
                if use_ken_burns:
                    # Efecto Ken Burns con parámetros aleatorios
                    params = self.ken_burns.generate_random_params(
                        zoom_end_range=(1.15, 1.25),
                        pan_range=(-0.08, 0.08)
                    )
                    
                    frames = self.ken_burns.generate_frames(
                        enhanced_img,
                        self.duration_per_image,
                        **params
                    )
                    
                    # Crear clip desde frames
                    img_clip = self.video_composer.create_clip_from_frames(
                        frames,
                        self.output_dir
                    )
                else:
                    # Clip simple
                    img_clip = self.video_composer.create_clip_from_image(
                        img_path,
                        self.duration_per_image
                    )
                
                # Aplicar transiciones
                if i == 0:
                    img_clip = self.video_composer.apply_fade(
                        img_clip,
                        fade_in=transition_duration,
                        fade_out=0
                    )
                elif i < len(image_paths) - 1:
                    img_clip = self.video_composer.apply_fade(
                        img_clip,
                        fade_in=0,
                        fade_out=transition_duration
                    )
                else:
                    img_clip = self.video_composer.apply_fade(
                        img_clip,
                        fade_in=0,
                        fade_out=transition_duration
                    )
                
                clips.append(img_clip)
            
            # Concatenar todos los clips
            logger.info("🔗 Concatenando clips...")
            final_video = self.video_composer.concatenate_clips(clips)
            
            # Escribir video final
            logger.info("💾 Guardando video...")
            success = self.video_composer.write_video(final_video, output_path)
            
            final_video.close()
            for clip in clips:
                clip.close()
            
            if success:
                logger.info(f"✅ Video compilado creado: {output_path.name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error creando video compilado: {e}")
            return False







