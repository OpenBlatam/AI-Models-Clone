"""
Script refactorizado para procesar videos, dividirlos en clips de 7 segundos 
y aplicar efectos de edición.
Usa los módulos refactorizados de video_processor.
"""
import logging
from pathlib import Path
from typing import Optional, Dict

from video_processor import (
    VideoSplitterWithEditing,
    DEFAULT_EDITING_CONFIG,
    DEFAULT_VIDEOS_DIR,
    filter_processed_videos,
    find_video_files,
    print_processing_stats
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CLIP_DURATION = 7.0  # Duración de cada clip en segundos


def process_video_to_7s_clips_with_editing(
    video_path: str,
    output_dir: Optional[Path] = None,
    editing_config: Optional[Dict] = None
) -> int:
    """
    Divide un video en clips de 7 segundos y aplica efectos de edición.
    
    Args:
        video_path: Ruta al video original
        output_dir: Directorio de salida (si es None, usa el mismo del video)
        editing_config: Configuración de efectos (si es None, usa la configuración por defecto)
    
    Returns:
        Número de clips creados exitosamente, 0 si hubo error
    """
    config = editing_config or DEFAULT_EDITING_CONFIG.copy()
    
    splitter = VideoSplitterWithEditing(
        clip_duration=CLIP_DURATION,
        editing_config=config
    )
    
    return splitter.split_video_with_editing(
        video_path=video_path,
        output_dir=output_dir
    )


def process_directory(
    directory_path: str,
    recursive: bool = False,
    editing_config: Optional[Dict] = None
) -> None:
    """
    Procesa todos los videos .mp4 en un directorio, dividiéndolos en clips de 7 segundos con edición.
    
    Args:
        directory_path: Ruta al directorio
        recursive: Si es True, busca también en subdirectorios
        editing_config: Configuración de efectos personalizada
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        logger.error(f"El directorio no existe: {directory_path}")
        return
    
    # Buscar y filtrar videos
    video_files = find_video_files(directory, recursive=recursive)
    video_files = filter_processed_videos(video_files)
    
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
    
    for video_file in video_files:
        clips_created = process_video_to_7s_clips_with_editing(
            str(video_file),
            editing_config=editing_config
        )
        if clips_created > 0:
            successful_videos += 1
            total_clips += clips_created
        else:
            failed_videos += 1
        logger.info("")
    
    print_processing_stats(
        successful=successful_videos,
        failed=failed_videos,
        total=len(video_files),
        total_clips=total_clips
    )


if __name__ == "__main__":
    # Directorio de videos
    videos_dir = DEFAULT_VIDEOS_DIR
    
    logger.info("="*50)
    logger.info("Procesador de Videos - Clips de 7 segundos con Edición (Refactorizado)")
    logger.info("="*50)
    logger.info(f"Directorio: {videos_dir}")
    logger.info(f"Duración por clip: {CLIP_DURATION} segundos")
    logger.info("")
    logger.info("Efectos aplicados:")
    logger.info(f"  - Fade in: {DEFAULT_EDITING_CONFIG['fade_in']}s")
    logger.info(f"  - Fade out: {DEFAULT_EDITING_CONFIG['fade_out']}s")
    logger.info(f"  - Brillo: {DEFAULT_EDITING_CONFIG['brightness']:.1%}")
    logger.info(f"  - Contraste: {DEFAULT_EDITING_CONFIG['contrast']:.1%}")
    logger.info(f"  - Saturación: {DEFAULT_EDITING_CONFIG['saturation']:.1%}")
    logger.info(f"  - Nitidez: {DEFAULT_EDITING_CONFIG['sharpness']:.1%}")
    logger.info("")
    
    # Procesar solo los videos en el directorio raíz (no recursivo)
    process_directory(videos_dir, recursive=False)




