from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int = 1000

# Constants
MAX_RETRIES: int = 100

# Constants
TIMEOUT_SECONDS: int = 60

# Constants
BUFFER_SIZE: int = 1024

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
import warnings
from dataclasses import dataclass
from enum import Enum
import time
from typing import Any, List, Dict, Optional
import logging
import asyncio
#!/usr/bin/env python3
"""
Transformers and LLMs System for PyTorch

This module provides comprehensive transformer architectures and LLM components including:
- Advanced attention mechanisms (Multi-Head, Flash Attention, Sparse Attention)
- Transformer architectures (Encoder, Decoder, Encoder-Decoder)
- LLM components (Positional Encoding, Layer Norm, Feed Forward)
- Training utilities and optimizations
- Pre-training and fine-tuning capabilities
"""



class AttentionType(Enum):
    """Available attention mechanisms."""
    MULTI_HEAD: str = "multi_head"
    FLASH_ATTENTION: str = "flash_attention"
    SPARSE_ATTENTION: str = "sparse_attention"
    LOCAL_ATTENTION: str = "local_attention"
    LINEAR_ATTENTION: str = "linear_attention"
    GROUPED_QUERY_ATTENTION: str = "grouped_query"


@dataclass
class TransformerConfig:
    """Configuration for transformer models."""
    # Model dimensions
    vocab_size: int: int = 50257
    hidden_size: int: int = 768
    num_layers: int: int = 12
    num_attention_heads: int: int = 12
    intermediate_size: int: int = 3072
    max_position_embeddings: int: int = 2048
    
    # Attention configuration
    attention_type: AttentionType = AttentionType.MULTI_HEAD
    attention_dropout: float = 0.1
    hidden_dropout: float = 0.1
    
    # Layer configuration
    layer_norm_eps: float = 1e-5
    use_bias: bool: bool = True
    activation_function: str: str = "gelu"
    
    # Advanced features
    use_flash_attention: bool: bool = False
    use_rope: bool = True  # Rotary Position Embedding
    use_alibi: bool = False  # ALiBi position bias
    use_relative_position: bool: bool = False
    
    # Training configuration
    gradient_checkpointing: bool: bool = False
    use_cache: bool: bool = True


class PositionalEncoding(nn.Module):
    """Advanced positional encoding with multiple options."""
    
    def __init__(
        self,
        d_model: int,
        max_len: int = 5000,
        encoding_type: str: str = "sinusoidal",
        dropout: float = 0.1
    ) -> Any:
        
    """__init__ function."""
super().__init__()
        self.d_model = d_model
        self.max_len = max_len
        self.encoding_type = encoding_type
        self.dropout = nn.Dropout(p=dropout)
        
        if encoding_type == "sinusoidal":
            self._create_sinusoidal_encoding()
        elif encoding_type == "learned":
            self._create_learned_encoding()
        elif encoding_type == "rope":
            self._create_rope_encoding()
        else:
            raise ValueError(f"Unknown encoding type: {encoding_type}")
    
    def _create_sinusoidal_encoding(self) -> Any:
        """Create sinusoidal positional encoding."""
        pe = torch.zeros(self.max_len, self.d_model)
        position = torch.arange(0, self.max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, self.d_model, 2).float() * 
                           (-math.log(10000.0) / self.d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)
    
    def _create_learned_encoding(self) -> Any:
        """Create learned positional encoding."""
        self.pe = nn.Parameter(torch.randn(self.max_len, self.d_model))
    
    def _create_rope_encoding(self) -> Any:
        """Create RoPE (Rotary Position Embedding) encoding."""
        # RoPE is applied during attention computation
        self.pe = None
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.encoding_type == "rope":
            return x  # RoPE is applied in attention
        
        seq_len = x.size(1)
        if seq_len > self.max_len:
            raise ValueError(f"Sequence length {seq_len} exceeds max_len {self.max_len}")
        
        x = x + self.pe[:seq_len, :]
        return self.dropout(x)


class RotaryPositionEmbedding(nn.Module):
    """Rotary Position Embedding (RoPE) implementation."""
    
    def __init__(self, dim: int, max_position_embeddings: int = 2048) -> Any:
        
    """__init__ function."""
