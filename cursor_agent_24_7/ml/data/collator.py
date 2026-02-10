"""
Data Collator - Collator para datos
====================================

Data collator para batching.
"""

import logging
from typing import Dict, List, Any, Optional
import torch
from transformers import DataCollatorForLanguageModeling

logger = logging.getLogger(__name__)


class DataCollator:
    """Data collator para código"""
    
    def __init__(
        self,
        tokenizer,
        mlm: bool = False,
        mlm_probability: float = 0.15,
        pad_to_multiple_of: Optional[int] = None
    ):
        self.tokenizer = tokenizer
        self.collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=mlm,
            mlm_probability=mlm_probability,
            pad_to_multiple_of=pad_to_multiple_of
        )
    
    def __call__(self, features: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        """Colapsar batch"""
        return self.collator(features)

