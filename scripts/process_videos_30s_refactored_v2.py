"""
Script refactorizado para procesar videos y dividirlos en clips de 8 segundos.
Usa los módulos refactorizados de video_processor.
"""
import logging
from pathlib import Path

from video_processor import VideoSplitter

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CLIP_DURATION = 8.0  # Duración de cada clip en segundos


def process_video_to_8s_clips(
    video_path: str,
    output_dir: Path = None
) -> int:
    """
    Divide un video en clips de 8 segundos.
    
    Args:
        video_path: Ruta al video original
        output_dir: Directorio de salida (si es None, usa el mismo del video)
    
    Returns:
        Número de clips creados exitosamente, 0 si hubo error
    """
    splitter = VideoSplitter(clip_duration=CLIP_DURATION)
    return splitter.split_video(video_path, output_dir=output_dir)


def process_directory(
    directory_path: str,
    recursive: bool = False
) -> None:
    """
    Procesa todos los videos .mp4 en un directorio, dividiéndolos en clips de 8 segundos.
    
    Args:
        directory_path: Ruta al directorio
        recursive: Si es True, busca también en subdirectorios
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        logger.error(f"El directorio no existe: {directory_path}")
        return
    
    # Buscar todos los archivos .mp4
    if recursive:
        video_files = list(directory.rglob("*.mp4"))
    else:
        video_files = list(directory.glob("*.mp4"))
    
    # Filtrar archivos que ya fueron procesados
    video_files = [
        f for f in video_files
        if "_part" not in f.stem
        and "_8s" not in f.stem
        and "_7s" not in f.stem
        and "_30s" not in f.stem
    ]
    
    if not video_files:
        logger.info("No se encontraron videos para procesar.")
        return
    
    logger.info(f"Se encontraron {len(video_files)} video(s) para procesar:")
    for vf in video_files:
        logger.info(f"  - {vf.name}")
    logger.info("")
    
    # Procesar cada video
    total_clips = 0
    successful_videos = 0
    failed_videos = 0
    
    splitter = VideoSplitter(clip_duration=CLIP_DURATION)
    
    for video_file in video_files:
        clips_created = splitter.split_video(str(video_file))
        if clips_created > 0:
            successful_videos += 1
            total_clips += clips_created
        else:
            failed_videos += 1
        logger.info("")
    
    logger.info("="*50)
    logger.info(f"Procesamiento completado:")
    logger.info(f"  ✓ Videos procesados exitosamente: {successful_videos}")
    logger.info(f"  ✗ Videos fallidos: {failed_videos}")
    logger.info(f"  📹 Total de clips creados: {total_clips}")
    logger.info(f"  📁 Total de videos: {len(video_files)}")


def main():
    """Función principal."""
    # Directorio de videos
    videos_dir = r"C:\Users\blatam\Videos"
    
    logger.info("="*50)
    logger.info("Procesador de Videos - Clips de 8 segundos (Refactorizado v2)")
    logger.info("="*50)
    logger.info(f"Directorio: {videos_dir}")
    logger.info(f"Duración por clip: {CLIP_DURATION} segundos")
    logger.info("")
    
    # Procesar solo los videos en el directorio raíz (no recursivo)
    process_directory(videos_dir, recursive=False)


if __name__ == "__main__":
    main()




