#!/usr/bin/env python3
"""
Tokenization and Sequence Handling System for Diffusion Models

Advanced tokenization and sequence processing system for text data,
including multiple tokenizer types, sequence handling, and integration
with diffusion models and transformers.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import (
    AutoTokenizer, CLIPTokenizer, T5Tokenizer, GPT2Tokenizer, BertTokenizer,
    PreTrainedTokenizer, PreTrainedTokenizerFast, BatchEncoding
)
from transformers.tokenization_utils_base import TruncationStrategy, PaddingStrategy
from diffusers import (
    StableDiffusionPipeline, StableDiffusionXLPipeline,
    CLIPTextModel, T5EncoderModel
)
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json
import time
import hashlib
from functools import lru_cache, wraps
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio
from collections import defaultdict, Counter
import re
import unicodedata
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenizerType(Enum):
    """Supported tokenizer types."""
    CLIP = "clip"
    T5 = "t5"
    GPT2 = "gpt2"
    BERT = "bert"
    AUTO = "auto"

class SequenceStrategy(Enum):
    """Sequence handling strategies."""
    TRUNCATE = "truncate"
    PAD = "pad"
    SLIDE = "slide"
    CHUNK = "chunk"

@dataclass
class TokenizerConfig:
    """Configuration for tokenizers."""
    model_name: str
    tokenizer_type: TokenizerType = TokenizerType.AUTO
    max_length: int = 77
    padding: str = "max_length"
    truncation: str = "longest_first"
    return_tensors: str = "pt"
    return_attention_mask: bool = True
    return_overflowing_tokens: bool = False
    return_special_tokens_mask: bool = False
    return_offsets_mapping: bool = False
    return_length: bool = False
    verbose: bool = True
    clean_up_tokenization_spaces: bool = True
    use_fast: bool = True
    trust_remote_code: bool = False
    cache_dir: Optional[str] = None
    local_files_only: bool = False

@dataclass
class SequenceConfig:
    """Configuration for sequence handling."""
    strategy: SequenceStrategy = SequenceStrategy.TRUNCATE
    max_length: int = 77
    min_length: int = 1
    stride: int = 0
    chunk_size: int = 512
    overlap: int = 50
    padding_side: str = "right"
    truncation_side: str = "right"
    pad_to_multiple_of: Optional[int] = None
    return_overflowing_tokens: bool = False
    return_special_tokens_mask: bool = True
    return_attention_mask: bool = True
    return_tensors: str = "pt"

@dataclass
class TextProcessingConfig:
    """Configuration for text processing."""
    lowercase: bool = False
    remove_punctuation: bool = False
    remove_numbers: bool = False
    remove_extra_whitespace: bool = True
    normalize_unicode: bool = True
    remove_stopwords: bool = False
    lemmatize: bool = False
    custom_filters: List[str] = field(default_factory=list)
    max_words: Optional[int] = None
    min_words: int = 1

class TextPreprocessor:
    """Advanced text preprocessing for diffusion models."""
    
    def __init__(self, config: TextProcessingConfig):
        self.config = config
        self._setup_filters()
    
    def _setup_filters(self):
        """Setup text processing filters."""
        self.filters = []
        
        if self.config.normalize_unicode:
            self.filters.append(self._normalize_unicode)
        
        if self.config.remove_extra_whitespace:
            self.filters.append(self._remove_extra_whitespace)
        
        if self.config.lowercase:
            self.filters.append(self._lowercase)
        
        if self.config.remove_punctuation:
            self.filters.append(self._remove_punctuation)
        
        if self.config.remove_numbers:
            self.filters.append(self._remove_numbers)
        
        # Add custom filters
        for filter_name in self.config.custom_filters:
            if hasattr(self, f"_filter_{filter_name}"):
                self.filters.append(getattr(self, f"_filter_{filter_name}"))
    
    def _normalize_unicode(self, text: str) -> str:
        """Normalize unicode characters."""
        return unicodedata.normalize('NFKC', text)
    
    def _remove_extra_whitespace(self, text: str) -> str:
        """Remove extra whitespace."""
        return ' '.join(text.split())
    
    def _lowercase(self, text: str) -> str:
        """Convert to lowercase."""
        return text.lower()
    
    def _remove_punctuation(self, text: str) -> str:
        """Remove punctuation."""
        return re.sub(r'[^\w\s]', '', text)
    
    def _remove_numbers(self, text: str) -> str:
        """Remove numbers."""
        return re.sub(r'\d+', '', text)
    
    def _filter_artistic_style(self, text: str) -> str:
        """Filter for artistic style prompts."""
        # Remove common unwanted words in artistic prompts
        unwanted_words = ['image', 'picture', 'photo', 'photograph', 'drawing']
        words = text.split()
        filtered_words = [w for w in words if w.lower() not in unwanted_words]
        return ' '.join(filtered_words)
    
    def _filter_diffusion_optimized(self, text: str) -> str:
        """Optimize text for diffusion models."""
        # Enhance common diffusion prompt patterns
        text = re.sub(r'\b(high quality|detailed|sharp focus)\b', 'high quality, detailed, sharp focus', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(blurry|low quality|pixelated)\b', '', text, flags=re.IGNORECASE)
        return text
    
    def process(self, text: str) -> str:
        """Process text through all filters."""
        processed_text = text
        
        for filter_func in self.filters:
            processed_text = filter_func(processed_text)
        
        # Apply word limits
        if self.config.max_words:
            words = processed_text.split()
            if len(words) > self.config.max_words:
                processed_text = ' '.join(words[:self.config.max_words])
        
        if len(processed_text.split()) < self.config.min_words:
            return ""
        
        return processed_text.strip()
    
    def process_batch(self, texts: List[str]) -> List[str]:
        """Process a batch of texts."""
        return [self.process(text) for text in texts]

class AdvancedTokenizer:
    """Advanced tokenizer with caching and optimization."""
    
    def __init__(self, config: TokenizerConfig):
        self.config = config
        self.tokenizer = None
        self._cache = {}
        self._lock = threading.Lock()
        self._setup_tokenizer()
    
    def _setup_tokenizer(self):
        """Setup tokenizer based on configuration."""
        try:
            logger.info(f"Loading tokenizer: {self.config.model_name}")
            
            # Determine tokenizer class based on type
            if self.config.tokenizer_type == TokenizerType.CLIP:
                tokenizer_class = CLIPTokenizer
            elif self.config.tokenizer_type == TokenizerType.T5:
                tokenizer_class = T5Tokenizer
            elif self.config.tokenizer_type == TokenizerType.GPT2:
                tokenizer_class = GPT2Tokenizer
            elif self.config.tokenizer_type == TokenizerType.BERT:
                tokenizer_class = BertTokenizer
            else:
                tokenizer_class = AutoTokenizer
            
            # Load tokenizer
            self.tokenizer = tokenizer_class.from_pretrained(
                self.config.model_name,
                use_fast=self.config.use_fast,
                trust_remote_code=self.config.trust_remote_code,
                cache_dir=self.config.cache_dir,
                local_files_only=self.config.local_files_only
            )
            
            # Set special tokens if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info(f"✅ Tokenizer loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load tokenizer: {e}")
            raise
    
    @lru_cache(maxsize=1000)
    def encode_text(self, text: str, **kwargs) -> List[int]:
        """Encode text with caching."""
        return self.tokenizer.encode(text, **kwargs)
    
    def encode_batch(self, texts: List[str], **kwargs) -> BatchEncoding:
        """Encode batch of texts efficiently."""
        return self.tokenizer(
            texts,
            padding=self.config.padding,
            truncation=self.config.truncation,
            max_length=self.config.max_length,
            return_tensors=self.config.return_tensors,
            return_attention_mask=self.config.return_attention_mask,
            return_overflowing_tokens=self.config.return_overflowing_tokens,
            return_special_tokens_mask=self.config.return_special_tokens_mask,
            return_offsets_mapping=self.config.return_offsets_mapping,
            return_length=self.config.return_length,
            verbose=self.config.verbose,
            clean_up_tokenization_spaces=self.config.clean_up_tokenization_spaces,
            **kwargs
        )
    
    def decode_tokens(self, tokens: Union[List[int], torch.Tensor], **kwargs) -> str:
        """Decode tokens to text."""
        if isinstance(tokens, torch.Tensor):
            tokens = tokens.tolist()
        return self.tokenizer.decode(tokens, **kwargs)
    
    def decode_batch(self, token_batches: Union[List[List[int]], torch.Tensor], **kwargs) -> List[str]:
        """Decode batch of token sequences."""
        if isinstance(token_batches, torch.Tensor):
            token_batches = token_batches.tolist()
        return [self.decode_tokens(tokens, **kwargs) for tokens in token_batches]
    
    def get_vocab_size(self) -> int:
        """Get vocabulary size."""
        return self.tokenizer.vocab_size
    
    def get_special_tokens(self) -> Dict[str, str]:
        """Get special tokens."""
        return {
            "pad_token": self.tokenizer.pad_token,
            "eos_token": self.tokenizer.eos_token,
            "bos_token": self.tokenizer.bos_token,
            "unk_token": self.tokenizer.unk_token,
            "mask_token": self.tokenizer.mask_token,
            "sep_token": getattr(self.tokenizer, 'sep_token', None)
        }
    
    def get_token_ids(self) -> Dict[str, int]:
        """Get special token IDs."""
        return {
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
            "bos_token_id": self.tokenizer.bos_token_id,
            "unk_token_id": self.tokenizer.unk_token_id,
            "mask_token_id": self.tokenizer.mask_token_id,
            "sep_token_id": getattr(self.tokenizer, 'sep_token_id', None)
        }

class SequenceHandler:
    """Advanced sequence handling for diffusion models."""
    
    def __init__(self, config: SequenceConfig):
        self.config = config
    
    def handle_sequence(self, tokens: List[int]) -> List[List[int]]:
        """Handle sequence based on strategy."""
        if self.config.strategy == SequenceStrategy.TRUNCATE:
            return self._truncate_sequence(tokens)
        elif self.config.strategy == SequenceStrategy.PAD:
            return self._pad_sequence(tokens)
        elif self.config.strategy == SequenceStrategy.SLIDE:
            return self._slide_window(tokens)
        elif self.config.strategy == SequenceStrategy.CHUNK:
            return self._chunk_sequence(tokens)
        else:
            raise ValueError(f"Unknown sequence strategy: {self.config.strategy}")
    
    def _truncate_sequence(self, tokens: List[int]) -> List[List[int]]:
        """Truncate sequence to max length."""
        if len(tokens) <= self.config.max_length:
            return [tokens]
        
        if self.config.truncation_side == "right":
            return [tokens[:self.config.max_length]]
        else:
            return [tokens[-self.config.max_length:]]
    
    def _pad_sequence(self, tokens: List[int]) -> List[List[int]]:
        """Pad sequence to max length."""
        if len(tokens) >= self.config.max_length:
            return self._truncate_sequence(tokens)
        
        padded = tokens.copy()
        if self.config.padding_side == "right":
            padded.extend([0] * (self.config.max_length - len(tokens)))
        else:
            padded = [0] * (self.config.max_length - len(tokens)) + padded
        
        return [padded]
    
    def _slide_window(self, tokens: List[int]) -> List[List[int]]:
        """Create sliding windows over sequence."""
        if len(tokens) <= self.config.max_length:
            return [tokens]
        
        windows = []
        for i in range(0, len(tokens) - self.config.max_length + 1, self.config.stride + 1):
            window = tokens[i:i + self.config.max_length]
            windows.append(window)
        
        return windows
    
    def _chunk_sequence(self, tokens: List[int]) -> List[List[int]]:
        """Split sequence into overlapping chunks."""
        if len(tokens) <= self.config.chunk_size:
            return [tokens]
        
        chunks = []
        for i in range(0, len(tokens), self.config.chunk_size - self.config.overlap):
            chunk = tokens[i:i + self.config.chunk_size]
            if len(chunk) >= self.config.min_length:
                chunks.append(chunk)
        
        return chunks
    
    def create_attention_mask(self, sequences: List[List[int]]) -> List[List[int]]:
        """Create attention masks for sequences."""
        masks = []
        for seq in sequences:
            mask = [1] * len(seq)
            if len(seq) < self.config.max_length:
                mask.extend([0] * (self.config.max_length - len(seq)))
            masks.append(mask)
        return masks

class DiffusionTextProcessor:
    """Specialized text processor for diffusion models."""
    
    def __init__(self, 
                 tokenizer_config: TokenizerConfig,
                 sequence_config: SequenceConfig,
                 text_config: TextProcessingConfig):
        self.tokenizer_config = tokenizer_config
        self.sequence_config = sequence_config
        self.text_config = text_config
        
        # Initialize components
        self.text_preprocessor = TextPreprocessor(text_config)
        self.tokenizer = AdvancedTokenizer(tokenizer_config)
        self.sequence_handler = SequenceHandler(sequence_config)
        
        # Text encoder for diffusion models
        self.text_encoder = None
        self._setup_text_encoder()
    
    def _setup_text_encoder(self):
        """Setup text encoder for diffusion models."""
        try:
            if self.tokenizer_config.tokenizer_type == TokenizerType.CLIP:
                self.text_encoder = CLIPTextModel.from_pretrained(
                    self.tokenizer_config.model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
            elif self.tokenizer_config.tokenizer_type == TokenizerType.T5:
                self.text_encoder = T5EncoderModel.from_pretrained(
                    self.tokenizer_config.model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
            
            if self.text_encoder:
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                self.text_encoder = self.text_encoder.to(device)
                self.text_encoder.eval()
                
                logger.info(f"✅ Text encoder loaded on {device}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load text encoder: {e}")
    
    def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """Process a single prompt for diffusion."""
        try:
            # Preprocess text
            processed_text = self.text_preprocessor.process(prompt)
            if not processed_text:
                raise ValueError("Empty text after preprocessing")
            
            # Tokenize
            tokens = self.tokenizer.encode_text(processed_text)
            
            # Handle sequence
            sequences = self.sequence_handler.handle_sequence(tokens)
            
            # Create attention masks
            attention_masks = self.sequence_handler.create_attention_mask(sequences)
            
            # Convert to tensors
            input_ids = torch.tensor(sequences[0])
            attention_mask = torch.tensor(attention_masks[0])
            
            return {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "text": processed_text,
                "original_text": prompt,
                "token_count": len(tokens)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process prompt: {e}")
            raise
    
    def process_prompts_batch(self, prompts: List[str]) -> Dict[str, Any]:
        """Process multiple prompts for diffusion."""
        try:
            # Preprocess texts
            processed_texts = self.text_preprocessor.process_batch(prompts)
            
            # Filter out empty texts
            valid_prompts = []
            valid_processed = []
            for i, (prompt, processed) in enumerate(zip(prompts, processed_texts)):
                if processed:
                    valid_prompts.append(prompt)
                    valid_processed.append(processed)
            
            if not valid_processed:
                raise ValueError("No valid prompts after preprocessing")
            
            # Tokenize batch
            batch_encoding = self.tokenizer.encode_batch(valid_processed)
            
            return {
                "input_ids": batch_encoding["input_ids"],
                "attention_mask": batch_encoding["attention_mask"],
                "texts": valid_processed,
                "original_texts": valid_prompts,
                "token_counts": [len(self.tokenizer.encode_text(text)) for text in valid_processed]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process prompts batch: {e}")
            raise
    
    @torch.no_grad()
    def encode_prompt(self, prompt: str) -> torch.Tensor:
        """Encode prompt to embeddings for diffusion."""
        try:
            if self.text_encoder is None:
                raise ValueError("Text encoder not available")
            
            # Process prompt
            processed = self.process_prompt(prompt)
            
            # Move to device
            device = next(self.text_encoder.parameters()).device
            input_ids = processed["input_ids"].unsqueeze(0).to(device)
            attention_mask = processed["attention_mask"].unsqueeze(0).to(device)
            
            # Encode
            with torch.no_grad():
                text_embeddings = self.text_encoder(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )[0]
            
            return text_embeddings
            
        except Exception as e:
            logger.error(f"❌ Failed to encode prompt: {e}")
            raise
    
    @torch.no_grad()
    def encode_prompts_batch(self, prompts: List[str]) -> torch.Tensor:
        """Encode multiple prompts to embeddings."""
        try:
            if self.text_encoder is None:
                raise ValueError("Text encoder not available")
            
            # Process prompts
            processed = self.process_prompts_batch(prompts)
            
            # Move to device
            device = next(self.text_encoder.parameters()).device
            input_ids = processed["input_ids"].to(device)
            attention_mask = processed["attention_mask"].to(device)
            
            # Encode
            with torch.no_grad():
                text_embeddings = self.text_encoder(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )[0]
            
            return text_embeddings
            
        except Exception as e:
            logger.error(f"❌ Failed to encode prompts batch: {e}")
            raise
    
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt characteristics."""
        try:
            # Process prompt
            processed = self.process_prompt(prompt)
            
            # Token analysis
            tokens = self.tokenizer.encode_text(processed["text"])
            decoded_tokens = [self.tokenizer.decode([t]) for t in tokens]
            
            # Word analysis
            words = processed["text"].split()
            
            analysis = {
                "original_length": len(prompt),
                "processed_length": len(processed["text"]),
                "word_count": len(words),
                "token_count": len(tokens),
                "avg_tokens_per_word": len(tokens) / len(words) if words else 0,
                "unique_words": len(set(words)),
                "unique_tokens": len(set(tokens)),
                "special_tokens": [t for t in tokens if t in self.tokenizer.get_token_ids().values()],
                "token_distribution": Counter(tokens),
                "word_distribution": Counter(words),
                "processed_text": processed["text"],
                "tokens": tokens,
                "decoded_tokens": decoded_tokens
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze prompt: {e}")
            raise

class TokenizationSequenceSystem:
    """Complete system for tokenization and sequence handling."""
    
    def __init__(self):
        self.processors: Dict[str, DiffusionTextProcessor] = {}
        self._lock = threading.Lock()
    
    def add_processor(self, 
                     name: str,
                     tokenizer_config: TokenizerConfig,
                     sequence_config: SequenceConfig,
                     text_config: TextProcessingConfig) -> DiffusionTextProcessor:
        """Add a text processor to the system."""
        try:
            with self._lock:
                if name in self.processors:
                    logger.warning(f"Processor {name} already exists, replacing...")
                
                processor = DiffusionTextProcessor(
                    tokenizer_config, sequence_config, text_config
                )
                self.processors[name] = processor
                
                logger.info(f"✅ Processor {name} added successfully")
                return processor
                
        except Exception as e:
            logger.error(f"❌ Failed to add processor {name}: {e}")
            raise
    
    def get_processor(self, name: str) -> Optional[DiffusionTextProcessor]:
        """Get processor by name."""
        return self.processors.get(name)
    
    def remove_processor(self, name: str):
        """Remove processor from system."""
        with self._lock:
            if name in self.processors:
                del self.processors[name]
                logger.info(f"✅ Processor {name} removed")
    
    def list_processors(self) -> List[str]:
        """List all available processors."""
        return list(self.processors.keys())
    
    def process_with_processor(self, 
                             processor_name: str, 
                             prompts: Union[str, List[str]]) -> Dict[str, Any]:
        """Process prompts with specific processor."""
        processor = self.get_processor(processor_name)
        if not processor:
            raise ValueError(f"Processor {processor_name} not found")
        
        if isinstance(prompts, str):
            return processor.process_prompt(prompts)
        else:
            return processor.process_prompts_batch(prompts)
    
    def encode_with_processor(self, 
                            processor_name: str, 
                            prompts: Union[str, List[str]]) -> torch.Tensor:
        """Encode prompts with specific processor."""
        processor = self.get_processor(processor_name)
        if not processor:
            raise ValueError(f"Processor {processor_name} not found")
        
        if isinstance(prompts, str):
            return processor.encode_prompt(prompts)
        else:
            return processor.encode_prompts_batch(prompts)
    
    def analyze_with_processor(self, 
                             processor_name: str, 
                             prompt: str) -> Dict[str, Any]:
        """Analyze prompt with specific processor."""
        processor = self.get_processor(processor_name)
        if not processor:
            raise ValueError(f"Processor {processor_name} not found")
        
        return processor.analyze_prompt(prompt)

# Production usage example
def main():
    """Production usage example."""
    try:
        # Initialize system
        system = TokenizationSequenceSystem()
        
        # Add CLIP processor for Stable Diffusion
        clip_tokenizer_config = TokenizerConfig(
            model_name="openai/clip-vit-base-patch32",
            tokenizer_type=TokenizerType.CLIP,
            max_length=77
        )
        
        clip_sequence_config = SequenceConfig(
            strategy=SequenceStrategy.TRUNCATE,
            max_length=77
        )
        
        clip_text_config = TextProcessingConfig(
            lowercase=False,
            remove_extra_whitespace=True,
            normalize_unicode=True,
            custom_filters=["artistic_style", "diffusion_optimized"]
        )
        
        clip_processor = system.add_processor(
            "clip", clip_tokenizer_config, clip_sequence_config, clip_text_config
        )
        
        # Add T5 processor for Stable Diffusion XL
        t5_tokenizer_config = TokenizerConfig(
            model_name="t5-base",
            tokenizer_type=TokenizerType.T5,
            max_length=77
        )
        
        t5_sequence_config = SequenceConfig(
            strategy=SequenceStrategy.TRUNCATE,
            max_length=77
        )
        
        t5_text_config = TextProcessingConfig(
            lowercase=False,
            remove_extra_whitespace=True,
            normalize_unicode=True
        )
        
        t5_processor = system.add_processor(
            "t5", t5_tokenizer_config, t5_sequence_config, t5_text_config
        )
        
        # Test processing
        test_prompts = [
            "A beautiful sunset over the mountains, digital art style",
            "A futuristic city with flying cars, sci-fi style",
            "A serene forest with ancient trees, fantasy art style"
        ]
        
        # Process with CLIP
        clip_results = system.process_with_processor("clip", test_prompts)
        print(f"CLIP processing results: {clip_results['input_ids'].shape}")
        
        # Process with T5
        t5_results = system.process_with_processor("t5", test_prompts)
        print(f"T5 processing results: {t5_results['input_ids'].shape}")
        
        # Analyze a prompt
        analysis = system.analyze_with_processor("clip", test_prompts[0])
        print(f"Prompt analysis: {analysis['word_count']} words, {analysis['token_count']} tokens")
        
    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")

if __name__ == "__main__":
    main()
