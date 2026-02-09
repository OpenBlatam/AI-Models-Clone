"""
Script para procesar videos, dividirlos en clips de 7 segundos y aplicar efectos de edición.
Procesa todos los videos .mp4 en el directorio especificado.
"""
import os
import subprocess
import re
from pathlib import Path
import imageio_ffmpeg
import logging
import math
from typing import Optional, Dict, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CLIP_DURATION = 7  # Duración de cada clip en segundos

# Configuración de efectos de edición
EDITING_CONFIG = {
    'fade_in': 0.5,  # Segundos de fade in
    'fade_out': 0.5,  # Segundos de fade out
    'brightness': 1.1,  # Aumento de brillo (1.0 = normal)
    'contrast': 1.15,  # Aumento de contraste (1.0 = normal)
    'saturation': 1.2,  # Aumento de saturación (1.0 = normal)
    'sharpness': 1.1,  # Aumento de nitidez
    'speed': 1.0,  # Velocidad (1.0 = normal, >1.0 = más rápido)
}

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

def get_video_info(video_path: str) -> Dict[str, any]:
    """
    Obtiene información del video (resolución, fps, etc.)
    
    Args:
        video_path: Ruta al video
    
    Returns:
        Diccionario con información del video
    """
    try:
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        
        cmd = [
            ffmpeg_path,
            '-i', video_path,
            '-f', 'null',
            '-'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        info = {}
        
        # Buscar resolución
        resolution_match = re.search(r'(\d+)x(\d+)', result.stderr)
        if resolution_match:
            info['width'] = int(resolution_match.group(1))
            info['height'] = int(resolution_match.group(2))
        
        # Buscar fps
        fps_match = re.search(r'(\d+(?:\.\d+)?)\s+fps', result.stderr)
        if fps_match:
            info['fps'] = float(fps_match.group(1))
        
        return info
    except Exception as e:
        logger.warning(f"No se pudo obtener información del video: {e}")
        return {}

def build_ffmpeg_filters(config: Dict, clip_duration: float) -> str:
    """
    Construye el filtro de ffmpeg con todos los efectos aplicados.
    
    Args:
        config: Configuración de efectos
        clip_duration: Duración del clip en segundos
    
    Returns:
        String con los filtros de ffmpeg
    """
    filters = []
    
    # Fade in y fade out
    fade_in = config.get('fade_in', 0)
    fade_out = config.get('fade_out', 0)
    
    if fade_in > 0 or fade_out > 0:
        if fade_in > 0:
            filters.append(f"fade=t=in:st=0:d={fade_in}")
        if fade_out > 0 and clip_duration > fade_out:
            # Calcular el tiempo de inicio del fade out
            fade_out_start = clip_duration - fade_out
            filters.append(f"fade=t=out:st={fade_out_start:.2f}:d={fade_out}")
    
    # Ajustes de color (brightness, contrast, saturation)
    brightness = config.get('brightness', 1.0)
    contrast = config.get('contrast', 1.0)
    saturation = config.get('saturation', 1.0)
    
    if brightness != 1.0 or contrast != 1.0 or saturation != 1.0:
        # eq = equalizer de color
        # brightness en eq va de -1.0 a 1.0, así que ajustamos
        brightness_eq = (brightness - 1.0) * 0.3  # Limitar el rango
        eq_filter = f"eq=brightness={brightness_eq:.2f}:contrast={contrast:.2f}:saturation={saturation:.2f}"
        filters.append(eq_filter)
    
    # Nitidez (unsharp)
    sharpness = config.get('sharpness', 1.0)
    if sharpness != 1.0:
        # Unsharp mask para nitidez
        luma_amount = (sharpness - 1.0) * 0.5
        filters.append(f"unsharp=5:5:{luma_amount:.2f}:5:5:0.0")
    
    # Combinar todos los filtros
    if filters:
        return ",".join(filters)
    return None

def process_video_to_7s_clips_with_editing(
    video_path: str, 
    output_dir: Path = None,
    editing_config: Optional[Dict] = None
) -> int:
    """
    Divide un video en clips de 7 segundos y aplica efectos de edición usando ffmpeg.
    
    Args:
        video_path: Ruta al video original
        output_dir: Directorio de salida (si es None, usa el mismo del video)
        editing_config: Configuración de efectos (si es None, usa la configuración por defecto)
    
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
        
        # Usar configuración por defecto si no se proporciona
        if editing_config is None:
            editing_config = EDITING_CONFIG.copy()
        
        logger.info(f"Procesando: {video_path}")
        
        # Obtener la duración del video
        duration = get_video_duration(str(video_path))
        if duration <= 0:
            logger.error(f"  No se pudo obtener la duración del video")
            return 0
        
        logger.info(f"  Duración original: {duration:.2f} segundos")
        
        # Obtener información del video
        video_info = get_video_info(str(video_path))
        if video_info:
            logger.info(f"  Resolución: {video_info.get('width', '?')}x{video_info.get('height', '?')}")
            logger.info(f"  FPS: {video_info.get('fps', '?')}")
        
        # Calcular número de clips necesarios
        num_clips = math.ceil(duration / CLIP_DURATION)
        logger.info(f"  Se crearán {num_clips} clip(s) de {CLIP_DURATION} segundos con edición")
        logger.info(f"  Efectos aplicados: fade in/out, brillo, contraste, saturación, nitidez")
        
        # Obtener la ruta de ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        
        # Nombre base para los clips
        name = video_path_obj.stem
        suffix = video_path_obj.suffix
        
        clips_created = 0
        
        # Crear cada clip
        for i in range(num_clips):
            start_time = i * CLIP_DURATION
            # El último clip puede ser más corto que 7 segundos
            clip_duration = min(CLIP_DURATION, duration - start_time)
            
            if clip_duration <= 0:
                break
            
            # Nombre del archivo de salida
            output_path = output_dir / f"{name}_edited_part{i+1:03d}_7s{suffix}"
            
            logger.info(f"  Creando clip {i+1}/{num_clips}: {start_time:.2f}s - {start_time + clip_duration:.2f}s")
            
            # Construir filtros de ffmpeg con la duración del clip
            video_filters = build_ffmpeg_filters(editing_config, clip_duration)
            
            # Ajustar velocidad si es necesario
            speed = editing_config.get('speed', 1.0)
            
            # Comando base de ffmpeg
            cmd = [
                ffmpeg_path,
                '-i', str(video_path),
                '-ss', str(start_time),  # Tiempo de inicio
                '-t', str(clip_duration),  # Duración del clip
            ]
            
            # Ajustar velocidad del video si es necesario
            if speed != 1.0:
                # Agregar setpts para cambiar velocidad
                if video_filters:
                    video_filters = f"{video_filters},setpts=PTS/{speed}"
                else:
                    video_filters = f"setpts=PTS/{speed}"
                # Ajustar audio también
                cmd.extend(['-af', f"atempo={speed}"])
            
            # Aplicar filtros de video si existen
            if video_filters:
                cmd.extend(['-vf', video_filters])
            
            # Codecs y calidad
            cmd.extend([
                '-c:v', 'libx264',  # Codec de video
                '-preset', 'medium',  # Preset de codificación
                '-crf', '23',  # Calidad (18-28, menor = mejor calidad)
                '-c:a', 'aac',  # Codec de audio
                '-b:a', '128k',  # Bitrate de audio
                '-avoid_negative_ts', 'make_zero',  # Evitar timestamps negativos
                '-y',  # Sobrescribir archivo de salida si existe
                str(output_path)
            ])
            
            try:
                # Ejecutar ffmpeg
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                clips_created += 1
                logger.info(f"    ✓ Clip editado guardado: {output_path.name}")
            except subprocess.CalledProcessError as e:
                logger.error(f"    ✗ Error creando clip {i+1}: {e.stderr[:200] if e.stderr else str(e)}")
                continue
        
        logger.info(f"  ✓ Video procesado: {clips_created}/{num_clips} clips creados con edición")
        return clips_created
        
    except Exception as e:
        logger.error(f"Error procesando {video_path}: {str(e)}")
        return 0

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
    
    # Buscar todos los archivos .mp4
    if recursive:
        video_files = list(directory.rglob("*.mp4"))
    else:
        video_files = list(directory.glob("*.mp4"))
    
    # Filtrar archivos que ya fueron procesados (que contienen "_edited_part" y "_7s" en el nombre)
    # También excluir los clips de 8 segundos ya procesados
    video_files = [
        f for f in video_files 
        if "_edited_part" not in f.stem 
        and "_7s" not in f.stem
        and "_part" not in f.stem  # Excluir clips ya procesados
        and "_30s" not in f.stem  # Excluir videos de 30s ya procesados
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
        logger.info("")  # Línea en blanco entre videos
    
    logger.info("="*50)
    logger.info(f"Procesamiento completado:")
    logger.info(f"  ✓ Videos procesados exitosamente: {successful_videos}")
    logger.info(f"  ✗ Videos fallidos: {failed_videos}")
    logger.info(f"  📹 Total de clips editados creados: {total_clips}")
    logger.info(f"  📁 Total de videos: {len(video_files)}")

if __name__ == "__main__":
    # Directorio de videos
    videos_dir = r"C:\Users\blatam\Videos"
    
    logger.info("="*50)
    logger.info("Procesador de Videos - Clips de 7 segundos con Edición")
    logger.info("="*50)
    logger.info(f"Directorio: {videos_dir}")
    logger.info(f"Duración por clip: {CLIP_DURATION} segundos")
    logger.info("")
    logger.info("Efectos aplicados:")
    logger.info(f"  - Fade in: {EDITING_CONFIG['fade_in']}s")
    logger.info(f"  - Fade out: {EDITING_CONFIG['fade_out']}s")
    logger.info(f"  - Brillo: {EDITING_CONFIG['brightness']:.1%}")
    logger.info(f"  - Contraste: {EDITING_CONFIG['contrast']:.1%}")
    logger.info(f"  - Saturación: {EDITING_CONFIG['saturation']:.1%}")
    logger.info(f"  - Nitidez: {EDITING_CONFIG['sharpness']:.1%}")
    logger.info("")
    
    # Procesar solo los videos en el directorio raíz (no recursivo)
    process_directory(videos_dir, recursive=False)

