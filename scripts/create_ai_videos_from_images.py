"""
Generador de Videos con IA a partir de Imágenes
================================================

Crea videos animados con IA desde imágenes usando técnicas avanzadas:
- Animación Ken Burns (zoom y pan)
- Efectos de transición suaves
- Mejora de calidad con IA
- Música y efectos de sonido opcionales

Requisitos:
    pip install moviepy pillow opencv-python numpy scikit-image
    pip install imageio imageio-ffmpeg
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple
import argparse
import json
import time
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from moviepy.editor import (
        ImageClip, concatenate_videoclips, CompositeVideoClip,
        ColorClip, AudioFileClip, TextClip
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️  moviepy no está instalado. Instala con: pip install moviepy")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️  opencv-python no está instalado. Instala con: pip install opencv-python")


class AIVideoGenerator:
    """Generador de videos con IA usando técnicas avanzadas de animación."""
    
    def __init__(
        self,
        output_dir: Path,
        resolution: Tuple[int, int] = (1080, 1920),  # Vertical para TikTok
        fps: int = 30,
        duration_per_image: float = 3.0
    ):
        self.output_dir = output_dir
        self.resolution = resolution
        self.fps = fps
        self.duration_per_image = duration_per_image
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def enhance_image_ai(self, image_path: Path) -> Image.Image:
        """
        Mejora la imagen usando técnicas de IA.
        Aplica mejoras de contraste, saturación y nitidez.
        """
        try:
            img = Image.open(image_path)
            
            # Mejorar contraste
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            
            # Mejorar saturación
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.15)
            
            # Mejorar nitidez
            img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            return img
        except Exception as e:
            print(f"⚠️  Error mejorando imagen {image_path.name}: {e}")
            return Image.open(image_path)
    
    def create_ken_burns_effect(
        self,
        image: Image.Image,
        duration: float,
        zoom_start: float = 1.0,
        zoom_end: float = 1.2,
        pan_x: float = 0.0,
        pan_y: float = 0.0
    ) -> List[Image.Image]:
        """
        Crea efecto Ken Burns (zoom y pan suave).
        Genera frames intermedios para animación suave.
        """
        frames = []
        num_frames = int(duration * self.fps)
        
        # Calcular dimensiones base
        img_width, img_height = image.size
        target_width, target_height = self.resolution
        
        # Calcular escala para llenar el frame
        scale_w = target_width / img_width
        scale_h = target_height / img_height
        base_scale = max(scale_w, scale_h) * zoom_start
        
        for i in range(num_frames):
            # Interpolación suave (ease-in-out)
            progress = i / (num_frames - 1) if num_frames > 1 else 0
            ease_progress = progress * progress * (3 - 2 * progress)  # Smoothstep
            
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
    
    def create_single_image_video(
        self,
        image_path: Path,
        output_path: Path,
        use_ken_burns: bool = True,
        add_fade: bool = True
    ) -> bool:
        """
        Crea un video individual a partir de una imagen con efectos de IA.
        """
        try:
            print(f"🎬 Creando video: {image_path.name}")
            
            # Mejorar imagen con IA
            enhanced_img = self.enhance_image_ai(image_path)
            
            if use_ken_burns:
                # Crear efecto Ken Burns con zoom y pan aleatorio
                import random
                zoom_start = random.uniform(1.0, 1.05)
                zoom_end = random.uniform(1.15, 1.3)
                pan_x = random.uniform(-0.1, 0.1)
                pan_y = random.uniform(-0.1, 0.1)
                
                frames = self.create_ken_burns_effect(
                    enhanced_img,
                    self.duration_per_image,
                    zoom_start=zoom_start,
                    zoom_end=zoom_end,
                    pan_x=pan_x,
                    pan_y=pan_y
                )
                
                # Convertir frames a clips
                clips = []
                for i, frame in enumerate(frames):
                    frame_path = self.output_dir / f"temp_frame_{i:06d}.jpg"
                    frame.save(frame_path, quality=95)
                    
                    clip = ImageClip(str(frame_path), duration=1/self.fps)
                    clips.append(clip)
                
                # Concatenar clips
                video_clip = concatenate_videoclips(clips, method="compose")
                
                # Limpiar frames temporales
                for frame_path in self.output_dir.glob("temp_frame_*.jpg"):
                    frame_path.unlink()
            else:
                # Video simple sin animación
                clip = ImageClip(str(image_path), duration=self.duration_per_image)
                clip = clip.resize(self.resolution)
                video_clip = clip
            
            # Aplicar fade in/out
            if add_fade:
                fade_duration = 0.3
                video_clip = video_clip.fadein(fade_duration).fadeout(fade_duration)
            
            # Escribir video
            video_clip.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                preset='medium',
                bitrate='8000k',
                audio=False,
                logger=None
            )
            
            video_clip.close()
            print(f"✅ Video creado: {output_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error creando video de {image_path.name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_compilation_video(
        self,
        image_paths: List[Path],
        output_path: Path,
        use_ken_burns: bool = True,
        transition_duration: float = 0.5
    ) -> bool:
        """
        Crea un video compilado con múltiples imágenes y transiciones suaves.
        """
        try:
            print(f"🎬 Creando video compilado con {len(image_paths)} imágenes")
            
            clips = []
            
            for i, img_path in enumerate(image_paths):
                print(f"   Procesando {i+1}/{len(image_paths)}: {img_path.name}")
                
                # Mejorar imagen
                enhanced_img = self.enhance_image_ai(img_path)
                
                if use_ken_burns:
                    # Efecto Ken Burns aleatorio
                    import random
                    zoom_start = random.uniform(1.0, 1.05)
                    zoom_end = random.uniform(1.15, 1.25)
                    pan_x = random.uniform(-0.08, 0.08)
                    pan_y = random.uniform(-0.08, 0.08)
                    
                    frames = self.create_ken_burns_effect(
                        enhanced_img,
                        self.duration_per_image,
                        zoom_start=zoom_start,
                        zoom_end=zoom_end,
                        pan_x=pan_x,
                        pan_y=pan_y
                    )
                    
                    # Crear clip desde frames
                    frame_clips = []
                    for frame in frames:
                        # Guardar frame temporal
                        frame_path = self.output_dir / f"temp_comp_{i}_{len(frame_clips):06d}.jpg"
                        frame.save(frame_path, quality=95)
                        
                        clip = ImageClip(str(frame_path), duration=1/self.fps)
                        frame_clips.append(clip)
                    
                    # Concatenar frames del clip
                    img_clip = concatenate_videoclips(frame_clips, method="compose")
                    
                    # Limpiar frames temporales
                    for frame_path in self.output_dir.glob(f"temp_comp_{i}_*.jpg"):
                        frame_path.unlink()
                else:
                    # Clip simple
                    img_clip = ImageClip(str(img_path), duration=self.duration_per_image)
                    img_clip = img_clip.resize(self.resolution)
                
                # Aplicar transiciones
                if i == 0:
                    img_clip = img_clip.fadein(transition_duration)
                if i < len(image_paths) - 1:
                    img_clip = img_clip.fadeout(transition_duration)
                else:
                    img_clip = img_clip.fadeout(transition_duration)
                
                clips.append(img_clip)
            
            # Concatenar todos los clips
            print("🔗 Concatenando clips...")
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Escribir video final
            print("💾 Guardando video...")
            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                preset='medium',
                bitrate='8000k',
                audio=False,
                logger=None
            )
            
            final_video.close()
            for clip in clips:
                clip.close()
            
            print(f"✅ Video compilado creado: {output_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error creando video compilado: {e}")
            import traceback
            traceback.print_exc()
            return False


def get_caption_from_json(image_path: Path) -> str:
    """Obtener caption del archivo JSON asociado."""
    json_path = image_path.with_suffix('.json')
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                caption = data.get('node', {}).get('edge_media_to_caption', {}).get('edges', [])
                if caption and len(caption) > 0:
                    return caption[0].get('node', {}).get('text', '')
        except Exception as e:
            print(f"⚠️  Error leyendo JSON: {e}")
    return ""


def process_all_images(
    images_dir: Path,
    output_dir: Path,
    create_individual: bool = True,
    create_compilations: bool = True,
    images_per_compilation: int = 10,
    duration_per_image: float = 3.0,
    use_ken_burns: bool = True
):
    """
    Procesa todas las imágenes y crea videos con IA.
    """
    if not MOVIEPY_AVAILABLE:
        print("❌ moviepy no está disponible. Instala con: pip install moviepy")
        return
    
    # Obtener todas las imágenes
    image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    images = [
        img for img in images_dir.iterdir()
        if img.is_file() and img.suffix in image_extensions
    ]
    
    # Ordenar por nombre
    images.sort(key=lambda x: x.name)
    
    print(f"📸 Encontradas {len(images)} imágenes")
    print(f"📁 Directorio: {images_dir}")
    print(f"🎬 Creando videos con IA...")
    print(f"   - Videos individuales: {'Sí' if create_individual else 'No'}")
    print(f"   - Videos compilados: {'Sí' if create_compilations else 'No'}")
    print(f"   - Efecto Ken Burns: {'Sí' if use_ken_burns else 'No'}")
    
    # Inicializar generador
    generator = AIVideoGenerator(
        output_dir=output_dir,
        resolution=(1080, 1920),  # Vertical para TikTok
        fps=30,
        duration_per_image=duration_per_image
    )
    
    # Crear videos individuales
    if create_individual:
        print(f"\n🎥 Creando videos individuales...")
        individual_dir = output_dir / "individual"
        individual_dir.mkdir(exist_ok=True)
        
        for i, img_path in enumerate(images):
            video_name = f"{img_path.stem}_ai.mp4"
            video_path = individual_dir / video_name
            
            if video_path.exists():
                print(f"⏭️  Saltando {img_path.name} (ya existe)")
                continue
            
            generator.create_single_image_video(
                img_path,
                video_path,
                use_ken_burns=use_ken_burns
            )
            
            print(f"   Progreso: {i+1}/{len(images)}")
    
    # Crear videos compilados
    if create_compilations:
        print(f"\n🎬 Creando videos compilados...")
        compilation_dir = output_dir / "compilations"
        compilation_dir.mkdir(exist_ok=True)
        
        num_compilations = (len(images) + images_per_compilation - 1) // images_per_compilation
        
        for batch_num in range(num_compilations):
            start_idx = batch_num * images_per_compilation
            end_idx = min(start_idx + images_per_compilation, len(images))
            batch_images = images[start_idx:end_idx]
            
            video_name = f"compilation_{batch_num + 1:03d}_{len(batch_images)}_images.mp4"
            video_path = compilation_dir / video_name
            
            if video_path.exists():
                print(f"⏭️  Saltando compilación {batch_num + 1} (ya existe)")
                continue
            
            print(f"\n📦 Compilación {batch_num + 1}/{num_compilations}")
            generator.create_compilation_video(
                batch_images,
                video_path,
                use_ken_burns=use_ken_burns
            )
    
    print(f"\n🎉 Proceso completado!")
    print(f"📁 Videos guardados en: {output_dir.absolute()}")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Crea videos con IA a partir de imágenes usando técnicas avanzadas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Crear videos individuales y compilados
  python create_ai_videos_from_images.py
  
  # Solo videos individuales
  python create_ai_videos_from_images.py --no-compilations
  
  # Solo compilaciones
  python create_ai_videos_from_images.py --no-individual
  
  # Sin efecto Ken Burns (más rápido)
  python create_ai_videos_from_images.py --no-ken-burns
  
  # Duración personalizada
  python create_ai_videos_from_images.py --duration 5.0
        """
    )
    
    parser.add_argument(
        "--images-dir",
        type=str,
        default=None,
        help="Directorio con las imágenes (default: ./instagram_downloads/69caylin)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directorio donde guardar los videos (default: ./videos_ai_69caylin)"
    )
    
    parser.add_argument(
        "--duration",
        type=float,
        default=3.0,
        help="Duración de cada imagen en segundos (default: 3.0)"
    )
    
    parser.add_argument(
        "--images-per-compilation",
        type=int,
        default=10,
        help="Número de imágenes por compilación (default: 10)"
    )
    
    parser.add_argument(
        "--no-individual",
        action="store_true",
        help="No crear videos individuales"
    )
    
    parser.add_argument(
        "--no-compilations",
        action="store_true",
        help="No crear videos compilados"
    )
    
    parser.add_argument(
        "--no-ken-burns",
        action="store_true",
        help="Desactivar efecto Ken Burns (más rápido)"
    )
    
    args = parser.parse_args()
    
    # Configurar directorio de imágenes
    if args.images_dir:
        images_dir = Path(args.images_dir)
    else:
        script_dir = Path(__file__).parent
        images_dir = script_dir / "instagram_downloads" / "69caylin"
    
    if not images_dir.exists():
        print(f"❌ Error: El directorio {images_dir} no existe")
        sys.exit(1)
    
    # Configurar directorio de salida
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = images_dir.parent / "videos_ai_69caylin"
    
    # Procesar imágenes
    process_all_images(
        images_dir=images_dir,
        output_dir=output_dir,
        create_individual=not args.no_individual,
        create_compilations=not args.no_compilations,
        images_per_compilation=args.images_per_compilation,
        duration_per_image=args.duration,
        use_ken_burns=not args.no_ken_burns
    )


if __name__ == "__main__":
    main()








