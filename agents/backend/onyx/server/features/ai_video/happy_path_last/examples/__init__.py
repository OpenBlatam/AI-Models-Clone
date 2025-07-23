"""
🎯 HAPPY PATH LAST - EXAMPLES MODULE
====================================

Módulo de ejemplos que muestra cómo usar el patrón happy path last en diferentes
escenarios: procesamiento de video, procesamiento de datos y operaciones asíncronas.
"""

from .video_processing import (
    process_video_happy_path_last,
    load_model_happy_path_last,
    process_video_decorated,
    VideoProcessingPipeline,
    process_video_mixed_pattern,
    process_video_happy_path_last_clean
)

from .data_processing import (
    process_data_happy_path_last,
    process_batch_data_happy_path_last,
    process_data_decorated,
    process_data_with_operation_decorated,
    DataProcessingPipeline,
    normalize_data_happy_path_last,
    scale_data_happy_path_last,
    filter_data_happy_path_last,
    process_data_mixed_pattern,
    process_data_happy_path_last_clean
)

from .async_examples import (
    async_process_video_happy_path_last,
    async_load_model_happy_path_last,
    async_load_model_decorated,
    async_process_video_decorated,
    AsyncVideoProcessingPipeline,
    async_process_video_batch,
    async_validate_resources,
    async_check_system_status,
    async_process_video_mixed_pattern,
    async_process_video_happy_path_last_clean
)

__all__ = [
    # Video processing examples
    "process_video_happy_path_last",
    "load_model_happy_path_last",
    "process_video_decorated",
    "VideoProcessingPipeline",
    "process_video_mixed_pattern",
    "process_video_happy_path_last_clean",
    
    # Data processing examples
    "process_data_happy_path_last",
    "process_batch_data_happy_path_last",
    "process_data_decorated",
    "process_data_with_operation_decorated",
    "DataProcessingPipeline",
    "normalize_data_happy_path_last",
    "scale_data_happy_path_last",
    "filter_data_happy_path_last",
    "process_data_mixed_pattern",
    "process_data_happy_path_last_clean",
    
    # Async examples
    "async_process_video_happy_path_last",
    "async_load_model_happy_path_last",
    "async_load_model_decorated",
    "async_process_video_decorated",
    "AsyncVideoProcessingPipeline",
    "async_process_video_batch",
    "async_validate_resources",
    "async_check_system_status",
    "async_process_video_mixed_pattern",
    "async_process_video_happy_path_last_clean"
] 