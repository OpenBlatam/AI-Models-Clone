"""
LLM Engine following Transformers library best practices.
Using official documentation recommendations for model loading and training.
"""

import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DataParallel, DistributedDataParallel
from torch.cuda.amp import GradScaler, autocast
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    Trainer, 
    TrainingArguments,
    BitsAndBytesConfig
)
from typing import Dict, Any, List, Optional, Union
import os
import time
from datetime import datetime
from dataclasses import dataclass, field
from datasets import Dataset
import json

from ..core.interfaces import CoreConfig
from ..utils.logging import get_logger
from ..utils.performance_optimization import create_performance_optimizer
from ..utils.advanced_training import create_trainer, TrainingConfig, TrainingMode

@dataclass
class MultiGPUTrainingConfig:
    """Configuration for multi-GPU training following best practices."""
    enable_multi_gpu: bool = True
    gpu_ids: List[int] = field(default_factory=lambda: [0])
    distributed_training: bool = False
    backend: str = "nccl"
    find_unused_parameters: bool = False
    gradient_as_bucket_view: bool = True
    static_graph: bool = True
    broadcast_buffers: bool = True
    gradient_accumulation_steps: int = 1

class GradientAccumulator:
    """Accumulate gradients over multiple steps for large effective batch sizes."""
    
    def __init__(self, accumulation_steps: int = 1):
        self.accumulation_steps = accumulation_steps
        self.current_step = 0
        self.logger = get_logger(__name__)
        
        if accumulation_steps > 1:
            self.logger.info(f"Gradient accumulation enabled with {accumulation_steps} steps")
    
    def backward_step(self, loss: torch.Tensor, scaler: Optional[GradScaler] = None):
        """Perform backward step with optional gradient scaling."""
        if scaler:
            scaler.scale(loss / self.accumulation_steps).backward()
        else:
            (loss / self.accumulation_steps).backward()
        
        self.current_step += 1
        
        if self.current_step % self.accumulation_steps == 0:
            if scaler:
                scaler.step(self.optimizer)
                scaler.update()
            else:
                self.optimizer.step()
            
            self.optimizer.zero_grad()
            self.current_step = 0

