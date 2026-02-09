"""
Script para crear videos cortos - Versión Refactorizada
========================================================
Versión refactorizada usando módulos de ai_video_generator.

Crea videos cortos a partir de imágenes usando moviepy o Grok API.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
import argparse
import logging

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Importar módulos refactorizados
try:
    from ai_video_generator import VideoProcessor
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    print("⚠ ai_video_generator no disponible. Ejecutar desde directorio scripts/")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GrokAPIClient:
    """Cliente para API de Grok (xAI)."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializar cliente Grok.
        
        Args:
            api_key: API key de xAI (opcional)
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                from xai import Grok
                self.client = Grok(api_key=self.api_key)
                logger.info("✓ Cliente Grok inicializado")
            except ImportError:
                logger.warning("⚠ xai-python no está instalado. Instala con: pip install xai-python")
            except Exception as e:
                logger.warning(f"⚠ Error inicializando Grok: {e}")
    
    def is_available(self) -> bool:
        """Verificar si Grok está disponible."""
        return self.client is not None
    
    def create_video(
        self,
        images: List[Path],
        output_path: Path,
        prompt: Optional[str] = None
    ) -> bool:
        """
        Crear video usando API de Grok.
        
        Args:
            images: Lista de rutas a imágenes
            output_path: Ruta de salida
            prompt: Prompt para generación
        
        Returns:
            True si se creó exitosamente
        """
        if not self.is_available():
            logger.warning("⚠ Grok no está disponible")
            return False
        
        try:
            if not prompt:
                prompt = (
                    f"Create a short engaging video from these {len(images)} Instagram images. "
                    f"Make it dynamic with smooth transitions, add subtle zoom effects, "
                    f"and create a cohesive visual story."
                )
            
            logger.info("📤 Intentando crear video con Grok API...")
            logger.warning("⚠ La generación de video con Grok API requiere configuración adicional")
            logger.info("💡 Usando moviepy como método alternativo...")
            
            # Nota: La API de Grok puede tener limitaciones para video generation
            # Por ahora, retornamos False para usar moviepy como fallback
            return False
            
        except Exception as e:
            logger.error(f"Error con API de Grok: {e}")
            return False


