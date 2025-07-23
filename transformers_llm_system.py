#!/usr/bin/env python3
"""
Transformers and LLM System

Comprehensive implementation using the Transformers library with:
- Pre-trained models and tokenizers
- Attention mechanisms and positional encodings
- Efficient fine-tuning techniques (LoRA, P-tuning)
- Proper tokenization and sequence handling
- Production-ready text processing pipeline
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import (
    AutoModel, AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, DataCollatorWithPadding, DataCollatorForLanguageModeling,
    get_linear_schedule_with_warmup, AdamW
)
from transformers.models.bert.modeling_bert import BertSelfAttention
from peft import LoraConfig, get_peft_model, TaskType, PromptTuningConfig
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import logging
from dataclasses import dataclass
from pathlib import Path
import json
import time
from datasets import Dataset
import evaluate


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check CUDA availability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {DEVICE}")


@dataclass
class TransformerConfig:
    """Configuration for transformer models and training.
    
    Attributes:
        model_name: Pre-trained model name
        max_length: Maximum sequence length
        batch_size: Training batch size
        learning_rate: Learning rate
        num_epochs: Number of training epochs
        use_lora: Whether to use LoRA fine-tuning
        use_prompt_tuning: Whether to use P-tuning
        lora_r: LoRA rank
        lora_alpha: LoRA alpha parameter
        lora_dropout: LoRA dropout rate
        prompt_length: Length of prompt tokens for P-tuning
    """
    
    model_name: str = "bert-base-uncased"
    max_length: int = 512
    batch_size: int = 16
    learning_rate: float = 2e-5
    num_epochs: int = 3
    use_lora: bool = True
    use_prompt_tuning: bool = False
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    prompt_length: int = 20


class CustomAttention(nn.Module):
    """Custom attention mechanism with positional encoding.
    
    This module implements a custom attention mechanism with
    proper positional encoding and gradient flow.
    """
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        """Initialize custom attention.
        
        Args:
            d_model: Model dimension
            num_heads: Number of attention heads
            dropout: Dropout probability
        """
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # Linear projections
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        self.scale = torch.sqrt(torch.FloatTensor([self.d_k]))
    
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass with attention computation.
        
        Args:
            query: Query tensor (batch_size, seq_len, d_model)
            key: Key tensor (batch_size, seq_len, d_model)
            value: Value tensor (batch_size, seq_len, d_model)
            mask: Optional attention mask
            
        Returns:
            Tuple of (output, attention_weights)
        """
        batch_size = query.size(0)
        
        # Linear transformations
        Q = self.w_q(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.w_k(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.w_v(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale.to(query.device)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        context = torch.matmul(attention_weights, V)
        context = context.transpose(1, 2).contiguous().view(
            batch_size, -1, self.d_model
        )
        
        # Output projection
        output = self.w_o(context)
        
        return output, attention_weights


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer models.
    
    This module implements sinusoidal positional encoding
    as described in the "Attention Is All You Need" paper.
    """
    
    def __init__(self, d_model: int, max_length: int = 5000, dropout: float = 0.1):
        """Initialize positional encoding.
        
        Args:
            d_model: Model dimension
            max_length: Maximum sequence length
            dropout: Dropout probability
        """
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        
        # Create positional encoding matrix
        pe = torch.zeros(max_length, d_model)
        position = torch.arange(0, max_length).unsqueeze(1).float()
        
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() *
            -(torch.log(torch.tensor(10000.0)) / d_model)
        )
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        
        # Register as buffer (not parameter)
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to input.
        
        Args:
            x: Input tensor (batch_size, seq_len, d_model)
            
        Returns:
            Tensor with positional encoding added
        """
        x = x + self.pe[:, :x.size(1)]
        return self.dropout(x)


class AdvancedTokenizer:
    """Advanced tokenizer with proper sequence handling.
    
    This class provides comprehensive tokenization capabilities
    with proper handling of special tokens and sequence lengths.
    """
    
    def __init__(self, model_name: str, max_length: int = 512):
        """Initialize tokenizer.
        
        Args:
            model_name: Pre-trained model name
            max_length: Maximum sequence length
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_length = max_length
        
        # Add padding token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        logger.info(f"Tokenizer initialized for {model_name}")
    
    def tokenize_text(
        self,
        texts: Union[str, List[str]],
        padding: bool = True,
        truncation: bool = True,
        return_tensors: str = "pt"
    ) -> Dict[str, torch.Tensor]:
        """Tokenize text with proper handling.
        
        Args:
            texts: Text or list of texts to tokenize
            padding: Whether to pad sequences
            truncation: Whether to truncate sequences
            return_tensors: Type of tensors to return
            
        Returns:
            Dictionary with tokenized inputs
        """
        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]
        
        # Tokenize with proper parameters
        tokenized = self.tokenizer(
            texts,
            padding=padding,
            truncation=truncation,
            max_length=self.max_length,
            return_tensors=return_tensors,
            return_attention_mask=True,
            return_token_type_ids=True
        )
        
        return tokenized
    
    def decode_tokens(
        self,
        token_ids: torch.Tensor,
        skip_special_tokens: bool = True
    ) -> List[str]:
        """Decode token IDs back to text.
        
        Args:
            token_ids: Token IDs to decode
            skip_special_tokens: Whether to skip special tokens
            
        Returns:
            List of decoded texts
        """
        if token_ids.dim() == 1:
            token_ids = token_ids.unsqueeze(0)
        
        decoded = self.tokenizer.batch_decode(
            token_ids,
            skip_special_tokens=skip_special_tokens
        )
        
        return decoded
    
    def get_vocab_size(self) -> int:
        """Get vocabulary size.
        
        Returns:
            Size of vocabulary
        """
        return self.tokenizer.vocab_size
    
    def get_special_tokens(self) -> Dict[str, int]:
        """Get special token mappings.
        
        Returns:
            Dictionary of special token mappings
        """
        return {
            'pad_token': self.tokenizer.pad_token_id,
            'unk_token': self.tokenizer.unk_token_id,
            'cls_token': self.tokenizer.cls_token_id,
            'sep_token': self.tokenizer.sep_token_id,
            'mask_token': self.tokenizer.mask_token_id
        }


class LoRAFineTuner:
    """LoRA (Low-Rank Adaptation) fine-tuning implementation.
    
    This class implements efficient fine-tuning using LoRA
    to reduce computational requirements while maintaining performance.
    """
    
    def __init__(self, model: nn.Module, config: TransformerConfig):
        """Initialize LoRA fine-tuner.
        
        Args:
            model: Pre-trained model
            config: Configuration for LoRA
        """
        self.model = model
        self.config = config
        
        # Configure LoRA
        lora_config = LoraConfig(
            task_type=TaskType.SEQ_CLS,
            r=config.lora_r,
            lora_alpha=config.lora_alpha,
            lora_dropout=config.lora_dropout,
            target_modules=["query", "value"]  # Apply to attention layers
        )
        
        # Apply LoRA to model
        self.model = get_peft_model(model, lora_config)
        
        logger.info("LoRA fine-tuning initialized")
    
    def train(
        self,
        train_dataset: Dataset,
        eval_dataset: Optional[Dataset] = None
    ) -> Dict[str, Any]:
        """Train model with LoRA.
        
        Args:
            train_dataset: Training dataset
            eval_dataset: Optional evaluation dataset
            
        Returns:
            Training results
        """
        # Training arguments
        training_args = TrainingArguments(
            output_dir="./lora_output",
            learning_rate=self.config.learning_rate,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            num_train_epochs=self.config.num_epochs,
            weight_decay=0.01,
            logging_dir="./logs",
            logging_steps=10,
            evaluation_strategy="epoch" if eval_dataset else "no",
            save_strategy="epoch",
            load_best_model_at_end=True if eval_dataset else False,
            push_to_hub=False
        )
        
        # Data collator
        data_collator = DataCollatorWithPadding(
            tokenizer=AutoTokenizer.from_pretrained(self.config.model_name)
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator
        )
        
        # Train
        results = trainer.train()
        
        return results


class PromptTuner:
    """P-tuning implementation for efficient fine-tuning.
    
    This class implements prompt tuning, which adds learnable
    prompt tokens to the input while keeping the model frozen.
    """
    
    def __init__(self, model: nn.Module, config: TransformerConfig):
        """Initialize prompt tuner.
        
        Args:
            model: Pre-trained model
            config: Configuration for prompt tuning
        """
        self.model = model
        self.config = config
        
        # Configure prompt tuning
        prompt_config = PromptTuningConfig(
            task_type=TaskType.SEQ_CLS,
            prompt_length=config.prompt_length,
            prompt_tuning_init=1,  # Random initialization
            token_dim=model.config.hidden_size
        )
        
        # Apply prompt tuning to model
        self.model = get_peft_model(model, prompt_config)
        
        logger.info("Prompt tuning initialized")
    
    def train(
        self,
        train_dataset: Dataset,
        eval_dataset: Optional[Dataset] = None
    ) -> Dict[str, Any]:
        """Train model with prompt tuning.
        
        Args:
            train_dataset: Training dataset
            eval_dataset: Optional evaluation dataset
            
        Returns:
            Training results
        """
        # Training arguments
        training_args = TrainingArguments(
            output_dir="./prompt_output",
            learning_rate=self.config.learning_rate,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            num_train_epochs=self.config.num_epochs,
            weight_decay=0.01,
            logging_dir="./logs",
            logging_steps=10,
            evaluation_strategy="epoch" if eval_dataset else "no",
            save_strategy="epoch",
            load_best_model_at_end=True if eval_dataset else False,
            push_to_hub=False
        )
        
        # Data collator
        data_collator = DataCollatorWithPadding(
            tokenizer=AutoTokenizer.from_pretrained(self.config.model_name)
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator
        )
        
        # Train
        results = trainer.train()
        
        return results


class TextProcessor:
    """Comprehensive text processing pipeline.
    
    This class provides end-to-end text processing capabilities
    including tokenization, sequence handling, and model inference.
    """
    
    def __init__(self, config: TransformerConfig):
        """Initialize text processor.
        
        Args:
            config: Configuration for text processing
        """
        self.config = config
        self.tokenizer = AdvancedTokenizer(config.model_name, config.max_length)
        
        # Load pre-trained model
        if "gpt" in config.model_name.lower():
            self.model = AutoModelForCausalLM.from_pretrained(config.model_name)
        else:
            self.model = AutoModelForSequenceClassification.from_pretrained(
                config.model_name,
                num_labels=2  # Binary classification
            )
        
        self.model.to(DEVICE)
        self.model.eval()
        
        logger.info(f"Text processor initialized with {config.model_name}")
    
    def preprocess_text(
        self,
        texts: Union[str, List[str]],
        labels: Optional[List[int]] = None
    ) -> Dataset:
        """Preprocess text for training.
        
        Args:
            texts: Text or list of texts
            labels: Optional labels for classification
            
        Returns:
            HuggingFace Dataset
        """
        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]
        
        # Tokenize texts
        tokenized = self.tokenizer.tokenize_text(texts)
        
        # Create dataset
        dataset_dict = {
            'input_ids': tokenized['input_ids'].tolist(),
            'attention_mask': tokenized['attention_mask'].tolist()
        }
        
        if 'token_type_ids' in tokenized:
            dataset_dict['token_type_ids'] = tokenized['token_type_ids'].tolist()
        
        if labels is not None:
            dataset_dict['labels'] = labels
        
        return Dataset.from_dict(dataset_dict)
    
    def generate_text(
        self,
        prompt: str,
        max_length: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """Generate text using the model.
        
        Args:
            prompt: Input prompt
            max_length: Maximum generation length
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            
        Returns:
            Generated text
        """
        # Tokenize prompt
        inputs = self.tokenizer.tokenize_text(prompt)
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.tokenizer.eos_token_id
            )
        
        # Decode
        generated_text = self.tokenizer.decode_tokens(outputs[0])
        return generated_text[0]
    
    def classify_text(self, texts: Union[str, List[str]]) -> List[Dict[str, Any]]:
        """Classify text using the model.
        
        Args:
            texts: Text or list of texts to classify
            
        Returns:
            List of classification results
        """
        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]
        
        # Tokenize
        inputs = self.tokenizer.tokenize_text(texts)
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = F.softmax(outputs.logits, dim=-1)
            predictions = torch.argmax(outputs.logits, dim=-1)
        
        # Format results
        results = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            results.append({
                'text': texts[i],
                'prediction': pred.item(),
                'confidence': prob[pred].item(),
                'probabilities': prob.tolist()
            })
        
        return results


def create_sample_dataset() -> Tuple[Dataset, Dataset]:
    """Create sample dataset for demonstration.
    
    Returns:
        Tuple of (train_dataset, eval_dataset)
    """
    # Sample texts and labels
    texts = [
        "This is a positive example.",
        "This is a negative example.",
        "I love this product!",
        "I hate this product.",
        "Great experience overall.",
        "Terrible experience overall.",
        "Highly recommended!",
        "Not recommended at all.",
        "Excellent service.",
        "Poor service."
    ]
    
    labels = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    
    # Create processor
    config = TransformerConfig()
    processor = TextProcessor(config)
    
    # Preprocess
    train_dataset = processor.preprocess_text(texts[:8], labels[:8])
    eval_dataset = processor.preprocess_text(texts[8:], labels[8:])
    
    return train_dataset, eval_dataset


def demonstrate_transformers_system():
    """Demonstrate the complete transformers and LLM system."""
    logger.info("Demonstrating Transformers and LLM System...")
    
    # Create configuration
    config = TransformerConfig(
        model_name="bert-base-uncased",
        use_lora=True,
        use_prompt_tuning=False
    )
    
    # Create text processor
    processor = TextProcessor(config)
    
    # Sample texts for classification
    sample_texts = [
        "I love this movie!",
        "This movie is terrible.",
        "Great performance by the actors.",
        "Boring and predictable plot."
    ]
    
    # Classify texts
    results = processor.classify_text(sample_texts)
    
    for result in results:
        logger.info(
            f"Text: {result['text']}\n"
            f"Prediction: {result['prediction']}\n"
            f"Confidence: {result['confidence']:.3f}\n"
        )
    
    # Generate text (if using a generative model)
    if "gpt" in config.model_name.lower():
        prompt = "The future of artificial intelligence is"
        generated = processor.generate_text(prompt, max_length=50)
        logger.info(f"Generated text: {generated}")
    
    # Demonstrate fine-tuning
    if config.use_lora:
        logger.info("Demonstrating LoRA fine-tuning...")
        
        # Create sample datasets
        train_dataset, eval_dataset = create_sample_dataset()
        
        # Initialize LoRA fine-tuner
        lora_tuner = LoRAFineTuner(processor.model, config)
        
        # Train (commented out for demonstration)
        # results = lora_tuner.train(train_dataset, eval_dataset)
        # logger.info(f"LoRA training results: {results}")
    
    logger.info("Transformers and LLM system demonstration completed!")


if __name__ == "__main__":
    demonstrate_transformers_system() 