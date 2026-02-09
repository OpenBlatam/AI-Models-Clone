# EFFICIENT FINE-TUNING TECHNIQUES

# ============================================================================
# LOW-RANK ADAPTATION (LoRA) IMPLEMENTATION
# ============================================================================

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass
import numpy as np

class LoRALayer(nn.Module):
    """Low-Rank Adaptation (LoRA) layer for efficient fine-tuning."""
    
    def __init__(self, in_features: int, out_features: int, rank: int = 16, 
                 alpha: float = 16.0, dropout: float = 0.1, bias: bool = True):
        super().__init__()
        
        self.rank = rank
        self.alpha = alpha
        self.scaling = alpha / rank
        self.dropout = dropout
        
        # LoRA matrices
        self.lora_A = nn.Parameter(torch.randn(rank, in_features) * 0.02)
        self.lora_B = nn.Parameter(torch.zeros(out_features, rank))
        
        # Initialize B with zeros
        nn.init.zeros_(self.lora_B)
        
        # Optional bias
        self.bias = nn.Parameter(torch.zeros(out_features)) if bias else None
        
        # Dropout layer
        self.dropout_layer = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through LoRA layer."""
        # LoRA computation: x @ A.T @ B.T * scaling
        lora_output = x @ self.lora_A.T @ self.lora_B.T * self.scaling
        
        # Apply dropout
        lora_output = self.dropout_layer(lora_output)
        
        # Add bias if present
        if self.bias is not None:
            lora_output = lora_output + self.bias
        
        return lora_output
    
    def get_adapter_parameters(self) -> List[nn.Parameter]:
        """Get LoRA adapter parameters."""
        return [self.lora_A, self.lora_B] + ([self.bias] if self.bias is not None else [])

class LoRALinear(nn.Module):
    """Linear layer with LoRA adaptation."""
    
    def __init__(self, in_features: int, out_features: int, rank: int = 16, 
                 alpha: float = 16.0, dropout: float = 0.1, bias: bool = True):
        super().__init__()
        
        self.base_layer = nn.Linear(in_features, out_features, bias=bias)
        self.lora_layer = LoRALayer(in_features, out_features, rank, alpha, dropout, bias=False)
        
        # Freeze base layer parameters
        for param in self.base_layer.parameters():
            param.requires_grad = False
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with LoRA adaptation."""
        base_output = self.base_layer(x)
        lora_output = self.lora_layer(x)
        return base_output + lora_output
    
    def get_adapter_parameters(self) -> List[nn.Parameter]:
        """Get LoRA adapter parameters."""
        return self.lora_layer.get_adapter_parameters()
    
    def merge_weights(self):
        """Merge LoRA weights into base layer (for inference)."""
        with torch.no_grad():
            # Update base layer weights
            self.base_layer.weight.data += (
                self.lora_layer.lora_B @ self.lora_layer.lora_A.T * self.lora_layer.scaling
            )
            
            # Update bias if present
            if self.base_layer.bias is not None and self.lora_layer.bias is not None:
                self.base_layer.bias.data += self.lora_layer.bias.data

class LoRAConfig:
    """Configuration for LoRA fine-tuning."""
    
    def __init__(self, rank: int = 16, alpha: float = 16.0, dropout: float = 0.1,
                 target_modules: Optional[List[str]] = None, bias: str = 'none'):
        self.rank = rank
        self.alpha = alpha
        self.dropout = dropout
        self.target_modules = target_modules or ['q_proj', 'v_proj', 'k_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj']
        self.bias = bias  # 'none', 'all', 'lora_only'

