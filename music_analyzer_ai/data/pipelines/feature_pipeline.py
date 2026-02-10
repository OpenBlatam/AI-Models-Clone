"""
Functional Feature Extraction Pipeline
Modular feature extraction using functional programming
"""

from typing import Callable, List, Dict, Any, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("Librosa not available")


class FeatureExtractionPipeline:
    """
    Functional pipeline for feature extraction
    Composable feature extractors
    """
    
    def __init__(self):
        self.extractors: List[Callable] = []
    
    def add_extractor(self, extractor: Callable, name: Optional[str] = None):
        """
        Add feature extractor to pipeline
        
        Args:
            extractor: Function that takes audio and returns features
            name: Optional name for the extractor
        """
        if name:
            extractor.__name__ = name
        self.extractors.append(extractor)
        logger.info(f"Added extractor: {extractor.__name__}")
    
    def extract(self, audio: np.ndarray, sr: int = 22050) -> Dict[str, np.ndarray]:
        """
        Extract features using all extractors
        
        Args:
            audio: Audio signal
            sr: Sample rate
        
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        for extractor in self.extractors:
            try:
                feature = extractor(audio, sr)
                features[extractor.__name__] = feature
            except Exception as e:
                logger.error(f"Error in extractor {extractor.__name__}: {str(e)}")
                features[extractor.__name__] = None
        
        return features
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> Dict[str, np.ndarray]:
        """Make pipeline callable"""
        return self.extract(audio, sr)


# Predefined feature extractors
def extract_mfcc(audio: np.ndarray, sr: int = 22050, n_mfcc: int = 13) -> np.ndarray:
    """Extract MFCC features"""
    if not LIBROSA_AVAILABLE:
        raise ImportError("Librosa required")
    
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
    return mfcc.T  # [time, n_mfcc]


def extract_chroma(audio: np.ndarray, sr: int = 22050) -> np.ndarray:
    """Extract chroma features"""
    if not LIBROSA_AVAILABLE:
        raise ImportError("Librosa required")
    
    chroma = librosa.feature.chroma(y=audio, sr=sr)
    return chroma.T  # [time, 12]


def extract_spectral_contrast(audio: np.ndarray, sr: int = 22050) -> np.ndarray:
    """Extract spectral contrast"""
    if not LIBROSA_AVAILABLE:
        raise ImportError("Librosa required")
    
    contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
    return contrast.T  # [time, n_bands]


def extract_tonnetz(audio: np.ndarray, sr: int = 22050) -> np.ndarray:
    """Extract tonnetz features"""
    if not LIBROSA_AVAILABLE:
        raise ImportError("Librosa required")
    
    tonnetz = librosa.feature.tonnetz(y=audio, sr=sr)
    return tonnetz.T  # [time, 6]


def extract_tempo(audio: np.ndarray, sr: int = 22050) -> float:
    """Extract tempo"""
    if not LIBROSA_AVAILABLE:
        raise ImportError("Librosa required")
    
    tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
    return float(tempo)


def extract_zero_crossing_rate(audio: np.ndarray, sr: int = 22050) -> np.ndarray:
    """Extract zero crossing rate"""
    if not LIBROSA_AVAILABLE:
        raise ImportError("Librosa required")
    
    zcr = librosa.feature.zero_crossing_rate(audio)
    return zcr.T  # [time, 1]


# Factory function for creating common pipelines
def create_standard_feature_pipeline() -> FeatureExtractionPipeline:
    """Create standard feature extraction pipeline"""
    pipeline = FeatureExtractionPipeline()
    
    pipeline.add_extractor(extract_mfcc, "mfcc")
    pipeline.add_extractor(extract_chroma, "chroma")
    pipeline.add_extractor(extract_spectral_contrast, "spectral_contrast")
    pipeline.add_extractor(extract_tonnetz, "tonnetz")
    pipeline.add_extractor(extract_zero_crossing_rate, "zcr")
    
    return pipeline



