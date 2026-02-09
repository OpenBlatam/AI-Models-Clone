from __future__ import annotations

from typing import List, Optional

import torch
from torch import nn


def kaiming_init(module: nn.Module) -> None:
    if isinstance(module, (nn.Conv1d, nn.Conv2d, nn.Linear)):
        nn.init.kaiming_normal_(module.weight, nonlinearity="relu")
        if module.bias is not None:
            nn.init.zeros_(module.bias)
    elif isinstance(module, (nn.LayerNorm, nn.BatchNorm1d, nn.BatchNorm2d)):
        if hasattr(module, "weight") and module.weight is not None:
            nn.init.ones_(module.weight)
        if hasattr(module, "bias") and module.bias is not None:
            nn.init.zeros_(module.bias)


class MLPBlock(nn.Module):
    def __init__(self, in_dim: int, hidden_dim: int, out_dim: Optional[int] = None, dropout: float = 0.0) -> None:
        super().__init__()
        out_dim = out_dim if out_dim is not None else in_dim
        self.fc1 = nn.Linear(in_dim, hidden_dim)
        self.act = nn.GELU()
        self.drop1 = nn.Dropout(p=dropout) if dropout > 0 else nn.Identity()
        self.fc2 = nn.Linear(hidden_dim, out_dim)
        self.drop2 = nn.Dropout(p=dropout) if dropout > 0 else nn.Identity()
        self.apply(kaiming_init)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.act(x)
        x = self.drop1(x)
        x = self.fc2(x)
        x = self.drop2(x)
        return x


class ResidualMLP(nn.Module):
    def __init__(self, dim: int, hidden_dim: int, dropout: float = 0.0) -> None:
        super().__init__()
        self.norm = nn.LayerNorm(dim)
        self.mlp = MLPBlock(dim, hidden_dim, dim, dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.mlp(self.norm(x))


class ConvBNAct(nn.Module):
    def __init__(self, in_ch: int, out_ch: int, kernel_size: int = 3, stride: int = 1, padding: Optional[int] = None) -> None:
        super().__init__()
        pad = kernel_size // 2 if padding is None else padding
        self.conv = nn.Conv2d(in_ch, out_ch, kernel_size, stride=stride, padding=pad, bias=False)
        self.bn = nn.BatchNorm2d(out_ch)
        self.act = nn.GELU()
        self.apply(kaiming_init)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.act(self.bn(self.conv(x)))


class DepthwiseSeparableConv(nn.Module):
    def __init__(self, in_ch: int, out_ch: int, kernel_size: int = 3, stride: int = 1) -> None:
        super().__init__()
        pad = kernel_size // 2
        self.depthwise = nn.Conv2d(in_ch, in_ch, kernel_size, stride=stride, padding=pad, groups=in_ch, bias=False)
        self.pointwise = nn.Conv2d(in_ch, out_ch, kernel_size=1, bias=False)
        self.bn = nn.BatchNorm2d(out_ch)
        self.act = nn.GELU()
        self.apply(kaiming_init)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.depthwise(x)
        x = self.pointwise(x)
        x = self.bn(x)
        return self.act(x)


class SqueezeExcitation(nn.Module):
    def __init__(self, channels: int, reduction: int = 4) -> None:
        super().__init__()
        hidden = max(1, channels // reduction)
        self.avg = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Conv2d(channels, hidden, 1),
            nn.GELU(),
            nn.Conv2d(hidden, channels, 1),
            nn.Sigmoid(),
        )
        self.apply(kaiming_init)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        scale = self.fc(self.avg(x))
        return x * scale


class ResidualCNNBlock(nn.Module):
    def __init__(self, channels: int, use_se: bool = True) -> None:
        super().__init__()
        self.conv1 = ConvBNAct(channels, channels, 3)
        self.conv2 = ConvBNAct(channels, channels, 3)
        self.se = SqueezeExcitation(channels) if use_se else nn.Identity()
        self.act = nn.GELU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.conv1(x)
        out = self.conv2(out)
        out = self.se(out)
        return self.act(out + x)


class SelfAttention(nn.Module):
    def __init__(self, dim: int, num_heads: int = 8, dropout: float = 0.0, causal: bool = False) -> None:
        super().__init__()
        assert dim % num_heads == 0, "dim must be divisible by num_heads"
        self.dim = dim
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        self.scale = self.head_dim ** -0.5
        self.causal = causal
        self.qkv = nn.Linear(dim, dim * 3, bias=False)
        self.proj = nn.Linear(dim, dim)
        self.drop = nn.Dropout(dropout) if dropout > 0 else nn.Identity()
        self.apply(kaiming_init)

    def forward(self, x: torch.Tensor, key_padding_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        B, T, C = x.shape
        qkv = self.qkv(x).reshape(B, T, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]  # [B, H, T, D]
        attn = (q @ k.transpose(-2, -1)) * self.scale
        if key_padding_mask is not None:
            # mask shape [B, T] where True means pad
            mask = key_padding_mask[:, None, None, :].to(dtype=attn.dtype) * (-1e9)
            attn = attn + mask
        if self.causal:
            causal_mask = torch.triu(torch.ones(T, T, device=x.device, dtype=torch.bool), diagonal=1)
            attn = attn.masked_fill(causal_mask, float("-inf"))
        attn = attn.softmax(dim=-1)
        attn = self.drop(attn)
        out = attn @ v  # [B, H, T, D]
        out = out.transpose(1, 2).reshape(B, T, C)
        out = self.proj(out)
        return out


class TransformerEncoderLayer(nn.Module):
    def __init__(self, dim: int, num_heads: int = 8, mlp_ratio: float = 4.0, dropout: float = 0.0, causal: bool = False) -> None:
        super().__init__()
        hidden_dim = int(dim * mlp_ratio)
        self.norm1 = nn.LayerNorm(dim)
        self.attn = SelfAttention(dim, num_heads=num_heads, dropout=dropout, causal=causal)
        self.norm2 = nn.LayerNorm(dim)
        self.mlp = MLPBlock(dim, hidden_dim, dim, dropout)

    def forward(self, x: torch.Tensor, key_padding_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        x = x + self.attn(self.norm1(x), key_padding_mask=key_padding_mask)
        x = x + self.mlp(self.norm2(x))
        return x


__all__ = [
    "kaiming_init",
    "MLPBlock",
    "ResidualMLP",
    "ConvBNAct",
    "DepthwiseSeparableConv",
    "SqueezeExcitation",
    "ResidualCNNBlock",
    "SelfAttention",
    "TransformerEncoderLayer",
]



