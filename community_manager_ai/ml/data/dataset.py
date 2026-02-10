"""
Dataset - Datasets para Entrenamiento
======================================

Datasets optimizados para entrenamiento rápido.
"""

import torch
from torch.utils.data import Dataset, DataLoader
from typing import List, Dict, Any, Optional
import numpy as np
from transformers import AutoTokenizer


class SocialMediaDataset(Dataset):
    """Dataset para posts de redes sociales"""
    
    def __init__(
        self,
        texts: List[str],
        labels: Optional[List[int]] = None,
        tokenizer: Optional[Any] = None,
        max_length: int = 512
    ):
        """
        Inicializar dataset
        
        Args:
            texts: Lista de textos
            labels: Lista de labels (opcional)
            tokenizer: Tokenizer a usar
            max_length: Longitud máxima
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self) -> int:
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        text = self.texts[idx]
        
        # Tokenizar
        if self.tokenizer:
            encoding = self.tokenizer(
                text,
                truncation=True,
                padding="max_length",
                max_length=self.max_length,
                return_tensors="pt"
            )
            item = {
                "input_ids": encoding["input_ids"].squeeze(),
                "attention_mask": encoding["attention_mask"].squeeze()
            }
        else:
            item = {"text": text}
        
        # Agregar label si existe
        if self.labels is not None:
            item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        
        return item


def create_fast_dataloader(
    dataset: Dataset,
    batch_size: int = 32,
    num_workers: int = 4,
    pin_memory: bool = True,
    prefetch_factor: int = 2
) -> DataLoader:
    """
    Crear DataLoader optimizado
    
    Args:
        dataset: Dataset
        batch_size: Tamaño de batch
        num_workers: Número de workers
        pin_memory: Pin memory para transferencia rápida a GPU
        prefetch_factor: Factor de prefetch
        
    Returns:
        DataLoader optimizado
    """
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        prefetch_factor=prefetch_factor,
        persistent_workers=True if num_workers > 0 else False
    )




