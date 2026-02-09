#!/usr/bin/env python3
"""
Transformers and LLM System for Diffusion Models

Comprehensive system for integrating transformers and large language models
with diffusion models, including:
- Advanced text encoding and processing
- Multi-modal transformers integration
- Optimized inference pipelines
- Production-ready error handling
- Memory-efficient operations
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForCausalLM, AutoModelForSeq2SeqLM,
    CLIPTextModel, CLIPTokenizer, T5Tokenizer, T5EncoderModel,
    pipeline, TextGenerationPipeline, TranslationPipeline,
    GenerationConfig, StoppingCriteria, StoppingCriteriaList
)
from diffusers import (
    StableDiffusionPipeline, StableDiffusionXLPipeline,
    DiffusionPipeline, AutoencoderKL, UNet2DConditionModel
)
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
import time
from functools import lru_cache, wraps
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TransformerConfig:
    """Configuration for transformer models."""
    model_name: str
    model_type: str = "text-generation"  # text-generation, text2text, clip, custom
    device: str = "auto"
    max_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    do_sample: bool = True
    num_return_sequences: int = 1
    use_cache: bool = True
    torch_dtype: str = "auto"
    low_cpu_mem_usage: bool = True

@dataclass
class LLMConfig:
    """Configuration for LLM operations."""
    model_name: str
    task: str = "text-generation"
    max_new_tokens: int = 100
    temperature: float = 0.7
    repetition_penalty: float = 1.1
    length_penalty: float = 1.0
    early_stopping: bool = True
    pad_token_id: Optional[int] = None
    eos_token_id: Optional[int] = None
    use_fast_tokenizer: bool = True

class CustomStoppingCriteria(StoppingCriteria):
    """Custom stopping criteria for text generation."""
    
    def __init__(self, stop_sequences: List[str], tokenizer):
        self.stop_sequences = stop_sequences
        self.tokenizer = tokenizer
        self.stop_ids = []
        
        for seq in stop_sequences:
            tokens = tokenizer.encode(seq, add_special_tokens=False)
            self.stop_ids.append(tokens)
    
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        for stop_id_sequence in self.stop_ids:
            if input_ids.shape[-1] >= len(stop_id_sequence):
                if torch.all(input_ids[0, -len(stop_id_sequence):] == torch.tensor(stop_id_sequence)):
                    return True
        return False

class OptimizedTextProcessor:
    """Optimized text processing for transformers."""
    
    def __init__(self, config: TransformerConfig):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.device = self._get_device()
        self._lock = threading.Lock()
        
        # Initialize model and tokenizer
        self._load_model()
    
    def _get_device(self) -> torch.device:
        """Get optimal device for model."""
        if self.config.device == "auto":
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return torch.device(self.config.device)
    
    def _load_model(self):
        """Load transformer model and tokenizer."""
        try:
            logger.info(f"Loading model: {self.config.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_name,
                use_fast=self.config.use_fast_tokenizer if hasattr(self.config, 'use_fast_tokenizer') else True
            )
            
            # Set pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model based on type
            if self.config.model_type == "text-generation":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model_name,
                    torch_dtype=self._get_torch_dtype(),
                    low_cpu_mem_usage=self.config.low_cpu_mem_usage,
                    device_map="auto" if self.device.type == "cuda" else None
                )
            elif self.config.model_type == "text2text":
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.config.model_name,
                    torch_dtype=self._get_torch_dtype(),
                    low_cpu_mem_usage=self.config.low_cpu_mem_usage,
                    device_map="auto" if self.device.type == "cuda" else None
                )
            elif self.config.model_type == "clip":
                self.model = CLIPTextModel.from_pretrained(
                    self.config.model_name,
                    torch_dtype=self._get_torch_dtype(),
                    low_cpu_mem_usage=self.config.low_cpu_mem_usage
                )
            else:
                self.model = AutoModel.from_pretrained(
                    self.config.model_name,
                    torch_dtype=self._get_torch_dtype(),
                    low_cpu_mem_usage=self.config.low_cpu_mem_usage
                )
            
            # Move to device if not using device_map
            if not hasattr(self.model, 'device_map'):
                self.model = self.model.to(self.device)
            
            self.model.eval()
            logger.info(f"✅ Model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    
    def _get_torch_dtype(self) -> torch.dtype:
        """Get optimal torch dtype."""
        if self.config.torch_dtype == "auto":
            return torch.float16 if self.device.type == "cuda" else torch.float32
        elif self.config.torch_dtype == "float16":
            return torch.float16
        elif self.config.torch_dtype == "bfloat16":
            return torch.bfloat16
        else:
            return torch.float32
    
    @torch.no_grad()
    def encode_text(self, text: str, max_length: Optional[int] = None) -> torch.Tensor:
        """Encode text to embeddings."""
        try:
            max_length = max_length or self.config.max_length
            
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=max_length,
                truncation=True,
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get embeddings
            with torch.cuda.amp.autocast() if self.device.type == "cuda" else torch.no_grad():
                outputs = self.model(**inputs)
                
                if hasattr(outputs, 'last_hidden_state'):
                    embeddings = outputs.last_hidden_state
                elif hasattr(outputs, 'hidden_states'):
                    embeddings = outputs.hidden_states[-1]
                else:
                    embeddings = outputs.logits
                
                return embeddings.mean(dim=1)  # Pool to sentence embedding
                
        except Exception as e:
            logger.error(f"❌ Failed to encode text: {e}")
            raise
    
    @torch.no_grad()
    def generate_text(self, prompt: str, config: Optional[LLMConfig] = None) -> str:
        """Generate text using the model."""
        try:
            if config is None:
                config = LLMConfig(
                    model_name=self.config.model_name,
                    max_new_tokens=100,
                    temperature=self.config.temperature
                )
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=self.config.max_length,
                truncation=True,
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Setup generation config
            generation_config = GenerationConfig(
                max_new_tokens=config.max_new_tokens,
                temperature=config.temperature,
                top_p=config.repetition_penalty,
                repetition_penalty=config.repetition_penalty,
                length_penalty=config.length_penalty,
                early_stopping=config.early_stopping,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                do_sample=self.config.do_sample,
                num_return_sequences=self.config.num_return_sequences
            )
            
            # Generate
            with torch.cuda.amp.autocast() if self.device.type == "cuda" else torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    generation_config=generation_config,
                    use_cache=self.config.use_cache
                )
            
            # Decode
            generated_text = self.tokenizer.decode(
                outputs[0], 
                skip_special_tokens=True
            )
            
            return generated_text
            
        except Exception as e:
            logger.error(f"❌ Failed to generate text: {e}")
            raise
    
    @torch.no_grad()
    def batch_encode_texts(self, texts: List[str], max_length: Optional[int] = None) -> torch.Tensor:
        """Encode multiple texts efficiently."""
        try:
            max_length = max_length or self.config.max_length
            
            # Tokenize batch
            inputs = self.tokenizer(
                texts,
                return_tensors="pt",
                max_length=max_length,
                truncation=True,
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get embeddings
            with torch.cuda.amp.autocast() if self.device.type == "cuda" else torch.no_grad():
                outputs = self.model(**inputs)
                
                if hasattr(outputs, 'last_hidden_state'):
                    embeddings = outputs.last_hidden_state
                elif hasattr(outputs, 'hidden_states'):
                    embeddings = outputs.hidden_states[-1]
                else:
                    embeddings = outputs.logits
                
                return embeddings.mean(dim=1)  # Pool to sentence embeddings
                
        except Exception as e:
            logger.error(f"❌ Failed to batch encode texts: {e}")
            raise

class MultiModalTransformer:
    """Multi-modal transformer for text and image processing."""
    
    def __init__(self, text_config: TransformerConfig, image_config: Optional[TransformerConfig] = None):
        self.text_config = text_config
        self.image_config = image_config
        self.text_processor = OptimizedTextProcessor(text_config)
        self.image_processor = None
        
        if image_config:
            self.image_processor = OptimizedTextProcessor(image_config)
    
    def encode_text_and_image(self, text: str, image: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        """Encode both text and image."""
        try:
            result = {
                "text_embeddings": self.text_processor.encode_text(text)
            }
            
            if image is not None and self.image_processor:
                # Process image (assuming image is already preprocessed)
                result["image_embeddings"] = self.image_processor.encode_text(text)  # Placeholder
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to encode text and image: {e}")
            raise
    
    def generate_with_image_context(self, text: str, image: Optional[torch.Tensor] = None) -> str:
        """Generate text with image context."""
        try:
            # For now, just use text generation
            # In a full implementation, you would combine text and image features
            return self.text_processor.generate_text(text)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate with image context: {e}")
            raise

class DiffusionTextEncoder:
    """Specialized text encoder for diffusion models."""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.model_name = model_name
        self.tokenizer = None
        self.text_encoder = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self._load_clip_model()
    
    def _load_clip_model(self):
        """Load CLIP model for text encoding."""
        try:
            logger.info(f"Loading CLIP model: {self.model_name}")
            
            self.tokenizer = CLIPTokenizer.from_pretrained(self.model_name)
            self.text_encoder = CLIPTextModel.from_pretrained(self.model_name)
            
            self.text_encoder = self.text_encoder.to(self.device)
            self.text_encoder.eval()
            
            logger.info(f"✅ CLIP model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load CLIP model: {e}")
            raise
    
    @torch.no_grad()
    def encode_prompt(self, prompt: str, max_length: int = 77) -> torch.Tensor:
        """Encode prompt for diffusion model."""
        try:
            # Tokenize
            inputs = self.tokenizer(
                prompt,
                padding="max_length",
                max_length=max_length,
                truncation=True,
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Encode
            text_embeddings = self.text_encoder(**inputs)[0]
            
            return text_embeddings
            
        except Exception as e:
            logger.error(f"❌ Failed to encode prompt: {e}")
            raise
    
    @torch.no_grad()
    def encode_prompts_batch(self, prompts: List[str], max_length: int = 77) -> torch.Tensor:
        """Encode multiple prompts efficiently."""
        try:
            # Tokenize batch
            inputs = self.tokenizer(
                prompts,
                padding="max_length",
                max_length=max_length,
                truncation=True,
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Encode
            text_embeddings = self.text_encoder(**inputs)[0]
            
            return text_embeddings
            
        except Exception as e:
            logger.error(f"❌ Failed to encode prompts batch: {e}")
            raise

class AdvancedLLMPipeline:
    """Advanced LLM pipeline with multiple capabilities."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.pipeline = None
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self._load_pipeline()
    
    def _load_pipeline(self):
        """Load LLM pipeline."""
        try:
            logger.info(f"Loading LLM pipeline: {self.config.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_name,
                use_fast=self.config.use_fast_tokenizer
            )
            
            # Set pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_name,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                low_cpu_mem_usage=True,
                device_map="auto" if self.device.type == "cuda" else None
            )
            
            # Create pipeline
            self.pipeline = TextGenerationPipeline(
                model=self.model,
                tokenizer=self.tokenizer,
                device=self.device if not hasattr(self.model, 'device_map') else None
            )
            
            logger.info(f"✅ LLM pipeline loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load LLM pipeline: {e}")
            raise
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text with advanced options."""
        try:
            # Merge config with kwargs
            generation_kwargs = {
                "max_new_tokens": self.config.max_new_tokens,
                "temperature": self.config.temperature,
                "repetition_penalty": self.config.repetition_penalty,
                "length_penalty": self.config.length_penalty,
                "early_stopping": self.config.early_stopping,
                "pad_token_id": self.tokenizer.pad_token_id,
                "eos_token_id": self.tokenizer.eos_token_id,
                **kwargs
            }
            
            # Generate
            result = self.pipeline(prompt, **generation_kwargs)
            
            return result[0]["generated_text"]
            
        except Exception as e:
            logger.error(f"❌ Failed to generate text: {e}")
            raise
    
    def generate_with_stopping(self, prompt: str, stop_sequences: List[str], **kwargs) -> str:
        """Generate text with custom stopping criteria."""
        try:
            # Create stopping criteria
            stopping_criteria = CustomStoppingCriteria(stop_sequences, self.tokenizer)
            
            # Generate with stopping criteria
            generation_kwargs = {
                "max_new_tokens": self.config.max_new_tokens,
                "temperature": self.config.temperature,
                "stopping_criteria": StoppingCriteriaList([stopping_criteria]),
                **kwargs
            }
            
            result = self.pipeline(prompt, **generation_kwargs)
            
            return result[0]["generated_text"]
            
        except Exception as e:
            logger.error(f"❌ Failed to generate with stopping: {e}")
            raise
    
    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """Generate text for multiple prompts."""
        try:
            results = []
            
            for prompt in prompts:
                result = self.generate_text(prompt, **kwargs)
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to batch generate: {e}")
            raise

# Production usage example
def main():
    """Production usage example."""
    try:
        # Initialize text processor
        text_config = TransformerConfig(
            model_name="gpt2",
            model_type="text-generation",
            max_length=512,
            temperature=0.7
        )
        
        text_processor = OptimizedTextProcessor(text_config)
        
        # Generate text
        prompt = "The future of artificial intelligence is"
        generated_text = text_processor.generate_text(prompt)
        print(f"Generated text: {generated_text}")
        
        # Initialize diffusion text encoder
        diffusion_encoder = DiffusionTextEncoder()
        
        # Encode prompt for diffusion
        diffusion_prompt = "A beautiful sunset over the mountains"
        embeddings = diffusion_encoder.encode_prompt(diffusion_prompt)
        print(f"Diffusion embeddings shape: {embeddings.shape}")
        
        # Initialize advanced LLM pipeline
        llm_config = LLMConfig(
            model_name="gpt2",
            max_new_tokens=50,
            temperature=0.8
        )
        
        llm_pipeline = AdvancedLLMPipeline(llm_config)
        
        # Generate with stopping criteria
        stop_sequences = ["END", "STOP"]
        result = llm_pipeline.generate_with_stopping(
            "Write a short story about a robot:",
            stop_sequences
        )
        print(f"LLM result: {result}")
        
    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")

if __name__ == "__main__":
    main()
