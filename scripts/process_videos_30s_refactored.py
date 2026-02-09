"""
Script para procesar videos y dividirlos en clips - Versión Refactorizada
==========================================================================
Versión refactorizada usando módulos separados.
"""

import logging
from pathlib import Path
from video_processor import BatchVideoProcessor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CLIP_DURATION = 8  # Duración de cada clip en segundos


def main():
    """Función principal."""
    # Directorio de videos
    videos_dir = r"C:\Users\blatam\Videos"
    
    logger.info("="*50)
    logger.info("Procesador de Videos - Clips de 8 segundos (Refactorizado)")
    logger.info("="*50)
    logger.info(f"Directorio: {videos_dir}")
    logger.info(f"Duración por clip: {CLIP_DURATION} segundos")
    logger.info("")
    
    # Crear procesador batch
    processor = BatchVideoProcessor(clip_duration=CLIP_DURATION)
    
    # Procesar solo los videos en el directorio raíz (no recursivo)
    stats = processor.process_directory(videos_dir, recursive=False)
    
    logger.info("")
    logger.info(f"Estadísticas finales: {stats}")


if __name__ == "__main__":
    main()






