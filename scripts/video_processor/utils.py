"""
Utilidades compartidas para procesamiento de videos.
Contiene funciones comunes y configuraciones.
"""

import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

# Configuración de efectos de edición por defecto
DEFAULT_EDITING_CONFIG = {
    'fade_in': 0.5,
    'fade_out': 0.5,
    'brightness': 1.1,
    'contrast': 1.15,
    'saturation': 1.2,
    'sharpness': 1.1,
    'speed': 1.0,
}

# Directorio de videos por defecto
DEFAULT_VIDEOS_DIR = r"C:\Users\blatam\Videos"


def filter_processed_videos(
    video_files: List[Path],
    exclude_patterns: Optional[List[str]] = None
) -> List[Path]:
    """
    Filtra videos que ya fueron procesados.
    
    Args:
        video_files: Lista de archivos de video
        exclude_patterns: Patrones adicionales a excluir
    
    Returns:
        Lista de videos filtrados
    """
    if exclude_patterns is None:
        exclude_patterns = []
    
    default_patterns = ["_part", "_7s", "_8s", "_30s", "_edited", "_trimmed"]
    all_patterns = default_patterns + exclude_patterns
    
    filtered = [
        f for f in video_files
        if not any(pattern in f.stem for pattern in all_patterns)
    ]
    
    return filtered


def find_video_files(
    directory: Path,
    recursive: bool = False,
    extensions: Optional[List[str]] = None
) -> List[Path]:
    """
    Encuentra archivos de video en un directorio.
    
    Args:
        directory: Directorio donde buscar
        recursive: Si es True, busca también en subdirectorios
        extensions: Extensiones de video a buscar (default: ['.mp4'])
    
    Returns:
        Lista de archivos de video encontrados
    """
    if extensions is None:
        extensions = ['.mp4']
    
    video_files = []
    
    if recursive:
        for ext in extensions:
            video_files.extend(directory.rglob(f"*{ext}"))
    else:
        for ext in extensions:
            video_files.extend(directory.glob(f"*{ext}"))
    
    return sorted(video_files)


def get_video_output_path(
    video_path: Path,
    output_dir: Optional[Path] = None,
    suffix: str = "",
    extension: Optional[str] = None
) -> Path:
    """
    Genera la ruta de salida para un video procesado.
    
    Args:
        video_path: Ruta al video original
        output_dir: Directorio de salida (si es None, usa el mismo del video)
        suffix: Sufijo para agregar al nombre (ej: "_edited", "_trimmed")
        extension: Extensión del archivo (si es None, usa la del video original)
    
    Returns:
        Ruta del archivo de salida
    """
    if output_dir is None:
        output_dir = video_path.parent
    
    if extension is None:
        extension = video_path.suffix
    
    output_name = f"{video_path.stem}{suffix}{extension}"
    return output_dir / output_name


def format_duration(seconds: float) -> str:
    """
    Formatea una duración en segundos a formato legible.
    
    Args:
        seconds: Duración en segundos
    
    Returns:
        String formateado (ej: "1h 23m 45s" o "45s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0:
        parts.append(f"{secs:.1f}s")
    
    return " ".join(parts) if parts else "0s"


def print_processing_stats(
    successful: int,
    failed: int,
    total: int,
    total_clips: Optional[int] = None
) -> None:
    """
    Imprime estadísticas de procesamiento.
    
    Args:
        successful: Número de videos procesados exitosamente
        failed: Número de videos fallidos
        total: Total de videos procesados
        total_clips: Total de clips creados (opcional)
    """
    logger.info("="*50)
    logger.info("Procesamiento completado:")
    logger.info(f"  ✓ Videos procesados exitosamente: {successful}")
    logger.info(f"  ✗ Videos fallidos: {failed}")
    if total_clips is not None:
        logger.info(f"  📹 Total de clips creados: {total_clips}")
    logger.info(f"  📁 Total de videos: {total}")
    logger.info("="*50)