class VideoBatchProcessor:
    """Procesador de videos en lotes."""
    
    def __init__(
        self,
        output_dir: Path,
        duration_per_image: float = 3.0,
        resolution: tuple = (1080, 1080),
        fps: int = 24
    ):
        """
        Inicializar procesador.
        
        Args:
            output_dir: Directorio de salida
            duration_per_image: Duración por imagen
            resolution: Resolución del video
            fps: Frames por segundo
        """
        self.output_dir = output_dir
        self.duration_per_image = duration_per_image
        self.resolution = resolution
        self.fps = fps
        
        # Inicializar procesador de videos
        if MODULES_AVAILABLE:
            self.video_processor = VideoProcessor(
                output_dir=output_dir,
                resolution=resolution,
                fps=fps,
                duration_per_image=duration_per_image
            )
        else:
            self.video_processor = None
    
    def get_image_files(self, images_dir: Path) -> List[Path]:
        """
        Obtener archivos de imagen.
        
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
    
    def process_batch(
        self,
        images_dir: Path,
        videos_per_batch: int = 10,
        use_grok: bool = False,
        grok_client: Optional[GrokAPIClient] = None
    ) -> dict:
        """
        Procesar directorio de imágenes creando videos en lotes.
        
        Args:
            images_dir: Directorio con imágenes
            videos_per_batch: Imágenes por video
            use_grok: Si True, intenta usar Grok
            grok_client: Cliente Grok (opcional)
        
        Returns:
            Diccionario con estadísticas
        """
        if not MODULES_AVAILABLE:
            logger.error("❌ ai_video_generator no está disponible")
            return {'successful': 0, 'failed': 0, 'total': 0}
        
        # Obtener imágenes
        images = self.get_image_files(images_dir)
        
        logger.info(f"📸 Encontradas {len(images)} imágenes")
        logger.info(f"📁 Directorio: {images_dir}")
        logger.info(f"🎬 Creando videos de {videos_per_batch} imágenes cada uno...")
        
        # Crear videos en lotes
        total_videos = (len(images) + videos_per_batch - 1) // videos_per_batch
        successful = 0
        failed = 0
        
        for batch_num in range(total_videos):
            start_idx = batch_num * videos_per_batch
            end_idx = min(start_idx + videos_per_batch, len(images))
            batch_images = images[start_idx:end_idx]
            
            # Nombre del video
            video_name = f"video_batch_{batch_num + 1:03d}_{len(batch_images)}_images.mp4"
            video_path = self.output_dir / video_name
            
            logger.info(f"\n🎥 Procesando lote {batch_num + 1}/{total_videos}")
            logger.info(f"   Imágenes: {start_idx + 1}-{end_idx} de {len(images)}")
            
            # Intentar usar Grok si está habilitado
            success = False
            if use_grok and grok_client and grok_client.is_available():
                success = grok_client.create_video(batch_images, video_path)
            
            # Si Grok falla o no está habilitado, usar moviepy
            if not success:
                success = self.video_processor.create_compilation_video(
                    batch_images,
                    video_path,
                    use_ken_burns=False,  # Sin Ken Burns para videos simples
                    transition_duration=0.5
                )
            
            if success:
                logger.info(f"✅ Video {batch_num + 1} creado: {video_path.name}")
                successful += 1
            else:
                logger.error(f"❌ Error creando video {batch_num + 1}")
                failed += 1
        
        return {
            'successful': successful,
            'failed': failed,
            'total': total_videos
        }


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Crea videos cortos a partir de imágenes usando Grok o moviepy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Usar moviepy (método por defecto)
  python create_videos_from_images_grok_refactored.py
  
  # Especificar directorio de imágenes
  python create_videos_from_images_grok_refactored.py --images-dir ./instagram_downloads/mialay18
  
  # Crear videos más largos (5 segundos por imagen)
  python create_videos_from_images_grok_refactored.py --duration 5.0
  
  # Intentar usar API de Grok
  python create_videos_from_images_grok_refactored.py --use-grok --grok-api-key tu_api_key
  
  # Más imágenes por video
  python create_videos_from_images_grok_refactored.py --videos-per-batch 20
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
        help="Directorio donde guardar los videos (default: ./videos_mialay18)"
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
    
    if not MODULES_AVAILABLE:
        logger.error("❌ Error: ai_video_generator no está disponible")
        logger.error("   Asegúrate de estar en el directorio scripts/")
        sys.exit(1)
    
    # Configurar directorio de imágenes
    if args.images_dir:
        images_dir = Path(args.images_dir)
    else:
        script_dir = Path(__file__).parent
        images_dir = script_dir / "instagram_downloads" / "mialay18"
    
    if not images_dir.exists():
        logger.error(f"❌ Error: El directorio {images_dir} no existe")
        sys.exit(1)
    
    # Configurar directorio de salida
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = images_dir.parent / "videos_mialay18"
    
    # Inicializar cliente Grok si se solicita
    grok_client = None
    if args.use_grok:
        grok_client = GrokAPIClient(api_key=args.grok_api_key)
        if not grok_client.is_available():
            logger.warning("⚠ Grok no está disponible, usando moviepy")
    
    # Inicializar procesador
    processor = VideoBatchProcessor(
        output_dir=output_dir,
        duration_per_image=args.duration,
        resolution=(1080, 1080),
        fps=24
    )
    
    # Procesar
    stats = processor.process_batch(
        images_dir=images_dir,
        videos_per_batch=args.videos_per_batch,
        use_grok=args.use_grok,
        grok_client=grok_client
    )
    
    # Resumen
    logger.info(f"\n🎉 Proceso completado!")
    logger.info(f"📁 Videos guardados en: {output_dir.absolute()}")
    logger.info(f"✓ Videos creados exitosamente: {stats['successful']}")
    logger.info(f"⚠ Videos con errores: {stats['failed']}")


if __name__ == "__main__":
    main()







