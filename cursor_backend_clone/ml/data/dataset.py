"""
Code Dataset - Dataset para código
===================================

Dataset personalizado para código.
"""

import logging
from typing import List, Dict, Any, Optional
import torch
from torch.utils.data import Dataset

logger = logging.getLogger(__name__)


class CodeDataset(Dataset):
    """Dataset para código"""
    
    def __init__(
        self,
        texts: List[str],
        tokenizer,
        max_length: int = 512,
        padding: str = "max_length",
        truncation: bool = True
    ):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.padding = padding
        self.truncation = truncation
    
    def __len__(self) -> int:
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Obtener item del dataset"""
        text = self.texts[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=self.truncation,
            max_length=self.max_length,
            padding=self.padding,
            return_tensors="pt"
        )
        
        # Convertir a tensores y remover dimensión extra
        return {
            k: v.squeeze(0) for k, v in encoding.items()
        }
    
    @classmethod
    def from_file(cls, filepath: str, tokenizer, **kwargs):
        """Crear dataset desde archivo"""
        with open(filepath, 'r', encoding='utf-8') as f:
            texts = [line.strip() for line in f if line.strip()]
        
        return cls(texts, tokenizer, **kwargs)
    
    @classmethod
    def from_list(cls, texts: List[str], tokenizer, **kwargs):
        """Crear dataset desde lista"""
        return cls(texts, tokenizer, **kwargs)


