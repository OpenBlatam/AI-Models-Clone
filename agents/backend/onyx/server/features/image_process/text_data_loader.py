#!/usr/bin/env python3
"""
Text Data Loader Module

This module provides comprehensive data loading capabilities for text data,
integrating with the tokenization system for efficient training.
"""

import torch
from torch.utils.data import Dataset, DataLoader, IterableDataset
from typing import Dict, List, Tuple, Optional, Union, Any, Iterator
import json
import csv
import logging
import random
import numpy as np
from pathlib import Path
import pickle
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import queue
import threading

from text_tokenization import BaseTokenizer, SequenceProcessor, TokenizerConfig

logger = logging.getLogger(__name__)


@dataclass
class DataLoaderConfig:
    """Configuration for data loader."""
    batch_size: int = 32
    max_length: int = 512
    shuffle: bool = True
    num_workers: int = 4
    pin_memory: bool = True
    drop_last: bool = False
    prefetch_factor: int = 2
    persistent_workers: bool = True


class TextDataset(Dataset):
    """Base text dataset class."""
    
    def __init__(self, texts: List[str], tokenizer: BaseTokenizer, 
                 max_length: int = 512, add_special_tokens: bool = True):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.add_special_tokens = add_special_tokens
        self.processor = SequenceProcessor(tokenizer, max_length)
    
    def __len__(self) -> int:
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        text = self.texts[idx]
        return self.processor.process_single_sequence(
            text, 
            add_special_tokens=self.add_special_tokens
        )


class ClassificationDataset(Dataset):
    """Dataset for text classification tasks."""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer: BaseTokenizer,
                 max_length: int = 512, add_special_tokens: bool = True):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.add_special_tokens = add_special_tokens
        self.processor = SequenceProcessor(tokenizer, max_length)
        
        # Validate inputs
        if len(texts) != len(labels):
            raise ValueError("Number of texts and labels must be equal")
    
    def __len__(self) -> int:
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        text = self.texts[idx]
        label = self.labels[idx]
        
        processed = self.processor.process_single_sequence(
            text, 
            add_special_tokens=self.add_special_tokens
        )
        processed['labels'] = torch.tensor(label, dtype=torch.long)
        
        return processed


class SequenceToSequenceDataset(Dataset):
    """Dataset for sequence-to-sequence tasks."""
    
    def __init__(self, source_texts: List[str], target_texts: List[str], 
                 tokenizer: BaseTokenizer, max_length: int = 512, 
                 add_special_tokens: bool = True):
        self.source_texts = source_texts
        self.target_texts = target_texts
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.add_special_tokens = add_special_tokens
        self.processor = SequenceProcessor(tokenizer, max_length)
        
        # Validate inputs
        if len(source_texts) != len(target_texts):
            raise ValueError("Number of source and target texts must be equal")
    
    def __len__(self) -> int:
        return len(self.source_texts)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        source_text = self.source_texts[idx]
        target_text = self.target_texts[idx]
        
        # Process source and target
        source_processed = self.processor.process_single_sequence(
            source_text, 
            add_special_tokens=self.add_special_tokens
        )
        target_processed = self.processor.process_single_sequence(
            target_text, 
            add_special_tokens=self.add_special_tokens
        )
        
        return {
            'input_ids': source_processed['input_ids'],
            'attention_mask': source_processed['attention_mask'],
            'labels': target_processed['input_ids'],
            'decoder_attention_mask': target_processed['attention_mask']
        }


class MaskedLanguageModelDataset(Dataset):
    """Dataset for masked language modeling tasks."""
    
    def __init__(self, texts: List[str], tokenizer: BaseTokenizer,
                 max_length: int = 512, mask_prob: float = 0.15,
                 add_special_tokens: bool = True):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.mask_prob = mask_prob
        self.add_special_tokens = add_special_tokens
        self.processor = SequenceProcessor(tokenizer, max_length)
    
    def __len__(self) -> int:
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        text = self.texts[idx]
        
        # Create masked sequence
        masked = self.processor.create_masked_sequences(
            [text], 
            mask_prob=self.mask_prob
        )
        
        return {
            'input_ids': masked['input_ids'].squeeze(0),
            'attention_mask': masked['attention_mask'].squeeze(0),
            'labels': masked['labels'].squeeze(0)
        }


