#!/usr/bin/env python3
"""
Text Tokenization and Sequence Handling Module

This module provides comprehensive text tokenization and sequence handling
capabilities for transformer models, including:
- Multiple tokenization strategies
- Sequence padding and truncation
- Special token handling
- Batch processing
- Vocabulary management
"""

import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional, Union, Any
import re
import json
import logging
from collections import Counter, defaultdict
import numpy as np
from dataclasses import dataclass
import pickle
import os

logger = logging.getLogger(__name__)


@dataclass
class TokenizerConfig:
    """Configuration for tokenizer."""
    vocab_size: int = 50000
    max_length: int = 512
    pad_token: str = "<PAD>"
    unk_token: str = "<UNK>"
    bos_token: str = "<BOS>"
    eos_token: str = "<EOS>"
    mask_token: str = "<MASK>"
    sep_token: str = "<SEP>"
    cls_token: str = "<CLS>"
    do_lower_case: bool = True
    remove_accents: bool = True
    strip_whitespace: bool = True


class BaseTokenizer:
    """Base tokenizer class with common functionality."""
    
    def __init__(self, config: TokenizerConfig):
        self.config = config
        self.vocab = {}
        self.id_to_token = {}
        self.special_tokens = {
            'pad': config.pad_token,
            'unk': config.unk_token,
            'bos': config.bos_token,
            'eos': config.eos_token,
            'mask': config.mask_token,
            'sep': config.sep_token,
            'cls': config.cls_token
        }
        
        # Initialize special tokens
        self._init_special_tokens()
    
    def _init_special_tokens(self):
        """Initialize special tokens in vocabulary."""
        for i, (key, token) in enumerate(self.special_tokens.items()):
            self.vocab[token] = i
            self.id_to_token[i] = token
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text according to configuration."""
        if self.config.do_lower_case:
            text = text.lower()
        
        if self.config.remove_accents:
            text = self._remove_accents(text)
        
        if self.config.strip_whitespace:
            text = ' '.join(text.split())
        
        return text
    
    def _remove_accents(self, text: str) -> str:
        """Remove accents from text."""
        import unicodedata
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if not unicodedata.combining(c)
        )
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into tokens. To be implemented by subclasses."""
        raise NotImplementedError
    
    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """Encode text to token IDs."""
        tokens = self.tokenize(text)
        token_ids = []
        
        if add_special_tokens and self.special_tokens['bos'] in self.vocab:
            token_ids.append(self.vocab[self.special_tokens['bos']])
        
        for token in tokens:
            token_id = self.vocab.get(token, self.vocab[self.special_tokens['unk']])
            token_ids.append(token_id)
        
        if add_special_tokens and self.special_tokens['eos'] in self.vocab:
            token_ids.append(self.vocab[self.special_tokens['eos']])
        
        return token_ids
    
    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs back to text."""
        tokens = []
        for token_id in token_ids:
            if token_id in self.id_to_token:
                token = self.id_to_token[token_id]
                if skip_special_tokens and token in self.special_tokens.values():
                    continue
                tokens.append(token)
        
        return self._detokenize(tokens)
    
    def _detokenize(self, tokens: List[str]) -> str:
        """Convert tokens back to text. To be implemented by subclasses."""
        return ' '.join(tokens)
    
    def pad_sequences(self, sequences: List[List[int]], 
                     max_length: Optional[int] = None,
                     padding: str = 'longest',
                     truncation: str = 'longest_first',
                     return_tensors: str = 'pt') -> Dict[str, torch.Tensor]:
        """Pad or truncate sequences to uniform length."""
        if max_length is None:
            max_length = self.config.max_length
        
        # Determine target length
        if padding == 'longest':
            target_length = min(max(len(seq) for seq in sequences), max_length)
        else:
            target_length = max_length
        
        # Pad and truncate sequences
        padded_sequences = []
        attention_masks = []
        
        for sequence in sequences:
            # Truncate if necessary
            if len(sequence) > target_length:
                if truncation == 'longest_first':
                    sequence = sequence[:target_length]
                elif truncation == 'only_first':
                    sequence = sequence[:target_length]
                elif truncation == 'only_second':
                    sequence = sequence[-target_length:]
            
            # Create attention mask
            attention_mask = [1] * len(sequence)
            
            # Pad if necessary
            if len(sequence) < target_length:
                pad_length = target_length - len(sequence)
                sequence.extend([self.vocab[self.special_tokens['pad']]] * pad_length)
                attention_mask.extend([0] * pad_length)
            
            padded_sequences.append(sequence)
            attention_masks.append(attention_mask)
        
        # Convert to tensors
        if return_tensors == 'pt':
            return {
                'input_ids': torch.tensor(padded_sequences, dtype=torch.long),
                'attention_mask': torch.tensor(attention_masks, dtype=torch.long)
            }
        else:
            return {
                'input_ids': padded_sequences,
                'attention_mask': attention_masks
            }
    
    def save(self, filepath: str):
        """Save tokenizer to file."""
        data = {
            'config': self.config,
            'vocab': self.vocab,
            'id_to_token': self.id_to_token,
            'special_tokens': self.special_tokens
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        logger.info(f"Tokenizer saved to: {filepath}")
    
    def load(self, filepath: str):
        """Load tokenizer from file."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        self.config = data['config']
        self.vocab = data['vocab']
        self.id_to_token = data['id_to_token']
        self.special_tokens = data['special_tokens']
        
        logger.info(f"Tokenizer loaded from: {filepath}")


