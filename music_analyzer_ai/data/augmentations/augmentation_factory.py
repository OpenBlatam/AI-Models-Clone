"""
Augmentation Factory
Creates augmentation pipelines
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

from .audio_augmentations import (
    TimeStretchAugmentation,
    PitchShiftAugmentation,
    NoiseAugmentation,
    VolumeAugmentation,
    TimeMaskAugmentation
)
from .feature_augmentations import (
    FeatureNoiseAugmentation,
    FeatureScaleAugmentation,
    FeatureShiftAugmentation
)
from ..transforms.compose import Compose


class AugmentationFactory:
    """Factory for creating augmentation pipelines"""
    
    @staticmethod
    def create_audio_augmentation_pipeline(
        augmentations: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> Compose:
        """
        Create audio augmentation pipeline
        
        Args:
            augmentations: List of augmentation names
            config: Configuration for augmentations
        
        Returns:
            Composed augmentation pipeline
        """
        config = config or {}
        aug_list = []
        
        for aug_name in augmentations:
            aug_name = aug_name.lower()
            
            if aug_name == "time_stretch":
                aug_list.append(TimeStretchAugmentation(
                    **config.get("time_stretch", {})
                ))
            elif aug_name == "pitch_shift":
                aug_list.append(PitchShiftAugmentation(
                    **config.get("pitch_shift", {})
                ))
            elif aug_name == "noise":
                aug_list.append(NoiseAugmentation(
                    **config.get("noise", {})
                ))
            elif aug_name == "volume":
                aug_list.append(VolumeAugmentation(
                    **config.get("volume", {})
                ))
            elif aug_name == "time_mask":
                aug_list.append(TimeMaskAugmentation(
                    **config.get("time_mask", {})
                ))
            else:
                logger.warning(f"Unknown audio augmentation: {aug_name}")
        
        return Compose(aug_list)
    
    @staticmethod
    def create_feature_augmentation_pipeline(
        augmentations: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> Compose:
        """
        Create feature augmentation pipeline
        
        Args:
            augmentations: List of augmentation names
            config: Configuration for augmentations
        
        Returns:
            Composed augmentation pipeline
        """
        config = config or {}
        aug_list = []
        
        for aug_name in augmentations:
            aug_name = aug_name.lower()
            
            if aug_name == "noise":
                aug_list.append(FeatureNoiseAugmentation(
                    **config.get("noise", {})
                ))
            elif aug_name == "scale":
                aug_list.append(FeatureScaleAugmentation(
                    **config.get("scale", {})
                ))
            elif aug_name == "shift":
                aug_list.append(FeatureShiftAugmentation(
                    **config.get("shift", {})
                ))
            else:
                logger.warning(f"Unknown feature augmentation: {aug_name}")
        
        return Compose(aug_list)


def create_augmentation(
    augmentation_type: str,
    augmentations: List[str],
    config: Optional[Dict[str, Any]] = None
) -> Compose:
    """
    Convenience function for creating augmentation pipelines
    
    Args:
        augmentation_type: "audio" or "feature"
        augmentations: List of augmentation names
        config: Configuration
    
    Returns:
        Augmentation pipeline
    """
    if augmentation_type == "audio":
        return AugmentationFactory.create_audio_augmentation_pipeline(
            augmentations, config
        )
    elif augmentation_type == "feature":
        return AugmentationFactory.create_feature_augmentation_pipeline(
            augmentations, config
        )
    else:
        raise ValueError(f"Unknown augmentation type: {augmentation_type}")



