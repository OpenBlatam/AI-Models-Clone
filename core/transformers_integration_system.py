#!/usr/bin/env python3
"""
Transformers Integration System for Diffusion Models

Advanced integration system for working with pre-trained models and tokenizers
from the Transformers library, including:
- Multi-model support and management
- Advanced tokenization strategies
- Model optimization and caching
- Production-ready inference pipelines
- Comprehensive error handling
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForCausalLM, AutoModelForSeq2SeqLM,
    AutoModelForMaskedLM, AutoModelForTokenClassification, AutoModelForSequenceClassification,
    CLIPTextModel, CLIPTokenizer, T5Tokenizer, T5EncoderModel, T5ForConditionalGeneration,
    GPT2Tokenizer, GPT2LMHeadModel, BERTTokenizer, BertModel,
    pipeline, TextGenerationPipeline, TranslationPipeline, SummarizationPipeline,
    GenerationConfig, StoppingCriteria, StoppingCriteriaList, PreTrainedTokenizer,
    PreTrainedModel, AutoConfig, AutoFeatureExtractor, AutoImageProcessor,
    Trainer, TrainingArguments, DataCollatorWithPadding, DataCollatorForLanguageModeling
)
from diffusers import (
    StableDiffusionPipeline, StableDiffusionXLPipeline,
    DiffusionPipeline, AutoencoderKL, UNet2DConditionModel,
    DDIMScheduler, DDPMScheduler, PNDMScheduler
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
from collections import defaultdict
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for transformer models."""
    model_name: str
    model_type: str = "auto"  # auto, text-generation, text2text, clip, bert, gpt2, t5
    task: str = "text-generation"  # text-generation, translation, summarization, classification
    device: str = "auto"
    torch_dtype: str = "auto"
    low_cpu_mem_usage: bool = True
    use_cache: bool = True
    trust_remote_code: bool = False
    revision: Optional[str] = None
    cache_dir: Optional[str] = None
    local_files_only: bool = False

@dataclass
class TokenizerConfig:
    """Configuration for tokenizers."""
    model_name: str
    use_fast: bool = True
    padding_side: str = "right"
    truncation_side: str = "right"
    model_max_length: Optional[int] = None
    pad_token: Optional[str] = None
    eos_token: Optional[str] = None
    bos_token: Optional[str] = None
    unk_token: Optional[str] = None
    mask_token: Optional[str] = None

@dataclass
class InferenceConfig:
    """Configuration for model inference."""
    max_length: int = 512
    max_new_tokens: int = 100
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    do_sample: bool = True
    num_return_sequences: int = 1
    repetition_penalty: float = 1.1
    length_penalty: float = 1.0
    early_stopping: bool = True
    pad_to_multiple_of: Optional[int] = None
    return_tensors: str = "pt"

