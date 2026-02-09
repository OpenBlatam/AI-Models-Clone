"""
Script para crear videos cortos a partir de imágenes usando Grok (xAI)
========================================================================

Este script toma las imágenes descargadas de Instagram y crea videos cortos
usando la API de Grok (xAI) o moviepy como alternativa.

Requisitos:
    pip install xai-python moviepy pillow openai-whisper

Uso:
    python create_videos_from_images_grok.py
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
import argparse
from PIL import Image
import time

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def create_video_with_moviepy(
    images: List[Path],
    output_path: Path,
    duration_per_image: float = 3.0,
    fps: int = 24,
    transition_duration: float = 0.5,
    resolution: tuple = (1080, 1080)
) -> bool:
    """
    Crea un video a partir de imágenes usando moviepy.
    
    Args:
        images: Lista de rutas a imágenes
        output_path: Ruta donde guardar el video
        duration_per_image: Duración de cada imagen en segundos
        fps: Frames por segundo
        transition_duration: Duración de las transiciones
        resolution: Resolución del video (ancho, alto)
    """
    try:
        from moviepy import ImageClip, concatenate_videoclips, ColorClip, CompositeVideoClip
        
        print(f"🎬 Creando video con {len(images)} imágenes...")
        print(f"📁 Salida: {output_path}")
        
        clips = []
        
        for i, img_path in enumerate(images):
            try:
                # Crear clip de imagen
                clip = ImageClip(str(img_path), duration=duration_per_image)
                
                # Redimensionar si es necesario
                from PIL import Image
                img = Image.open(img_path)
                img_width, img_height = img.size
                
                # Calcular escala para mantener aspecto y llenar el frame
                scale_w = resolution[0] / img_width
                scale_h = resolution[1] / img_height
                scale = max(scale_w, scale_h)  # Usar max para llenar el frame
                
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                clip = clip.resized((new_width, new_height))
                
                # Centrar en el frame
                x_center = (resolution[0] - new_width) // 2
                y_center = (resolution[1] - new_height) // 2
                clip = clip.set_position((x_center, y_center))
                
                # Crear clip con fondo negro del tamaño correcto
                bg = ColorClip(size=resolution, color=(0, 0, 0), duration=duration_per_image)
                clip = CompositeVideoClip([bg, clip], size=resolution)
                
                # Aplicar fade in/out para transiciones suaves
                if i > 0:
                    clip = clip.fadein(transition_duration)
                if i < len(images) - 1:
                    clip = clip.fadeout(transition_duration)
                
                clips.append(clip)
                
                print(f"✅ Procesada imagen {i+1}/{len(images)}: {img_path.name}")
                
            except Exception as e:
                print(f"⚠️  Error procesando {img_path.name}: {e}")
                continue
        
        if not clips:
            print("❌ No se pudieron procesar imágenes")
            return False
        
        # Concatenar clips
        print("🔗 Concatenando clips...")
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Escribir video
        print("💾 Guardando video...")
        final_clip.write_videofile(
            str(output_path),
            fps=fps,
            codec='libx264',
            audio=False,
            preset='medium',
            bitrate='8000k',
            logger=None  # Reducir output
        )
        
        # Cerrar clips para liberar memoria
        final_clip.close()
        for clip in clips:
            clip.close()
        
        print(f"✅ Video creado exitosamente: {output_path}")
        return True
        
    except ImportError:
        print("❌ Error: moviepy no está instalado")
        print("💡 Instala con: pip install moviepy")
        return False
    except Exception as e:
        print(f"❌ Error creando video: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_video_with_grok_api(
    images: List[Path],
    output_path: Path,
    api_key: Optional[str] = None,
    prompt: Optional[str] = None
) -> bool:
    """
    Crea un video usando la API de Grok (xAI).
    
    Args:
        images: Lista de rutas a imágenes
        output_path: Ruta donde guardar el video
        api_key: API key de xAI (opcional, puede estar en variable de entorno)
        prompt: Prompt para la generación del video
    """
    try:
        from xai import Grok
        
        # Obtener API key
        if not api_key:
            api_key = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
        
        if not api_key:
            print("⚠️  No se encontró API key de Grok")
            print("💡 Establece la variable de entorno XAI_API_KEY o GROK_API_KEY")
            return False
        
        print(f"🤖 Usando API de Grok para crear video...")
        
        # Inicializar cliente Grok
        grok = Grok(api_key=api_key)
        
        # Crear prompt si no se proporciona
        if not prompt:
            prompt = f"Create a short engaging video from these {len(images)} Instagram images. Make it dynamic with smooth transitions, add subtle zoom effects, and create a cohesive visual story."
        
        # Procesar imágenes (convertir a base64 o subir)
        print("📤 Subiendo imágenes a Grok...")
        
        # Nota: La API de Grok puede tener limitaciones para video generation
        # Por ahora, usaremos moviepy como método principal
        print("⚠️  La generación de video con Grok API requiere configuración adicional")
        print("💡 Usando moviepy como método alternativo...")
        return False
        
    except ImportError:
        print("⚠️  xai-python no está instalado")
        print("💡 Instala con: pip install xai-python")
        return False
    except Exception as e:
        print(f"⚠️  Error con API de Grok: {e}")
        return False


def process_images_directory(
    images_dir: Path,
    output_dir: Optional[Path] = None,
    videos_per_batch: int = 10,
    duration_per_image: float = 3.0,
    use_grok: bool = False,
    grok_api_key: Optional[str] = None
) -> None:
    """
    Procesa todas las imágenes en un directorio y crea videos cortos.
    
    Args:
        images_dir: Directorio con las imágenes
        output_dir: Directorio donde guardar los videos
        videos_per_batch: Número de imágenes por video
        duration_per_image: Duración de cada imagen en segundos
        use_grok: Si True, intenta usar API de Grok
        grok_api_key: API key de Grok (opcional)
    """
    # Configurar directorio de salida (carpeta separada)
    if output_dir is None:
        # Crear carpeta "videos" al mismo nivel que la carpeta de imágenes
        output_dir = images_dir.parent / "videos_mialay18"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Obtener todas las imágenes
    image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    images = [
        img for img in images_dir.iterdir()
        if img.is_file() and img.suffix in image_extensions
    ]
    
    # Ordenar por nombre (fecha)
    images.sort(key=lambda x: x.name)
    
    print(f"📸 Encontradas {len(images)} imágenes")
    print(f"📁 Directorio: {images_dir}")
    print(f"🎬 Creando videos de {videos_per_batch} imágenes cada uno...")
    
    # Crear videos en lotes
    total_videos = (len(images) + videos_per_batch - 1) // videos_per_batch
    
    for batch_num in range(total_videos):
        start_idx = batch_num * videos_per_batch
        end_idx = min(start_idx + videos_per_batch, len(images))
        batch_images = images[start_idx:end_idx]
        
        # Nombre del video
        video_name = f"video_batch_{batch_num + 1:03d}_{len(batch_images)}_images.mp4"
        video_path = output_dir / video_name
        
        print(f"\n🎥 Procesando lote {batch_num + 1}/{total_videos}")
        print(f"   Imágenes: {start_idx + 1}-{end_idx} de {len(images)}")
        
        # Intentar usar Grok si está habilitado
        success = False
        if use_grok:
            success = create_video_with_grok_api(
                batch_images,
                video_path,
                grok_api_key
            )
        
        # Si Grok falla o no está habilitado, usar moviepy
        if not success:
            success = create_video_with_moviepy(
                batch_images,
                video_path,
                duration_per_image=duration_per_image
            )
        
        if success:
            print(f"✅ Video {batch_num + 1} creado: {video_path.name}")
        else:
            print(f"❌ Error creando video {batch_num + 1}")
    
    print(f"\n🎉 Proceso completado!")
    print(f"📁 Videos guardados en: {output_dir.absolute()}")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Crea videos cortos a partir de imágenes usando Grok o moviepy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Usar moviepy (método por defecto)
  python create_videos_from_images_grok.py
  
  # Especificar directorio de imágenes
  python create_videos_from_images_grok.py --images-dir ./instagram_downloads/mialay18
  
  # Crear videos más largos (5 segundos por imagen)
  python create_videos_from_images_grok.py --duration 5.0
  
  # Intentar usar API de Grok
  python create_videos_from_images_grok.py --use-grok --grok-api-key tu_api_key
  
  # Más imágenes por video
  python create_videos_from_images_grok.py --videos-per-batch 20
        """
    )
    
    parser.add_argument(
        "--images-dir",
        type=str,
        default=None,
        help="Directorio con las imágenes (default: ./instagram_downloads/mialay18)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directorio donde guardar los videos (default: ./videos)"
    )
    
    parser.add_argument(
        "--videos-per-batch",
        type=int,
        default=10,
        help="Número de imágenes por video (default: 10)"
    )
    
    parser.add_argument(
        "--duration",
        type=float,
        default=3.0,
        help="Duración de cada imagen en segundos (default: 3.0)"
    )
    
    parser.add_argument(
        "--use-grok",
        action="store_true",
        help="Intentar usar API de Grok (requiere XAI_API_KEY)"
    )
    
    parser.add_argument(
        "--grok-api-key",
        type=str,
        default=None,
        help="API key de Grok (opcional, puede estar en XAI_API_KEY)"
    )
    
    args = parser.parse_args()
    
    # Configurar directorio de imágenes
    if args.images_dir:
        images_dir = Path(args.images_dir)
    else:
        # Buscar en el directorio de scripts
        script_dir = Path(__file__).parent
        images_dir = script_dir / "instagram_downloads" / "mialay18"
    
    if not images_dir.exists():
        print(f"❌ Error: El directorio {images_dir} no existe")
        sys.exit(1)
    
    # Configurar directorio de salida
    output_dir = Path(args.output_dir) if args.output_dir else None
    
    # Procesar imágenes
    process_images_directory(
        images_dir=images_dir,
        output_dir=output_dir,
        videos_per_batch=args.videos_per_batch,
        duration_per_image=args.duration,
        use_grok=args.use_grok,
        grok_api_key=args.grok_api_key
    )


if __name__ == "__main__":
    main()