class LoRAModel(nn.Module):
    """Base class for models with LoRA adaptation."""
    
    def __init__(self, base_model: nn.Module, lora_config: LoRAConfig):
        super().__init__()
        
        self.base_model = base_model
        self.lora_config = lora_config
        
        # Apply LoRA to target modules
        self._apply_lora_to_model()
        
        # Freeze base model parameters
        self._freeze_base_model()
    
    def _apply_lora_to_model(self):
        """Apply LoRA to target modules in the base model."""
        for name, module in self.base_model.named_modules():
            if any(target in name for target in self.lora_config.target_modules):
                if isinstance(module, nn.Linear):
                    # Replace with LoRA linear layer
                    parent_name = '.'.join(name.split('.')[:-1])
                    child_name = name.split('.')[-1]
                    
                    if parent_name:
                        parent = self.base_model.get_submodule(parent_name)
                        setattr(parent, child_name, LoRALinear(
                            module.in_features, module.out_features,
                            self.lora_config.rank, self.lora_config.alpha,
                            self.lora_config.dropout, module.bias is not None
                        ))
                    else:
                        # Root level module
                        setattr(self.base_model, child_name, LoRALinear(
                            module.in_features, module.out_features,
                            self.lora_config.rank, self.lora_config.alpha,
                            self.lora_config.dropout, module.bias is not None
                        ))
    
    def _freeze_base_model(self):
        """Freeze base model parameters."""
        for param in self.base_model.parameters():
            param.requires_grad = False
    
    def get_trainable_parameters(self) -> List[nn.Parameter]:
        """Get only the trainable LoRA parameters."""
        trainable_params = []
        for module in self.modules():
            if isinstance(module, LoRALayer):
                trainable_params.extend(module.parameters())
            elif isinstance(module, LoRALinear):
                trainable_params.extend(module.get_adapter_parameters())
        return trainable_params
    
    def forward(self, *args, **kwargs):
        """Forward pass through the base model."""
        return self.base_model(*args, **kwargs)
    
    def merge_lora_weights(self):
        """Merge all LoRA weights into base model."""
        for module in self.modules():
            if isinstance(module, LoRALinear):
                module.merge_weights()

# ============================================================================
# P-TUNING IMPLEMENTATION
# ============================================================================

class PromptEmbedding(nn.Module):
    """Learnable prompt embeddings for P-tuning."""
    
    def __init__(self, num_prompts: int, prompt_length: int, hidden_size: int):
        super().__init__()
        
        self.num_prompts = num_prompts
        self.prompt_length = prompt_length
        self.hidden_size = hidden_size
        
        # Learnable prompt embeddings
        self.prompt_embeddings = nn.Parameter(
            torch.randn(num_prompts, prompt_length, hidden_size) * 0.02
        )
        
        # Optional prompt encoder
        self.prompt_encoder = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size)
        )
    
    def forward(self, batch_size: int) -> torch.Tensor:
        """Get prompt embeddings for current batch."""
        # Expand prompt embeddings to batch size
        prompt_embeds = self.prompt_embeddings.unsqueeze(0).expand(batch_size, -1, -1, -1)
        
        # Apply prompt encoder
        encoded_prompts = self.prompt_encoder(prompt_embeds)
        
        return encoded_prompts

