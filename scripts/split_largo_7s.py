"""
Script refactorizado para dividir el video 'largo.mp4' en clips de 7 segundos.
Usa los módulos refactorizados de video_processor.
"""
import logging
from pathlib import Path

from video_processor import (
    VideoSplitterWithEditing,
    DEFAULT_EDITING_CONFIG,
    DEFAULT_VIDEOS_DIR
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CLIP_DURATION = 7.0


def main():
    """Función principal."""
    # Ruta al video largo
    video_path = Path(DEFAULT_VIDEOS_DIR) / "largo.mp4"
    
    if not video_path.exists():
        logger.error(f"El archivo no existe: {video_path}")
        return
    
    logger.info("="*50)
    logger.info("Dividiendo video 'largo.mp4' en clips de 7 segundos")
    logger.info("="*50)
    logger.info(f"Video: {video_path}")
    logger.info("")
    
    # Crear splitter con edición
    splitter = VideoSplitterWithEditing(
        clip_duration=CLIP_DURATION,
        editing_config=DEFAULT_EDITING_CONFIG
    )
    
    # Procesar el video (los clips se guardarán en el mismo directorio)
    clips_created = splitter.split_video_with_editing(video_path)
    
    if clips_created > 0:
        logger.info("")
        logger.info("="*50)
        logger.info(f"✓ Proceso completado: {clips_created} clips creados")
        logger.info(f"✓ Los clips están en: {video_path_obj.parent}")
        logger.info("="*50)
    else:
        logger.error("✗ Error: No se pudieron crear los clips")


if __name__ == "__main__":
    main()