class StreamingTextDataset(IterableDataset):
    """Streaming dataset for large text files."""
    
    def __init__(self, file_path: str, tokenizer: BaseTokenizer,
                 max_length: int = 512, chunk_size: int = 1000,
                 add_special_tokens: bool = True):
        self.file_path = file_path
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.chunk_size = chunk_size
        self.add_special_tokens = add_special_tokens
        self.processor = SequenceProcessor(tokenizer, max_length)
    
    def __iter__(self) -> Iterator[Dict[str, torch.Tensor]]:
        worker_info = torch.utils.data.get_worker_info()
        
        # Determine file range for this worker
        if worker_info is None:
            # Single worker
            start = 0
            end = None
        else:
            # Multiple workers
            file_size = Path(self.file_path).stat().st_size
            per_worker = file_size // worker_info.num_workers
            start = worker_info.id * per_worker
            end = start + per_worker if worker_info.id < worker_info.num_workers - 1 else None
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            if start > 0:
                f.seek(start)
                # Read until next line boundary
                f.readline()
            
            buffer = []
            for line in f:
                if end is not None and f.tell() >= end:
                    break
                
                line = line.strip()
                if line:
                    buffer.append(line)
                
                if len(buffer) >= self.chunk_size:
                    for text in buffer:
                        yield self.processor.process_single_sequence(
                            text, 
                            add_special_tokens=self.add_special_tokens
                        )
                    buffer = []
            
            # Process remaining buffer
            for text in buffer:
                yield self.processor.process_single_sequence(
                    text, 
                    add_special_tokens=self.add_special_tokens
                )


class DataLoaderFactory:
    """Factory class for creating data loaders."""
    
    @staticmethod
    def create_text_loader(texts: List[str], tokenizer: BaseTokenizer,
                          config: DataLoaderConfig, **kwargs) -> DataLoader:
        """Create a data loader for plain text data."""
        dataset = TextDataset(
            texts=texts,
            tokenizer=tokenizer,
            max_length=config.max_length,
            **kwargs
        )
        
        return DataLoader(
            dataset,
            batch_size=config.batch_size,
            shuffle=config.shuffle,
            num_workers=config.num_workers,
            pin_memory=config.pin_memory,
            drop_last=config.drop_last,
            prefetch_factor=config.prefetch_factor,
            persistent_workers=config.persistent_workers
        )
    
    @staticmethod
    def create_classification_loader(texts: List[str], labels: List[int],
                                   tokenizer: BaseTokenizer, config: DataLoaderConfig,
                                   **kwargs) -> DataLoader:
        """Create a data loader for classification tasks."""
        dataset = ClassificationDataset(
            texts=texts,
            labels=labels,
            tokenizer=tokenizer,
            max_length=config.max_length,
            **kwargs
        )
        
        return DataLoader(
            dataset,
            batch_size=config.batch_size,
            shuffle=config.shuffle,
            num_workers=config.num_workers,
            pin_memory=config.pin_memory,
            drop_last=config.drop_last,
            prefetch_factor=config.prefetch_factor,
            persistent_workers=config.persistent_workers
        )
    
    @staticmethod
    def create_seq2seq_loader(source_texts: List[str], target_texts: List[str],
                             tokenizer: BaseTokenizer, config: DataLoaderConfig,
                             **kwargs) -> DataLoader:
        """Create a data loader for sequence-to-sequence tasks."""
        dataset = SequenceToSequenceDataset(
            source_texts=source_texts,
            target_texts=target_texts,
            tokenizer=tokenizer,
            max_length=config.max_length,
            **kwargs
        )
        
        return DataLoader(
            dataset,
            batch_size=config.batch_size,
            shuffle=config.shuffle,
            num_workers=config.num_workers,
            pin_memory=config.pin_memory,
            drop_last=config.drop_last,
            prefetch_factor=config.prefetch_factor,
            persistent_workers=config.persistent_workers
        )
    
    @staticmethod
    def create_mlm_loader(texts: List[str], tokenizer: BaseTokenizer,
                         config: DataLoaderConfig, mask_prob: float = 0.15,
                         **kwargs) -> DataLoader:
        """Create a data loader for masked language modeling."""
        dataset = MaskedLanguageModelDataset(
            texts=texts,
            tokenizer=tokenizer,
            max_length=config.max_length,
            mask_prob=mask_prob,
            **kwargs
        )
        
        return DataLoader(
            dataset,
            batch_size=config.batch_size,
            shuffle=config.shuffle,
            num_workers=config.num_workers,
            pin_memory=config.pin_memory,
            drop_last=config.drop_last,
            prefetch_factor=config.prefetch_factor,
            persistent_workers=config.persistent_workers
        )
    
    @staticmethod
    def create_streaming_loader(file_path: str, tokenizer: BaseTokenizer,
                              config: DataLoaderConfig, chunk_size: int = 1000,
                              **kwargs) -> DataLoader:
        """Create a streaming data loader for large files."""
        dataset = StreamingTextDataset(
            file_path=file_path,
            tokenizer=tokenizer,
            max_length=config.max_length,
            chunk_size=chunk_size,
            **kwargs
        )
        
        return DataLoader(
            dataset,
            batch_size=config.batch_size,
            num_workers=config.num_workers,
            pin_memory=config.pin_memory,
            drop_last=config.drop_last,
            prefetch_factor=config.prefetch_factor,
            persistent_workers=config.persistent_workers
        )


