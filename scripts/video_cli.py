"""
CLI unificado para procesamiento de videos.
Permite dividir, recortar y aplicar efectos a videos desde la línea de comandos.
"""
import argparse
import logging
import sys
from pathlib import Path

from video_processor import (
    VideoSplitter,
    VideoSplitterWithEditing,
    VideoTrimmer,
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


def split_video(args):
    """Divide un video en clips."""
    video_path = Path(args.video)
    
    if not video_path.exists():
        logger.error(f"El video no existe: {video_path}")
        return 1
    
    if args.editing:
        # Usar splitter con edición
        splitter = VideoSplitterWithEditing(
            clip_duration=args.duration,
            editing_config=DEFAULT_EDITING_CONFIG
        )
        clips_created = splitter.split_video_with_editing(
            str(video_path),
            output_dir=Path(args.output) if args.output else None
        )
    else:
        # Usar splitter simple
        splitter = VideoSplitter(clip_duration=args.duration)
        clips_created = splitter.split_video(
            str(video_path),
            output_dir=Path(args.output) if args.output else None
        )
    
    if clips_created > 0:
        logger.info(f"✓ Proceso completado: {clips_created} clips creados")
        return 0
    else:
        logger.error("✗ Error: No se pudieron crear los clips")
        return 1


def trim_video(args):
    """Recorta un video a una duración específica."""
    video_path = Path(args.video)
    
    if not video_path.exists():
        logger.error(f"El video no existe: {video_path}")
        return 1
    
    output_path = Path(args.output) if args.output else video_path.parent / f"{video_path.stem}_trimmed{video_path.suffix}"
    
    trimmer = VideoTrimmer(use_moviepy=args.moviepy)
    
    if trimmer.trim_video(video_path, output_path, args.duration):
        logger.info(f"✓ Video recortado: {output_path.name}")
        return 0
    else:
        logger.error("✗ Error: No se pudo recortar el video")
        return 1


def process_directory(args):
    """Procesa todos los videos en un directorio."""
    directory = Path(args.directory or DEFAULT_VIDEOS_DIR)
    
    if not directory.exists():
        logger.error(f"El directorio no existe: {directory}")
        return 1
    
    if args.command == 'split':
        if args.editing:
            splitter = VideoSplitterWithEditing(
                clip_duration=args.duration,
                editing_config=DEFAULT_EDITING_CONFIG
            )
            # Procesar cada video
            video_files = find_video_files(directory, recursive=False)
            video_files = filter_processed_videos(video_files)
            
            total_clips = 0
            for video_file in video_files:
                logger.info(f"Procesando: {video_file.name}")
                clips = splitter.split_video_with_editing(str(video_file))
                total_clips += clips
                logger.info("")
            
            logger.info(f"✓ Total de clips creados: {total_clips}")
        else:
            splitter = VideoSplitter(clip_duration=args.duration)
            video_files = find_video_files(directory, recursive=False)
            video_files = filter_processed_videos(video_files)
            
            total_clips = 0
            for video_file in video_files:
                logger.info(f"Procesando: {video_file.name}")
                clips = splitter.split_video(str(video_file))
                total_clips += clips
                logger.info("")
            
            logger.info(f"✓ Total de clips creados: {total_clips}")
    
    elif args.command == 'trim':
        trimmer = VideoTrimmer(use_moviepy=args.moviepy)
        stats = trimmer.trim_directory(
            input_directory=str(directory),
            output_directory=args.output,
            duration=args.duration
        )
        logger.info(f"✓ Videos recortados: {stats['successful']}")
        logger.info(f"✗ Videos fallidos: {stats['failed']}")
    
    return 0


def main():
    """Función principal del CLI."""
    parser = argparse.ArgumentParser(
        description='CLI unificado para procesamiento de videos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Dividir un video en clips de 7 segundos con edición
  python video_cli.py split video.mp4 --duration 7 --editing

  # Dividir un video en clips de 8 segundos sin edición
  python video_cli.py split video.mp4 --duration 8

  # Recortar un video a 30 segundos
  python video_cli.py trim video.mp4 --duration 30

  # Procesar todos los videos en un directorio
  python video_cli.py split-dir --directory "C:\\Users\\blatam\\Videos" --duration 7 --editing
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando split
    split_parser = subparsers.add_parser('split', help='Dividir un video en clips')
    split_parser.add_argument('video', help='Ruta al video')
    split_parser.add_argument('--duration', type=float, default=7.0, help='Duración de cada clip en segundos (default: 7.0)')
    split_parser.add_argument('--output', '-o', help='Directorio de salida (opcional)')
    split_parser.add_argument('--editing', '-e', action='store_true', help='Aplicar efectos de edición')
    split_parser.set_defaults(func=split_video)
    
    # Comando trim
    trim_parser = subparsers.add_parser('trim', help='Recortar un video')
    trim_parser.add_argument('video', help='Ruta al video')
    trim_parser.add_argument('--duration', type=float, default=30.0, help='Duración objetivo en segundos (default: 30.0)')
    trim_parser.add_argument('--output', '-o', help='Ruta del video de salida (opcional)')
    trim_parser.add_argument('--moviepy', action='store_true', help='Usar MoviePy en lugar de ffmpeg')
    trim_parser.set_defaults(func=trim_video)
    
    # Comando split-dir
    split_dir_parser = subparsers.add_parser('split-dir', help='Dividir todos los videos en un directorio')
    split_dir_parser.add_argument('--directory', '-d', help='Directorio con videos (default: C:\\Users\\blatam\\Videos)')
    split_dir_parser.add_argument('--duration', type=float, default=7.0, help='Duración de cada clip en segundos (default: 7.0)')
    split_dir_parser.add_argument('--editing', '-e', action='store_true', help='Aplicar efectos de edición')
    split_dir_parser.set_defaults(func=process_directory)
    
    # Comando trim-dir
    trim_dir_parser = subparsers.add_parser('trim-dir', help='Recortar todos los videos en un directorio')
    trim_dir_parser.add_argument('--directory', '-d', help='Directorio con videos (default: C:\\Users\\blatam\\Videos)')
    trim_dir_parser.add_argument('--duration', type=float, default=30.0, help='Duración objetivo en segundos (default: 30.0)')
    trim_dir_parser.add_argument('--output', '-o', help='Directorio de salida (opcional)')
    trim_dir_parser.add_argument('--moviepy', action='store_true', help='Usar MoviePy en lugar de ffmpeg')
    trim_dir_parser.set_defaults(func=process_directory)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())




