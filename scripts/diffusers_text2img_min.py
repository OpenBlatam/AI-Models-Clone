from __future__ import annotations

import os
from pathlib import Path

import torch


def get_device_and_dtype() -> tuple[str, torch.dtype]:
    use_fp16 = bool(int(os.getenv("FP16", "1"))) and torch.cuda.is_available()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if use_fp16 and device == "cuda" else torch.float32
    return device, dtype


def maybe_enable_memory_opts(pipe) -> None:  # type: ignore[no-untyped-def]
    try:
        pipe.enable_attention_slicing()
    except Exception:
        pass
    try:
        pipe.enable_sequential_cpu_offload()
    except Exception:
        try:
            pipe.enable_model_cpu_offload()
        except Exception:
            pass
    try:
        pipe.enable_vae_slicing()
    except Exception:
        pass
    try:
        pipe.enable_xformers_memory_efficient_attention()
    except Exception:
        pass


def main() -> None:
    model_id = os.getenv("MODEL_ID", "stabilityai/stable-diffusion-2-1")
    prompt = os.getenv(
        "PROMPT",
        "a photo of a robotic hummingbird, ultra-detailed, studio lighting, 8k, sharp focus",
    )
    negative = os.getenv("NEGATIVE", "lowres, blurry, worst quality, jpeg artifacts")
    steps = int(os.getenv("STEPS", "25"))
    guidance = float(os.getenv("GUIDANCE", "7.0"))
    seed = int(os.getenv("SEED", "42"))
    height = int(os.getenv("H", os.getenv("HEIGHT", "768")))
    width = int(os.getenv("W", os.getenv("WIDTH", "768")))
    out_dir = Path(os.getenv("OUT", "outputs/diffusers"))
    out_dir.mkdir(parents=True, exist_ok=True)

    device, dtype = get_device_and_dtype()

    use_sdxl = bool(int(os.getenv("USE_SDXL", "0"))) or "xl" in model_id.lower()
    if use_sdxl and model_id == "stabilityai/stable-diffusion-2-1":
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"

    if use_sdxl:
        from diffusers import StableDiffusionXLPipeline  # lazy import

        pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=dtype)
    else:
        from diffusers import StableDiffusionPipeline  # lazy import

        pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype)

    pipe = pipe.to(device)
    maybe_enable_memory_opts(pipe)

    generator = torch.Generator(device=device).manual_seed(seed)

    if use_sdxl:
        image = pipe(
            prompt=prompt,
            negative_prompt=negative,
            height=height,
            width=width,
            num_inference_steps=steps,
            guidance_scale=guidance,
            generator=generator,
        ).images[0]
    else:
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
    out_path = out_dir / f"text2img_{slug}.png"
    image.save(out_path)


if __name__ == "__main__":
    main()



