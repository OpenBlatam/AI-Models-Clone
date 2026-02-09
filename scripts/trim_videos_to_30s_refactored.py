"""
Script para recortar videos a 30 segundos - Versión Refactorizada
===================================================================
Versión refactorizada usando módulos separados.
"""

import logging
from pathlib import Path
from video_processor import VideoTrimmer

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DURATION = 30.0  # Duración objetivo en segundos


def main():
    """Función principal."""
    import sys
    
    # Directorio de videos (puede pasarse como argumento)
    if len(sys.argv) > 1:
        input_directory = sys.argv[1]
    else:
        input_directory = r"C:\Users\blatam\Videos"
    
    # Directorio de salida (opcional)
    output_directory = None
    if len(sys.argv) > 2:
        output_directory = sys.argv[2]
    
    logger.info("="*50)
    logger.info("Recortador de Videos a 30 segundos (Refactorizado)")
    logger.info("="*50)
    logger.info(f"Directorio de entrada: {input_directory}")
    if output_directory:
        logger.info(f"Directorio de salida: {output_directory}")
    else:
        logger.info("Los videos se guardarán en el mismo directorio con sufijo '_trimmed'")
    logger.info(f"Duración objetivo: {DURATION} segundos")
    logger.info("")
    
    # Crear trimmer
    trimmer = VideoTrimmer(use_moviepy=False)
    
    # Procesar videos
    stats = trimmer.trim_directory(
        input_directory=input_directory,
        output_directory=output_directory,
        duration=DURATION
    )
    
    logger.info("")
    logger.info(f"Estadísticas finales: {stats}")


if __name__ == "__main__":
    main()






