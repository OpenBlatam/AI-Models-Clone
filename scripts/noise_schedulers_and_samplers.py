from __future__ import annotations

import os
from pathlib import Path

import torch


def get_device_and_dtype() -> tuple[str, torch.dtype]:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    use_fp16 = bool(int(os.getenv("FP16", "1"))) and device == "cuda"
    return device, (torch.float16 if use_fp16 else torch.float32)


def maybe_enable_memory_opts(pipe) -> None:  # type: ignore[no-untyped-def]
    for fn in (
        getattr(pipe, "enable_attention_slicing", None),
        getattr(pipe, "enable_sequential_cpu_offload", None),
        getattr(pipe, "enable_model_cpu_offload", None),
        getattr(pipe, "enable_vae_slicing", None),
        getattr(pipe, "enable_xformers_memory_efficient_attention", None),
    ):
        try:
            if fn:
                fn()
        except Exception:
            pass


def build_pipeline(model_id: str, dtype: torch.dtype, use_sdxl: bool):
    if use_sdxl:
        from diffusers import StableDiffusionXLPipeline

        return StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=dtype)
    else:
        from diffusers import StableDiffusionPipeline

        return StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype)


def make_scheduler(name: str, pipe) -> object:  # type: ignore[no-untyped-def]
    # Creates scheduler from the current pipeline scheduler config with optional overrides
    name = name.lower()
    cfg = pipe.scheduler.config

    # Lazy imports to keep startup fast
    from diffusers import (
        DDPMScheduler,
        DDIMScheduler,
        PNDMScheduler,
        LMSDiscreteScheduler,
        EulerDiscreteScheduler,
        EulerAncestralDiscreteScheduler,
        HeunDiscreteScheduler,
        KDPM2DiscreteScheduler,
        KDPM2AncestralDiscreteScheduler,
        DPMSolverMultistepScheduler,
    )

    if name in ("ddpm",):
        return DDPMScheduler.from_config(cfg)
    if name in ("ddim",):
        # eta is not set here; Diffusers' DDIM defaults are robust
        return DDIMScheduler.from_config(cfg)
    if name in ("pndm",):
        return PNDMScheduler.from_config(cfg)
    if name in ("lms", "lms_karras"):
        use_karras_sigmas = name.endswith("karras") or bool(int(os.getenv("KARRAS", "1")))
        return LMSDiscreteScheduler.from_config({**cfg, "use_karras_sigmas": use_karras_sigmas})
    if name in ("euler", "euler_a", "euler_karras", "euler_a_karras"):
        use_karras_sigmas = name.endswith("karras") or bool(int(os.getenv("KARRAS", "1")))
        if "_a" in name:
            return EulerAncestralDiscreteScheduler.from_config({**cfg, "use_karras_sigmas": use_karras_sigmas})
        return EulerDiscreteScheduler.from_config({**cfg, "use_karras_sigmas": use_karras_sigmas})
    if name in ("heun", "heun_karras"):
        use_karras_sigmas = name.endswith("karras") or bool(int(os.getenv("KARRAS", "1")))
        return HeunDiscreteScheduler.from_config({**cfg, "use_karras_sigmas": use_karras_sigmas})
    if name in ("dpm2", "dpm2_a"):
        if name.endswith("_a"):
            return KDPM2AncestralDiscreteScheduler.from_config(cfg)
        return KDPM2DiscreteScheduler.from_config(cfg)
    if name in ("dpmpp_2m", "dpmpp_sde", "dpmpp_2m_karras", "dpmpp_sde_karras"):
        use_sde = name.startswith("dpmpp_sde")
        use_karras_sigmas = name.endswith("karras") or bool(int(os.getenv("KARRAS", "1")))
        return DPMSolverMultistepScheduler.from_config({**cfg, "use_karras_sigmas": use_karras_sigmas, "use_sde": use_sde})

    # Default fallback
    return DPMSolverMultistepScheduler.from_config(cfg)


