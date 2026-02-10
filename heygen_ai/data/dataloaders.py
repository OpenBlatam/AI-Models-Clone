"""
Data Loaders for HeyGen AI
===========================

Implements efficient data loading following best practices:
- Proper DataLoader configuration
- Collate functions for batching
- Data augmentation
- Caching and prefetching
"""

import logging
from typing import Any, Callable, Dict, List, Optional

import torch
from torch.utils.data import DataLoader, Dataset, random_split
from torch.nn.utils.rnn import pad_sequence

logger = logging.getLogger(__name__)


def create_dataloader(
    dataset: Dataset,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 4,
    pin_memory: bool = True,
    drop_last: bool = False,
    collate_fn: Optional[Callable] = None,
) -> DataLoader:
    """Create a DataLoader with best practices.
    
    Args:
        dataset: PyTorch dataset
        batch_size: Batch size
        shuffle: Whether to shuffle data
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
        persistent_workers=num_workers > 0,
    )


def collate_text_sequences(batch: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
    """Collate function for text sequences with padding.
    
    Args:
        batch: List of samples with 'input_ids' and 'attention_mask'
    
    Returns:
        Batched tensors
    """
    input_ids = [sample['input_ids'] for sample in batch]
    attention_masks = [sample.get('attention_mask') for sample in batch]
    labels = [sample.get('labels') for sample in batch]
    
    # Pad sequences
    input_ids = pad_sequence(input_ids, batch_first=True, padding_value=0)
    
    if attention_masks[0] is not None:
        attention_masks = pad_sequence(
            attention_masks,
            batch_first=True,
            padding_value=0
        )
    else:
        # Create attention mask from input_ids
        attention_masks = (input_ids != 0).long()
    
    result = {
        'input_ids': input_ids,
        'attention_mask': attention_masks,
    }
    
    if labels[0] is not None:
        if isinstance(labels[0], torch.Tensor):
            labels = pad_sequence(labels, batch_first=True, padding_value=-100)
        else:
            labels = torch.tensor(labels)
        result['labels'] = labels
    
    return result


def split_dataset(
    dataset: Dataset,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    random_seed: Optional[int] = None,
) -> tuple[Dataset, Dataset, Dataset]:
    """Split dataset into train, validation, and test sets.
    
    Args:
        dataset: Full dataset
        train_ratio: Proportion for training
        val_ratio: Proportion for validation
        test_ratio: Proportion for testing
        random_seed: Random seed for reproducibility
    
    Returns:
        Tuple of (train_dataset, val_dataset, test_dataset)
    
    Raises:
        ValueError: If ratios don't sum to 1.0
    """
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
        raise ValueError("Ratios must sum to 1.0")
    
    if random_seed is not None:
        generator = torch.Generator().manual_seed(random_seed)
    else:
        generator = None
    
    total_size = len(dataset)
    train_size = int(total_size * train_ratio)
    val_size = int(total_size * val_ratio)
    test_size = total_size - train_size - val_size
    
    train_dataset, val_dataset, test_dataset = random_split(
        dataset,
        [train_size, val_size, test_size],
        generator=generator,
    )
    
    return train_dataset, val_dataset, test_dataset



