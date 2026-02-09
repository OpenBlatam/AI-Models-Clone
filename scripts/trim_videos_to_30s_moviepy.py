"""
Script alternativo para recortar videos a 30 segundos usando moviepy.
Este script no requiere ffmpeg en el PATH, pero necesita la librería moviepy instalada.
"""

import os
from pathlib import Path
from typing import List
import sys

try:
    from moviepy import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    try:
        # Fallback para versiones antiguas de moviepy
        from moviepy.editor import VideoFileClip
        MOVIEPY_AVAILABLE = True
    except ImportError:
        MOVIEPY_AVAILABLE = False


def get_video_files(directory: str) -> List[Path]:
    """Obtiene todos los archivos de video en el directorio."""
    video_extensions = ['.mp4', '.MP4', '.mov', '.MOV', '.avi', '.AVI', '.mkv', '.MKV']
    video_files = []
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"[ERROR] El directorio {directory} no existe.")
        return []
    
    # Buscar archivos de video en el directorio raíz
    for ext in video_extensions:
        video_files.extend(directory_path.glob(f"*{ext}"))
    
    return sorted(video_files)


def trim_video_moviepy(input_path: Path, output_path: Path, duration: float = 30.0) -> bool:
    """
    Recorta un video a la duración especificada usando moviepy.
    
    Args:
        input_path: Ruta del video de entrada
        output_path: Ruta del video de salida
        duration: Duración en segundos (default: 30)
    
    Returns:
        True si el proceso fue exitoso, False en caso contrario
    """
    try:
        # Cargar video
        video = VideoFileClip(str(input_path))
        
        # Obtener duración real del video
        video_duration = video.duration
        
        # Si el video es más corto que la duración objetivo, usar la duración real
        trim_duration = min(duration, video_duration)
        
        # Recortar video
        trimmed_video = video.subclip(0, trim_duration)
        
        # Guardar video recortado
        trimmed_video.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            logger=None  # Suprimir logs de moviepy
        )
        
        # Cerrar clips para liberar memoria
        trimmed_video.close()
        video.close()
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Error al procesar: {e}")
        return False


def process_videos(input_directory: str, output_directory: str = None, duration: float = 30.0) -> None:
    """
    Procesa todos los videos en el directorio de entrada.
    
    Args:
        input_directory: Directorio con los videos de entrada
        output_directory: Directorio para videos de salida (si es None, sobrescribe los originales)
        duration: Duración objetivo en segundos (default: 30)
    """
    print(f"[*] Procesando videos en: {input_directory}")
    print(f"[*] Duracion objetivo: {duration} segundos\n")
    
    # Verificar moviepy
    if not MOVIEPY_AVAILABLE:
        print("[ERROR] moviepy no esta instalado.")
        print("")
        print("Para instalar moviepy:")
        print("  pip install moviepy")
        print("")
        sys.exit(1)
    
    # Obtener lista de videos
    video_files = get_video_files(input_directory)
    
    if not video_files:
        print("[WARNING] No se encontraron archivos de video en el directorio.")
        return
    
    print(f"[*] Encontrados {len(video_files)} archivo(s) de video:\n")
    
    # Crear directorio de salida si se especifica
    if output_directory:
        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"[*] Videos de salida se guardaran en: {output_directory}\n")
    else:
        print("[WARNING] Los videos originales seran sobrescritos (se creara backup).\n")
    
    # Procesar cada video
    successful = 0
    failed = 0
    skipped = 0
    
    for i, video_file in enumerate(video_files, 1):
        print(f"[{i}/{len(video_files)}] Procesando: {video_file.name}")
        
        try:
            # Obtener duración del video
            video = VideoFileClip(str(video_file))
            original_duration = video.duration
            video.close()
            
            if original_duration <= duration:
                print(f"  [INFO] El video ya es de {original_duration:.2f}s (menor o igual a {duration}s), saltando...")
                skipped += 1
                continue
            
            print(f"  [*] Duracion original: {original_duration:.2f}s")
            
            # Determinar ruta de salida
            if output_directory:
                output_file = Path(output_directory) / video_file.name
                input_file = video_file
            else:
                # Crear backup del original antes de sobrescribir
                original_name = video_file.name
                backup_file = video_file.with_name(f"{video_file.stem}.original{video_file.suffix}")
                if not backup_file.exists():
                    print(f"  [*] Creando backup: {backup_file.name}")
                    video_file.rename(backup_file)
                    input_file = backup_file
                else:
                    input_file = backup_file
                # El archivo de salida será el nombre original
                output_file = video_file.parent / original_name
            
            # Recortar video
            print(f"  [*] Recortando a {duration}s...")
            if trim_video_moviepy(input_file, output_file, duration):
                file_size_mb = output_file.stat().st_size / (1024 * 1024)
                print(f"  [OK] Completado: {output_file.name} ({file_size_mb:.2f} MB)")
                successful += 1
            else:
                print(f"  [ERROR] Fallo: {video_file.name}")
                failed += 1
                
        except Exception as e:
            print(f"  [ERROR] Error al procesar {video_file.name}: {e}")
            failed += 1
        
        print()
    
    # Resumen
    print("=" * 60)
    print("[RESUMEN]")
    print(f"  [OK] Exitosos: {successful}")
    print(f"  [ERROR] Fallidos: {failed}")
    print(f"  [SKIP] Omitidos: {skipped}")
    print("=" * 60)


def main():
    """Función principal."""
    # Directorio de entrada
    input_dir = r"C:\Users\blatam\Videos"
    
    # Directorio de salida (None para sobrescribir originales)
    # Descomenta la siguiente línea para guardar en una carpeta separada:
    # output_dir = r"C:\Users\blatam\Videos\trimmed_30s"
    output_dir = None  # Sobrescribir originales (con backup)
    
    # Duración objetivo
    duration = 30.0
    
    process_videos(input_dir, output_dir, duration)


if __name__ == "__main__":
    main()