def main() -> None:
    # Configuration via environment variables
    model_id = os.getenv("MODEL_ID", "runwayml/stable-diffusion-v1-5")
    use_sdxl = bool(int(os.getenv("USE_SDXL", "0"))) or "xl" in model_id.lower()
    if use_sdxl and model_id == "runwayml/stable-diffusion-v1-5":
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"

    prompt = os.getenv("PROMPT", "a highly detailed macro photo of a mechanical insect, bokeh, 50mm")
    negative = os.getenv("NEGATIVE", "lowres, blurry, worst quality, jpeg artifacts")
    scheduler_name = os.getenv("SCHED", "dpmpp_2m_karras")
    steps = int(os.getenv("STEPS", "30"))
    guidance = float(os.getenv("GUIDANCE", "7.0"))
    seed = int(os.getenv("SEED", "1337"))
    width = int(os.getenv("W", os.getenv("WIDTH", "768")))
    height = int(os.getenv("H", os.getenv("HEIGHT", "768")))
    out_dir = Path(os.getenv("OUT", "outputs/schedulers"))
    out_dir.mkdir(parents=True, exist_ok=True)

    device, dtype = get_device_and_dtype()
    generator = torch.Generator(device=device).manual_seed(seed)

    pipe = build_pipeline(model_id, dtype, use_sdxl).to(device)
    pipe.scheduler = make_scheduler(scheduler_name, pipe)
    maybe_enable_memory_opts(pipe)

    image = pipe(
        prompt=prompt,
        negative_prompt=negative,
        height=height,
        width=width,
        num_inference_steps=steps,
        guidance_scale=guidance,
        generator=generator,
    ).images[0]

    slug = model_id.split("/")[-1].replace(".", "_")
    out_path = out_dir / f"{scheduler_name}_{slug}.png"
    image.save(out_path)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import math
from typing import Literal, Tuple

import torch
from torch import nn


def linear_beta_schedule(num_steps: int, beta_start: float = 1e-4, beta_end: float = 2e-2) -> torch.Tensor:
    return torch.linspace(beta_start, beta_end, num_steps, dtype=torch.float32)


def cosine_alpha_bar(t: torch.Tensor) -> torch.Tensor:
    return torch.cos((t + 0.008) / 1.008 * math.pi / 2).pow(2)


def cosine_beta_schedule(num_steps: int) -> torch.Tensor:
    ts = torch.linspace(0, 1, num_steps + 1, dtype=torch.float32)
    alphas_cum = cosine_alpha_bar(ts)
    betas = 1 - (alphas_cum[1:] / alphas_cum[:-1]).clamp(0, 0.999)
    return betas


def quadratic_beta_schedule(num_steps: int, beta_max: float = 2e-2) -> torch.Tensor:
    x = torch.linspace(0, 1, num_steps, dtype=torch.float32)
    return (x**2) * beta_max


def sigmoid_beta_schedule(num_steps: int, start: float = -6, end: float = 6, max_beta: float = 2e-2) -> torch.Tensor:
    x = torch.linspace(start, end, num_steps)
    return torch.sigmoid(x) * max_beta


class DiffusionPrecompute:
    def __init__(self, betas: torch.Tensor, device: torch.device) -> None:
        self.device = device
        self.betas = betas.to(device)
        self.alphas = 1.0 - self.betas
        self.alphas_cum = torch.cumprod(self.alphas, dim=0)
        self.sqrt_alphas_cum = torch.sqrt(self.alphas_cum)
        self.sqrt_one_minus_ac = torch.sqrt(1.0 - self.alphas_cum)
        self.sqrt_recip_alpha = torch.sqrt(1.0 / self.alphas)
        self.posterior_var = self.betas * torch.cat([torch.tensor([1.0], device=device), self.alphas_cum[:-1]]) / (1.0 - self.alphas_cum).clamp(min=1e-20)

    @staticmethod
    def extract(coeffs: torch.Tensor, t: torch.Tensor, shape: torch.Size) -> torch.Tensor:
        out = coeffs.gather(0, t).float()
        return out.reshape(-1, *([1] * (len(shape) - 1)))


def q_sample(x0: torch.Tensor, t: torch.Tensor, noise: torch.Tensor, pre: DiffusionPrecompute) -> torch.Tensor:
    return pre.extract(pre.sqrt_alphas_cum, t, x0.shape) * x0 + pre.extract(pre.sqrt_one_minus_ac, t, x0.shape) * noise


def predict_x0_from_eps(x_t: torch.Tensor, eps: torch.Tensor, t: torch.Tensor, pre: DiffusionPrecompute) -> torch.Tensor:
    return (x_t - pre.extract(pre.sqrt_one_minus_ac, t, x_t.shape) * eps) / pre.extract(pre.sqrt_alphas_cum, t, x_t.shape)


@torch.no_grad()
def ddpm_step(model: nn.Module, x_t: torch.Tensor, t: torch.Tensor, pre: DiffusionPrecompute) -> torch.Tensor:
    eps = model(x_t, t)
    mean = pre.extract(pre.sqrt_recip_alpha, t, x_t.shape) * (x_t - pre.extract(pre.betas / pre.sqrt_one_minus_ac, t, x_t.shape) * eps)
    var = pre.extract(pre.posterior_var, t, x_t.shape)
    noise = torch.randn_like(x_t)
    nonzero = (t > 0).float().view(-1, *([1] * (x_t.dim() - 1)))
    return mean + nonzero * torch.sqrt(var) * noise