class P_TuningModel(nn.Module):
    """P-tuning model with learnable prompt embeddings."""
    
    def __init__(self, base_model: nn.Module, num_prompts: int = 20, 
                 prompt_length: int = 10, hidden_size: int = 768):
        super().__init__()
        
        self.base_model = base_model
        self.num_prompts = num_prompts
        self.prompt_length = prompt_length
        self.hidden_size = hidden_size
        
        # Prompt embeddings
        self.prompt_embeddings = PromptEmbedding(num_prompts, prompt_length, hidden_size)
        
        # Freeze base model parameters
        self._freeze_base_model()
    
    def _freeze_base_model(self):
        """Freeze base model parameters."""
        for param in self.base_model.parameters():
            param.requires_grad = False
    
    def forward(self, input_ids: torch.Tensor, prompt_ids: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass with P-tuning."""
        batch_size = input_ids.size(0)
        
        # Get prompt embeddings
        if prompt_ids is not None:
            prompt_idx = prompt_ids
        else:
            prompt_idx = torch.zeros(batch_size, dtype=torch.long, device=input_ids.device)
        
        prompt_embeds = self.prompt_embeddings(batch_size)
        selected_prompts = prompt_embeds[torch.arange(batch_size), prompt_idx]
        
        # Get base model embeddings
        if hasattr(self.base_model, 'embeddings'):
            base_embeds = self.base_model.embeddings(input_ids)
        else:
            # Fallback for models without explicit embeddings
            base_embeds = self.base_model.get_input_embeddings()(input_ids)
        
        # Concatenate prompts with input embeddings
        combined_embeds = torch.cat([selected_prompts, base_embeds], dim=1)
        
        # Forward through base model
        outputs = self.base_model(inputs_embeds=combined_embeds)
        
        return outputs
    
    def get_trainable_parameters(self) -> List[nn.Parameter]:
        """Get only the trainable prompt parameters."""
        return list(self.prompt_embeddings.parameters())

# ============================================================================
# ADAPTIVE LoRA (AdaLoRA) IMPLEMENTATION
# ============================================================================

class AdaLoRALayer(nn.Module):
    """Adaptive LoRA with dynamic rank allocation."""
    
    def __init__(self, in_features: int, out_features: int, max_rank: int = 64,
                 alpha: float = 16.0, dropout: float = 0.1, bias: bool = True):
        super().__init__()
        
        self.max_rank = max_rank
        self.alpha = alpha
        self.dropout = dropout
        
        # Full rank LoRA matrices
        self.lora_A = nn.Parameter(torch.randn(max_rank, in_features) * 0.02)
        self.lora_B = nn.Parameter(torch.zeros(out_features, max_rank))
        
        # Initialize B with zeros
        nn.init.zeros_(self.lora_B)
        
        # Adaptive rank allocation
        self.rank_importance = nn.Parameter(torch.ones(max_rank))
        self.current_rank = max_rank
        
        # Optional bias
        self.bias = nn.Parameter(torch.zeros(out_features)) if bias else None
        
        # Dropout layer
        self.dropout_layer = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with adaptive rank."""
        # Get current rank based on importance
        current_rank = self._get_current_rank()
        
        # LoRA computation with current rank
        lora_output = x @ self.lora_A[:current_rank].T @ self.lora_B[:, :current_rank].T * (self.alpha / current_rank)
        
        # Apply dropout
        lora_output = self.dropout_layer(lora_output)
        
        # Add bias if present
        if self.bias is not None:
            lora_output = lora_output + self.bias
        
        return lora_output
    
    def _get_current_rank(self) -> int:
        """Get current rank based on importance scores."""
        # Sort importance scores
        sorted_importance, _ = torch.sort(self.rank_importance, descending=True)
        
        # Find rank that captures 90% of total importance
        cumulative_importance = torch.cumsum(sorted_importance, dim=0)
        total_importance = cumulative_importance[-1]
        threshold = 0.9 * total_importance
        
        current_rank = torch.sum(cumulative_importance < threshold).item() + 1
        current_rank = max(1, min(current_rank, self.max_rank))
        
        self.current_rank = current_rank
        return current_rank
    
    def update_rank_importance(self, gradients: torch.Tensor):
        """Update rank importance based on gradients."""
        if gradients is not None:
            # Compute gradient norm for each rank
            grad_norms = torch.norm(gradients.view(self.max_rank, -1), dim=1)
            
            # Update importance scores
            self.rank_importance.data = 0.9 * self.rank_importance.data + 0.1 * grad_norms

class AdaLoRALinear(nn.Module):
    """Linear layer with AdaLoRA adaptation."""
    
    def __init__(self, in_features: int, out_features: int, max_rank: int = 64,
                 alpha: float = 16.0, dropout: float = 0.1, bias: bool = True):
        super().__init__()
        
        self.base_layer = nn.Linear(in_features, out_features, bias=bias)
        self.adalora_layer = AdaLoRALayer(in_features, out_features, max_rank, alpha, dropout, bias=False)
        
        # Freeze base layer parameters
        for param in self.base_layer.parameters():
            param.requires_grad = False
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with AdaLoRA adaptation."""
        base_output = self.base_layer(x)
        adalora_output = self.adalora_layer(x)
        return base_output + adalora_output
    
    def update_rank_importance(self, gradients: torch.Tensor):
        """Update rank importance in AdaLoRA layer."""
        self.adalora_layer.update_rank_importance(gradients)

# ============================================================================
# PREFIX TUNING IMPLEMENTATION
# ============================================================================

class PrefixTuning(nn.Module):
    """Prefix Tuning for parameter-efficient fine-tuning."""
    
    def __init__(self, num_layers: int, hidden_size: int, prefix_length: int = 20,
                 num_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        self.prefix_length = prefix_length
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads
        
        # Learnable prefix embeddings for each layer
        self.prefix_embeddings = nn.Parameter(
            torch.randn(num_layers, 2, prefix_length, hidden_size) * 0.02
        )
        
        # Prefix projection layers
        self.prefix_projection = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size)
        )
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, batch_size: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get prefix embeddings for current batch."""
        # Project prefix embeddings
        projected_prefix = self.prefix_projection(self.prefix_embeddings)
        
        # Split into key and value prefixes
        key_prefix = projected_prefix[:, 0]  # [num_layers, prefix_length, hidden_size]
        value_prefix = projected_prefix[:, 1]  # [num_layers, prefix_length, hidden_size]
        
        # Expand to batch size
        key_prefix = key_prefix.unsqueeze(0).expand(batch_size, -1, -1, -1)
        value_prefix = value_prefix.unsqueeze(0).expand(batch_size, -1, -1, -1)
        
        # Apply dropout
        key_prefix = self.dropout(key_prefix)
        value_prefix = self.dropout(value_prefix)
        
        return key_prefix, value_prefix

class PrefixTuningModel(nn.Module):
    """Model with Prefix Tuning adaptation."""
    
    def __init__(self, base_model: nn.Module, num_layers: int, hidden_size: int,
                 prefix_length: int = 20, num_heads: int = 8):
        super().__init__()
        
        self.base_model = base_model
        self.prefix_tuning = PrefixTuning(num_layers, hidden_size, prefix_length, num_heads)
        
        # Freeze base model parameters
        self._freeze_base_model()
    
    def _freeze_base_model(self):
        """Freeze base model parameters."""
        for param in self.base_model.parameters():
            param.requires_grad = False
    
    def forward(self, input_ids: torch.Tensor, **kwargs) -> torch.Tensor:
        """Forward pass with prefix tuning."""
        batch_size = input_ids.size(0)
        device = input_ids.device
        
        # Get prefix embeddings
        key_prefix, value_prefix = self.prefix_tuning(batch_size, device)
        
        # Forward through base model with prefixes
        # This would need to be adapted based on the specific base model architecture
        outputs = self.base_model(input_ids, key_prefix=key_prefix, value_prefix=value_prefix, **kwargs)
        
        return outputs
    
    def get_trainable_parameters(self) -> List[nn.Parameter]:
        """Get only the trainable prefix parameters."""
        return list(self.prefix_tuning.parameters())

# ============================================================================
# QLoRA IMPLEMENTATION
# ============================================================================

class QLoRALinear(nn.Module):
    """QLoRA: Quantized LoRA for memory efficiency."""
    
    def __init__(self, in_features: int, out_features: int, rank: int = 16,
                 alpha: float = 16.0, dropout: float = 0.1, bias: bool = True,
                 bits: int = 4):
        super().__init__()
        
        self.bits = bits
        self.rank = rank
        self.alpha = alpha
        self.scaling = alpha / rank
        
        # Quantized base layer (simplified implementation)
        self.base_layer = nn.Linear(in_features, out_features, bias=bias)
        
        # LoRA layer
        self.lora_layer = LoRALayer(in_features, out_features, rank, alpha, dropout, bias=False)
        
        # Freeze base layer parameters
        for param in self.base_layer.parameters():
            param.requires_grad = False
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with QLoRA."""
        # Quantized forward pass (simplified)
        base_output = self.base_layer(x)
        lora_output = self.lora_layer(x)
        return base_output + lora_output
    
    def get_adapter_parameters(self) -> List[nn.Parameter]:
        """Get LoRA adapter parameters."""
        return self.lora_layer.get_adapter_parameters()

# ============================================================================
# FINE-TUNING MANAGER
# ============================================================================

class FineTuningManager:
    """Manager for different fine-tuning techniques."""
    
    def __init__(self, base_model: nn.Module, technique: str = 'lora', **kwargs):
        self.base_model = base_model
        self.technique = technique
        
        # Apply selected fine-tuning technique
        if technique == 'lora':
            lora_config = LoRAConfig(**kwargs)
            self.adapted_model = LoRAModel(base_model, lora_config)
        elif technique == 'p_tuning':
            self.adapted_model = P_TuningModel(base_model, **kwargs)
        elif technique == 'adalora':
            # Apply AdaLoRA to linear layers
            self.adapted_model = self._apply_adalora_to_model(base_model, **kwargs)
        elif technique == 'prefix_tuning':
            self.adapted_model = PrefixTuningModel(base_model, **kwargs)
        elif technique == 'qlora':
            self.adapted_model = self._apply_qlora_to_model(base_model, **kwargs)
        else:
            raise ValueError(f"Unknown fine-tuning technique: {technique}")
    
    def _apply_adalora_to_model(self, model: nn.Module, **kwargs) -> nn.Module:
        """Apply AdaLoRA to linear layers in the model."""
        # Create a wrapper class to add the required method
        class AdaLoRAModelWrapper(nn.Module):
            def __init__(self, base_model):
                super().__init__()
                self.base_model = base_model
                self._apply_adalora()
            
            def _apply_adalora(self):
                """Apply AdaLoRA to linear layers."""
                for name, module in self.base_model.named_modules():
                    if isinstance(module, nn.Linear):
                        # Replace with AdaLoRA linear layer
                        parent_name = '.'.join(name.split('.')[:-1])
                        child_name = name.split('.')[-1]
                        
                        if parent_name:
                            parent = self.base_model.get_submodule(parent_name)
                            setattr(parent, child_name, AdaLoRALinear(
                                module.in_features, module.out_features, **kwargs
                            ))
                        else:
                            setattr(self.base_model, child_name, AdaLoRALinear(
                                module.in_features, module.out_features, **kwargs
                            ))
            
            def forward(self, *args, **kwargs):
                return self.base_model(*args, **kwargs)
            
            def get_trainable_parameters(self):
                """Get trainable AdaLoRA parameters."""
                trainable_params = []
                for module in self.base_model.modules():
                    if isinstance(module, AdaLoRALinear):
                        trainable_params.extend(module.adalora_layer.parameters())
                return trainable_params
        
        return AdaLoRAModelWrapper(model)
    
    def _apply_qlora_to_model(self, model: nn.Module, **kwargs) -> nn.Module:
        """Apply QLoRA to linear layers in the model."""
        # Create a wrapper class to add the required method
        class QLoRAModelWrapper(nn.Module):
            def __init__(self, base_model):
                super().__init__()
                self.base_model = base_model
                self._apply_qlora()
            
            def _apply_qlora(self):
                """Apply QLoRA to linear layers."""
                for name, module in self.base_model.named_modules():
                    if isinstance(module, nn.Linear):
                        # Replace with QLoRA linear layer
                        parent_name = '.'.join(name.split('.')[:-1])
                        child_name = name.split('.')[-1]
                        
                        if parent_name:
                            parent = self.base_model.get_submodule(parent_name)
                            setattr(parent, child_name, QLoRALinear(
                                module.in_features, module.out_features, **kwargs
                            ))
                        else:
                            setattr(self.base_model, child_name, QLoRALinear(
                                module.in_features, module.out_features, **kwargs
                            ))
            
            def forward(self, *args, **kwargs):
                return self.base_model(*args, **kwargs)
            
            def get_trainable_parameters(self):
                """Get trainable QLoRA parameters."""
                trainable_params = []
                for module in self.base_model.modules():
                    if isinstance(module, QLoRALinear):
                        trainable_params.extend(module.get_adapter_parameters())
                return trainable_params
        
        return QLoRAModelWrapper(model)
    
    def get_trainable_parameters(self) -> List[nn.Parameter]:
        """Get trainable parameters for the selected technique."""
        return self.adapted_model.get_trainable_parameters()
    
    def get_parameter_count(self) -> Dict[str, int]:
        """Get parameter counts for analysis."""
        total_params = sum(p.numel() for p in self.base_model.parameters())
        trainable_params = sum(p.numel() for p in self.get_trainable_parameters())
        
        return {
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'frozen_parameters': total_params - trainable_params,
            'trainable_ratio': trainable_params / total_params
        }
    
    def merge_adapters(self):
        """Merge adapter weights into base model (for LoRA)."""
        if hasattr(self.adapted_model, 'merge_lora_weights'):
            self.adapted_model.merge_lora_weights()
    
    def save_adapters(self, path: str):
        """Save adapter weights."""
        torch.save(self.get_trainable_parameters(), path)
    
    def load_adapters(self, path: str):
        """Load adapter weights."""
        adapter_weights = torch.load(path)
        # Implementation depends on the specific technique

# ============================================================================
# TRAINING UTILITIES
# ============================================================================

class AdapterTrainer:
    """Trainer for adapter-based fine-tuning."""
    
    def __init__(self, model: nn.Module, learning_rate: float = 1e-4,
                 weight_decay: float = 0.01, warmup_steps: int = 100):
        self.model = model
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.warmup_steps = warmup_steps
        
        # Get trainable parameters
        self.trainable_params = self.model.get_trainable_parameters()
        
        # Setup optimizer
        self.optimizer = torch.optim.AdamW(
            self.trainable_params,
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        # Setup scheduler
        self.scheduler = torch.optim.lr_scheduler.LinearLR(
            self.optimizer,
            start_factor=0.1,
            total_iters=warmup_steps
        )
    
    def train_step(self, batch: Dict[str, torch.Tensor], loss_fn: Callable) -> float:
        """Single training step."""
        self.optimizer.zero_grad()
        
        # Forward pass
        outputs = self.model(**batch)
        loss = loss_fn(outputs, batch)
        
        # Backward pass
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.trainable_params, max_norm=1.0)
        
        # Optimizer step
        self.optimizer.step()
        self.scheduler.step()
        
        return loss.item()
    
    def get_learning_rate(self) -> float:
        """Get current learning rate."""
        return self.optimizer.param_groups[0]['lr']

# ============================================================================
# DEMO AND TESTING
# ============================================================================

def test_fine_tuning_techniques():
    """Test different fine-tuning techniques."""
    
    print("Testing Efficient Fine-Tuning Techniques")
    print("=" * 60)
    
    # Create a base model with proper module names for LoRA
    class TestBaseModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.q_proj = nn.Linear(100, 200)
            self.v_proj = nn.Linear(100, 200)
            self.k_proj = nn.Linear(100, 200)
            self.o_proj = nn.Linear(200, 100)
            self.classifier = nn.Linear(100, 10)
        
        def forward(self, x):
            q = self.q_proj(x)
            v = self.v_proj(x)
            k = self.k_proj(x)
            o = self.o_proj(q + v + k)
            return self.classifier(o)
    
    base_model = TestBaseModel()
    
    print(f"Base model parameters: {sum(p.numel() for p in base_model.parameters()):,}")
    
    # Test LoRA
    print("\n1. Testing LoRA:")
    lora_manager = FineTuningManager(base_model, technique='lora', rank=16, alpha=16.0)
    lora_params = lora_manager.get_parameter_count()
    print(f"   Trainable parameters: {lora_params['trainable_parameters']:,}")
    print(f"   Trainable ratio: {lora_params['trainable_ratio']:.2%}")
    
    # Test P-tuning
    print("\n2. Testing P-tuning:")
    p_tuning_manager = FineTuningManager(base_model, technique='p_tuning', 
                                       num_prompts=5, prompt_length=10, hidden_size=100)
    p_tuning_params = p_tuning_manager.get_parameter_count()
    print(f"   Trainable parameters: {p_tuning_params['trainable_parameters']:,}")
    print(f"   Trainable ratio: {p_tuning_params['trainable_ratio']:.2%}")
    
    # Test AdaLoRA
    print("\n3. Testing AdaLoRA:")
    adalora_manager = FineTuningManager(base_model, technique='adalora', 
                                      max_rank=32, alpha=16.0)
    adalora_params = adalora_manager.get_parameter_count()
    print(f"   Trainable parameters: {adalora_params['trainable_parameters']:,}")
    print(f"   Trainable ratio: {adalora_params['trainable_ratio']:.2%}")
    
    # Test QLoRA
    print("\n4. Testing QLoRA:")
    qlora_manager = FineTuningManager(base_model, technique='qlora', 
                                    rank=16, alpha=16.0, bits=4)
    qlora_params = qlora_manager.get_parameter_count()
    print(f"   Trainable parameters: {qlora_params['trainable_parameters']:,}")
    print(f"   Trainable ratio: {qlora_params['trainable_ratio']:.2%}")
    
    # Test training
    print("\n5. Testing Adapter Training:")
    try:
        # Create dummy data
        dummy_input = torch.randn(32, 100)
        dummy_target = torch.randint(0, 10, (32,))
        
        # Create trainer
        trainer = AdapterTrainer(lora_manager.adapted_model, learning_rate=1e-4)
        
        # Define loss function
        def dummy_loss(outputs, batch):
            return F.cross_entropy(outputs, batch['target'])
        
        # Training step
        batch = {'input': dummy_input, 'target': dummy_target}
        
        # Create a simple test model for training
        class TestModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.layers = nn.Sequential(
                    nn.Linear(100, 50),
                    nn.ReLU(),
                    nn.Linear(50, 10)
                )
            
            def forward(self, **kwargs):
                input_tensor = kwargs.get('input')
                if input_tensor is None:
                    raise ValueError("No input provided")
                return self.layers(input_tensor)
            
            def get_trainable_parameters(self):
                return list(self.parameters())
        
        test_model = TestModel()
        
        # Create trainer with test model
        test_trainer = AdapterTrainer(test_model, learning_rate=1e-4)
        
        try:
            # Create a simple batch
            simple_batch = {'input': dummy_input, 'target': dummy_target}
            
            # Define simple loss function
            def simple_loss(outputs, batch):
                return F.cross_entropy(outputs, batch['target'])
            
            # Training step
            loss = test_trainer.train_step(simple_batch, simple_loss)
            print(f"   ✓ Training step successful. Loss: {loss:.4f}")
            print(f"   ✓ Learning rate: {test_trainer.get_learning_rate():.6f}")
        except Exception as e:
            print(f"   ✗ Training failed: {e}")
        
    except Exception as e:
        print(f"   ✗ Training failed: {e}")
    
    print("\n" + "=" * 60)
    print("All fine-tuning technique tests completed!")

if __name__ == "__main__":
    test_fine_tuning_techniques()
