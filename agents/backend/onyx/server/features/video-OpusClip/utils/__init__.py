"""
Video Processing Utilities

Core utilities for batch operations, validation, parallel processing, and configuration.
"""

from .batch_utils import (
    BatchMetrics,
    _optimized_batch_timeit,
    _vectorized_batch_operation,
    _parallel_batch_operation,
    OptimizedBatchMixin
)

from .validation import (
    _validate_youtube_url,
    _validate_language,
    _validate_video_clip_times,
    _validate_viral_score,
    _validate_caption
)

from .constants import (
    PANDAS_AVAILABLE,
    SENTRY_AVAILABLE,
    SLOW_OPERATION_THRESHOLD,
    DEFAULT_MAX_WORKERS,
    CACHE_SIZE_URLS,
    CACHE_SIZE_LANGUAGES
)

from .parallel_utils import (
    HybridParallelProcessor,
    VideoParallelProcessor,
    parallel_map,
    async_batch_process,
    joblib_parallel_process,
    ray_parallel_process,
    dask_parallel_process,
    numba_parallel_process,
    ParallelConfig,
    BackendType,
    setup_async_loop,
    get_optimal_chunk_size,
    estimate_processing_time
)

__all__ = [
    # Batch utilities
    'BatchMetrics',
    '_optimized_batch_timeit',
    '_vectorized_batch_operation',
    '_parallel_batch_operation',
    'OptimizedBatchMixin',
    
    # Validation
    '_validate_youtube_url',
    '_validate_language',
    '_validate_video_clip_times',
    '_validate_viral_score',
    '_validate_caption',
    
    # Constants
    'PANDAS_AVAILABLE',
    'SENTRY_AVAILABLE',
    'SLOW_OPERATION_THRESHOLD',
    'DEFAULT_MAX_WORKERS',
    'CACHE_SIZE_URLS',
    'CACHE_SIZE_LANGUAGES',
    
    # Parallel processing
    'HybridParallelProcessor',
    'VideoParallelProcessor',
    'parallel_map',
    'async_batch_process',
    'joblib_parallel_process',
    'ray_parallel_process',
    'dask_parallel_process',
    'numba_parallel_process',
    'ParallelConfig',
    'BackendType',
    'setup_async_loop',
    'get_optimal_chunk_size',
    'estimate_processing_time',
] 