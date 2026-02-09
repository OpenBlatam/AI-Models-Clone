from __future__ import annotations

from typing import Literal, Optional

import torch
import torch.nn.functional as F
from torch import nn


def init_module_weights(
    module: nn.Module,
    method: Literal[
        "kaiming_normal",
        "kaiming_uniform",
        "xavier_normal",
        "xavier_uniform",
        "orthogonal",
    ] = "kaiming_normal",
    nonlinearity: str = "relu",
    gain: float = 1.0,
) -> None:
    if isinstance(module, (nn.Conv1d, nn.Conv2d, nn.Conv3d, nn.Linear)):
        if method == "kaiming_normal":
            nn.init.kaiming_normal_(module.weight, nonlinearity=nonlinearity)
        elif method == "kaiming_uniform":
            nn.init.kaiming_uniform_(module.weight, nonlinearity=nonlinearity)
        elif method == "xavier_normal":
            nn.init.xavier_normal_(module.weight, gain=nn.init.calculate_gain(nonlinearity))
        elif method == "xavier_uniform":
            nn.init.xavier_uniform_(module.weight, gain=nn.init.calculate_gain(nonlinearity))
        elif method == "orthogonal":
            nn.init.orthogonal_(module.weight, gain=gain)
        else:
            raise ValueError(f"Unknown init method: {method}")
        if module.bias is not None:
            nn.init.zeros_(module.bias)
    elif isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d, nn.LayerNorm, nn.GroupNorm)):
        if hasattr(module, "weight") and module.weight is not None:
            nn.init.ones_(module.weight)
        if hasattr(module, "bias") and module.bias is not None:
            nn.init.zeros_(module.bias)


class WeightStandardizedConv2d(nn.Conv2d):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int | tuple[int, int], stride: int | tuple[int, int] = 1, padding: int | tuple[int, int] = 0, dilation: int | tuple[int, int] = 1, groups: int = 1, bias: bool = True, eps: float = 1e-5):
        super().__init__(
            in_channels,
            out_channels,
            kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
            groups=groups,
            bias=bias,
            padding_mode="zeros",
        )
        self.eps = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        weight = self.weight
        mean = weight.mean(dim=(1, 2, 3), keepdim=True)
        var = weight.var(dim=(1, 2, 3), keepdim=True, unbiased=False)
        weight = (weight - mean) / torch.sqrt(var + self.eps)
        return F.conv2d(
            x,
            weight,
            self.bias,
            self.stride,
            self.padding,
            self.dilation,
            self.groups,
        )


def apply_spectral_norm(module: nn.Module) -> nn.Module:
    for child in module.modules():
        if isinstance(child, (nn.Conv1d, nn.Conv2d, nn.Conv3d, nn.Linear)):
            try:
                nn.utils.spectral_norm(child)
            except Exception:
                pass
    return module


class ConvWSGNAct(nn.Module):
    def __init__(self, in_ch: int, out_ch: int, k: int = 3, s: int = 1, g: int = 8, dropout: float = 0.0):
        super().__init__()
        pad = k // 2
        self.conv = WeightStandardizedConv2d(in_ch, out_ch, k, stride=s, padding=pad, bias=False)
        self.gn = nn.GroupNorm(num_groups=min(g, out_ch), num_channels=out_ch)
        self.drop = nn.Dropout2d(p=dropout) if dropout > 0 else nn.Identity()
        self.act = nn.GELU()
        self.apply(lambda m: init_module_weights(m, method="kaiming_normal", nonlinearity="relu"))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv(x)
        x = self.gn(x)
        x = self.drop(x)
        x = self.act(x)
        return x


class ResidualWSGNBlock(nn.Module):
    def __init__(self, channels: int, groups: int = 8, dropout: float = 0.0):
        super().__init__()
        self.conv1 = ConvWSGNAct(channels, channels, 3, 1, groups, dropout)
        self.conv2 = ConvWSGNAct(channels, channels, 3, 1, groups, dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv2(self.conv1(x)) + x


class PreNormMLP(nn.Module):
    def __init__(self, dim: int, hidden_dim: int, dropout: float = 0.0):
        super().__init__()
        self.norm = nn.LayerNorm(dim)
        self.fc1 = nn.Linear(dim, hidden_dim)
        self.act = nn.GELU()
        self.drop1 = nn.Dropout(dropout) if dropout > 0 else nn.Identity()
        self.fc2 = nn.Linear(hidden_dim, dim)
        self.drop2 = nn.Dropout(dropout) if dropout > 0 else nn.Identity()
        self.apply(lambda m: init_module_weights(m, method="kaiming_normal", nonlinearity="relu"))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.norm(x)
        y = self.fc1(y)
        y = self.act(y)
        y = self.drop1(y)
        y = self.fc2(y)
        y = self.drop2(y)
        return x + y


class DemoCNN(nn.Module):
    def __init__(self, in_ch: int = 3, width: int = 64, depth: int = 4, num_classes: int = 10):
        super().__init__()
        stem = [ConvWSGNAct(in_ch, width, 3)]
        blocks = [ResidualWSGNBlock(width) for _ in range(depth)]
        head = [nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.LayerNorm(width), nn.Linear(width, num_classes)]
        self.net = nn.Sequential(*stem, *blocks, *head)
        apply_spectral_norm(self.net)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)



