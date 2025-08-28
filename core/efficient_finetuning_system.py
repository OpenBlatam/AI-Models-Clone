#!/usr/bin/env python3
"""
Efficient Fine-tuning System for Diffusion Models

Advanced implementation of parameter-efficient fine-tuning techniques
for diffusion models and transformers, including:
- LoRA (Low-Rank Adaptation)
- QLoRA (Quantized LoRA)
- P-tuning and Prompt Tuning
- AdaLoRA and other adaptive methods
- Comprehensive training and inference pipelines
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import math
import numpy as np
from typing import Optional, Tuple, List, Dict, Any, Union, Callable
from dataclasses import dataclass, field
import logging
from pathlib import Path
import json
import time
from functools import lru_cache
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LoRAConfig:
    """Configuration for LoRA fine-tuning."""
    r: int = 16  # Rank of low-rank adaptation
    alpha: float = 32.0  # Scaling factor
    dropout: float = 0.1
    bias: str = "none"  # none, all, lora_only
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    modules_to_save: List[str] = field(default_factory=list)
    layers_to_transform: Optional[List[int]] = None
    layers_pattern: Optional[str] = None
    rank_pattern: Optional[Dict[str, int]] = None
    alpha_pattern: Optional[Dict[str, float]] = None
    use_rslora: bool = False  # Rank-Stabilized LoRA
    use_dora: bool = False  # DoRA (DoRA: Weight-Decomposed Low-Rank Adaptation)
    use_oft: bool = False  # Orthogonal Fine-Tuning

@dataclass
class QLoRAConfig:
    """Configuration for QLoRA fine-tuning."""
    lora_config: LoRAConfig = field(default_factory=LoRAConfig)
    bits: int = 4  # Quantization bits (4, 8)
    group_size: int = 128  # Group size for quantization
    double_quant: bool = True  # Double quantization
    compute_dtype: torch.dtype = torch.float16
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "k_proj", "v_proj", "o_proj"])
    use_nested_quant: bool = False
    use_4bit: bool = True
    use_8bit: bool = False

@dataclass
class PTuningConfig:
    """Configuration for P-tuning."""
    num_virtual_tokens: int = 20
    encoder_hidden_size: int = 128
    encoder_num_layers: int = 2
    encoder_dropout: float = 0.1
    prefix_projection: bool = True
    pre_seq_len: int = 20
    prefix_hidden_size: int = 512
    prefix_dropout: float = 0.1

@dataclass
class AdaLoRAConfig:
    """Configuration for AdaLoRA."""
    lora_config: LoRAConfig = field(default_factory=LoRAConfig)
    target_rank: int = 8
    init_r: int = 12
    tinit: int = 200
    tfinal: int = 1000
    delta_t: int = 10
    beta1: float = 0.85
    beta2: float = 0.85
    orth_reg_weight: float = 0.5
    total_step: int = 0

class LoRALayer(nn.Module):
    """Low-Rank Adaptation layer."""
    
    def __init__(self, in_features: int, out_features: int, config: LoRAConfig):
        super().__init__()
        self.config = config
        self.in_features = in_features
        self.out_features = out_features
        
        # LoRA parameters
        self.lora_A = nn.Parameter(torch.zeros(config.r, in_features))
        self.lora_B = nn.Parameter(torch.zeros(out_features, config.r))
        self.scaling = config.alpha / config.r
        
        # Optional bias
        if config.bias == "all":
            self.lora_bias = nn.Parameter(torch.zeros(out_features))
        elif config.bias == "lora_only":
            self.lora_bias = nn.Parameter(torch.zeros(out_features))
        else:
            self.lora_bias = None
        
        # Dropout
        self.dropout = nn.Dropout(config.dropout)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize LoRA weights."""
        # Initialize A with Kaiming uniform
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
        # Initialize B with zeros
        nn.init.zeros_(self.lora_B)
        
        if self.lora_bias is not None:
            nn.init.zeros_(self.lora_bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass of LoRA layer."""
        # LoRA computation
        lora_output = self.dropout(x @ self.lora_A.T) @ self.lora_B.T
        
        # Apply scaling
        lora_output = lora_output * self.scaling
        
        # Add bias if present
        if self.lora_bias is not None:
            lora_output = lora_output + self.lora_bias
        
        return lora_output
    
    def merge_weights(self, base_weight: torch.Tensor) -> torch.Tensor:
        """Merge LoRA weights with base weights."""
        return base_weight + (self.lora_A.T @ self.lora_B.T) * self.scaling
    
    def get_delta_weight(self) -> torch.Tensor:
        """Get the delta weight matrix."""
        return (self.lora_A.T @ self.lora_B.T) * self.scaling

class LoRALinear(nn.Module):
    """Linear layer with LoRA adaptation."""
    
    def __init__(self, linear_layer: nn.Linear, config: LoRAConfig):
        super().__init__()
        self.linear = linear_layer
        self.lora = LoRALayer(linear_layer.in_features, linear_layer.out_features, config)
        self.config = config
        
        # Freeze base layer
        for param in self.linear.parameters():
            param.requires_grad = False
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass combining base and LoRA outputs."""
        base_output = self.linear(x)
        lora_output = self.lora(x)
        return base_output + lora_output
    
    def merge_weights(self):
        """Merge LoRA weights into base weights."""
        with torch.no_grad():
            self.linear.weight.data = self.lora.merge_weights(self.linear.weight.data)
            if self.lora.lora_bias is not None and self.linear.bias is not None:
                self.linear.bias.data = self.linear.bias.data + self.lora.lora_bias.data

class QLoRALinear(nn.Module):
    """Quantized Linear layer with LoRA adaptation."""
    
    def __init__(self, linear_layer: nn.Linear, config: QLoRAConfig):
        super().__init__()
        self.config = config
        self.linear = linear_layer
        
        # Quantize base weights
        self._quantize_weights()
        
        # Add LoRA
        self.lora = LoRALayer(linear_layer.in_features, linear_layer.out_features, config.lora_config)
        
        # Freeze quantized weights
        for param in self.linear.parameters():
            param.requires_grad = False
    
    def _quantize_weights(self):
        """Quantize the base weights."""
        if self.config.use_4bit:
            self._quantize_4bit()
        elif self.config.use_8bit:
            self._quantize_8bit()
    
    def _quantize_4bit(self):
        """4-bit quantization."""
        # Simplified 4-bit quantization
        weight = self.linear.weight.data
        scale = weight.abs().max() / 7.0  # 4-bit range: -8 to 7
        quantized = torch.round(weight / scale).clamp(-8, 7)
        self.linear.weight.data = quantized * scale
    
    def _quantize_8bit(self):
        """8-bit quantization."""
        weight = self.linear.weight.data
        scale = weight.abs().max() / 127.0  # 8-bit range: -128 to 127
        quantized = torch.round(weight / scale).clamp(-128, 127)
        self.linear.weight.data = quantized * scale
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with quantized weights and LoRA."""
        base_output = self.linear(x)
        lora_output = self.lora(x)
        return base_output + lora_output

class PTuningV2(nn.Module):
    """P-tuning v2 implementation."""
    
    def __init__(self, config: PTuningConfig, hidden_size: int):
        super().__init__()
        self.config = config
        self.hidden_size = hidden_size
        
        # Virtual token embeddings
        self.prefix_tokens = nn.Parameter(
            torch.randn(config.num_virtual_tokens, hidden_size)
        )
        
        # Prefix encoder
        if config.prefix_projection:
            self.prefix_encoder = nn.Sequential(
                nn.Linear(hidden_size, config.prefix_hidden_size),
                nn.Tanh(),
                nn.Linear(config.prefix_hidden_size, hidden_size)
            )
        else:
            self.prefix_encoder = None
        
        # Dropout
        self.dropout = nn.Dropout(config.prefix_dropout)
        
        # Initialize
        self._init_weights()
    
    def _init_weights(self):
        """Initialize prefix tokens."""
        nn.init.normal_(self.prefix_tokens, std=0.02)
    
    def forward(self, batch_size: int) -> torch.Tensor:
        """Generate prefix embeddings."""
        prefix_tokens = self.prefix_tokens.unsqueeze(0).expand(batch_size, -1, -1)
        
        if self.prefix_encoder is not None:
            prefix_tokens = self.prefix_encoder(prefix_tokens)
        
        return self.dropout(prefix_tokens)

class AdaLoRALayer(nn.Module):
    """AdaLoRA layer with adaptive rank allocation."""
    
    def __init__(self, in_features: int, out_features: int, config: AdaLoRAConfig):
        super().__init__()
        self.config = config
        self.in_features = in_features
        self.out_features = out_features
        
        # Initialize with higher rank
        self.lora_A = nn.Parameter(torch.zeros(config.init_r, in_features))
        self.lora_B = nn.Parameter(torch.zeros(out_features, config.init_r))
        self.lora_E = nn.Parameter(torch.zeros(config.init_r, config.init_r))
        
        # Importance scores
        self.importance = nn.Parameter(torch.ones(config.init_r))
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize AdaLoRA weights."""
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
        nn.init.zeros_(self.lora_B)
        nn.init.eye_(self.lora_E)
        nn.init.ones_(self.importance)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with adaptive rank."""
        # Compute effective rank
        effective_rank = min(self.config.target_rank, self.config.init_r)
        
        # Select top-k components
        _, indices = torch.topk(self.importance, effective_rank)
        
        # Extract selected components
        A_selected = self.lora_A[indices]
        B_selected = self.lora_B[:, indices]
        E_selected = self.lora_E[indices][:, indices]
        
        # Compute output
        output = x @ A_selected.T @ E_selected @ B_selected.T
        return output * (self.config.lora_config.alpha / effective_rank)
    
    def update_importance(self, step: int):
        """Update importance scores."""
        if step < self.config.tinit:
            return
        
        # Compute importance based on gradient magnitude
        with torch.no_grad():
            grad_A = self.lora_A.grad.abs().mean(dim=1) if self.lora_A.grad is not None else torch.zeros_like(self.importance)
            grad_B = self.lora_B.grad.abs().mean(dim=0) if self.lora_B.grad is not None else torch.zeros_like(self.importance)
            
            importance = (grad_A + grad_B) / 2
            self.importance.data = self.config.beta1 * self.importance.data + (1 - self.config.beta1) * importance

class LoRAManager:
    """Manager for LoRA fine-tuning."""
    
    def __init__(self, model: nn.Module, config: LoRAConfig):
        self.model = model
        self.config = config
        self.lora_layers = {}
        self._apply_lora()
    
    def _apply_lora(self):
        """Apply LoRA to target modules."""
        for name, module in self.model.named_modules():
            if self._should_apply_lora(name, module):
                self._replace_with_lora(name, module)
    
    def _should_apply_lora(self, name: str, module: nn.Module) -> bool:
        """Check if LoRA should be applied to this module."""
        if not isinstance(module, nn.Linear):
            return False
        
        # Check target modules
        for target in self.config.target_modules:
            if target in name:
                return True
        
        # Check layer patterns
        if self.config.layers_pattern:
            import re
            if re.search(self.config.layers_pattern, name):
                return True
        
        return False
    
    def _replace_with_lora(self, name: str, module: nn.Module):
        """Replace module with LoRA version."""
        parent_name = '.'.join(name.split('.')[:-1])
        child_name = name.split('.')[-1]
        
        if parent_name:
            parent = self.model.get_submodule(parent_name)
            setattr(parent, child_name, LoRALinear(module, self.config))
        else:
            setattr(self.model, child_name, LoRALinear(module, self.config))
        
        self.lora_layers[name] = getattr(parent if parent_name else self.model, child_name)
    
    def get_trainable_parameters(self) -> List[nn.Parameter]:
        """Get trainable parameters."""
        trainable_params = []
        for layer in self.lora_layers.values():
            trainable_params.extend(layer.lora.parameters())
        return trainable_params
    
    def merge_weights(self):
        """Merge all LoRA weights into base weights."""
        for layer in self.lora_layers.values():
            layer.merge_weights()
    
    def save_lora_weights(self, path: str):
        """Save LoRA weights."""
        lora_state_dict = {}
        for name, layer in self.lora_layers.items():
            lora_state_dict[f"{name}.lora_A"] = layer.lora.lora_A.data
            lora_state_dict[f"{name}.lora_B"] = layer.lora.lora_B.data
            if layer.lora.lora_bias is not None:
                lora_state_dict[f"{name}.lora_bias"] = layer.lora.lora_bias.data
        
        torch.save(lora_state_dict, path)
        logger.info(f"LoRA weights saved to {path}")
    
    def load_lora_weights(self, path: str):
        """Load LoRA weights."""
        lora_state_dict = torch.load(path, map_location='cpu')
        
        for name, layer in self.lora_layers.items():
            if f"{name}.lora_A" in lora_state_dict:
                layer.lora.lora_A.data = lora_state_dict[f"{name}.lora_A"]
            if f"{name}.lora_B" in lora_state_dict:
                layer.lora.lora_B.data = lora_state_dict[f"{name}.lora_B"]
            if f"{name}.lora_bias" in lora_state_dict and layer.lora.lora_bias is not None:
                layer.lora.lora_bias.data = lora_state_dict[f"{name}.lora_bias"]
        
        logger.info(f"LoRA weights loaded from {path}")

class EfficientFineTuningTrainer:
    """Trainer for efficient fine-tuning methods."""
    
    def __init__(self, model: nn.Module, config: Union[LoRAConfig, QLoRAConfig, PTuningConfig]):
        self.model = model
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Setup based on config type
        if isinstance(config, LoRAConfig):
            self.lora_manager = LoRAManager(model, config)
            self.trainable_params = self.lora_manager.get_trainable_parameters()
        elif isinstance(config, QLoRAConfig):
            self.lora_manager = LoRAManager(model, config.lora_config)
            self.trainable_params = self.lora_manager.get_trainable_parameters()
        elif isinstance(config, PTuningConfig):
            self.p_tuning = PTuningV2(config, model.config.hidden_size if hasattr(model, 'config') else 768)
            self.trainable_params = list(self.p_tuning.parameters())
        else:
            raise ValueError(f"Unsupported config type: {type(config)}")
        
        # Move to device
        self.model.to(self.device)
        if hasattr(self, 'p_tuning'):
            self.p_tuning.to(self.device)
    
    def setup_optimizer(self, learning_rate: float = 1e-4, weight_decay: float = 0.01):
        """Setup optimizer for training."""
        self.optimizer = torch.optim.AdamW(
            self.trainable_params,
            lr=learning_rate,
            weight_decay=weight_decay
        )
    
    def setup_scheduler(self, num_training_steps: int, warmup_steps: int = 100):
        """Setup learning rate scheduler."""
        from transformers import get_linear_schedule_with_warmup
        
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=num_training_steps
        )
    
    def train_step(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """Single training step."""
        self.model.train()
        self.optimizer.zero_grad()
        
        # Move batch to device
        batch = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v for k, v in batch.items()}
        
        # Forward pass
        if hasattr(self, 'p_tuning'):
            # P-tuning: prepend prefix tokens
            batch_size = batch['input_ids'].size(0)
            prefix_embeddings = self.p_tuning(batch_size)
            
            # Modify input embeddings
            if hasattr(self.model, 'get_input_embeddings'):
                embeddings = self.model.get_input_embeddings()(batch['input_ids'])
                embeddings = torch.cat([prefix_embeddings, embeddings], dim=1)
                
                # Update attention mask
                prefix_len = prefix_embeddings.size(1)
                batch['attention_mask'] = torch.cat([
                    torch.ones(batch_size, prefix_len, device=self.device),
                    batch['attention_mask']
                ], dim=1)
                
                # Forward pass with modified embeddings
                outputs = self.model(inputs_embeds=embeddings, attention_mask=batch['attention_mask'])
            else:
                outputs = self.model(**batch)
        else:
            # LoRA/QLoRA: standard forward pass
            outputs = self.model(**batch)
        
        # Compute loss
        loss = outputs.loss if hasattr(outputs, 'loss') else outputs[0]
        
        # Backward pass
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.trainable_params, max_norm=1.0)
        
        # Optimizer step
        self.optimizer.step()
        self.scheduler.step()
        
        return {"loss": loss.item(), "learning_rate": self.scheduler.get_last_lr()[0]}
    
    def save_checkpoint(self, path: str):
        """Save training checkpoint."""
        checkpoint = {
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict(),
            "config": self.config
        }
        
        if hasattr(self, 'lora_manager'):
            checkpoint["lora_state_dict"] = {
                name: layer.lora.state_dict() for name, layer in self.lora_layers.items()
            }
        
        if hasattr(self, 'p_tuning'):
            checkpoint["p_tuning_state_dict"] = self.p_tuning.state_dict()
        
        torch.save(checkpoint, path)
        logger.info(f"Checkpoint saved to {path}")
    
    def load_checkpoint(self, path: str):
        """Load training checkpoint."""
        checkpoint = torch.load(path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        
        if "lora_state_dict" in checkpoint and hasattr(self, 'lora_manager'):
            for name, state_dict in checkpoint["lora_state_dict"].items():
                if name in self.lora_layers:
                    self.lora_layers[name].lora.load_state_dict(state_dict)
        
        if "p_tuning_state_dict" in checkpoint and hasattr(self, 'p_tuning'):
            self.p_tuning.load_state_dict(checkpoint["p_tuning_state_dict"])
        
        logger.info(f"Checkpoint loaded from {path}")

class EfficientFineTuningSystem:
    """Complete system for efficient fine-tuning."""
    
    def __init__(self, model: nn.Module):
        self.model = model
        self.trainers = {}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def setup_lora(self, config: LoRAConfig) -> LoRAManager:
        """Setup LoRA fine-tuning."""
        trainer = EfficientFineTuningTrainer(self.model, config)
        self.trainers["lora"] = trainer
        return trainer.lora_manager
    
    def setup_qlora(self, config: QLoRAConfig) -> LoRAManager:
        """Setup QLoRA fine-tuning."""
        trainer = EfficientFineTuningTrainer(self.model, config)
        self.trainers["qlora"] = trainer
        return trainer.lora_manager
    
    def setup_p_tuning(self, config: PTuningConfig) -> PTuningV2:
        """Setup P-tuning fine-tuning."""
        trainer = EfficientFineTuningTrainer(self.model, config)
        self.trainers["p_tuning"] = trainer
        return trainer.p_tuning
    
    def get_trainer(self, method: str) -> EfficientFineTuningTrainer:
        """Get trainer for specific method."""
        if method not in self.trainers:
            raise ValueError(f"Trainer for method '{method}' not found. Available: {list(self.trainers.keys())}")
        return self.trainers[method]
    
    def train(self, method: str, dataloader: DataLoader, num_epochs: int = 3, 
              learning_rate: float = 1e-4, save_path: str = "checkpoints"):
        """Train using specified method."""
        trainer = self.get_trainer(method)
        
        # Setup optimizer and scheduler
        total_steps = len(dataloader) * num_epochs
        trainer.setup_optimizer(learning_rate=learning_rate)
        trainer.setup_scheduler(num_training_steps=total_steps)
        
        # Training loop
        logger.info(f"Starting {method} training for {num_epochs} epochs")
        
        for epoch in range(num_epochs):
            epoch_loss = 0.0
            num_batches = 0
            
            for batch in dataloader:
                metrics = trainer.train_step(batch)
                epoch_loss += metrics["loss"]
                num_batches += 1
                
                if num_batches % 100 == 0:
                    logger.info(f"Epoch {epoch+1}, Batch {num_batches}, Loss: {metrics['loss']:.4f}")
            
            avg_loss = epoch_loss / num_batches
            logger.info(f"Epoch {epoch+1} completed. Average loss: {avg_loss:.4f}")
            
            # Save checkpoint
            checkpoint_path = Path(save_path) / f"{method}_epoch_{epoch+1}.pt"
            checkpoint_path.parent.mkdir(exist_ok=True)
            trainer.save_checkpoint(str(checkpoint_path))
        
        logger.info(f"{method} training completed!")
    
    def merge_and_save(self, method: str, output_path: str):
        """Merge fine-tuned weights and save model."""
        if method == "lora" or method == "qlora":
            trainer = self.get_trainer(method)
            trainer.lora_manager.merge_weights()
            
            # Save merged model
            torch.save(self.model.state_dict(), output_path)
            logger.info(f"Merged {method} model saved to {output_path}")
        
        elif method == "p_tuning":
            # For P-tuning, save the prefix encoder
            trainer = self.get_trainer(method)
            torch.save(trainer.p_tuning.state_dict(), output_path)
            logger.info(f"P-tuning model saved to {output_path}")

# Production usage example
def main():
    """Production usage example."""
    try:
        # Example: Setup LoRA for a transformer model
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        # Load model
        model_name = "gpt2"
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Setup efficient fine-tuning system
        system = EfficientFineTuningSystem(model)
        
        # LoRA configuration
        lora_config = LoRAConfig(
            r=16,
            alpha=32.0,
            dropout=0.1,
            target_modules=["c_attn", "c_proj"]
        )
        
        # Setup LoRA
        lora_manager = system.setup_lora(lora_config)
        
        # QLoRA configuration
        qlora_config = QLoRAConfig(
            lora_config=LoRAConfig(r=8, alpha=16.0),
            bits=4,
            group_size=128,
            double_quant=True
        )
        
        # Setup QLoRA
        qlora_manager = system.setup_qlora(qlora_config)
        
        # P-tuning configuration
        p_tuning_config = PTuningConfig(
            num_virtual_tokens=20,
            encoder_hidden_size=128,
            prefix_projection=True
        )
        
        # Setup P-tuning
        p_tuning = system.setup_p_tuning(p_tuning_config)
        
        print("✅ Efficient fine-tuning system setup completed!")
        print(f"LoRA parameters: {sum(p.numel() for p in lora_manager.get_trainable_parameters()):,}")
        print(f"QLoRA parameters: {sum(p.numel() for p in qlora_manager.get_trainable_parameters()):,}")
        print(f"P-tuning parameters: {sum(p.numel() for p in p_tuning.parameters()):,}")
        
    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")

if __name__ == "__main__":
    main() 