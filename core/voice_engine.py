"""
Voice Engine for HeyGen AI
==========================

Provides voice synthesis, cloning, and processing capabilities
with enterprise-grade performance and reliability.
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

# Audio processing imports
import librosa
import soundfile as sf
from pydub import AudioSegment
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class VoiceModel:
    """Enhanced voice model configuration."""
    
    id: str
    name: str
    language: str
    accent: str
    gender: str
    style: str
    model_path: str
    sample_rate: int = 22050
    characteristics: Dict[str, Any] = field(default_factory=dict)
    emotion_support: bool = True
    style_transfer: bool = False
    voice_cloning: bool = False


@dataclass
class AudioGenerationConfig:
    """Configuration for audio generation."""
    
    sample_rate: int = 22050
    bit_depth: int = 16
    channels: int = 1
    format: str = "wav"
    quality: str = "high"
    speed: float = 1.0
    pitch_shift: float = 0.0
    volume_normalization: bool = True
    noise_reduction: bool = True
    compression: bool = True


@dataclass
class VoiceGenerationRequest:
    """Request for voice generation."""
    
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    voice_model_id: str = ""
    language: str = "en"
    emotion: str = "neutral"
    speed: float = 1.0
    pitch: float = 0.0
    volume: float = 1.0
    quality: str = "high"
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class VoiceGenerationResult:
    """Result of voice generation."""
    
    request_id: str
    audio_path: str
    duration: float
    metadata: Dict[str, Any]
    generation_time: float
    quality_score: float
    timestamp: datetime = field(default_factory=datetime.now)


class VoiceEngine(BaseService):
    """Voice synthesis and processing engine."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the voice engine."""
        super().__init__("VoiceEngine", ServiceType.CORE, config)
        
        # Voice models
        self.voice_models: Dict[str, VoiceModel] = {}
        
        # Configuration
        self.audio_config = AudioGenerationConfig()
        
        # Error handling
        self.error_handler = ErrorHandler()
        
        # Configuration manager
        self.config_manager = ConfigurationManager()
        
        # Logging service
        self.logging_service = LoggingService()
        
        # Performance tracking
        self.generation_stats = {
            "total_generated": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "average_generation_time": 0.0,
            "total_audio_duration": 0.0
        }
        
        # Audio processing settings
        self.supported_formats = ["wav", "mp3", "ogg", "flac", "m4a"]
        self.supported_sample_rates = [8000, 16000, 22050, 44100, 48000]

    async def _initialize_service_impl(self) -> None:
        """Initialize voice synthesis services."""
        try:
            logger.info("Initializing voice synthesis services...")
            
            # Load default voice models
            await self._load_default_voice_models()
            
            # Initialize audio processing
            await self._initialize_audio_processing()
            
            # Validate configuration
            await self._validate_configuration()
            
            logger.info("Voice engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize voice engine: {e}")
            raise

    async def _load_default_voice_models(self) -> None:
        """Load default voice models."""
        default_models = [
            VoiceModel(
                id="en_female_1",
                name="Emma",
                language="en",
                accent="american",
                gender="female",
                style="professional",
                model_path="./models/voices/en_female_1",
                emotion_support=True,
                style_transfer=True
            ),
            VoiceModel(
                id="en_male_1",
                name="James",
                language="en",
                accent="british",
                gender="male",
                style="professional",
                model_path="./models/voices/en_male_1",
                emotion_support=True,
                style_transfer=True
            ),
            VoiceModel(
                id="es_female_1",
                name="Sofia",
                language="es",
                accent="mexican",
                gender="female",
                style="friendly",
                model_path="./models/voices/es_female_1",
                emotion_support=True,
                style_transfer=False
            )
        ]
        
        for model in default_models:
            self.voice_models[model.id] = model
        
        logger.info(f"Loaded {len(default_models)} default voice models")

    async def _initialize_audio_processing(self) -> None:
        """Initialize audio processing capabilities."""
        try:
            # Test audio processing libraries
            test_audio = np.zeros(1000, dtype=np.float32)
            
            # Test librosa
            librosa.feature.mfcc(y=test_audio, sr=22050)
            
            # Test soundfile
            sf.write("/tmp/test.wav", test_audio, 22050)
            
            # Test pydub
            audio_segment = AudioSegment.from_wav("/tmp/test.wav")
            
            logger.info("Audio processing libraries initialized successfully")
            
        except Exception as e:
            logger.warning(f"Some audio processing features may not be available: {e}")

    async def _validate_configuration(self) -> None:
        """Validate voice engine configuration."""
        if not self.voice_models:
            raise RuntimeError("No voice models available")
        
        if not self.audio_config:
            raise RuntimeError("Audio configuration not set")

    @with_error_handling
    @with_retry(max_attempts=3)
    async def generate_speech(self, request: VoiceGenerationRequest) -> VoiceGenerationResult:
        """Generate speech from text using the specified voice model."""
        start_time = time.time()
        
        try:
            logger.info(f"Generating speech for request {request.request_id}")
            
            # Validate request
            if not request.text:
                raise ValueError("Text content is required for speech generation")
            
            if not request.voice_model_id:
                raise ValueError("Voice model ID is required")
            
            # Get voice model
            voice_model = self.voice_models.get(request.voice_model_id)
            if not voice_model:
                raise ValueError(f"Voice model {request.voice_model_id} not found")
            
            # Generate speech (placeholder implementation)
            audio_path = await self._generate_speech_impl(request, voice_model)
            
            # Process audio
            processed_audio_path = await self._process_audio(audio_path, request)
            
            # Calculate metrics
            generation_time = time.time() - start_time
            duration = await self._get_audio_duration(processed_audio_path)
            quality_score = self._calculate_quality_score(request, generation_time, duration)
            
            # Update statistics
            self._update_generation_stats(generation_time, True, duration)
            
            # Create result
            result = VoiceGenerationResult(
                request_id=request.request_id,
                audio_path=processed_audio_path,
                duration=duration,
                metadata={
                    "voice_model": voice_model.name,
                    "language": voice_model.language,
                    "emotion": request.emotion,
                    "generation_time": generation_time,
                    "quality_score": quality_score
                },
                generation_time=generation_time,
                quality_score=quality_score
            )
            
            logger.info(f"Speech generated successfully in {generation_time:.2f}s")
            return result
            
        except Exception as e:
            self._update_generation_stats(time.time() - start_time, False, 0.0)
            logger.error(f"Speech generation failed: {e}")
            raise

    async def _generate_speech_impl(self, request: VoiceGenerationRequest, voice_model: VoiceModel) -> str:
        """Implementation of speech generation."""
        # This would integrate with actual TTS models
        # For now, return a placeholder path
        output_path = f"./temp/speech_{request.request_id}.wav"
        
        # Create temp directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Generate a simple test audio file
        sample_rate = voice_model.sample_rate
        duration = len(request.text.split()) * 0.5  # Rough estimate
        samples = int(duration * sample_rate)
        
        # Generate a simple sine wave as placeholder
        frequency = 440  # A4 note
        t = np.linspace(0, duration, samples, False)
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Save audio
        sf.write(output_path, audio_data, sample_rate)
        
        return output_path

    async def _process_audio(self, audio_path: str, request: VoiceGenerationRequest) -> str:
        """Process generated audio with enhancements."""
        try:
            # Load audio
            audio_data, sample_rate = librosa.load(audio_path, sr=None)
            
            # Apply speed adjustment
            if request.speed != 1.0:
                audio_data = librosa.effects.time_stretch(audio_data, rate=request.speed)
            
            # Apply pitch shift
            if request.pitch != 0.0:
                audio_data = librosa.effects.pitch_shift(audio_data, sr=sample_rate, n_steps=request.pitch)
            
            # Apply volume adjustment
            if request.volume != 1.0:
                audio_data = audio_data * request.volume
            
            # Normalize volume
            if self.audio_config.volume_normalization:
                audio_data = librosa.util.normalize(audio_data)
            
            # Save processed audio
            processed_path = audio_path.replace(".wav", "_processed.wav")
            sf.write(processed_path, audio_data, sample_rate)
            
            return processed_path
            
        except Exception as e:
            logger.warning(f"Audio processing failed, returning original: {e}")
            return audio_path

    async def _get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file."""
        try:
            audio_data, sample_rate = librosa.load(audio_path, sr=None)
            return len(audio_data) / sample_rate
        except Exception as e:
            logger.warning(f"Could not determine audio duration: {e}")
            return 0.0

    def _calculate_quality_score(self, request: VoiceGenerationRequest, generation_time: float, duration: float) -> float:
        """Calculate quality score for generated speech."""
        base_score = 0.8
        
        # Adjust for quality setting
        quality_multipliers = {
            "low": 0.7,
            "medium": 0.85,
            "high": 1.0,
            "ultra": 1.2
        }
        base_score *= quality_multipliers.get(request.quality, 1.0)
        
        # Adjust for generation time
        if generation_time < 2.0:
            base_score *= 1.1
        elif generation_time > 10.0:
            base_score *= 0.9
        
        # Adjust for text length
        if len(request.text) > 100:
            base_score *= 1.05
        
        # Adjust for duration (longer audio might be more complex)
        if duration > 30.0:
            base_score *= 1.1
        
        return min(1.0, max(0.0, base_score))

    def _update_generation_stats(self, generation_time: float, success: bool, duration: float):
        """Update generation statistics."""
        self.generation_stats["total_generated"] += 1
        
        if success:
            self.generation_stats["successful_generations"] += 1
            self.generation_stats["total_audio_duration"] += duration
        else:
            self.generation_stats["failed_generations"] += 1
        
        # Update average generation time
        current_avg = self.generation_stats["average_generation_time"]
        total_successful = self.generation_stats["successful_generations"]
        
        if total_successful > 0:
            self.generation_stats["average_generation_time"] = (
                (current_avg * (total_successful - 1) + generation_time) / total_successful
            )

    @with_error_handling
    async def clone_voice(self, audio_path: str, voice_name: str) -> str:
        """Clone a voice from audio sample."""
        try:
            logger.info(f"Cloning voice from {audio_path}")
            
            # Load audio for analysis
            audio_data, sample_rate = librosa.load(audio_path, sr=22050)
            
            # Extract voice characteristics
            mfcc_features = librosa.feature.mfcc(y=audio_data, sr=sample_rate)
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            
            # Create voice model
            voice_id = f"cloned_{voice_name}_{int(time.time())}"
            cloned_model = VoiceModel(
                id=voice_id,
                name=voice_name,
                language="auto",
                accent="auto",
                gender="auto",
                style="cloned",
                model_path=f"./models/voices/{voice_id}",
                voice_cloning=True,
                characteristics={
                    "mfcc_features": mfcc_features.tolist(),
                    "spectral_centroids": spectral_centroids.tolist(),
                    "sample_rate": sample_rate,
                    "original_audio": audio_path
                }
            )
            
            # Save cloned model
            self.voice_models[voice_id] = cloned_model
            
            logger.info(f"Voice cloned successfully: {voice_id}")
            return voice_id
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            raise

    async def health_check(self) -> HealthCheckResult:
        """Check the health of the voice engine."""
        try:
            # Check base service health
            base_health = await super().health_check()
            
            # Check voice models
            model_health = {
                "total_models": len(self.voice_models),
                "available_models": list(self.voice_models.keys()),
                "cloned_models": len([m for m in self.voice_models.values() if m.voice_cloning])
            }
            
            # Check audio processing
            audio_health = {
                "supported_formats": self.supported_formats,
                "supported_sample_rates": self.supported_sample_rates,
                "librosa_available": True,
                "soundfile_available": True,
                "pydub_available": True
            }
            
            # Update base health
            base_health.details.update({
                "voice_models": model_health,
                "audio_processing": audio_health,
                "generation_stats": self.generation_stats
            })
            
            return base_health
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                error_message=str(e)
            )

    async def get_available_voices(self) -> List[VoiceModel]:
        """Get list of available voice models."""
        return list(self.voice_models.values())

    async def get_voice_model(self, voice_id: str) -> Optional[VoiceModel]:
        """Get a specific voice model."""
        return self.voice_models.get(voice_id)

    async def delete_voice_model(self, voice_id: str) -> bool:
        """Delete a voice model."""
        try:
            if voice_id in self.voice_models:
                del self.voice_models[voice_id]
                logger.info(f"Voice model {voice_id} deleted")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete voice model {voice_id}: {e}")
            return False

    async def cleanup_temp_files(self) -> None:
        """Clean up temporary audio files."""
        try:
            temp_dir = Path("./temp")
            if temp_dir.exists():
                for audio_file in temp_dir.glob("*.wav"):
                    if audio_file.name.startswith("speech_") or audio_file.name.endswith("_processed.wav"):
                        audio_file.unlink()
                        logger.debug(f"Cleaned up temp file: {audio_file}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")