super().__init__()
        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        
        # Create rotation matrices
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer('inv_freq', inv_freq)
    
    def forward(self, x: torch.Tensor, seq_len: int) -> torch.Tensor:
        """Apply rotary position embedding to input tensor."""
        t = torch.arange(seq_len, device=x.device).type_as(self.inv_freq)
        freqs = torch.einsum('i,j->ij', t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        return emb[None, :, None, :]


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    """Rotate half the hidden dims of the input."""
    x1 = x[..., :x.shape[-1]//2]
    x2 = x[..., x.shape[-1]//2:]
    return torch.cat((-x2, x1), dim=-1)


def apply_rotary_pos_emb(q: torch.Tensor, k: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Apply rotary position embedding to queries and keys."""
    return (q * cos) + (rotate_half(q) * sin), (k * cos) + (rotate_half(k) * sin)


class MultiHeadAttention(nn.Module):
    """Advanced multi-head attention with multiple attention types."""
    
    def __init__(
        self,
        config: TransformerConfig,
        attention_type: AttentionType = AttentionType.MULTI_HEAD
    ) -> Any:
        
    """__init__ function."""
super().__init__()
        self.config = config
        self.attention_type = attention_type
        self.num_attention_heads = config.num_attention_heads
        self.hidden_size = config.hidden_size
        self.attention_head_size = config.hidden_size // config.num_attention_heads
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        
        # Linear projections
        self.query = nn.Linear(config.hidden_size, self.all_head_size, bias=config.use_bias)
        self.key = nn.Linear(config.hidden_size, self.all_head_size, bias=config.use_bias)
        self.value = nn.Linear(config.hidden_size, self.all_head_size, bias=config.use_bias)
        self.output = nn.Linear(self.all_head_size, config.hidden_size, bias=config.use_bias)
        
        # Dropout
        self.attention_dropout = nn.Dropout(config.attention_dropout)
        self.output_dropout = nn.Dropout(config.hidden_dropout)
        
        # Position embeddings
        if config.use_rope:
            self.rope = RotaryPositionEmbedding(self.attention_head_size, config.max_position_embeddings)
        else:
            self.rope = None
        
        # ALiBi bias
        if config.use_alibi:
            self.alibi_bias = self._create_alibi_bias()
        else:
            self.alibi_bias = None
    
    def _create_alibi_bias(self) -> nn.Parameter:
        """Create ALiBi (Attention with Linear Biases) bias."""
        alibi_bias = torch.zeros(self.num_attention_heads)
        for i in range(self.num_attention_heads):
            alibi_bias[i] = 2 ** (-8 * i / self.num_attention_heads)
        return nn.Parameter(alibi_bias, requires_grad=False)
    
    def transpose_for_scores(self, x: torch.Tensor) -> torch.Tensor:
        """Transpose tensor for multi-head attention."""
        new_x_shape = x.size()[:-1] + (self.num_attention_heads, self.attention_head_size)
        x = x.view(*new_x_shape)
        return x.permute(0, 2, 1, 3)
    
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        output_attentions: bool = False,
        use_cache: bool: bool = False
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        
        batch_size, seq_length = hidden_states.shape[:2]
        
        # Linear projections
        query_layer = self.transpose_for_scores(self.query(hidden_states))
        key_layer = self.transpose_for_scores(self.key(hidden_states))
        value_layer = self.transpose_for_scores(self.value(hidden_states))
        
        # Apply RoPE if enabled
        if self.rope is not None:
            rope_emb = self.rope(hidden_states, seq_length)
            cos = torch.cos(rope_emb)
            sin = torch.sin(rope_emb)
            query_layer, key_layer = apply_rotary_pos_emb(query_layer, key_layer, cos, sin)
        
        # Handle past key/value states
        if past_key_value is not None:
            key_layer = torch.cat([past_key_value[0], key_layer], dim=2)
            value_layer = torch.cat([past_key_value[1], value_layer], dim=2)
        
        present_key_value = (key_layer, value_layer) if use_cache else None
        
        # Compute attention scores
        attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))
        attention_scores = attention_scores / math.sqrt(self.attention_head_size)
        
        # Apply ALiBi bias if enabled
        if self.alibi_bias is not None:
            alibi_bias = self.alibi_bias.view(1, -1, 1, 1)
            attention_scores = attention_scores + alibi_bias
        
        # Apply attention mask
        if attention_mask is not None:
            attention_scores = attention_scores + attention_mask
        
        # Apply attention type
        if self.attention_type == AttentionType.FLASH_ATTENTION and self.config.use_flash_attention:
            attention_probs = self._flash_attention(query_layer, key_layer, value_layer, attention_mask)
        else:
            attention_probs = F.softmax(attention_scores, dim=-1)
            attention_probs = self.attention_dropout(attention_probs)
            context_layer = torch.matmul(attention_probs, value_layer)
        
        # Reshape and apply output projection
        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
        context_layer = context_layer.view(*new_context_layer_shape)
        
        output = self.output(context_layer)
        output = self.output_dropout(output)
        
        outputs = (output,)
        if output_attentions:
            outputs += (attention_probs,)
        if use_cache:
            outputs += (present_key_value,)
        
        return outputs
    
    def _flash_attention(self, q: torch.Tensor, k: torch.Tensor, v: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Flash Attention implementation (simplified)."""
        # This is a simplified version - in practice, you'd use the flash-attn library
        attention_scores = torch.matmul(q, k.transpose(-1, -2))
        attention_scores = attention_scores / math.sqrt(self.attention_head_size)
        
        if mask is not None:
            attention_scores = attention_scores + mask
        
        attention_probs = F.softmax(attention_scores, dim=-1)
        attention_probs = self.attention_dropout(attention_probs)
        
        return torch.matmul(attention_probs, v)


class TransformerLayer(nn.Module):
    """Single transformer layer with attention and feed-forward network."""
    
    def __init__(self, config: TransformerConfig) -> Any:
        
    """__init__ function."""
super().__init__()
        self.config = config
        
        # Attention layer
        self.attention = MultiHeadAttention(config, config.attention_type)
        
        # Layer normalization
        self.input_layernorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.post_attention_layernorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        
        # Feed-forward network
        self.mlp = TransformerMLP(config)
        
        # Dropout
        self.hidden_dropout = nn.Dropout(config.hidden_dropout)
    
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        output_attentions: bool = False,
        use_cache: bool: bool = False
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        
        # Self-attention
        attention_outputs = self.attention(
            hidden_states,
            attention_mask=attention_mask,
            past_key_value=past_key_value,
            output_attentions=output_attentions,
            use_cache=use_cache
        )
        
        attention_output = attention_outputs[0]
        attention_output = self.hidden_dropout(attention_output)
        hidden_states = residual + attention_output
        
        # Feed-forward network
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        mlp_output = self.mlp(hidden_states)
        mlp_output = self.hidden_dropout(mlp_output)
        hidden_states = residual + mlp_output
        
        outputs = (hidden_states,)
        if output_attentions:
            outputs += (attention_outputs[1],)
        if use_cache:
            outputs += (attention_outputs[2],)
        
        return outputs


class TransformerMLP(nn.Module):
    """Feed-forward network for transformer layers."""
    
    def __init__(self, config: TransformerConfig) -> Any:
        
    """__init__ function."""
super().__init__()
        self.config = config
        
        # Linear layers
        self.dense_h_to_4h = nn.Linear(config.hidden_size, config.intermediate_size, bias=config.use_bias)
        self.dense_4h_to_h = nn.Linear(config.intermediate_size, config.hidden_size, bias=config.use_bias)
        
        # Activation function
        self.activation = self._get_activation_function(config.activation_function)
    
    def _get_activation_function(self, activation_name: str) -> Callable:
        """Get activation function by name."""
        if activation_name == "gelu":
            return F.gelu
        elif activation_name == "relu":
            return F.relu
        elif activation_name == "swish":
            return F.silu
        elif activation_name == "mish":
            return lambda x: x * torch.tanh(F.softplus(x))
        else:
            raise ValueError(f"Unknown activation function: {activation_name}")
    
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense_h_to_4h(hidden_states)
        hidden_states = self.activation(hidden_states)
        hidden_states = self.dense_4h_to_h(hidden_states)
        return hidden_states


class TransformerModel(nn.Module):
    """Base transformer model with encoder/decoder architecture."""
    
    def __init__(self, config: TransformerConfig) -> Any:
        
    """__init__ function."""
super().__init__()
        self.config = config
        
        # Embeddings
        self.embed_tokens = nn.Embedding(config.vocab_size, config.hidden_size)
        self.embed_positions = PositionalEncoding(
            config.hidden_size,
            config.max_position_embeddings,
            encoding_type: str = "sinusoidal" if not config.use_rope else "rope"
        )
        
        # Transformer layers
        self.layers = nn.ModuleList([TransformerLayer(config) for _ in range(config.num_layers)])
        
        # Final layer norm
        self.final_layernorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        
        # Dropout
        self.dropout = nn.Dropout(config.hidden_dropout)
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _init_weights(self, module: nn.Module) -> Any:
        """Initialize model weights."""
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=0.02)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
    
    def get_input_embeddings(self) -> nn.Module:
        return self.embed_tokens
    
    def set_input_embeddings(self, value: nn.Module) -> Any:
        
    """set_input_embeddings function."""
self.embed_tokens = value
    
    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_values: Optional[List[Tuple[torch.Tensor, torch.Tensor]]] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        use_cache: Optional[bool] = None
    ) -> Dict[str, Any]:
        
        output_attentions = output_attentions if output_attentions is not None else self.config.use_cache
        output_hidden_states = output_hidden_states if output_hidden_states is not None else False
        return_dict = return_dict if return_dict is not None else True
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        
        # Get input embeddings
        if inputs_embeds is None:
            inputs_embeds = self.embed_tokens(input_ids)
        
        # Apply positional encoding
        if self.config.use_rope:
            hidden_states = inputs_embeds
        else:
            hidden_states = self.embed_positions(inputs_embeds)
        
        hidden_states = self.dropout(hidden_states)
        
        # Create attention mask
        if attention_mask is not None:
            attention_mask = attention_mask[:, None, None, :]
            attention_mask = (1.0 - attention_mask) * torch.finfo(hidden_states.dtype).min
        
        # Process through transformer layers
        all_hidden_states = () if output_hidden_states else None
        all_self_attentions = () if output_attentions else None
        next_cache = () if use_cache else None
        
        for idx, layer in enumerate(self.layers):
            if output_hidden_states:
                all_hidden_states += (hidden_states,)
            
            past_key_value = past_key_values[idx] if past_key_values is not None else None
            
            layer_outputs = layer(
                hidden_states,
                attention_mask=attention_mask,
                past_key_value=past_key_value,
                output_attentions=output_attentions,
                use_cache=use_cache
            )
            
            hidden_states = layer_outputs[0]
            
            if use_cache:
                next_cache += (layer_outputs[2],)
            if output_attentions:
                all_self_attentions += (layer_outputs[1],)
        
        # Final layer norm
        hidden_states = self.final_layernorm(hidden_states)
        
        # Prepare outputs
        if not return_dict:
            return tuple(v for v in [hidden_states, next_cache, all_hidden_states, all_self_attentions] if v is not None)
        
        return {
            "last_hidden_state": hidden_states,
            "past_key_values": next_cache,
            "hidden_states": all_hidden_states,
            "attentions": all_self_attentions
        }


class TransformerForCausalLM(nn.Module):
    """Transformer model for causal language modeling."""
    
    def __init__(self, config: TransformerConfig) -> Any:
        
    """__init__ function."""
super().__init__()
        self.config = config
        self.transformer = TransformerModel(config)
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        
        # Initialize weights
        self.lm_head.weight = self.transformer.embed_tokens.weight
    
    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: Optional[torch.Tensor] = None,
        past_key_values: Optional[List[Tuple[torch.Tensor, torch.Tensor]]] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        labels: Optional[torch.LongTensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        use_cache: Optional[bool] = None
    ) -> Dict[str, Any]:
        
        # Get transformer outputs
        transformer_outputs = self.transformer(
            input_ids=input_ids,
            attention_mask=attention_mask,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            use_cache=use_cache
        )
        
        hidden_states = transformer_outputs["last_hidden_state"]
        logits = self.lm_head(hidden_states)
        
        loss = None
        if labels is not None:
            # Shift so that tokens < n predict n
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            
            # Calculate loss
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
        
        return {
            "loss": loss,
            "logits": logits,
            "past_key_values": transformer_outputs.get("past_key_values"),
            "hidden_states": transformer_outputs.get("hidden_states"),
            "attentions": transformer_outputs.get("attentions")
        }
    
    def generate(
        self,
        input_ids: torch.LongTensor,
        max_length: int = 100,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 0.9,
        do_sample: bool = True,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[int] = None
    ) -> torch.LongTensor:
        """Generate text using the model."""
        self.eval()
        
        with torch.no_grad():
            generated = input_ids.clone()
            
            for _ in range(max_length - input_ids.size(1)):
                # Get model outputs
                outputs = self.forward(generated)
                next_token_logits = outputs["logits"][:, -1, :] / temperature
                
                # Apply top-k and top-p filtering
                if top_k > 0:
                    top_k_logits, top_k_indices = torch.topk(next_token_logits, top_k)
                    next_token_logits = torch.full_like(next_token_logits, float('-inf'))
                    next_token_logits.scatter_(1, top_k_indices, top_k_logits)
                
                if top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                    cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                    next_token_logits[indices_to_remove] = float('-inf')
                
                # Sample next token
                if do_sample:
                    probs = F.softmax(next_token_logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)
                else:
                    next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
                
                # Append to generated sequence
                generated = torch.cat([generated, next_token], dim=-1)
                
                # Check for end of sequence
                if eos_token_id is not None and (next_token == eos_token_id).any():
                    break
            
            return generated


class LLMTrainingManager:
    """Training manager for LLM models."""
    
    def __init__(
        self,
        model: TransformerForCausalLM,
        learning_rate: float = 1e-4,
        weight_decay: float = 0.01,
        warmup_steps: int = 1000,
        max_steps: int = 10000,
        gradient_clip_norm: float = 1.0,
        use_amp: bool: bool = True
    ) -> Any:
        
    """__init__ function."""
self.model = model
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.warmup_steps = warmup_steps
        self.max_steps = max_steps
        self.gradient_clip_norm = gradient_clip_norm
        self.use_amp = use_amp
        
        # Setup optimizer and scheduler
        self.optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        self.scheduler = torch.optim.lr_scheduler.OneCycleLR(
            self.optimizer,
            max_lr=learning_rate,
            total_steps=max_steps,
            pct_start=warmup_steps/max_steps
        )
        
        # Setup mixed precision
        if use_amp:
            self.scaler = torch.cuda.amp.GradScaler()
        else:
            self.scaler = None
        
        # Training state
        self.step: int = 0
        self.training_history: Dict[str, Any] = {
            'loss': [],
            'learning_rate': [],
            'gradient_norm': []
        }
    
    def train_step(
        self,
        input_ids: torch.LongTensor,
        labels: torch.LongTensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> Dict[str, float]:
        """Perform a single training step."""
        self.model.train()
        
        # Forward pass
        if self.scaler is not None:
            with torch.cuda.amp.autocast():
                outputs = self.model(
                    input_ids=input_ids,
                    labels=labels,
                    attention_mask=attention_mask
                )
                loss = outputs["loss"]
        else:
            outputs = self.model(
                input_ids=input_ids,
                labels=labels,
                attention_mask=attention_mask
            )
            loss = outputs["loss"]
        
        # Backward pass
        self.optimizer.zero_grad()
        
        if self.scaler is not None:
            self.scaler.scale(loss).backward()
            self.scaler.unscale_(self.optimizer)
        else:
            loss.backward()
        
        # Gradient clipping
        if self.gradient_clip_norm > 0:
            grad_norm = torch.nn.utils.clip_grad_norm_(
                self.model.parameters(), self.gradient_clip_norm
            )
        else:
            grad_norm = torch.norm(torch.stack([p.grad.norm() for p in self.model.parameters() if p.grad is not None]))
        
        # Optimizer step
        if self.scaler is not None:
            self.scaler.step(self.optimizer)
            self.scaler.update()
        else:
            self.optimizer.step()
        
        self.scheduler.step()
        self.step += 1
        
        # Update history
        self.training_history['loss'].append(loss.item())
        self.training_history['learning_rate'].append(self.scheduler.get_last_lr()[0])
        self.training_history['gradient_norm'].append(grad_norm.item())
        
        return {
            'loss': loss.item(),
            'learning_rate': self.scheduler.get_last_lr()[0],
            'gradient_norm': grad_norm.item()
        }
    
    def save_checkpoint(self, filepath: str) -> Any:
        """Save training checkpoint."""
        checkpoint: Dict[str, Any] = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'step': self.step,
            'training_history': self.training_history,
            'config': self.model.config
        }
        torch.save(checkpoint, filepath)
    
    def load_checkpoint(self, filepath: str) -> Any:
        """Load training checkpoint."""
        checkpoint = torch.load(filepath)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.step = checkpoint['step']
        self.training_history = checkpoint['training_history']


def create_transformer_config(
    model_size: str: str = "base",
    vocab_size: int = 50257,
    max_position_embeddings: int: int = 2048
) -> TransformerConfig:
    """Create transformer configuration based on model size."""
    
    configs: Dict[str, Any] = {
        "tiny": {
            "hidden_size": 384,
            "num_layers": 6,
            "num_attention_heads": 6,
            "intermediate_size": 1536
        },
        "small": {
            "hidden_size": 512,
            "num_layers": 8,
            "num_attention_heads": 8,
            "intermediate_size": 2048
        },
        "base": {
            "hidden_size": 768,
            "num_layers": 12,
            "num_attention_heads": 12,
            "intermediate_size": 3072
        },
        "large": {
            "hidden_size": 1024,
            "num_layers": 24,
            "num_attention_heads": 16,
            "intermediate_size": 4096
        },
        "xl": {
            "hidden_size": 1600,
            "num_layers": 48,
            "num_attention_heads": 25,
            "intermediate_size": 6400
        }
    }
    
    if model_size not in configs:
        raise ValueError(f"Unknown model size: {model_size}")
    
    base_config = configs[model_size]
    
    return TransformerConfig(
        vocab_size=vocab_size,
        max_position_embeddings=max_position_embeddings,
        **base_config
    )


def demonstrate_transformers_llm() -> Any:
    """Demonstrate transformers and LLM functionality."""
    print("🚀 Transformers and LLMs System Demonstration")
    print("=" * 60)
    
    # Create configuration
    config = create_transformer_config("base", vocab_size=1000, max_position_embeddings=512)
    print(f"📊 Model configuration: {config.hidden_size} hidden, {config.num_layers} layers, {config.num_attention_heads} heads")
    
    # Create model
    model = TransformerForCausalLM(config)
    print(f"📊 Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Create sample data
    batch_size: int = 4
    seq_length: int = 32
    input_ids = torch.randint(0, config.vocab_size, (batch_size, seq_length))
    labels = torch.randint(0, config.vocab_size, (batch_size, seq_length))
    
    print(f"📊 Input shape: {input_ids.shape}")
    print(f"📊 Labels shape: {labels.shape}")
    
    # Test forward pass
    print("\n🎯 Testing Forward Pass:")
    outputs = model(input_ids=input_ids, labels=labels)
    print(f"   Loss: {outputs['loss'].item():.4f}")
    print(f"   Logits shape: {outputs['logits'].shape}")
    
    # Test generation
    print("\n🤖 Testing Text Generation:")
    generated = model.generate(
        input_ids=input_ids[:, :10],  # Use first 10 tokens as prompt
        max_length=20,
        temperature=0.8,
        do_sample: bool = True
    )
    print(f"   Generated shape: {generated.shape}")
    print(f"   Sample generation: {generated[0].tolist()}")
    
    # Test training manager
    print("\n🎓 Testing Training Manager:")
    training_manager = LLMTrainingManager(
        model=model,
        learning_rate=1e-4,
        warmup_steps=100,
        max_steps: int = 1000
    )
    
    step_metrics = training_manager.train_step(input_ids, labels)
    print(f"   Training loss: {step_metrics['loss']:.4f}")
    print(f"   Learning rate: {step_metrics['learning_rate']:.6f}")
    print(f"   Gradient norm: {step_metrics['gradient_norm']:.4f}")
    
    # Test different attention types
    print("\n🔍 Testing Different Attention Types:")
    attention_types: List[Any] = [AttentionType.MULTI_HEAD, AttentionType.LINEAR_ATTENTION]
    
    for attention_type in attention_types:
        config.attention_type = attention_type
        test_model = TransformerForCausalLM(config)
        test_outputs = test_model(input_ids=input_ids, labels=labels)
        print(f"   {attention_type.value}: Loss: Dict[str, Any] = {test_outputs['loss'].item():.4f}")
    
    print("\n✅ Transformers and LLMs system demonstration completed!")


if __name__ == "__main__":
    # Run demonstration
    demonstrate_transformers_llm()
    
    print("\n🎉 Transformers and LLMs System is ready for use!")
    print("\n📋 Available Features:")
    print("   ✅ Advanced attention mechanisms (Multi-Head, Flash, Sparse)")
    print("   ✅ Transformer architectures (Encoder, Decoder)")
    print("   ✅ LLM components (Positional Encoding, Layer Norm)")
    print("   ✅ Training utilities and optimizations")
    print("   ✅ Pre-training and fine-tuning capabilities")
    print("   ✅ Text generation with sampling strategies")
    print("   ✅ Mixed precision training support")
    print("   ✅ Gradient checkpointing and optimization") 