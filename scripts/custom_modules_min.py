from __future__ import annotations

import torch
import torch.nn as nn


class WeightStandardizedConv2d(nn.Conv2d):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        weight = self.weight
        mean = weight.mean(dim=(1, 2, 3), keepdim=True)
        var = weight.var(dim=(1, 2, 3), keepdim=True, unbiased=False)
        w = (weight - mean) / torch.sqrt(var + 1e-5)
        return nn.functional.conv2d(x, w, self.bias, self.stride, self.padding, self.dilation, self.groups)


class ResidualBlock(nn.Module):
    def __init__(self, channels: int) -> None:
        super().__init__()
        self.conv1 = WeightStandardizedConv2d(channels, channels, 3, padding=1)
        self.gn1 = nn.GroupNorm(8, channels)
        self.conv2 = WeightStandardizedConv2d(channels, channels, 3, padding=1)
        self.gn2 = nn.GroupNorm(8, channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = torch.relu(self.gn1(self.conv1(x)))
        h = self.gn2(self.conv2(h))
        return torch.relu(h + x)


class TinyUNet(nn.Module):
    def __init__(self, in_ch: int = 3, base: int = 32, num_classes: int = 10) -> None:
        super().__init__()
        self.enc1 = nn.Sequential(nn.Conv2d(in_ch, base, 3, padding=1), ResidualBlock(base))
        self.pool1 = nn.MaxPool2d(2)
        self.enc2 = nn.Sequential(nn.Conv2d(base, base * 2, 3, padding=1), ResidualBlock(base * 2))
        self.pool2 = nn.MaxPool2d(2)
        self.bottleneck = ResidualBlock(base * 2)
        self.up1 = nn.ConvTranspose2d(base * 2, base, 2, stride=2)
        self.dec1 = ResidualBlock(base)
        self.out = nn.Conv2d(base, num_classes, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool1(e1))
        b = self.bottleneck(self.pool2(e2))
        d1 = self.up1(b)
        d1 = d1 + e1[:, : d1.size(1), : d1.size(2), : d1.size(3)]  # naive skip align
        d1 = self.dec1(d1)
        return self.out(d1)


if __name__ == "__main__":
    x = torch.randn(2, 3, 64, 64)
    model = TinyUNet()
    y = model(x)
    print(y.shape)



