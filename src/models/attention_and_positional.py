from __future__ import annotations

import math
from typing import Optional

import torch
import torch.nn as nn


def sinusoidal_positional_encoding(seq_len: int, dim: int, device: torch.device | None = None) -> torch.Tensor:
    position = torch.arange(seq_len, device=device, dtype=torch.float32).unsqueeze(1)
    div_term = torch.exp(torch.arange(0, dim, 2, device=device, dtype=torch.float32) * (-math.log(10000.0) / dim))
    pe = torch.zeros(seq_len, dim, device=device)
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)
    return pe  # [T, D]


def apply_rotary_pos_emb(q: torch.Tensor, k: torch.Tensor, base: int = 10000) -> tuple[torch.Tensor, torch.Tensor]:
    # q,k: [B, H, T, D]
    b, h, t, d = q.shape
    device = q.device
    half = d // 2
    freqs = torch.exp(-math.log(base) * torch.arange(0, half, device=device, dtype=torch.float32) / half)
    pos = torch.arange(t, device=device, dtype=torch.float32)
    angles = pos[:, None] * freqs[None, :]  # [T, half]
    sin = torch.sin(angles)[None, None, :, :]  # [1,1,T,half]
    cos = torch.cos(angles)[None, None, :, :]  # [1,1,T,half]

    def rotate(x: torch.Tensor) -> torch.Tensor:
        x1, x2 = x[..., :half], x[..., half:]
        return torch.cat([x1 * cos - x2 * sin, x1 * sin + x2 * cos], dim=-1)

    return rotate(q), rotate(k)


class MultiHeadSelfAttention(nn.Module):
    def __init__(self, dim: int, num_heads: int = 8, dropout: float = 0.0, causal: bool = False, rotary: bool = False) -> None:
        super().__init__()
        assert dim % num_heads == 0
        self.dim = dim
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        self.scale = self.head_dim ** -0.5
        self.causal = causal
        self.rotary = rotary
        self.qkv = nn.Linear(dim, dim * 3, bias=False)
        self.proj = nn.Linear(dim, dim)
        self.drop = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x: torch.Tensor, key_padding_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        b, t, c = x.shape
        qkv = self.qkv(x).reshape(b, t, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]  # [B, H, T, D]
        if self.rotary:
            q, k = apply_rotary_pos_emb(q, k)
        attn = (q @ k.transpose(-2, -1)) * self.scale
        if key_padding_mask is not None:
            mask = key_padding_mask[:, None, None, :].to(dtype=attn.dtype) * (-1e9)
            attn = attn + mask
        if self.causal:
            causal_mask = torch.triu(torch.ones(t, t, device=x.device, dtype=torch.bool), diagonal=1)
            attn = attn.masked_fill(causal_mask, float("-inf"))
        attn = attn.softmax(dim=-1)
        attn = self.drop(attn)
        out = attn @ v
        out = out.transpose(1, 2).reshape(b, t, c)
        return self.proj(out)


__all__ = [
    "sinusoidal_positional_encoding",
    "apply_rotary_pos_emb",
    "MultiHeadSelfAttention",
]



