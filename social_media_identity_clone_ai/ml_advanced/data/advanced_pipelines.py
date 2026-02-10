"""
Pipelines avanzados de procesamiento de datos
"""

import torch
from torch.utils.data import Dataset, DataLoader
from typing import List, Dict, Any, Optional, Callable
import logging
from functools import partial

logger = logging.getLogger(__name__)


class DataPipeline:
    """Pipeline de procesamiento de datos"""
    
    def __init__(self):
        self.transforms = []
    
    def add_transform(self, transform: Callable):
        """Agrega transformación al pipeline"""
        self.transforms.append(transform)
        return self
    
    def apply(self, data: Any) -> Any:
        """Aplica todas las transformaciones"""
        result = data
        for transform in self.transforms:
            result = transform(result)
        return result


class PreprocessingPipeline:
    """Pipeline de preprocesamiento"""
    
    def __init__(self, tokenizer: Any, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def preprocess_text(
        self,
        text: str,
        padding: str = "max_length",
        truncation: bool = True
    ) -> Dict[str, torch.Tensor]:
        """Preprocesa texto"""
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding=padding,
            truncation=truncation,
            return_tensors="pt"
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze()
        }
    
    def preprocess_batch(
        self,
        texts: List[str]
    ) -> Dict[str, torch.Tensor]:
        """Preprocesa batch de textos"""
        encodings = self.tokenizer(
            texts,
            max_length=self.max_length,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )
        return {
            "input_ids": encodings["input_ids"],
            "attention_mask": encodings["attention_mask"]
        }


class PostprocessingPipeline:
    """Pipeline de postprocesamiento"""
    
    def __init__(self, tokenizer: Any):
        self.tokenizer = tokenizer
    
    def decode_logits(
        self,
        logits: torch.Tensor,
        skip_special_tokens: bool = True
    ) -> str:
        """Decodifica logits a texto"""
        predictions = torch.argmax(logits, dim=-1)
        text = self.tokenizer.decode(predictions, skip_special_tokens=skip_special_tokens)
        return text
    
    def sample_from_logits(
        self,
        logits: torch.Tensor,
        temperature: float = 1.0,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None
    ) -> torch.Tensor:
        """Sampling de logits"""
        if temperature != 1.0:
            logits = logits / temperature
        
        if top_k is not None:
            # Top-k sampling
            indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
            logits[indices_to_remove] = float('-inf')
        
        if top_p is not None:
            # Nucleus sampling
            sorted_logits, sorted_indices = torch.sort(logits, descending=True)
            cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
            sorted_indices_to_remove = cumulative_probs > top_p
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = 0
            indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
            logits[indices_to_remove] = float('-inf')
        
        probs = torch.softmax(logits, dim=-1)
        return torch.multinomial(probs, num_samples=1)




