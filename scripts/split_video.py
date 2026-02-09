"""
Script genérico para dividir cualquier video en clips de 7 segundos.
Usa los módulos refactorizados de video_processor.
"""
import logging
import sys
from pathlib import Path

from video_processor import (
    VideoSplitterWithEditing,
    DEFAULT_EDITING_CONFIG,
    DEFAULT_VIDEOS_DIR,
    filter_processed_videos,
    find_video_files
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CLIP_DURATION = 7.0


def find_video(video_name: str) -> Path:
    """
    Busca un video en el directorio de videos.
    
    Args:
        video_name: Nombre del video (con o sin extensión)
    
    Returns:
        Path al video encontrado
    """
    videos_dir = Path(DEFAULT_VIDEOS_DIR)
    
    # Si no tiene extensión, agregar .mp4
    if not video_name.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        video_name = f"{video_name}.mp4"
    
    video_path = videos_dir / video_name
    
    if not video_path.exists():
        # Buscar sin extensión exacta
        for ext in ['.mp4', '.avi', '.mov', '.mkv']:
            alt_path = videos_dir / f"{Path(video_name).stem}{ext}"
            if alt_path.exists():
                return alt_path
        
        raise FileNotFoundError(f"Video no encontrado: {video_name}")
    
    return video_path


def list_available_videos() -> list:
    """Lista los videos disponibles para procesar."""
    videos_dir = Path(DEFAULT_VIDEOS_DIR)
    video_files = find_video_files(videos_dir, recursive=False)
    return filter_processed_videos(video_files)


def split_video(video_path: str, clip_duration: float = CLIP_DURATION) -> int:
    """
    Divide un video en clips.
    
    Args:
        video_path: Ruta al video
        clip_duration: Duración de cada clip en segundos
    
    Returns:
        Número de clips creados
    """
    video_path_obj = Path(video_path)
    
    if not video_path_obj.exists():
        logger.error(f"El archivo no existe: {video_path}")
        return 0
    
    logger.info("="*50)
    logger.info(f"Dividiendo video '{video_path_obj.name}' en clips de {clip_duration} segundos")
    logger.info("="*50)
    logger.info(f"Video: {video_path}")
    logger.info("")
    
    # Crear splitter con edición
    splitter = VideoSplitterWithEditing(
        clip_duration=clip_duration,
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
        return clips_created
    else:
        logger.error("✗ Error: No se pudieron crear los clips")
        return 0


def main():
    """Función principal."""
    if len(sys.argv) > 1:
        # Video especificado como argumento
        video_name = sys.argv[1]
        try:
            video_path = find_video(video_name)
            split_video(str(video_path))
        except FileNotFoundError as e:
            logger.error(str(e))
            logger.info("\nVideos disponibles:")
            for v in list_available_videos()[:10]:
                logger.info(f"  - {v.name}")
    else:
        # Mostrar videos disponibles y procesar el primero
        available_videos = list_available_videos()
        
        if not available_videos:
            logger.error("No se encontraron videos para procesar.")
            return
        
        logger.info("Videos disponibles:")
        for i, v in enumerate(available_videos[:10], 1):
            logger.info(f"  {i}. {v.name}")
        
        # Procesar el primer video disponible
        logger.info("")
        logger.info(f"Procesando el primer video: {available_videos[0].name}")
        split_video(str(available_videos[0]))


if __name__ == "__main__":
    main()




