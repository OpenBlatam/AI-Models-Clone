"""
Script refactorizado para recortar videos a 30 segundos.
Usa los módulos refactorizados de video_processor.
"""
import logging
import sys
from pathlib import Path

from video_processor import VideoTrimmer

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DURATION = 30.0  # Duración objetivo en segundos


def check_ffmpeg() -> bool:
    """Verifica si ffmpeg está disponible."""
    try:
        from video_processor import VideoTrimmer
        trimmer = VideoTrimmer()
        return True
    except Exception:
        return False


def main():
    """Función principal."""
    # Directorio de entrada
    input_dir = r"C:\Users\blatam\Videos"
    
    # Directorio de salida (None para crear archivos con sufijo _trimmed)
    output_dir = None
    
    # Duración objetivo
    duration = DURATION
    
    logger.info("="*50)
    logger.info("Recortador de Videos - 30 segundos (Refactorizado)")
    logger.info("="*50)
    logger.info(f"Directorio: {input_dir}")
    logger.info(f"Duración objetivo: {duration} segundos")
    logger.info("")
    
    # Verificar ffmpeg
    if not check_ffmpeg():
        logger.error("ffmpeg no está disponible")
        logger.info("")
        logger.info("Para instalar ffmpeg en Windows:")
        logger.info("1. Descarga desde: https://www.gyan.dev/ffmpeg/builds/")
        logger.info("2. Extrae el archivo ZIP")
        logger.info("3. Agrega la carpeta 'bin' al PATH del sistema")
        logger.info("")
        logger.info("O instala usando chocolatey:")
        logger.info("  choco install ffmpeg")
        logger.info("")
        logger.info("O usando winget:")
        logger.info("  winget install ffmpeg")
        logger.info("")
        sys.exit(1)
    
    # Crear trimmer
    trimmer = VideoTrimmer(use_moviepy=False)
    
    # Procesar directorio
    stats = trimmer.trim_directory(
        input_directory=input_dir,
        output_directory=output_dir,
        duration=duration
    )
    
    logger.info("")
    logger.info("="*50)
    logger.info("Resumen:")
    logger.info(f"  ✓ Videos recortados exitosamente: {stats['successful']}")
    logger.info(f"  ✗ Videos fallidos: {stats['failed']}")
    logger.info(f"  📁 Total de videos: {stats['total']}")
    logger.info("="*50)


if __name__ == "__main__":
    main()