class ModelCache:
    """Intelligent model caching system."""
    
    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.access_times: Dict[str, float] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get model from cache."""
        with self._lock:
            if key in self.cache:
                model, _ = self.cache[key]
                self.access_times[key] = time.time()
                return model
            return None
    
    def put(self, key: str, model: Any):
        """Put model in cache with LRU eviction."""
        with self._lock:
            if len(self.cache) >= self.max_size:
                # Remove least recently used
                lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
                del self.cache[lru_key]
                del self.access_times[lru_key]
            
            self.cache[key] = (model, time.time())
            self.access_times[key] = time.time()
    
    def clear(self):
        """Clear cache."""
        with self._lock:
            self.cache.clear()
            self.access_times.clear()

class AdvancedTokenizer:
    """Advanced tokenizer with caching and optimization."""
    
    def __init__(self, config: TokenizerConfig):
        self.config = config
        self.tokenizer = None
        self._cache = {}
        self._lock = threading.Lock()
        
        self._load_tokenizer()
    
    def _load_tokenizer(self):
        """Load tokenizer with configuration."""
        try:
            logger.info(f"Loading tokenizer: {self.config.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_name,
                use_fast=self.config.use_fast,
                padding_side=self.config.padding_side,
                truncation_side=self.config.truncation_side,
                model_max_length=self.config.model_max_length,
                trust_remote_code=self.config.trust_remote_code,
                cache_dir=self.config.cache_dir,
                local_files_only=self.config.local_files_only
            )
            
            # Set special tokens
            if self.config.pad_token and self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.config.pad_token
            if self.config.eos_token and self.tokenizer.eos_token is None:
                self.tokenizer.eos_token = self.config.eos_token
            if self.config.bos_token and self.tokenizer.bos_token is None:
                self.tokenizer.bos_token = self.config.bos_token
            if self.config.unk_token and self.tokenizer.unk_token is None:
                self.tokenizer.unk_token = self.config.unk_token
            if self.config.mask_token and self.tokenizer.mask_token is None:
                self.tokenizer.mask_token = self.config.mask_token
            
            # Set pad token if not present
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
    
    def encode_batch(self, texts: List[str], **kwargs) -> Dict[str, torch.Tensor]:
        """Encode batch of texts efficiently."""
        return self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors=self.config.return_tensors,
            **kwargs
        )
    
    def decode_tokens(self, tokens: Union[List[int], torch.Tensor], **kwargs) -> str:
        """Decode tokens to text."""
        if isinstance(tokens, torch.Tensor):
            tokens = tokens.tolist()
        return self.tokenizer.decode(tokens, **kwargs)
    
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
            "mask_token": self.tokenizer.mask_token
        }

class OptimizedModelLoader:
    """Optimized model loader with caching and memory management."""
    
    def __init__(self, cache_size: int = 5):
        self.model_cache = ModelCache(cache_size)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._lock = threading.Lock()
    
    def _get_model_key(self, config: ModelConfig) -> str:
        """Generate unique key for model configuration."""
        key_data = {
            "model_name": config.model_name,
            "model_type": config.model_type,
            "task": config.task,
            "torch_dtype": config.torch_dtype,
            "revision": config.revision
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    def _get_torch_dtype(self, dtype_str: str) -> torch.dtype:
        """Get torch dtype from string."""
        if dtype_str == "auto":
            return torch.float16 if self.device.type == "cuda" else torch.float32
        elif dtype_str == "float16":
            return torch.float16
        elif dtype_str == "bfloat16":
            return torch.bfloat16
        elif dtype_str == "float32":
            return torch.float32
        else:
            return torch.float32
    
    def load_model(self, config: ModelConfig) -> PreTrainedModel:
        """Load model with caching and optimization."""
        model_key = self._get_model_key(config)
        
        # Check cache first
        cached_model = self.model_cache.get(model_key)
        if cached_model is not None:
            logger.info(f"✅ Model loaded from cache: {config.model_name}")
            return cached_model
        
        try:
            logger.info(f"Loading model: {config.model_name}")
            
            # Determine model class based on type
            if config.model_type == "auto":
                model_class = AutoModel
            elif config.model_type == "text-generation":
                model_class = AutoModelForCausalLM
            elif config.model_type == "text2text":
                model_class = AutoModelForSeq2SeqLM
            elif config.model_type == "masked-lm":
                model_class = AutoModelForMaskedLM
            elif config.model_type == "token-classification":
                model_class = AutoModelForTokenClassification
            elif config.model_type == "sequence-classification":
                model_class = AutoModelForSequenceClassification
            elif config.model_type == "clip":
                model_class = CLIPTextModel
            elif config.model_type == "t5":
                model_class = T5ForConditionalGeneration
            elif config.model_type == "bert":
                model_class = BertModel
            elif config.model_type == "gpt2":
                model_class = GPT2LMHeadModel
            else:
                model_class = AutoModel
            
            # Load model
            model = model_class.from_pretrained(
                config.model_name,
                torch_dtype=self._get_torch_dtype(config.torch_dtype),
                low_cpu_mem_usage=config.low_cpu_mem_usage,
                trust_remote_code=config.trust_remote_code,
                revision=config.revision,
                cache_dir=config.cache_dir,
                local_files_only=config.local_files_only,
                device_map="auto" if self.device.type == "cuda" else None
            )
            
            # Move to device if not using device_map
            if not hasattr(model, 'device_map'):
                model = model.to(self.device)
            
            model.eval()
            
            # Cache model
            self.model_cache.put(model_key, model)
            
            logger.info(f"✅ Model loaded successfully on {self.device}")
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    
    def clear_cache(self):
        """Clear model cache."""
        self.model_cache.clear()
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

class TransformersPipeline:
    """Advanced transformers pipeline with multiple capabilities."""
    
    def __init__(self, model_config: ModelConfig, tokenizer_config: TokenizerConfig):
        self.model_config = model_config
        self.tokenizer_config = tokenizer_config
        self.model_loader = OptimizedModelLoader()
        self.tokenizer = AdvancedTokenizer(tokenizer_config)
        self.model = None
        self.pipeline = None
        
        self._load_pipeline()
    
    def _load_pipeline(self):
        """Load model and create pipeline."""
        try:
            # Load model
            self.model = self.model_loader.load_model(self.model_config)
            
            # Create pipeline based on task
            if self.model_config.task == "text-generation":
                self.pipeline = TextGenerationPipeline(
                    model=self.model,
                    tokenizer=self.tokenizer.tokenizer,
                    device=self.model.device if not hasattr(self.model, 'device_map') else None
                )
            elif self.model_config.task == "translation":
                self.pipeline = TranslationPipeline(
                    model=self.model,
                    tokenizer=self.tokenizer.tokenizer,
                    device=self.model.device if not hasattr(self.model, 'device_map') else None
                )
            elif self.model_config.task == "summarization":
                self.pipeline = SummarizationPipeline(
                    model=self.model,
                    tokenizer=self.tokenizer.tokenizer,
                    device=self.model.device if not hasattr(self.model, 'device_map') else None
                )
            else:
                # Generic pipeline
                self.pipeline = pipeline(
                    task=self.model_config.task,
                    model=self.model,
                    tokenizer=self.tokenizer.tokenizer,
                    device=self.model.device if not hasattr(self.model, 'device_map') else None
                )
            
            logger.info(f"✅ Pipeline created for task: {self.model_config.task}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create pipeline: {e}")
            raise
    
    def generate_text(self, prompt: str, config: Optional[InferenceConfig] = None) -> str:
        """Generate text using the pipeline."""
        try:
            if config is None:
                config = InferenceConfig()
            
            # Setup generation parameters
            generation_kwargs = {
                "max_new_tokens": config.max_new_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "top_k": config.top_k,
                "do_sample": config.do_sample,
                "num_return_sequences": config.num_return_sequences,
                "repetition_penalty": config.repetition_penalty,
                "length_penalty": config.length_penalty,
                "early_stopping": config.early_stopping,
                "pad_token_id": self.tokenizer.tokenizer.pad_token_id,
                "eos_token_id": self.tokenizer.tokenizer.eos_token_id
            }
            
            # Generate
            result = self.pipeline(prompt, **generation_kwargs)
            
            if isinstance(result, list):
                return result[0]["generated_text"]
            else:
                return result["generated_text"]
                
        except Exception as e:
            logger.error(f"❌ Failed to generate text: {e}")
            raise
    
    def batch_generate(self, prompts: List[str], config: Optional[InferenceConfig] = None) -> List[str]:
        """Generate text for multiple prompts."""
        try:
            results = []
            
            for prompt in prompts:
                result = self.generate_text(prompt, config)
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to batch generate: {e}")
            raise
    
    def encode_text(self, text: str) -> torch.Tensor:
        """Encode text to embeddings."""
        try:
            inputs = self.tokenizer.encode_batch([text])
            
            with torch.no_grad():
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

class MultiModelManager:
    """Manager for multiple transformer models."""
    
    def __init__(self):
        self.models: Dict[str, TransformersPipeline] = {}
        self.model_loader = OptimizedModelLoader()
        self._lock = threading.Lock()
    
    def add_model(self, name: str, model_config: ModelConfig, tokenizer_config: TokenizerConfig):
        """Add a model to the manager."""
        try:
            with self._lock:
                if name in self.models:
                    logger.warning(f"Model {name} already exists, replacing...")
                
                pipeline = TransformersPipeline(model_config, tokenizer_config)
                self.models[name] = pipeline
                
                logger.info(f"✅ Model {name} added successfully")
                
        except Exception as e:
            logger.error(f"❌ Failed to add model {name}: {e}")
            raise
    
    def get_model(self, name: str) -> Optional[TransformersPipeline]:
        """Get model by name."""
        return self.models.get(name)
    
    def remove_model(self, name: str):
        """Remove model from manager."""
        with self._lock:
            if name in self.models:
                del self.models[name]
                logger.info(f"✅ Model {name} removed")
    
    def list_models(self) -> List[str]:
        """List all available models."""
        return list(self.models.keys())
    
    def clear_all(self):
        """Clear all models and cache."""
        with self._lock:
            self.models.clear()
            self.model_loader.clear_cache()
            logger.info("✅ All models cleared")

class DiffusionTextProcessor:
    """Specialized text processor for diffusion models."""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.model_name = model_name
        self.tokenizer = None
        self.text_encoder = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self._load_clip_model()
    
    def _load_clip_model(self):
        """Load CLIP model for diffusion text processing."""
        try:
            logger.info(f"Loading CLIP model for diffusion: {self.model_name}")
            
            self.tokenizer = CLIPTokenizer.from_pretrained(self.model_name)
            self.text_encoder = CLIPTextModel.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32
            )
            
            self.text_encoder = self.text_encoder.to(self.device)
            self.text_encoder.eval()
            
            logger.info(f"✅ CLIP model loaded for diffusion on {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load CLIP model: {e}")
            raise
    
    @torch.no_grad()
    def encode_prompt(self, prompt: str, max_length: int = 77) -> torch.Tensor:
        """Encode prompt for diffusion model."""
        try:
            inputs = self.tokenizer(
                prompt,
                padding="max_length",
                max_length=max_length,
                truncation=True,
                return_tensors="pt"
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            text_embeddings = self.text_encoder(**inputs)[0]
            
            return text_embeddings
            
        except Exception as e:
            logger.error(f"❌ Failed to encode prompt: {e}")
            raise
    
    @torch.no_grad()
    def encode_prompts_batch(self, prompts: List[str], max_length: int = 77) -> torch.Tensor:
        """Encode multiple prompts for diffusion."""
        try:
            inputs = self.tokenizer(
                prompts,
                padding="max_length",
                max_length=max_length,
                truncation=True,
                return_tensors="pt"
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            text_embeddings = self.text_encoder(**inputs)[0]
            
            return text_embeddings
            
        except Exception as e:
            logger.error(f"❌ Failed to encode prompts batch: {e}")
            raise

# Production usage example
def main():
    """Production usage example."""
    try:
        # Initialize multi-model manager
        manager = MultiModelManager()
        
        # Add GPT-2 model
        gpt2_model_config = ModelConfig(
            model_name="gpt2",
            model_type="text-generation",
            task="text-generation"
        )
        gpt2_tokenizer_config = TokenizerConfig(model_name="gpt2")
        
        manager.add_model("gpt2", gpt2_model_config, gpt2_tokenizer_config)
        
        # Add BERT model
        bert_model_config = ModelConfig(
            model_name="bert-base-uncased",
            model_type="bert",
            task="text-generation"
        )
        bert_tokenizer_config = TokenizerConfig(model_name="bert-base-uncased")
        
        manager.add_model("bert", bert_model_config, bert_tokenizer_config)
        
        # Use GPT-2 for text generation
        gpt2_pipeline = manager.get_model("gpt2")
        if gpt2_pipeline:
            result = gpt2_pipeline.generate_text("The future of AI is")
            print(f"GPT-2 result: {result}")
        
        # Use BERT for text encoding
        bert_pipeline = manager.get_model("bert")
        if bert_pipeline:
            embeddings = bert_pipeline.encode_text("Hello world")
            print(f"BERT embeddings shape: {embeddings.shape}")
        
        # Initialize diffusion text processor
        diffusion_processor = DiffusionTextProcessor()
        diffusion_embeddings = diffusion_processor.encode_prompt("A beautiful sunset")
        print(f"Diffusion embeddings shape: {diffusion_embeddings.shape}")
        
    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")

if __name__ == "__main__":
    main()
