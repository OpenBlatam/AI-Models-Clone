"""
Gesture and Emotion Controller for HeyGen AI
============================================

Manages real-time body gestures and facial emotions for dynamic,
human-like avatar behavior with enterprise-grade performance.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
import uuid

# Core imports
from .base_service import BaseService, ServiceType, HealthCheckResult, ServiceStatus
from .error_handler import ErrorHandler, with_error_handling, with_retry
from .config_manager import ConfigurationManager
from .logging_service import LoggingService

# MediaPipe imports
try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

# Computer vision imports
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class GestureConfig:
    """Configuration for a specific gesture."""
    
    gesture_id: str
    name: str
    category: str
    confidence_threshold: float = 0.7
    duration: float = 2.0
    intensity: float = 1.0
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmotionConfig:
    """Configuration for a specific emotion."""
    
    emotion_id: str
    name: str
    intensity: float = 1.0
    duration: float = 3.0
    blend_mode: str = "smooth"
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GestureSequence:
    """Sequence of gestures for natural movement."""
    
    sequence_id: str
    name: str
    gestures: List[GestureConfig]
    timing: List[float]
    loop: bool = False
    priority: int = 1


@dataclass
class EmotionSequence:
    """Sequence of emotions for natural expression."""
    
    sequence_id: str
    name: str
    emotions: List[EmotionConfig]
    timing: List[float]
    loop: bool = False
    priority: int = 1


@dataclass
class GestureRequest:
    """Request for gesture generation."""
    
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    gesture_type: str = ""
    intensity: float = 1.0
    duration: float = 2.0
    context: str = "neutral"
    custom_parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EmotionRequest:
    """Request for emotion generation."""
    
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    emotion_type: str = ""
    intensity: float = 1.0
    duration: float = 3.0
    blend_with_current: bool = True
    custom_parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class GestureEmotionController(BaseService):
    """Controller for managing gestures and emotions in real-time."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the gesture and emotion controller."""
        super().__init__("GestureEmotionController", ServiceType.PHASE2, config)
        
        # Configuration paths
        self.config_path = Path("./data/gesture_emotion")
        
        # Gesture and emotion sequences
        self.gesture_sequences: Dict[str, GestureSequence] = {}
        self.emotion_sequences: Dict[str, EmotionSequence] = {}
        
        # Current state
        self.current_gesture: Optional[GestureConfig] = None
        self.current_emotion: Optional[EmotionConfig] = None
        self.is_active = False
        
        # MediaPipe setup
        self.mp_pose = None
        self.mp_face_mesh = None
        self.pose_detector = None
        self.face_detector = None
        
        # Error handling
        self.error_handler = ErrorHandler()
        
        # Configuration manager
        self.config_manager = ConfigurationManager()
        
        # Logging service
        self.logging_service = LoggingService()
        
        # Performance tracking
        self.controller_stats = {
            "total_gestures": 0,
            "total_emotions": 0,
            "successful_gestures": 0,
            "successful_emotions": 0,
            "failed_gestures": 0,
            "failed_emotions": 0,
            "average_processing_time": 0.0
        }
        
        # Supported gestures and emotions
        self.supported_gestures = [
            "wave", "point", "thumbs_up", "thumbs_down", "clap", "nod", "shake_head",
            "shrug", "fold_arms", "hands_on_hips", "thinking_pose", "victory"
        ]
        
        self.supported_emotions = [
            "happy", "sad", "angry", "surprised", "confused", "excited", "calm",
            "worried", "confident", "shy", "determined", "thoughtful"
        ]

    async def _initialize_service_impl(self) -> None:
        """Initialize gesture and emotion detection services."""
        try:
            logger.info("Initializing gesture and emotion controller...")
            
            # Check dependencies
            await self._check_dependencies()
            
            # Initialize MediaPipe
            await self._initialize_mediapipe()
            
            # Load default sequences
            await self._load_default_sequences()
            
            # Validate configuration
            await self._validate_configuration()
            
            logger.info("Gesture and emotion controller initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize gesture and emotion controller: {e}")
            raise

    async def _check_dependencies(self) -> None:
        """Check required dependencies."""
        missing_deps = []
        
        if not MEDIAPIPE_AVAILABLE:
            missing_deps.append("mediapipe")
        
        if not OPENCV_AVAILABLE:
            missing_deps.append("opencv-python")
        
        if missing_deps:
            logger.warning(f"Missing dependencies: {missing_deps}")
            logger.warning("Some gesture and emotion features may not be available")

    async def _initialize_mediapipe(self) -> None:
        """Initialize MediaPipe for pose and face detection."""
        try:
            if MEDIAPIPE_AVAILABLE:
                # Initialize pose detection
                self.mp_pose = mp.solutions.pose
                self.pose_detector = self.mp_pose.Pose(
                    static_image_mode=False,
                    model_complexity=1,
                    smooth_landmarks=True,
                    enable_segmentation=False,
                    smooth_segmentation=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                
                # Initialize face mesh
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_detector = self.mp_face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                
                logger.info("MediaPipe initialized successfully")
            else:
                logger.warning("MediaPipe not available, using fallback methods")
                
        except Exception as e:
            logger.warning(f"MediaPipe initialization had issues: {e}")

    async def _load_default_sequences(self) -> None:
        """Load default gesture and emotion sequences."""
        try:
            # Default gesture sequences
            default_gestures = [
                GestureSequence(
                    sequence_id="greeting",
                    name="Greeting Sequence",
                    gestures=[
                        GestureConfig("wave", "Wave", "hand", 0.8, 2.0, 1.0),
                        GestureConfig("nod", "Nod", "head", 0.7, 1.0, 0.8)
                    ],
                    timing=[0.0, 1.0],
                    loop=False,
                    priority=1
                ),
                GestureSequence(
                    sequence_id="thinking",
                    name="Thinking Sequence",
                    gestures=[
                        GestureConfig("thinking_pose", "Thinking Pose", "body", 0.9, 3.0, 1.0),
                        GestureConfig("fold_arms", "Fold Arms", "body", 0.8, 2.0, 0.9)
                    ],
                    timing=[0.0, 1.5],
                    loop=False,
                    priority=2
                )
            ]
            
            # Default emotion sequences
            default_emotions = [
                EmotionSequence(
                    sequence_id="happy_greeting",
                    name="Happy Greeting",
                    emotions=[
                        EmotionConfig("happy", "Happy", 0.9, 2.0, "smooth"),
                        EmotionConfig("excited", "Excited", 0.7, 1.0, "blend")
                    ],
                    timing=[0.0, 1.0],
                    loop=False,
                    priority=1
                ),
                EmotionSequence(
                    sequence_id="thoughtful",
                    name="Thoughtful Expression",
                    emotions=[
                        EmotionConfig("thoughtful", "Thoughtful", 0.8, 3.0, "smooth"),
                        EmotionConfig("calm", "Calm", 0.6, 2.0, "blend")
                    ],
                    timing=[0.0, 2.0],
                    loop=False,
                    priority=2
                )
            ]
            
            # Store sequences
            for sequence in default_gestures:
                self.gesture_sequences[sequence.sequence_id] = sequence
            
            for sequence in default_emotions:
                self.emotion_sequences[sequence.sequence_id] = sequence
            
            logger.info(f"Loaded {len(default_gestures)} gesture and {len(default_emotions)} emotion sequences")
            
        except Exception as e:
            logger.warning(f"Failed to load default sequences: {e}")

    async def _validate_configuration(self) -> None:
        """Validate controller configuration."""
        if not self.supported_gestures:
            raise RuntimeError("No supported gestures configured")
        
        if not self.supported_emotions:
            raise RuntimeError("No supported emotions configured")

    @with_error_handling
    @with_retry(max_attempts=3)
    async def generate_gesture(self, request: GestureRequest) -> str:
        """Generate a gesture based on the request."""
        start_time = time.time()
        
        try:
            logger.info(f"Generating gesture for request {request.request_id}")
            
            # Validate request
            if not request.gesture_type:
                raise ValueError("Gesture type is required")
            
            if request.gesture_type not in self.supported_gestures:
                raise ValueError(f"Unsupported gesture type: {request.gesture_type}")
            
            # Create gesture configuration
            gesture_config = GestureConfig(
                gesture_id=f"gesture_{request.request_id}",
                name=request.gesture_type,
                category=self._get_gesture_category(request.gesture_type),
                confidence_threshold=0.7,
                duration=request.duration,
                intensity=request.intensity,
                parameters=request.custom_parameters
            )
            
            # Apply gesture
            gesture_path = await self._apply_gesture(gesture_config)
            
            # Update current gesture
            self.current_gesture = gesture_config
            
            # Calculate processing time
            processing_time = time.time() - start_time
            quality_score = self._calculate_gesture_quality(request, processing_time)
            
            # Update statistics
            self._update_gesture_stats(processing_time, True)
            
            logger.info(f"Gesture generated successfully in {processing_time:.2f}s")
            return gesture_path
            
        except Exception as e:
            self._update_gesture_stats(time.time() - start_time, False)
            logger.error(f"Gesture generation failed: {e}")
            raise

    async def _apply_gesture(self, gesture_config: GestureConfig) -> str:
        """Apply the gesture to the avatar."""
        try:
            # This would integrate with the avatar system
            # For now, return a placeholder path
            output_path = f"./temp/gesture_{gesture_config.gesture_id}.json"
            
            # Create temp directory if it doesn't exist
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Create gesture data
            gesture_data = {
                "gesture_id": gesture_config.gesture_id,
                "name": gesture_config.name,
                "category": gesture_config.category,
                "duration": gesture_config.duration,
                "intensity": gesture_config.intensity,
                "parameters": gesture_config.parameters,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save gesture data
            import json
            with open(output_path, 'w') as f:
                json.dump(gesture_data, f, indent=2)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to apply gesture: {e}")
            raise

    def _get_gesture_category(self, gesture_type: str) -> str:
        """Get the category for a gesture type."""
        gesture_categories = {
            "wave": "hand",
            "point": "hand",
            "thumbs_up": "hand",
            "thumbs_down": "hand",
            "clap": "hand",
            "nod": "head",
            "shake_head": "head",
            "shrug": "body",
            "fold_arms": "body",
            "hands_on_hips": "body",
            "thinking_pose": "body",
            "victory": "hand"
        }
        return gesture_categories.get(gesture_type, "body")

    def _calculate_gesture_quality(self, request: GestureRequest, processing_time: float) -> float:
        """Calculate quality score for generated gesture."""
        base_score = 0.8
        
        # Adjust for intensity
        if request.intensity > 0.8:
            base_score *= 1.1
        elif request.intensity < 0.3:
            base_score *= 0.9
        
        # Adjust for processing time
        if processing_time < 0.5:
            base_score *= 1.1
        elif processing_time > 2.0:
            base_score *= 0.9
        
        # Adjust for duration
        if request.duration > 5.0:
            base_score *= 0.9
        
        return min(1.0, max(0.0, base_score))

    def _update_gesture_stats(self, processing_time: float, success: bool):
        """Update gesture statistics."""
        self.controller_stats["total_gestures"] += 1
        
        if success:
            self.controller_stats["successful_gestures"] += 1
        else:
            self.controller_stats["failed_gestures"] += 1
        
        # Update average processing time
        current_avg = self.controller_stats["average_processing_time"]
        total_successful = self.controller_stats["successful_gestures"] + self.controller_stats["successful_emotions"]
        
        if total_successful > 0:
            self.controller_stats["average_processing_time"] = (
                (current_avg * (total_successful - 1) + processing_time) / total_successful
            )

    @with_error_handling
    @with_retry(max_attempts=3)
    async def generate_emotion(self, request: EmotionRequest) -> str:
        """Generate an emotion based on the request."""
        start_time = time.time()
        
        try:
            logger.info(f"Generating emotion for request {request.request_id}")
            
            # Validate request
            if not request.emotion_type:
                raise ValueError("Emotion type is required")
            
            if request.emotion_type not in self.supported_emotions:
                raise ValueError(f"Unsupported emotion type: {request.emotion_type}")
            
            # Create emotion configuration
            emotion_config = EmotionConfig(
                emotion_id=f"emotion_{request.request_id}",
                name=request.emotion_type,
                intensity=request.intensity,
                duration=request.duration,
                blend_mode=request.blend_with_current and "blend" or "smooth",
                parameters=request.custom_parameters
            )
            
            # Apply emotion
            emotion_path = await self._apply_emotion(emotion_config)
            
            # Update current emotion
            self.current_emotion = emotion_config
            
            # Calculate processing time
            processing_time = time.time() - start_time
            quality_score = self._calculate_emotion_quality(request, processing_time)
            
            # Update statistics
            self._update_emotion_stats(processing_time, True)
            
            logger.info(f"Emotion generated successfully in {processing_time:.2f}s")
            return emotion_path
            
        except Exception as e:
            self._update_emotion_stats(time.time() - start_time, False)
            logger.error(f"Emotion generation failed: {e}")
            raise

    async def _apply_emotion(self, emotion_config: EmotionConfig) -> str:
        """Apply the emotion to the avatar."""
        try:
            # This would integrate with the avatar system
            # For now, return a placeholder path
            output_path = f"./temp/emotion_{emotion_config.emotion_id}.json"
            
            # Create temp directory if it doesn't exist
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Create emotion data
            emotion_data = {
                "emotion_id": emotion_config.emotion_id,
                "name": emotion_config.name,
                "intensity": emotion_config.intensity,
                "duration": emotion_config.duration,
                "blend_mode": emotion_config.blend_mode,
                "parameters": emotion_config.parameters,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save emotion data
            import json
            with open(output_path, 'w') as f:
                json.dump(emotion_data, f, indent=2)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to apply emotion: {e}")
            raise

    def _calculate_emotion_quality(self, request: EmotionRequest, processing_time: float) -> float:
        """Calculate quality score for generated emotion."""
        base_score = 0.8
        
        # Adjust for intensity
        if request.intensity > 0.8:
            base_score *= 1.1
        elif request.intensity < 0.3:
            base_score *= 0.9
        
        # Adjust for processing time
        if processing_time < 0.3:
            base_score *= 1.1
        elif processing_time > 1.5:
            base_score *= 0.9
        
        # Adjust for duration
        if request.duration > 5.0:
            base_score *= 0.9
        
        # Adjust for blend mode
        if request.blend_with_current:
            base_score *= 1.05
        
        return min(1.0, max(0.0, base_score))

    def _update_emotion_stats(self, processing_time: float, success: bool):
        """Update emotion statistics."""
        self.controller_stats["total_emotions"] += 1
        
        if success:
            self.controller_stats["successful_emotions"] += 1
        else:
            self.controller_stats["failed_emotions"] += 1
        
        # Update average processing time
        current_avg = self.controller_stats["average_processing_time"]
        total_successful = self.controller_stats["successful_gestures"] + self.controller_stats["successful_emotions"]
        
        if total_successful > 0:
            self.controller_stats["average_processing_time"] = (
                (current_avg * (total_successful - 1) + processing_time) / total_successful
            )

    async def health_check(self) -> HealthCheckResult:
        """Check the health of the gesture and emotion controller."""
        try:
            # Check base service health
            base_health = await super().health_check()
            
            # Check dependencies
            dependencies = {
                "mediapipe": MEDIAPIPE_AVAILABLE,
                "opencv": OPENCV_AVAILABLE
            }
            
            # Check MediaPipe services
            mediapipe_health = {
                "pose_detector": self.pose_detector is not None,
                "face_detector": self.face_detector is not None
            }
            
            # Check sequences
            sequence_health = {
                "gesture_sequences": len(self.gesture_sequences),
                "emotion_sequences": len(self.emotion_sequences),
                "supported_gestures": len(self.supported_gestures),
                "supported_emotions": len(self.supported_emotions)
            }
            
            # Update base health
            base_health.details.update({
                "dependencies": dependencies,
                "mediapipe_services": mediapipe_health,
                "sequences": sequence_health,
                "controller_stats": self.controller_stats
            })
            
            return base_health
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                error_message=str(e)
            )

    async def get_available_gestures(self) -> List[str]:
        """Get list of available gesture types."""
        return self.supported_gestures.copy()

    async def get_available_emotions(self) -> List[str]:
        """Get list of available emotion types."""
        return self.supported_emotions.copy()

    async def get_gesture_sequence(self, sequence_id: str) -> Optional[GestureSequence]:
        """Get a specific gesture sequence."""
        return self.gesture_sequences.get(sequence_id)

    async def get_emotion_sequence(self, sequence_id: str) -> Optional[EmotionSequence]:
        """Get a specific emotion sequence."""
        return self.emotion_sequences.get(sequence_id)

    async def play_sequence(self, sequence_type: str, sequence_id: str) -> bool:
        """Play a gesture or emotion sequence."""
        try:
            if sequence_type == "gesture":
                sequence = self.gesture_sequences.get(sequence_id)
                if sequence:
                    for i, gesture in enumerate(sequence.gestures):
                        await asyncio.sleep(sequence.timing[i])
                        await self.generate_gesture(GestureRequest(
                            gesture_type=gesture.name,
                            intensity=gesture.intensity,
                            duration=gesture.duration
                        ))
                    return True
            elif sequence_type == "emotion":
                sequence = self.emotion_sequences.get(sequence_id)
                if sequence:
                    for i, emotion in enumerate(sequence.emotions):
                        await asyncio.sleep(sequence.timing[i])
                        await self.generate_emotion(EmotionRequest(
                            emotion_type=emotion.name,
                            intensity=emotion.intensity,
                            duration=emotion.duration
                        ))
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to play sequence {sequence_type}:{sequence_id}: {e}")
            return False

    async def cleanup_temp_files(self) -> None:
        """Clean up temporary gesture and emotion files."""
        try:
            temp_dir = Path("./temp")
            if temp_dir.exists():
                for gesture_file in temp_dir.glob("gesture_*.json"):
                    gesture_file.unlink()
                    logger.debug(f"Cleaned up temp file: {gesture_file}")
                for emotion_file in temp_dir.glob("emotion_*.json"):
                    emotion_file.unlink()
                    logger.debug(f"Cleaned up temp file: {emotion_file}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")