@torch.no_grad()
def ddim_step(model: nn.Module, x_t: torch.Tensor, t: torch.Tensor, t_prev: torch.Tensor, pre: DiffusionPrecompute, eta: float = 0.0) -> torch.Tensor:
    eps = model(x_t, t)
    x0_pred = predict_x0_from_eps(x_t, eps, t, pre)
    a_t = pre.extract(pre.alphas_cum, t, x_t.shape)
    a_prev = pre.extract(pre.alphas_cum, t_prev, x_t.shape)
    sigma = eta * torch.sqrt((1 - a_prev) / (1 - a_t) * (1 - a_t / a_prev))
    dir_term = torch.sqrt(torch.clamp(a_prev - sigma**2, min=0.0)) * ((x_t - torch.sqrt(a_t) * x0_pred) / torch.sqrt(1 - a_t))
    noise = torch.randn_like(x_t)
    return torch.sqrt(a_prev) * x0_pred + dir_term + sigma * noise


def make_schedule(kind: Literal["linear", "cosine", "quadratic", "sigmoid"], num_steps: int) -> torch.Tensor:
    if kind == "linear":
        return linear_beta_schedule(num_steps)
    if kind == "cosine":
        return cosine_beta_schedule(num_steps)
    if kind == "quadratic":
        return quadratic_beta_schedule(num_steps)
    if kind == "sigmoid":
        return sigmoid_beta_schedule(num_steps)
    raise ValueError(kind)


class TinyEpsModel(nn.Module):
    def __init__(self, channels: int = 64, time_dim: int = 128) -> None:
        super().__init__()
        self.time = nn.Sequential(nn.Linear(time_dim, time_dim), nn.SiLU(), nn.Linear(time_dim, time_dim))
        self.in_conv = nn.Conv2d(1, channels, 3, padding=1)
        self.block = nn.Sequential(
            nn.GroupNorm(8, channels), nn.SiLU(), nn.Conv2d(channels, channels, 3, padding=1),
            nn.GroupNorm(8, channels), nn.SiLU(), nn.Conv2d(channels, channels, 3, padding=1),
        )
        self.out = nn.Conv2d(channels, 1, 3, padding=1)
        self.time_dim = time_dim

    @staticmethod
    def t_embed(t: torch.Tensor, dim: int) -> torch.Tensor:
        half = dim // 2
        freqs = torch.exp(-math.log(10000.0) * torch.arange(0, half, dtype=torch.float32, device=t.device) / float(half))
        args = t.float()[:, None] * freqs[None, :]
        emb = torch.cat([torch.sin(args), torch.cos(args)], dim=-1)
        if dim % 2 == 1:
            emb = torch.nn.functional.pad(emb, (0, 1))
        return emb

    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        t_emb = self.time(self.t_embed(t, self.time_dim))
        h = self.in_conv(x)
        h = self.block(h + t_emb[:, :, None, None])
        return self.out(h)


def main() -> None:
    ap = argparse.ArgumentParser(description="Noise schedulers and samplers demo")
    ap.add_argument("--schedule", choices=["linear", "cosine", "quadratic", "sigmoid"], default="cosine")
    ap.add_argument("--sampler", choices=["ddpm", "ddim"], default="ddim")
    ap.add_argument("--steps", type=int, default=1000)
    ap.add_argument("--ddim-steps", type=int, default=50)
    ap.add_argument("--eta", type=float, default=0.0)
    args = ap.parse_args()

    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")
    betas = make_schedule(args.schedule, args.steps)
    pre = DiffusionPrecompute(betas, device)
    model = TinyEpsModel().to(device).eval()

    with torch.no_grad():
        if args.sampler == "ddpm":
            x = torch.randn(4, 1, 32, 32, device=device)
            for step in reversed(range(args.steps)):
                t = torch.full((x.size(0),), step, device=device, dtype=torch.long)
                x = ddpm_step(model, x, t, pre)
        else:
            x = torch.randn(4, 1, 32, 32, device=device)
            timesteps = torch.linspace(args.steps - 1, 0, args.ddim_steps, dtype=torch.long, device=device)
            for i in range(args.ddim_steps):
                t = timesteps[i].repeat(x.size(0))
                t_prev = timesteps[i + 1].repeat(x.size(0)) if i + 1 < args.ddim_steps else torch.zeros_like(t)
                x = ddim_step(model, x, t, t_prev, pre, eta=args.eta)
        print(tuple(x.shape))


if __name__ == "__main__":
    main()


