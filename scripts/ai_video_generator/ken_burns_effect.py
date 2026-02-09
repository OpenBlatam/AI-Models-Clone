"""
Ken Burns Effect
================
Efecto Ken Burns (zoom y pan suave) para animación de imágenes.
"""

import logging
import random
from pathlib import Path
from typing import List, Tuple
from PIL import Image

logger = logging.getLogger(__name__)


class KenBurnsEffect:
    """Generador de efecto Ken Burns (zoom y pan)."""
    
    def __init__(
        self,
        resolution: Tuple[int, int] = (1080, 1920),
        fps: int = 30
    ):
        """
        Inicializar generador de efecto Ken Burns.
        
        Args:
            resolution: Resolución objetivo (ancho, alto)
            fps: Frames por segundo
        """
        self.resolution = resolution
        self.fps = fps
    
    def generate_frames(
        self,
        image: Image.Image,
        duration: float,
        zoom_start: float = 1.0,
        zoom_end: float = 1.2,
        pan_x: float = 0.0,
        pan_y: float = 0.0
    ) -> List[Image.Image]:
        """
        Generar frames para efecto Ken Burns.
        
        Args:
            image: Imagen a animar
            duration: Duración en segundos
            zoom_start: Zoom inicial
            zoom_end: Zoom final
            pan_x: Pan horizontal (-1 a 1)
            pan_y: Pan vertical (-1 a 1)
        
        Returns:
            Lista de frames (imágenes PIL)
        """
        frames = []
        num_frames = int(duration * self.fps)
        
        if num_frames == 0:
            return frames
        
        # Calcular dimensiones
        img_width, img_height = image.size
        target_width, target_height = self.resolution
        
        # Calcular escala base para llenar el frame
        scale_w = target_width / img_width
        scale_h = target_height / img_height
        base_scale = max(scale_w, scale_h) * zoom_start
        
        for i in range(num_frames):
            # Interpolación suave (ease-in-out usando smoothstep)
            progress = i / (num_frames - 1) if num_frames > 1 else 0
            ease_progress = progress * progress * (3 - 2 * progress)
            
            # Calcular zoom actual
            current_zoom = zoom_start + (zoom_end - zoom_start) * ease_progress
            current_scale = base_scale * current_zoom
            
            # Calcular pan actual
            current_pan_x = pan_x * ease_progress
            current_pan_y = pan_y * ease_progress
            
            # Redimensionar imagen
            new_width = int(img_width * current_scale)
            new_height = int(img_height * current_scale)
            scaled_img = image.resize((new_width, new_height), Image.LANCZOS)
            
            # Crear frame del tamaño objetivo
            frame = Image.new('RGB', (target_width, target_height), (0, 0, 0))
            
            # Calcular posición para centrar con pan
            x_offset = (target_width - new_width) // 2 + int(current_pan_x * target_width)
            y_offset = (target_height - new_height) // 2 + int(current_pan_y * target_height)
            
            # Pegar imagen en el frame
            frame.paste(scaled_img, (x_offset, y_offset))
            
            frames.append(frame)
        
        return frames
    
    def generate_random_params(
        self,
        zoom_start_range: Tuple[float, float] = (1.0, 1.05),
        zoom_end_range: Tuple[float, float] = (1.15, 1.3),
        pan_range: Tuple[float, float] = (-0.1, 0.1)
    ) -> dict:
        """
        Generar parámetros aleatorios para efecto Ken Burns.
        
        Args:
            zoom_start_range: Rango para zoom inicial
            zoom_end_range: Rango para zoom final
            pan_range: Rango para pan (x e y)
        
        Returns:
            Diccionario con parámetros
        """
        return {
            'zoom_start': random.uniform(*zoom_start_range),
            'zoom_end': random.uniform(*zoom_end_range),
            'pan_x': random.uniform(*pan_range),
            'pan_y': random.uniform(*pan_range)
        }







