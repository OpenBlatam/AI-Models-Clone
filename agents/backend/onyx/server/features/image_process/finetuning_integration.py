#!/usr/bin/env python3
"""
Fine-tuning Integration Module

Integrates LoRA and P-tuning with the transformer system.
"""

import torch
import torch.nn as nn
from typing import Dict, Any, List

# Import fine-tuning modules
try:
    from lora_finetuning import LoRALayer, LoRAFineTuner
    from ptuning_module import PTuningModule, PTuningFineTuner
    FINETUNING_AVAILABLE = True
except ImportError:
    FINETUNING_AVAILABLE = False


def apply_lora_to_model(model: nn.Module, target_modules: List[str], 
                       r: int = 16, alpha: float = 32.0) -> nn.Module:
    """Apply LoRA to a model."""
    if not FINETUNING_AVAILABLE:
        return model
    
    fine_tuner = LoRAFineTuner(model, target_modules, r, alpha)
    fine_tuner.freeze_base_model()
    return fine_tuner.model


def apply_p_tuning_to_model(model: nn.Module, config: Dict[str, Any]) -> PTuningFineTuner:
    """Apply P-tuning to a model."""
    if not FINETUNING_AVAILABLE:
        return None
    
    fine_tuner = PTuningFineTuner(model, config)
    return fine_tuner


def get_finetuning_stats(model: nn.Module, fine_tuner) -> Dict[str, Any]:
    """Get fine-tuning statistics."""
    if not FINETUNING_AVAILABLE:
        return {"error": "Fine-tuning not available"}
    
    if hasattr(fine_tuner, 'get_parameter_stats'):
        return fine_tuner.get_parameter_stats()
    else:
        return {"error": "Invalid fine-tuner"}


# Example usage
if __name__ == "__main__":
    print("Fine-tuning integration module ready!")
    print(f"Fine-tuning available: {FINETUNING_AVAILABLE}")


