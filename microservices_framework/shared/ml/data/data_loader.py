"""
Data Loading Utilities
Functional programming approach for data processing pipelines.
"""

import torch
from torch.utils.data import Dataset, DataLoader, random_split
from typing import List, Dict, Any, Optional, Callable
from functools import partial
import logging

logger = logging.getLogger(__name__)


class TextDataset(Dataset):
    """
    Generic text dataset following functional programming principles.
    """
    
    def __init__(
        self,
        texts: List[str],
        tokenizer: Any,
        max_length: int = 512,
        truncation: bool = True,
        padding: bool = True,
        return_labels: bool = False,
    ):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.truncation = truncation
        self.padding = padding
        self.return_labels = return_labels
    
    def __len__(self) -> int:
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        text = self.texts[idx]
        
        # Tokenize
        encoded = self.tokenizer(
            text,
            max_length=self.max_length,
            truncation=self.truncation,
            padding="max_length" if self.padding else False,
            return_tensors="pt",
        )
        
        result = {
            "input_ids": encoded["input_ids"].squeeze(),
            "attention_mask": encoded["attention_mask"].squeeze(),
        }
        
        if self.return_labels:
            # For language modeling, labels are same as input_ids
            result["labels"] = encoded["input_ids"].squeeze()
        
        return result


def create_dataloader(
    dataset: Dataset,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 0,
    pin_memory: bool = True,
    drop_last: bool = False,
    collate_fn: Optional[Callable] = None,
) -> DataLoader:
    """
    Create DataLoader with optimized settings.
    
    Args:
        dataset: PyTorch dataset
        batch_size: Batch size
        shuffle: Whether to shuffle
        num_workers: Number of worker processes
        pin_memory: Pin memory for faster GPU transfer
        drop_last: Drop last incomplete batch
        collate_fn: Custom collate function
        
    Returns:
        Configured DataLoader
    """
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory and torch.cuda.is_available(),
        drop_last=drop_last,
        collate_fn=collate_fn,
    )


def split_dataset(
    dataset: Dataset,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42,
) -> tuple:
    """
    Split dataset into train/val/test sets.
    
    Args:
        dataset: Dataset to split
        train_ratio: Training set ratio
        val_ratio: Validation set ratio
        test_ratio: Test set ratio
        seed: Random seed
        
    Returns:
        Tuple of (train_dataset, val_dataset, test_dataset)
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1.0"
    
    total_size = len(dataset)
    train_size = int(train_ratio * total_size)
    val_size = int(val_ratio * total_size)
    test_size = total_size - train_size - val_size
    
    generator = torch.Generator().manual_seed(seed)
    return random_split(
        dataset,
        [train_size, val_size, test_size],
        generator=generator,
    )


def collate_fn_padding(batch: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
    """
    Collate function with dynamic padding.
    Functional approach to batch processing.
    """
    input_ids = [item["input_ids"] for item in batch]
    attention_masks = [
        item.get("attention_mask", torch.ones_like(ids))
        for item, ids in zip(batch, input_ids)
    ]
    
    # Find max length in batch
    max_length = max(len(ids) for ids in input_ids)
    
    # Pad sequences
    padded_input_ids = []
    padded_attention_masks = []
    
    for ids, mask in zip(input_ids, attention_masks):
        pad_length = max_length - len(ids)
        padded_input_ids.append(
            torch.cat([ids, torch.zeros(pad_length, dtype=ids.dtype)])
        )
        padded_attention_masks.append(
            torch.cat([mask, torch.zeros(pad_length, dtype=mask.dtype)])
        )
    
    result = {
        "input_ids": torch.stack(padded_input_ids),
        "attention_mask": torch.stack(padded_attention_masks),
    }
    
    # Add labels if present
    if "labels" in batch[0]:
        labels = [item["labels"] for item in batch]
        padded_labels = []
        for label in labels:
            pad_length = max_length - len(label)
            padded_labels.append(
                torch.cat([label, torch.full((pad_length,), -100, dtype=label.dtype)])
            )
        result["labels"] = torch.stack(padded_labels)
    
    return result


# Functional data processing pipeline
def create_data_pipeline(
    texts: List[str],
    tokenizer: Any,
    max_length: int = 512,
    batch_size: int = 32,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    shuffle: bool = True,
    num_workers: int = 0,
) -> Dict[str, DataLoader]:
    """
    Create complete data pipeline from raw texts.
    Functional composition of data processing steps.
    
    Args:
        texts: List of input texts
        tokenizer: Tokenizer instance
        max_length: Maximum sequence length
        batch_size: Batch size
        train_ratio: Training split ratio
        val_ratio: Validation split ratio
        test_ratio: Test split ratio
        shuffle: Whether to shuffle training data
        num_workers: Number of data loader workers
        
    Returns:
        Dictionary with train/val/test DataLoaders
    """
    # Create dataset
    dataset = TextDataset(
        texts=texts,
        tokenizer=tokenizer,
        max_length=max_length,
        return_labels=True,
    )
    
    # Split dataset
    train_dataset, val_dataset, test_dataset = split_dataset(
        dataset,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio,
    )
    
    # Create data loaders
    train_loader = create_dataloader(
        train_dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=collate_fn_padding,
    )
    
    val_loader = create_dataloader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        collate_fn=collate_fn_padding,
    )
    
    test_loader = create_dataloader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        collate_fn=collate_fn_padding,
    )
    
    return {
        "train": train_loader,
        "val": val_loader,
        "test": test_loader,
    }



