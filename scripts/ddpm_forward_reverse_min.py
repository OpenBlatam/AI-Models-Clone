from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.utils import save_image


def get_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def sinusoidal_embedding(timesteps: torch.Tensor, dim: int) -> torch.Tensor:
    half = dim // 2
    freqs = torch.exp(
        -math.log(10000) * torch.arange(0, half, dtype=torch.float32, device=timesteps.device) / max(half, 1)
    )
    args = timesteps.float().unsqueeze(1) * freqs.unsqueeze(0)
    emb = torch.cat([torch.sin(args), torch.cos(args)], dim=1)
    if dim % 2 == 1:
        emb = F.pad(emb, (0, 1))
    return emb


class TinyDenoiser(nn.Module):
    def __init__(self, channels: int = 64, time_dim: int = 128) -> None:
        super().__init__()
        self.time_mlp = nn.Sequential(
            nn.Linear(time_dim, channels), nn.SiLU(), nn.Linear(channels, channels)
        )
        self.net = nn.Sequential(
            nn.Conv2d(1, channels, 3, padding=1),
            nn.GroupNorm(8, channels),
            nn.SiLU(),
            nn.Conv2d(channels, channels, 3, padding=1),
            nn.GroupNorm(8, channels),
            nn.SiLU(),
            nn.Conv2d(channels, 1, 3, padding=1),
        )

    def forward(self, x: torch.Tensor, t_emb: torch.Tensor) -> torch.Tensor:  # predicts noise
        temb = self.time_mlp(t_emb).view(t_emb.shape[0], -1, 1, 1)
        return self.net(x + temb)


def make_beta_schedule(T: int, beta_start: float = 1e-4, beta_end: float = 0.02) -> torch.Tensor:
    return torch.linspace(beta_start, beta_end, T)


@torch.no_grad()
def p_sample_loop(
    model: nn.Module,
    shape: Tuple[int, int, int, int],
    betas: torch.Tensor,
    alphas: torch.Tensor,
    alpha_bars: torch.Tensor,
    device: str,
) -> torch.Tensor:
    x = torch.randn(shape, device=device)
    T = betas.shape[0]
    time_dim = 128
    for i in reversed(range(T)):
        t = torch.full((shape[0],), i, device=device, dtype=torch.long)
        t_emb = sinusoidal_embedding(t, time_dim)
        eps = model(x, t_emb)
        a_t = alphas[i]
        ab_t = alpha_bars[i]
        b_t = betas[i]
        mean = (1.0 / torch.sqrt(a_t)) * (x - (b_t / torch.sqrt(1 - ab_t)) * eps)
        if i > 0:
            noise = torch.randn_like(x)
            x = mean + torch.sqrt(b_t) * noise
        else:
            x = mean
    return x.clamp(-1, 1)


def train_tiny_ddpm() -> None:
    device = get_device()
    torch.manual_seed(int(os.getenv("SEED", "0")))

    # Hyper-params
    T = int(os.getenv("T", "200"))
    steps = int(os.getenv("STEPS", "500"))
    bs = int(os.getenv("BS", "32"))
    lr = float(os.getenv("LR", "2e-4"))
    img_size = int(os.getenv("SIZE", "32"))

    # Schedule
    betas = make_beta_schedule(T).to(device)
    alphas = 1.0 - betas
    alpha_bars = torch.cumprod(alphas, dim=0)

    # Model
    model = TinyDenoiser().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)

    # Tiny synthetic dataset (random "images")
    for step in range(steps):
        x0 = torch.randn(bs, 1, img_size, img_size, device=device).clamp(-1, 1)
        t = torch.randint(0, T, (bs,), device=device)
        a_bar_t = alpha_bars[t].view(bs, 1, 1, 1)
        noise = torch.randn_like(x0)
        xt = torch.sqrt(a_bar_t) * x0 + torch.sqrt(1 - a_bar_t) * noise

        t_emb = sinusoidal_embedding(t, 128)
        pred_noise = model(xt, t_emb)
        loss = F.mse_loss(pred_noise, noise)

        opt.zero_grad(set_to_none=True)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()

    # Sample
    with torch.no_grad():
        x_samples = p_sample_loop(
            model=model,
            shape=(4, 1, img_size, img_size),
            betas=betas,
            alphas=alphas,
            alpha_bars=alpha_bars,
            device=device,
        )
    out_dir = Path("outputs/ddpm")
    out_dir.mkdir(parents=True, exist_ok=True)
    save_image((x_samples + 1) / 2, out_dir / "samples.png", nrow=2)


if __name__ == "__main__":
    train_tiny_ddpm()