class DataPreprocessor:
    """Handles data preprocessing and augmentation."""
    
    def __init__(self, tokenizer: BaseTokenizer):
        self.tokenizer = tokenizer
    
    def preprocess_texts(self, texts: List[str], 
                        lowercase: bool = True,
                        remove_punctuation: bool = False,
                        remove_numbers: bool = False,
                        remove_stopwords: bool = False) -> List[str]:
        """Preprocess a list of texts."""
        processed_texts = []
        
        for text in texts:
            processed = self.preprocess_single_text(
                text, lowercase, remove_punctuation, remove_numbers, remove_stopwords
            )
            processed_texts.append(processed)
        
        return processed_texts
    
    def preprocess_single_text(self, text: str, 
                              lowercase: bool = True,
                              remove_punctuation: bool = False,
                              remove_numbers: bool = False,
                              remove_stopwords: bool = False) -> str:
        """Preprocess a single text."""
        if lowercase:
            text = text.lower()
        
        if remove_punctuation:
            import string
            text = text.translate(str.maketrans('', '', string.punctuation))
        
        if remove_numbers:
            import re
            text = re.sub(r'\d+', '', text)
        
        if remove_stopwords:
            text = self._remove_stopwords(text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _remove_stopwords(self, text: str) -> str:
        """Remove stopwords from text."""
        # Simple English stopwords list
        stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with'
        }
        
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in stopwords]
        return ' '.join(filtered_words)
    
    def augment_text(self, text: str, 
                    synonym_replacement: bool = False,
                    random_insertion: bool = False,
                    random_deletion: bool = False,
                    random_swap: bool = False) -> str:
        """Apply text augmentation techniques."""
        augmented = text
        
        if synonym_replacement:
            augmented = self._synonym_replacement(augmented)
        
        if random_insertion:
            augmented = self._random_insertion(augmented)
        
        if random_deletion:
            augmented = self._random_deletion(augmented)
        
        if random_swap:
            augmented = self._random_swap(augmented)
        
        return augmented
    
    def _synonym_replacement(self, text: str) -> str:
        """Replace words with synonyms."""
        # Simple synonym dictionary (in practice, use WordNet or similar)
        synonyms = {
            'good': ['great', 'excellent', 'fine'],
            'bad': ['poor', 'terrible', 'awful'],
            'big': ['large', 'huge', 'enormous'],
            'small': ['tiny', 'little', 'miniature']
        }
        
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in synonyms:
                words[i] = random.choice(synonyms[word.lower()])
        
        return ' '.join(words)
    
    def _random_insertion(self, text: str) -> str:
        """Randomly insert words."""
        words = text.split()
        if len(words) < 2:
            return text
        
        # Simple random word insertion
        insert_words = ['very', 'really', 'quite', 'extremely']
        insert_pos = random.randint(0, len(words))
        insert_word = random.choice(insert_words)
        
        words.insert(insert_pos, insert_word)
        return ' '.join(words)
    
    def _random_deletion(self, text: str) -> str:
        """Randomly delete words."""
        words = text.split()
        if len(words) < 3:
            return text
        
        # Randomly delete a word
        delete_pos = random.randint(0, len(words) - 1)
        words.pop(delete_pos)
        
        return ' '.join(words)
    
    def _random_swap(self, text: str) -> str:
        """Randomly swap adjacent words."""
        words = text.split()
        if len(words) < 2:
            return text
        
        # Randomly swap two adjacent words
        swap_pos = random.randint(0, len(words) - 2)
        words[swap_pos], words[swap_pos + 1] = words[swap_pos + 1], words[swap_pos]
        
        return ' '.join(words)