class WordTokenizer(BaseTokenizer):
    """Word-based tokenizer with vocabulary building."""
    
    def __init__(self, config: TokenizerConfig):
        super().__init__(config)
        self.word_freq = Counter()
    
    def train(self, texts: List[str]):
        """Train tokenizer on a list of texts."""
        # Collect word frequencies
        for text in texts:
            processed_text = self.preprocess_text(text)
            words = processed_text.split()
            self.word_freq.update(words)
        
        # Build vocabulary
        self._build_vocab()
        logger.info(f"Trained tokenizer with vocabulary size: {len(self.vocab)}")
    
    def _build_vocab(self):
        """Build vocabulary from word frequencies."""
        # Start with special tokens
        vocab_size = len(self.special_tokens)
        
        # Add most frequent words
        for word, freq in self.word_freq.most_common(self.config.vocab_size - vocab_size):
            self.vocab[word] = len(self.vocab)
            self.id_to_token[len(self.vocab) - 1] = word
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        processed_text = self.preprocess_text(text)
        return processed_text.split()
    
    def _detokenize(self, tokens: List[str]) -> str:
        """Convert tokens back to text."""
        return ' '.join(tokens)


class SubwordTokenizer(BaseTokenizer):
    """Subword tokenizer using Byte Pair Encoding (BPE)."""
    
    def __init__(self, config: TokenizerConfig):
        super().__init__(config)
        self.merges = {}
        self.word_freq = Counter()
    
    def train(self, texts: List[str]):
        """Train BPE tokenizer on texts."""
        # Preprocess and collect word frequencies
        for text in texts:
            processed_text = self.preprocess_text(text)
            words = processed_text.split()
            self.word_freq.update(words)
        
        # Build BPE merges
        self._build_bpe_merges()
        
        # Build vocabulary
        self._build_vocab()
        logger.info(f"Trained BPE tokenizer with vocabulary size: {len(self.vocab)}")
    
    def _build_bpe_merges(self):
        """Build BPE merges from word frequencies."""
        # Initialize with character-level tokens
        vocab = set()
        for word in self.word_freq.keys():
            for char in word:
                vocab.add(char)
        
        # Add special tokens
        for token in self.special_tokens.values():
            vocab.add(token)
        
        # Perform BPE merges
        num_merges = self.config.vocab_size - len(vocab)
        
        for _ in range(num_merges):
            # Find most frequent pair
            pair_freq = Counter()
            for word, freq in self.word_freq.items():
                word_tokens = list(word)
                for i in range(len(word_tokens) - 1):
                    pair = (word_tokens[i], word_tokens[i + 1])
                    pair_freq[pair] += freq
            
            if not pair_freq:
                break
            
            # Get most frequent pair
            best_pair = pair_freq.most_common(1)[0][0]
            self.merges[best_pair] = len(self.merges)
            
            # Update word frequencies
            new_word_freq = Counter()
            for word, freq in self.word_freq.items():
                new_word = self._apply_merge(word, best_pair)
                new_word_freq[new_word] += freq
            
            self.word_freq = new_word_freq
    
    def _apply_merge(self, word: str, pair: Tuple[str, str]) -> str:
        """Apply a BPE merge to a word."""
        if len(word) < 2:
            return word
        
        result = []
        i = 0
        while i < len(word) - 1:
            if (word[i], word[i + 1]) == pair:
                result.append(word[i] + word[i + 1])
                i += 2
            else:
                result.append(word[i])
                i += 1
        
        if i < len(word):
            result.append(word[i])
        
        return ''.join(result)
    
    def _build_vocab(self):
        """Build vocabulary from BPE merges."""
        # Add special tokens
        vocab_size = len(self.special_tokens)
        
        # Add all unique tokens from merges
        all_tokens = set()
        for pair in self.merges.keys():
            all_tokens.add(pair[0])
            all_tokens.add(pair[1])
            all_tokens.add(pair[0] + pair[1])
        
        # Add tokens to vocabulary
        for token in all_tokens:
            if len(self.vocab) < self.config.vocab_size:
                self.vocab[token] = len(self.vocab)
                self.id_to_token[len(self.vocab) - 1] = token
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using BPE."""
        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        tokens = []
        
        for word in words:
            word_tokens = self._tokenize_word(word)
            tokens.extend(word_tokens)
        
        return tokens
    
    def _tokenize_word(self, word: str) -> List[str]:
        """Tokenize a single word using BPE."""
        if word in self.vocab:
            return [word]
        
        # Apply merges
        current_word = word
        while len(current_word) > 1:
            # Find best merge
            best_merge = None
            for pair in self.merges.keys():
                if pair[0] in current_word and pair[1] in current_word:
                    # Find position of merge
                    pos = current_word.find(pair[0])
                    if pos != -1 and pos + 1 < len(current_word) and current_word[pos + 1] == pair[1]:
                        best_merge = pair
                        break
            
            if best_merge is None:
                break
            
            current_word = self._apply_merge(current_word, best_merge)
        
        # Split into individual characters if not in vocab
        if current_word not in self.vocab:
            return list(current_word)
        else:
            return [current_word]
    
    def _detokenize(self, tokens: List[str]) -> str:
        """Convert tokens back to text."""
        return ''.join(tokens).replace('▁', ' ')


class HuggingFaceTokenizer(BaseTokenizer):
    """Wrapper for Hugging Face tokenizers."""
    
    def __init__(self, config: TokenizerConfig, tokenizer_name: str = "bert-base-uncased"):
        super().__init__(config)
        try:
            from transformers import AutoTokenizer
            self.hf_tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
            
            # Update special tokens
            self.special_tokens = {
                'pad': self.hf_tokenizer.pad_token or config.pad_token,
                'unk': self.hf_tokenizer.unk_token or config.unk_token,
                'bos': self.hf_tokenizer.bos_token or config.bos_token,
                'eos': self.hf_tokenizer.eos_token or config.eos_token,
                'mask': self.hf_tokenizer.mask_token or config.mask_token,
                'sep': self.hf_tokenizer.sep_token or config.sep_token,
                'cls': self.hf_tokenizer.cls_token or config.cls_token
            }
            
            # Update vocabulary
            self.vocab = self.hf_tokenizer.get_vocab()
            self.id_to_token = {v: k for k, v in self.vocab.items()}
            
            logger.info(f"Loaded HuggingFace tokenizer: {tokenizer_name}")
            
        except ImportError:
            logger.error("transformers library not available. Install with: pip install transformers")
            raise
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using HuggingFace tokenizer."""
        return self.hf_tokenizer.tokenize(text)
    
    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """Encode text using HuggingFace tokenizer."""
        return self.hf_tokenizer.encode(text, add_special_tokens=add_special_tokens)
    
    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs using HuggingFace tokenizer."""
        return self.hf_tokenizer.decode(token_ids, skip_special_tokens=skip_special_tokens)
    
    def _detokenize(self, tokens: List[str]) -> str:
        """Convert tokens back to text."""
        return self.hf_tokenizer.convert_tokens_to_string(tokens)


class SequenceProcessor:
    """Handles sequence processing for transformer models."""
    
    def __init__(self, tokenizer: BaseTokenizer, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def process_single_sequence(self, text: str, 
                               add_special_tokens: bool = True,
                               padding: str = 'longest',
                               truncation: str = 'longest_first') -> Dict[str, torch.Tensor]:
        """Process a single text sequence."""
        token_ids = self.tokenizer.encode(text, add_special_tokens=add_special_tokens)
        
        # Truncate if necessary
        if len(token_ids) > self.max_length:
            if truncation == 'longest_first':
                token_ids = token_ids[:self.max_length]
            elif truncation == 'only_first':
                token_ids = token_ids[:self.max_length]
            elif truncation == 'only_second':
                token_ids = token_ids[-self.max_length:]
        
        # Create attention mask
        attention_mask = [1] * len(token_ids)
        
        # Pad if necessary
        if padding == 'longest' and len(token_ids) < self.max_length:
            pad_length = self.max_length - len(token_ids)
            pad_token_id = self.tokenizer.vocab[self.tokenizer.special_tokens['pad']]
            token_ids.extend([pad_token_id] * pad_length)
            attention_mask.extend([0] * pad_length)
        
        return {
            'input_ids': torch.tensor([token_ids], dtype=torch.long),
            'attention_mask': torch.tensor([attention_mask], dtype=torch.long)
        }
    
    def process_batch(self, texts: List[str],
                     add_special_tokens: bool = True,
                     padding: str = 'longest',
                     truncation: str = 'longest_first') -> Dict[str, torch.Tensor]:
        """Process a batch of text sequences."""
        return self.tokenizer.pad_sequences(
            [self.tokenizer.encode(text, add_special_tokens=add_special_tokens) for text in texts],
            max_length=self.max_length,
            padding=padding,
            truncation=truncation,
            return_tensors='pt'
        )
    
    def create_masked_sequences(self, texts: List[str], 
                               mask_prob: float = 0.15,
                               mask_token_id: Optional[int] = None) -> Dict[str, torch.Tensor]:
        """Create masked sequences for MLM training."""
        if mask_token_id is None:
            mask_token_id = self.tokenizer.vocab[self.tokenizer.special_tokens['mask']]
        
        processed = self.process_batch(texts)
        input_ids = processed['input_ids'].clone()
        labels = processed['input_ids'].clone()
        
        # Create mask
        mask = torch.rand(input_ids.shape) < mask_prob
        
        # Don't mask special tokens
        special_token_ids = [
            self.tokenizer.vocab[token] for token in self.tokenizer.special_tokens.values()
        ]
        for token_id in special_token_ids:
            mask = mask & (input_ids != token_id)
        
        # Apply masking
        input_ids[mask] = mask_token_id
        labels[~mask] = -100  # Ignore non-masked tokens in loss
        
        return {
            'input_ids': input_ids,
            'attention_mask': processed['attention_mask'],
            'labels': labels
        }


class VocabularyManager:
    """Manages vocabulary operations and statistics."""
    
    def __init__(self, tokenizer: BaseTokenizer):
        self.tokenizer = tokenizer
        self.token_stats = defaultdict(int)
    
    def update_stats(self, token_ids: List[int]):
        """Update token frequency statistics."""
        for token_id in token_ids:
            self.token_stats[token_id] += 1
    
    def get_vocab_stats(self) -> Dict[str, Any]:
        """Get vocabulary statistics."""
        total_tokens = sum(self.token_stats.values())
        
        stats = {
            'vocab_size': len(self.tokenizer.vocab),
            'total_tokens': total_tokens,
            'unique_tokens': len(self.token_stats),
            'most_common_tokens': [],
            'least_common_tokens': [],
            'special_token_stats': {}
        }
        
        # Most and least common tokens
        sorted_tokens = sorted(self.token_stats.items(), key=lambda x: x[1], reverse=True)
        stats['most_common_tokens'] = [
            (self.tokenizer.id_to_token[token_id], count)
            for token_id, count in sorted_tokens[:10]
        ]
        stats['least_common_tokens'] = [
            (self.tokenizer.id_to_token[token_id], count)
            for token_id, count in sorted_tokens[-10:]
        ]
        
        # Special token statistics
        for token_name, token in self.tokenizer.special_tokens.items():
            token_id = self.tokenizer.vocab.get(token, None)
            if token_id is not None:
                stats['special_token_stats'][token_name] = {
                    'token': token,
                    'count': self.token_stats.get(token_id, 0)
                }
        
        return stats
    
    def get_coverage_stats(self, texts: List[str]) -> Dict[str, float]:
        """Get vocabulary coverage statistics."""
        total_tokens = 0
        covered_tokens = 0
        oov_tokens = 0
        
        for text in texts:
            tokens = self.tokenizer.tokenize(text)
            total_tokens += len(tokens)
            
            for token in tokens:
                if token in self.tokenizer.vocab:
                    covered_tokens += 1
                else:
                    oov_tokens += 1
        
        return {
            'coverage_rate': covered_tokens / total_tokens if total_tokens > 0 else 0.0,
            'oov_rate': oov_tokens / total_tokens if total_tokens > 0 else 0.0,
            'total_tokens': total_tokens,
            'covered_tokens': covered_tokens,
            'oov_tokens': oov_tokens
        }


# Example usage and testing
if __name__ == "__main__":
    # Test configuration
    config = TokenizerConfig(
        vocab_size=1000,
        max_length=128,
        do_lower_case=True
    )
    
    # Test texts
    test_texts = [
        "Hello world! This is a test sentence.",
        "Another example text for tokenization.",
        "The quick brown fox jumps over the lazy dog."
    ]
    
    print("Testing Word Tokenizer:")
    word_tokenizer = WordTokenizer(config)
    word_tokenizer.train(test_texts)
    
    processor = SequenceProcessor(word_tokenizer, max_length=64)
    batch_result = processor.process_batch(test_texts)
    print(f"Batch input shape: {batch_result['input_ids'].shape}")
    
    print("\nTesting Subword Tokenizer:")
    subword_tokenizer = SubwordTokenizer(config)
    subword_tokenizer.train(test_texts)
    
    # Test tokenization
    test_text = "Hello world test"
    tokens = subword_tokenizer.tokenize(test_text)
    token_ids = subword_tokenizer.encode(test_text)
    decoded = subword_tokenizer.decode(token_ids)
    
    print(f"Original: {test_text}")
    print(f"Tokens: {tokens}")
    print(f"Token IDs: {token_ids}")
    print(f"Decoded: {decoded}")
    
    print("\nText tokenization module ready!")


