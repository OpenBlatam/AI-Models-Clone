"""
Script para procesar videos y dividirlos en clips de 8 segundos.
Procesa todos los videos .mp4 en el directorio especificado.
"""
import os
import subprocess
import re
from pathlib import Path
import imageio_ffmpeg
import logging
import math

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CLIP_DURATION = 8  # Duración de cada clip en segundos

def get_video_duration(video_path: str) -> float:
    """
    Obtiene la duración de un video en segundos usando ffmpeg.
    
    Args:
        video_path: Ruta al video
    
    Returns:
        Duración en segundos, o 0 si hay error
    """
    try:
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        
        # Usar ffmpeg para obtener la duración del video
        cmd = [
            ffmpeg_path,
            '-i', video_path,
            '-f', 'null',
            '-'
        ]
        
        # Ejecutar y capturar stderr donde está la información
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        # Buscar la duración en el stderr
        # Formato: Duration: HH:MM:SS.mmm
        duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})', result.stderr)
        if duration_match:
            hours = int(duration_match.group(1))
            minutes = int(duration_match.group(2))
            seconds = int(duration_match.group(3))
            milliseconds = int(duration_match.group(4))
            total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 100.0
            return total_seconds
        
        return 0
    except Exception as e:
        logger.warning(f"No se pudo obtener la duración del video: {e}")
        return 0

def process_video_to_8s_clips(video_path: str, output_dir: Path = None) -> int:
    """
    Divide un video en clips de 8 segundos usando ffmpeg.
    
    Args:
        video_path: Ruta al video original
        output_dir: Directorio de salida (si es None, usa el mismo del video)
    
    Returns:
        Número de clips creados exitosamente, 0 si hubo error
    """
    try:
        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            logger.error(f"El archivo no existe: {video_path}")
            return 0
        
        # Usar el directorio del video si no se especifica otro
        if output_dir is None:
            output_dir = video_path_obj.parent
        
        logger.info(f"Procesando: {video_path}")
        
        # Obtener la duración del video
        duration = get_video_duration(str(video_path))
        if duration <= 0:
            logger.error(f"  No se pudo obtener la duración del video")
            return 0
        
        logger.info(f"  Duración original: {duration:.2f} segundos")
        
        # Calcular número de clips necesarios
        num_clips = math.ceil(duration / CLIP_DURATION)
        logger.info(f"  Se crearán {num_clips} clip(s) de {CLIP_DURATION} segundos")
        
        # Obtener la ruta de ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        
        # Nombre base para los clips
        name = video_path_obj.stem
        suffix = video_path_obj.suffix
        
        clips_created = 0
        
        # Crear cada clip
        for i in range(num_clips):
            start_time = i * CLIP_DURATION
            # El último clip puede ser más corto que 8 segundos
            clip_duration = min(CLIP_DURATION, duration - start_time)
            
            if clip_duration <= 0:
                break
            
            # Nombre del archivo de salida
            output_path = output_dir / f"{name}_part{i+1:03d}_8s{suffix}"
            
            logger.info(f"  Creando clip {i+1}/{num_clips}: {start_time:.2f}s - {start_time + clip_duration:.2f}s")
            
            # Comando ffmpeg para extraer el segmento
            cmd = [
                ffmpeg_path,
                '-i', str(video_path),
                '-ss', str(start_time),  # Tiempo de inicio
                '-t', str(clip_duration),  # Duración del clip
                '-c:v', 'libx264',  # Codec de video
                '-c:a', 'aac',  # Codec de audio
                '-preset', 'medium',  # Preset de codificación
                '-avoid_negative_ts', 'make_zero',  # Evitar timestamps negativos
                '-y',  # Sobrescribir archivo de salida si existe
                str(output_path)
            ]
            
            try:
                # Ejecutar ffmpeg
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                clips_created += 1
                logger.info(f"    ✓ Clip guardado: {output_path.name}")
            except subprocess.CalledProcessError as e:
                logger.error(f"    ✗ Error creando clip {i+1}: {e.stderr[:200]}")
                continue
        
        logger.info(f"  ✓ Video procesado: {clips_created}/{num_clips} clips creados")
        return clips_created
        
    except Exception as e:
        logger.error(f"Error procesando {video_path}: {str(e)}")
        return 0

def process_directory(directory_path: str, recursive: bool = False) -> None:
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
    
    # Filtrar archivos que ya fueron procesados (que contienen "_part" y "_8s" en el nombre)
    video_files = [f for f in video_files if "_part" not in f.stem and "_8s" not in f.stem]
    
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
        clips_created = process_video_to_8s_clips(str(video_file))
        if clips_created > 0:
            successful_videos += 1
            total_clips += clips_created
        else:
            failed_videos += 1
        logger.info("")  # Línea en blanco entre videos
    
    logger.info("="*50)
    logger.info(f"Procesamiento completado:")
    logger.info(f"  ✓ Videos procesados exitosamente: {successful_videos}")
    logger.info(f"  ✗ Videos fallidos: {failed_videos}")
    logger.info(f"  📹 Total de clips creados: {total_clips}")
    logger.info(f"  📁 Total de videos: {len(video_files)}")

if __name__ == "__main__":
    # Directorio de videos
    videos_dir = r"C:\Users\blatam\Videos"
    
    logger.info("="*50)
    logger.info("Procesador de Videos - Clips de 8 segundos")
    logger.info("="*50)
    logger.info(f"Directorio: {videos_dir}")
    logger.info(f"Duración por clip: {CLIP_DURATION} segundos")
    logger.info("")
    
    # Procesar solo los videos en el directorio raíz (no recursivo)
    process_directory(videos_dir, recursive=False)

