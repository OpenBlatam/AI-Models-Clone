"""
Generador de Videos con IA - Versión Refactorizada
==================================================
Versión refactorizada usando módulos separados.

Crea videos animados con IA desde imágenes usando técnicas avanzadas:
- Animación Ken Burns (zoom y pan)
- Efectos de transición suaves
- Mejora de calidad con IA
"""

import sys
import logging
from pathlib import Path
import argparse

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from ai_video_generator import VideoProcessor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
    
    Args:
        images_dir: Directorio con imágenes
        output_dir: Directorio de salida
        create_individual: Si True, crear videos individuales
        create_compilations: Si True, crear videos compilados
        images_per_compilation: Imágenes por compilación
        duration_per_image: Duración por imagen
        use_ken_burns: Si True, usar efecto Ken Burns
    """
    try:
        # Inicializar procesador
        processor = VideoProcessor(
            output_dir=output_dir,
            resolution=(1080, 1920),  # Vertical para TikTok
            fps=30,
            duration_per_image=duration_per_image
        )
        
        # Obtener imágenes
        images = processor.get_image_files(images_dir)
        
        logger.info(f"📸 Encontradas {len(images)} imágenes")
        logger.info(f"📁 Directorio: {images_dir}")
        logger.info(f"🎬 Creando videos con IA...")
        logger.info(f"   - Videos individuales: {'Sí' if create_individual else 'No'}")
        logger.info(f"   - Videos compilados: {'Sí' if create_compilations else 'No'}")
        logger.info(f"   - Efecto Ken Burns: {'Sí' if use_ken_burns else 'No'}")
        
        # Crear videos individuales
        if create_individual:
            logger.info(f"\n🎥 Creando videos individuales...")
            individual_dir = output_dir / "individual"
            individual_dir.mkdir(exist_ok=True)
            
            for i, img_path in enumerate(images):
                video_name = f"{img_path.stem}_ai.mp4"
                video_path = individual_dir / video_name
                
                if video_path.exists():
                    logger.info(f"⏭️  Saltando {img_path.name} (ya existe)")
                    continue
                
                processor.create_single_video(
                    img_path,
                    video_path,
                    use_ken_burns=use_ken_burns
                )
                
                logger.info(f"   Progreso: {i+1}/{len(images)}")
        
        # Crear videos compilados
        if create_compilations:
            logger.info(f"\n🎬 Creando videos compilados...")
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
                    logger.info(f"⏭️  Saltando compilación {batch_num + 1} (ya existe)")
                    continue
                
                logger.info(f"\n📦 Compilación {batch_num + 1}/{num_compilations}")
                processor.create_compilation_video(
                    batch_images,
                    video_path,
                    use_ken_burns=use_ken_burns
                )
        
        logger.info(f"\n🎉 Proceso completado!")
        logger.info(f"📁 Videos guardados en: {output_dir.absolute()}")
        
    except Exception as e:
        logger.error(f"Error en procesamiento: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Crea videos con IA a partir de imágenes usando técnicas avanzadas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Crear videos individuales y compilados
  python create_ai_videos_from_images_refactored.py
  
  # Solo videos individuales
  python create_ai_videos_from_images_refactored.py --no-compilations
  
  # Solo compilaciones
  python create_ai_videos_from_images_refactored.py --no-individual
  
  # Sin efecto Ken Burns (más rápido)
  python create_ai_videos_from_images_refactored.py --no-ken-burns
  
  # Duración personalizada
  python create_ai_videos_from_images_refactored.py --duration 5.0
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
        logger.error(f"❌ Error: El directorio {images_dir} no existe")
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