class LLMEngine(Engine):
    """LLM Engine following Transformers best practices."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # Initialize performance optimizer
        self.performance_optimizer = create_performance_optimizer(config)
        
        # Model and tokenizer
        self.model = None
        self.tokenizer = None
        
        # Multi-GPU configuration
        self.multi_gpu_config = MultiGPUTrainingConfig(**config.get('multi_gpu', {}))
        
        # Mixed precision configuration
        self.mixed_precision = config.get('mixed_precision', True)
        self.scaler = None
        
        # GPU and memory management
        self.gpu_manager = None
        self.memory_manager = None
        
        # Initialize components
        self._initialize_model()
        self._setup_multi_gpu()
    
    def _get_device(self) -> torch.device:
        """Get the appropriate device for the model."""
        if torch.cuda.is_available():
            return torch.device(f"cuda:{self.multi_gpu_config.gpu_ids[0]}")
        else:
            return torch.device("cpu")
    
    def _initialize_model(self):
        """Initialize the transformer model following Transformers best practices."""
        try:
            # Load tokenizer with recommended settings
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.get('model_name', 'gpt2'),
                trust_remote_code=True,  # For custom models
                use_fast=True  # Use fast tokenizer when available
            )
            
            # Set padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with quantization support following best practices
            if self.config.get('quantization', False):
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",  # Recommended quantization type
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True  # Memory optimization
                )
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.get('model_name', 'gpt2'),
                    quantization_config=bnb_config,
                    device_map="auto",  # Automatic device mapping
                    trust_remote_code=True,
                    torch_dtype=torch.float16  # Memory optimization
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.get('model_name', 'gpt2'),
                    trust_remote_code=True,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
            
            # Apply performance optimizations
            self.model = self.performance_optimizer.optimize_model(self.model)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize model: {e}")
            raise
    
    def _setup_multi_gpu(self):
        """Setup multi-GPU training following best practices."""
        if not torch.cuda.is_available():
            return
        
        if len(self.multi_gpu_config.gpu_ids) > 1:
            if self.multi_gpu_config.distributed_training:
                # Distributed training setup
                if not dist.is_initialized():
                    dist.init_process_group(
                        backend=self.multi_gpu_config.backend,
                        init_method='env://'
                    )
                
                self.model = DistributedDataParallel(
                    self.model,
                    device_ids=[self.device],
                    find_unused_parameters=self.multi_gpu_config.find_unused_parameters,
                    gradient_as_bucket_view=self.multi_gpu_config.gradient_as_bucket_view,
                    static_graph=self.multi_gpu_config.static_graph,
                    broadcast_buffers=self.multi_gpu_config.broadcast_buffers
                )
            else:
                # DataParallel setup
                self.model = DataParallel(
                    self.model, 
                    device_ids=self.multi_gpu_config.gpu_ids
                )
            
            # Initialize gradient accumulator
            self.gradient_accumulator = GradientAccumulator(
                self.multi_gpu_config.gradient_accumulation_steps
            )
    
    def _execute_operation(self, operation: str, **kwargs) -> Any:
        """Execute LLM operations following best practices."""
        try:
            if operation == "generate_text":
                return self.generate_text(**kwargs)
            elif operation == "fine_tune":
                return self.fine_tune_model(**kwargs)
            elif operation == "evaluate":
                return self.evaluate_model(**kwargs)
            elif operation == "save_model":
                return self.save_model(**kwargs)
            elif operation == "load_model":
                return self.load_model(**kwargs)
            else:
                raise ValueError(f"Unknown operation: {operation}")
        except Exception as e:
            self.logger.error(f"Operation {operation} failed: {e}")
            raise
    
    def generate_text(self, prompt: str, max_length: int = 100, temperature: float = 0.7, 
                     top_p: float = 0.9, do_sample: bool = True) -> str:
        """Generate text using the transformer model following best practices."""
        try:
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            # Generate text with optimized inference
            with torch.no_grad():
                outputs = self.performance_optimizer.optimize_inference(
                    self.model, inputs
                )
                
                # Apply generation parameters
                generated_ids = self.model.generate(
                    inputs,
                    max_length=max_length,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=do_sample,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    use_cache=True  # Enable KV cache for efficiency
                )
            
            # Decode output
            generated_text = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
            return generated_text
            
        except Exception as e:
            self.logger.error(f"Text generation failed: {e}")
            raise
    
    def fine_tune_model(self, training_data: List[Dict[str, str]], 
                       epochs: int = 3, batch_size: int = 4, 
                       learning_rate: float = 5e-5) -> Dict[str, Any]:
        """Fine-tune the transformer model using advanced training system."""
        try:
            # Create training configuration
            training_config = TrainingConfig(
                epochs=epochs,
                batch_size=batch_size,
                learning_rate=learning_rate,
                mixed_precision=self.mixed_precision,
                gradient_accumulation_steps=self.multi_gpu_config.gradient_accumulation_steps,
                training_mode=TrainingMode.DATA_PARALLEL if len(self.multi_gpu_config.gpu_ids) > 1 else TrainingMode.SINGLE_GPU,
                gpu_ids=self.multi_gpu_config.gpu_ids
            )
            
            # Create trainer
            trainer = create_trainer(self.model, training_config, "transformers")
            
            # Prepare dataset
            dataset = self._prepare_training_data(training_data)
            
            # Create dataloader with optimizations
            dataloader = torch.utils.data.DataLoader(
                dataset,
                batch_size=batch_size,
                shuffle=True,
                num_workers=self.config.get('num_workers', 4),
                pin_memory=True,
                prefetch_factor=2
            )
            
            # Optimize dataloader
            dataloader = self.performance_optimizer.optimize_data_loading(dataloader)
            
            # Training loop
            for epoch in range(epochs):
                # Train epoch
                train_metrics = trainer.train_epoch(dataloader)
                
                # Log metrics
                self.logger.info(f"Epoch {epoch+1}/{epochs}: {train_metrics}")
                
                # Save checkpoint
                if (epoch + 1) % 5 == 0:
                    checkpoint_path = f"./checkpoints/llm_checkpoint_epoch_{epoch+1}.pt"
                    trainer.save_checkpoint(checkpoint_path)
            
            # Save final model
            trainer.save_checkpoint("./checkpoints/llm_final_model.pt", is_best=True)
            
            return {
                "status": "success",
                "message": "Model fine-tuning completed successfully",
                "checkpoint_path": "./checkpoints/llm_final_model.pt"
            }
            
        except Exception as e:
            self.logger.error(f"Fine-tuning failed: {e}")
            raise
    
    def _prepare_training_data(self, training_data: List[Dict[str, str]]) -> Dataset:
        """Prepare training data following best practices."""
        # This is a placeholder - implement based on your data format
        class TextDataset(Dataset):
            def __init__(self, data, tokenizer, max_length=512):
                self.data = data
                self.tokenizer = tokenizer
                self.max_length = max_length
            
            def __len__(self):
                return len(self.data)
            
            def __getitem__(self, idx):
                item = self.data[idx]
                text = item.get('text', '')
                
                # Tokenize with proper padding and truncation
                encoding = self.tokenizer(
                    text,
                    truncation=True,
                    padding='max_length',
                    max_length=self.max_length,
                    return_tensors='pt'
                )
                
                return {
                    'input_ids': encoding['input_ids'].squeeze(),
                    'attention_mask': encoding['attention_mask'].squeeze(),
                    'labels': encoding['input_ids'].squeeze()
                }
        
        return TextDataset(training_data, self.tokenizer)
    
    def evaluate_model(self, test_data: List[Dict[str, str]]) -> Dict[str, float]:
        """Evaluate model performance following best practices."""
        try:
            # Prepare test dataset
            test_dataset = self._prepare_training_data(test_data)
            test_dataloader = torch.utils.data.DataLoader(
                test_dataset,
                batch_size=32,
                shuffle=False,
                num_workers=4,
                pin_memory=True
            )
            
            # Evaluation
            self.model.eval()
            total_loss = 0.0
            total_tokens = 0
            
            with torch.no_grad():
                for batch in test_dataloader:
                    # Move to device
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    labels = batch['labels'].to(self.device)
                    
                    # Forward pass
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels=labels
                    )
                    
                    total_loss += outputs.loss.item()
                    total_tokens += labels.numel()
            
            # Calculate metrics
            avg_loss = total_loss / len(test_dataloader)
            perplexity = torch.exp(torch.tensor(avg_loss))
            
            return {
                'test_loss': avg_loss,
                'perplexity': perplexity.item(),
                'total_tokens': total_tokens
            }
            
        except Exception as e:
            self.logger.error(f"Evaluation failed: {e}")
            raise
    
    def save_model(self, path: str) -> bool:
        """Save the transformer model following best practices."""
        try:
            # Create directory
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Save model
            self.model.save_pretrained(path)
            
            # Save tokenizer
            self.tokenizer.save_pretrained(path)
            
            # Save configuration
            config_path = os.path.join(path, "engine_config.json")
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            self.logger.info(f"Model saved to {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")
            return False
    
    def load_model(self, path: str) -> bool:
        """Load the transformer model following best practices."""
        try:
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                path,
                trust_remote_code=True,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
            
            # Move to device and apply optimizations
            self.model = self.performance_optimizer.optimize_model(self.model)
            
            # Setup multi-GPU if needed
            self._setup_multi_gpu()
            
            self.logger.info(f"Model loaded from {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get engine health status following best practices."""
        try:
            # Basic health info
            health = {
                'status': 'healthy',
                'model_loaded': self.model is not None,
                'tokenizer_loaded': self.tokenizer is not None,
                'device': str(self.device),
                'mixed_precision': self.mixed_precision
            }
            
            # Performance stats
            if hasattr(self, 'performance_optimizer'):
                health.update(self.performance_optimizer.get_performance_stats())
            
            # Multi-GPU info
            if hasattr(self, 'multi_gpu_config'):
                health.update({
                    'multi_gpu_enabled': self.multi_gpu_config.enable_multi_gpu,
                    'gpu_count': len(self.multi_gpu_config.gpu_ids),
                    'distributed_training': self.multi_gpu_config.distributed_training
                })
            
            return health
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def shutdown(self):
        """Shutdown the engine following best practices."""
        try:
            # Clean up distributed training
            if hasattr(self, 'dist') and dist.is_initialized():
                dist.destroy_process_group()
            
            # Clean up memory
            if hasattr(self, 'performance_optimizer'):
                self.performance_optimizer.memory_cleanup()
            
            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            self.logger.info("LLM Engine shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")


# Legacy alias for backward compatibility
LLMEngines = LLMEngine


