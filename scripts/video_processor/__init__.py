"""
Video Processor - Módulo Refactorizado
======================================
Módulo refactorizado para procesamiento de videos con ffmpeg.
"""

from .video_info import VideoInfoExtractor
from .video_splitter import VideoSplitter
from .video_editor import VideoEditor
from .video_trimmer import VideoTrimmer
from .batch_processor import BatchVideoProcessor
from .video_splitter_with_editing import VideoSplitterWithEditing
from .utils import (
    DEFAULT_EDITING_CONFIG,
    DEFAULT_VIDEOS_DIR,
    filter_processed_videos,
    find_video_files,
    get_video_output_path,
    format_duration,
    print_processing_stats
)

__version__ = '2.2.0'
__all__ = [
    'VideoInfoExtractor',
    'VideoSplitter',
    'VideoEditor',
    'VideoTrimmer',
    'BatchVideoProcessor',
    'VideoSplitterWithEditing',
    'DEFAULT_EDITING_CONFIG',
    'DEFAULT_VIDEOS_DIR',
    'filter_processed_videos',
    'find_video_files',
    'get_video_output_path',
    'format_duration',
    'print_processing_stats'
]






