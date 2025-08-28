from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.utils import save_image


# --------- Schedules ---------
def linear_beta_schedule(num_timesteps: int, beta_start: float = 1e-4, beta_end: float = 0.02) -> torch.Tensor:
    return torch.linspace(beta_start, beta_end, num_timesteps)


def compute_alphas(betas: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    alphas = 1.0 - betas
    alpha_bars = torch.cumprod(alphas, dim=0)
    sqrt_alpha_bars = torch.sqrt(alpha_bars)
    sqrt_one_minus_alpha_bars = torch.sqrt(1.0 - alpha_bars)
    return sqrt_alpha_bars, sqrt_one_minus_alpha_bars, alphas


# --------- Time Embedding ---------
def sinusoidal_embedding(timesteps: torch.Tensor, dim: int) -> torch.Tensor:
    half = dim // 2
    freqs = torch.exp(-math.log(10000) * torch.arange(0, half, device=timesteps.device) / max(half, 1))
    args = timesteps.float().unsqueeze(1) * freqs.unsqueeze(0)
    emb = torch.cat([torch.sin(args), torch.cos(args)], dim=1)
    if dim % 2 == 1:
        emb = F.pad(emb, (0, 1))
    return emb


# --------- Model ---------
class TinyUNetNoisePredictor(nn.Module):
    def __init__(self, channels: int = 64, time_dim: int = 128) -> None:
        super().__init__()
        self.time_mlp = nn.Sequential(
            nn.Linear(time_dim, channels), nn.SiLU(), nn.Linear(channels, channels)
        )
        self.conv1 = nn.Conv2d(1, channels, 3, padding=1)
        self.gn1 = nn.GroupNorm(8, channels)
        self.conv2 = nn.Conv2d(channels, channels, 3, padding=1)
        self.gn2 = nn.GroupNorm(8, channels)
        self.conv_out = nn.Conv2d(channels, 1, 3, padding=1)

    def forward(self, x: torch.Tensor, t_emb: torch.Tensor) -> torch.Tensor:
        temb = self.time_mlp(t_emb).view(t_emb.shape[0], -1, 1, 1)
        h = self.conv1(x + temb)
        h = self.gn1(h)
        h = F.silu(h)
        h = self.conv2(h)
        h = self.gn2(h)
        h = F.silu(h)
        return self.conv_out(h)


# --------- Forward Diffusion q(x_t | x_0) ---------
def q_sample(
    x0: torch.Tensor,
    t: torch.Tensor,
    sqrt_alpha_bars: torch.Tensor,
    sqrt_one_minus_alpha_bars: torch.Tensor,
    noise: torch.Tensor | None = None,
) -> torch.Tensor:
    if noise is None:
        noise = torch.randn_like(x0)
    s_a = sqrt_alpha_bars[t].view(x0.shape[0], 1, 1, 1)
    s_1ma = sqrt_one_minus_alpha_bars[t].view(x0.shape[0], 1, 1, 1)
    return s_a * x0 + s_1ma * noise


# --------- Reverse Diffusion p(x_{t-1} | x_t) ---------
@torch.no_grad()
def p_sample_step(
    model: nn.Module,
    x_t: torch.Tensor,
    t: torch.Tensor,
    betas: torch.Tensor,
    alphas: torch.Tensor,
    alpha_bars: torch.Tensor,
    time_dim: int = 128,
) -> torch.Tensor:
    eps = model(x_t, sinusoidal_embedding(t, time_dim))
    a_t = alphas[t].view(x_t.shape[0], 1, 1, 1)
    ab_t = alpha_bars[t].view(x_t.shape[0], 1, 1, 1)
    b_t = betas[t].view(x_t.shape[0], 1, 1, 1)
    mean = (1.0 / torch.sqrt(a_t)) * (x_t - (b_t / torch.sqrt(1 - ab_t)) * eps)
    nonzero_mask = (t > 0).float().view(x_t.shape[0], 1, 1, 1)
    noise = torch.randn_like(x_t)
    return mean + nonzero_mask * torch.sqrt(b_t) * noise


@torch.no_grad()
def p_sample_loop(
    model: nn.Module,
    shape: Tuple[int, int, int, int],
    betas: torch.Tensor,
    alphas: torch.Tensor,
    alpha_bars: torch.Tensor,
    device: str,
    time_dim: int = 128,
) -> torch.Tensor:
    x = torch.randn(shape, device=device)
    T = betas.shape[0]
    for i in reversed(range(T)):
        t = torch.full((shape[0],), i, device=device, dtype=torch.long)
        x = p_sample_step(model, x, t, betas, alphas, alpha_bars, time_dim=time_dim)
    return x.clamp(-1, 1)


def demo_train_and_sample() -> None:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(int(os.getenv("SEED", "0")))

    # Hyperparameters
    T = int(os.getenv("T", "200"))
    train_steps = int(os.getenv("STEPS", "400"))
    batch_size = int(os.getenv("BS", "32"))
    lr = float(os.getenv("LR", "2e-4"))
    img_size = int(os.getenv("SIZE", "32"))
    time_dim = 128

    # Schedules
    betas = linear_beta_schedule(T).to(device)
    sqrt_alpha_bars, sqrt_one_minus_alpha_bars, alphas = compute_alphas(betas)
    alpha_bars = (sqrt_alpha_bars ** 2).contiguous()  # exact cprod(alphas)

    # Model and optimizer
    model = TinyUNetNoisePredictor(time_dim=time_dim).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)

    # Tiny synthetic training loop (random images)
    for step in range(train_steps):
        x0 = torch.randn(batch_size, 1, img_size, img_size, device=device).clamp(-1, 1)
        t = torch.randint(0, T, (batch_size,), device=device)
        noise = torch.randn_like(x0)
        x_t = q_sample(x0, t, sqrt_alpha_bars, sqrt_one_minus_alpha_bars, noise)

        pred_noise = model(x_t, sinusoidal_embedding(t, time_dim))
        loss = F.mse_loss(pred_noise, noise)

        opt.zero_grad(set_to_none=True)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()

    # Sampling
    with torch.no_grad():
        samples = p_sample_loop(
            model=model,
            shape=(4, 1, img_size, img_size),
            betas=betas,
            alphas=alphas,
            alpha_bars=alpha_bars,
            device=device,
            time_dim=time_dim,
        )
    out_dir = Path("outputs/ddpm_processes")
    out_dir.mkdir(parents=True, exist_ok=True)
    save_image((samples + 1) / 2, out_dir / "samples.png", nrow=2)


if __name__ == "__main__":
    demo_train_and_sample()



