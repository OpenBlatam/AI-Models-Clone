import logging
from pathlib import Path
import time
import psutil
from typing import Optional, Dict

class VideoProcessingError(Exception):
    def __init__(self, code: str, message: str, user_message: Optional[str] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.user_message = user_message or message

    def to_dict(self) -> Dict:
        return {
            "error": self.code,
            "message": self.user_message
        }

def error_factory(code: str, message: str, user_message: Optional[str] = None) -> Dict:
    logging.error(f"{code}: {message}")
    return VideoProcessingError(code, message, user_message).to_dict()

def process_video(video_path: str, batch_size: int, quality: float) -> dict:
    if video_path is None:
        return error_factory(
            "MISSING_PATH",
            "video_path is required.",
            "Please provide a valid video file path."
        )
    if not Path(video_path).exists():
        return error_factory(
            "FILE_NOT_FOUND",
            f"Video file not found: {video_path}",
            "The specified video file does not exist. Please check the path and try again."
        )
    if batch_size <= 0 or batch_size > 32:
        return error_factory(
            "INVALID_BATCH",
            f"Invalid batch_size: {batch_size}",
            "Batch size must be between 1 and 32."
        )
    if quality < 0.0 or quality > 1.0:
        return error_factory(
            "INVALID_QUALITY",
            f"Invalid quality: {quality}",
            "Quality must be between 0.0 and 1.0."
        )
    if psutil.virtual_memory().available / (1024 * 1024 * 1024) < 1.0:
        return error_factory(
            "INSUFFICIENT_MEMORY",
            "Insufficient memory.",
            "Not enough system memory available to process the video."
        )
    if psutil.cpu_percent(interval=0.1) > 90.0:
        return error_factory(
            "SYSTEM_OVERLOADED",
            "System overloaded.",
            "The system is currently overloaded. Please try again later."
        )

    logging.info(f"Processing video: {video_path}, batch_size: {batch_size}, quality: {quality}")
    print(f"✅ Processing video: {video_path}")
    print(f"✅ Batch size: {batch_size}")
    print(f"✅ Quality: {quality}")
    time.sleep(1)
    return {
        "success": True,
        "video_path": video_path,
        "batch_size": batch_size,
        "quality": quality,
        "processed": True,
        "message": "Video processed successfully."
    } 