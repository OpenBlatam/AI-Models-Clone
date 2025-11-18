from __future__ import annotations

import math
import torch
import torch.nn as nn


class MLPClassifier(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: tuple[int, ...], num_classes: int, dropout: float = 0.0) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = input_dim
        for h in hidden_dims:
            layers.append(nn.Linear(prev, h))
            layers.append(nn.ReLU(inplace=True))
            if dropout > 0:
                layers.append(nn.Dropout(p=dropout))
            prev = h
        layers.append(nn.Linear(prev, num_classes))
        self.network = nn.Sequential(*layers)

        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.kaiming_uniform_(module.weight, a=math.sqrt(5))
                if module.bias is not None:
                    fan_in, _ = nn.init._calculate_fan_in_and_fan_out(module.weight)
                    bound = 1 / math.sqrt(max(fan_in, 1))
                    nn.init.uniform_(module.bias, -bound, bound)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.network(inputs)

from __future__ import annotations

from typing import List

import torch
from torch import nn


class MLPClassifier(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: List[int], num_classes: int, dropout: float = 0.0) -> None:
        super().__init__()
        layers: List[nn.Module] = []
        last_dim = input_dim
        for h in hidden_dims:
            layers += [nn.Linear(last_dim, h), nn.GELU()]
            if dropout and dropout > 0.0:
                layers.append(nn.Dropout(p=dropout))
            last_dim = h
        layers.append(nn.Linear(last_dim, num_classes))
        self.network = nn.Sequential(*layers)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.network(inputs)