class DataLoaderManager:
    """Manages multiple data loaders and provides utilities."""
    
    def __init__(self, tokenizer: BaseTokenizer, config: DataLoaderConfig):
        self.tokenizer = tokenizer
        self.config = config
        self.preprocessor = DataPreprocessor(tokenizer)
        self.loaders = {}
    
    def create_text_loader(self, texts: List[str], name: str = "default", **kwargs) -> DataLoader:
        """Create and store a text data loader."""
        loader = DataLoaderFactory.create_text_loader(
            texts, self.tokenizer, self.config, **kwargs
        )
        self.loaders[name] = loader
        return loader
    
    def create_classification_loader(self, texts: List[str], labels: List[int],
                                   name: str = "classification", **kwargs) -> DataLoader:
        """Create and store a classification data loader."""
        loader = DataLoaderFactory.create_classification_loader(
            texts, labels, self.tokenizer, self.config, **kwargs
        )
        self.loaders[name] = loader
        return loader
    
    def create_seq2seq_loader(self, source_texts: List[str], target_texts: List[str],
                             name: str = "seq2seq", **kwargs) -> DataLoader:
        """Create and store a sequence-to-sequence data loader."""
        loader = DataLoaderFactory.create_seq2seq_loader(
            source_texts, target_texts, self.tokenizer, self.config, **kwargs
        )
        self.loaders[name] = loader
        return loader
    
    def create_mlm_loader(self, texts: List[str], name: str = "mlm",
                         mask_prob: float = 0.15, **kwargs) -> DataLoader:
        """Create and store a masked language modeling data loader."""
        loader = DataLoaderFactory.create_mlm_loader(
            texts, self.tokenizer, self.config, mask_prob, **kwargs
        )
        self.loaders[name] = loader
        return loader
    
    def get_loader(self, name: str) -> Optional[DataLoader]:
        """Get a stored data loader by name."""
        return self.loaders.get(name)
    
    def list_loaders(self) -> List[str]:
        """List all stored data loader names."""
        return list(self.loaders.keys())
    
    def remove_loader(self, name: str):
        """Remove a stored data loader."""
        if name in self.loaders:
            del self.loaders[name]
    
    def preprocess_and_create_loader(self, texts: List[str], name: str = "preprocessed",
                                   **preprocessing_kwargs) -> DataLoader:
        """Preprocess texts and create a data loader."""
        processed_texts = self.preprocessor.preprocess_texts(texts, **preprocessing_kwargs)
        return self.create_text_loader(processed_texts, name)
    
    def augment_and_create_loader(self, texts: List[str], name: str = "augmented",
                                 augmentation_factor: int = 2, **augmentation_kwargs) -> DataLoader:
        """Augment texts and create a data loader."""
        augmented_texts = []
        for text in texts:
            augmented_texts.append(text)  # Original text
            for _ in range(augmentation_factor - 1):
                augmented = self.preprocessor.augment_text(text, **augmentation_kwargs)
                augmented_texts.append(augmented)
        
        return self.create_text_loader(augmented_texts, name)


# Example usage and testing
if __name__ == "__main__":
    from text_tokenization import TokenizerConfig, WordTokenizer
    
    # Test configuration
    tokenizer_config = TokenizerConfig(vocab_size=1000, max_length=128)
    loader_config = DataLoaderConfig(batch_size=4, max_length=64)
    
    # Create tokenizer
    tokenizer = WordTokenizer(tokenizer_config)
    
    # Test texts
    test_texts = [
        "Hello world! This is a test sentence.",
        "Another example text for tokenization.",
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning is fascinating."
    ]
    
    # Train tokenizer
    tokenizer.train(test_texts)
    
    # Create data loader manager
    manager = DataLoaderManager(tokenizer, loader_config)
    
    # Create different types of loaders
    text_loader = manager.create_text_loader(test_texts, "test")
    
    # Test classification loader
    labels = [0, 1, 0, 1]
    classification_loader = manager.create_classification_loader(
        test_texts, labels, "classification"
    )
    
    # Test sequence-to-sequence loader
    target_texts = [
        "Bonjour le monde! Ceci est une phrase de test.",
        "Un autre exemple de texte pour la tokenisation.",
        "Le renard rapide saute par-dessus le chien paresseux.",
        "L'apprentissage automatique est fascinant."
    ]
    seq2seq_loader = manager.create_seq2seq_loader(
        test_texts, target_texts, "seq2seq"
    )
    
    # Test MLM loader
    mlm_loader = manager.create_mlm_loader(test_texts, "mlm")
    
    # Test data loading
    print("Testing text loader:")
    for batch in text_loader:
        print(f"Batch shape: {batch['input_ids'].shape}")
        break
    
    print("\nTesting classification loader:")
    for batch in classification_loader:
        print(f"Batch shape: {batch['input_ids'].shape}")
        print(f"Labels: {batch['labels']}")
        break
    
    print("\nText data loader module ready!")


