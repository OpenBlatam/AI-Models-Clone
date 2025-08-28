from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import torch
from PIL import Image


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


def load_image(path: str, size: Optional[tuple[int, int]] = None) -> Image.Image:
    img = Image.open(path).convert("RGB")
    if size is not None:
        img = img.resize(size, Image.LANCZOS)
    return img


def load_mask(path: str, size: Optional[tuple[int, int]] = None) -> Image.Image:
    mask = Image.open(path).convert("L")
    if size is not None:
        mask = mask.resize(size, Image.NEAREST)
    return mask


def build_pipelines(model_id: str, dtype: torch.dtype, use_sdxl: bool):
    if use_sdxl:
        from diffusers import (
            StableDiffusionXLPipeline,
            StableDiffusionXLImg2ImgPipeline,
            StableDiffusionXLInpaintPipeline,
        )

        return (
            StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=dtype),
            StableDiffusionXLImg2ImgPipeline.from_pretrained(model_id, torch_dtype=dtype),
            StableDiffusionXLInpaintPipeline.from_pretrained(model_id, torch_dtype=dtype),
        )
    else:
        from diffusers import (
            StableDiffusionPipeline,
            StableDiffusionImg2ImgPipeline,
            StableDiffusionInpaintPipeline,
        )

        return (
            StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype),
            StableDiffusionImg2ImgPipeline.from_pretrained(model_id, torch_dtype=dtype),
            StableDiffusionInpaintPipeline.from_pretrained(model_id, torch_dtype=dtype),
        )


def maybe_build_refiner(model_id: str, dtype: torch.dtype):
    from diffusers import StableDiffusionXLRefinerPipeline

    return StableDiffusionXLRefinerPipeline.from_pretrained(model_id, torch_dtype=dtype)


def main() -> None:
    task = os.getenv("TASK", "txt2img")  # txt2img | img2img | inpaint
    model_id = os.getenv("MODEL_BASE", "stabilityai/stable-diffusion-xl-base-1.0")
    use_sdxl = bool(int(os.getenv("USE_SDXL", "1"))) or "xl" in model_id.lower()
    if not use_sdxl and model_id == "stabilityai/stable-diffusion-xl-base-1.0":
        model_id = "runwayml/stable-diffusion-v1-5"

    prompt = os.getenv("PROMPT", "a cinematic portrait of a cybernetic falcon, volumetric lighting, 85mm")
    negative = os.getenv("NEGATIVE", "lowres, blurry, worst quality, jpeg artifacts")
    steps = int(os.getenv("STEPS", "30"))
    guidance = float(os.getenv("GUIDANCE", "7.0"))
    seed = int(os.getenv("SEED", "2024"))
    width = int(os.getenv("W", os.getenv("WIDTH", "1024" if use_sdxl else "768")))
    height = int(os.getenv("H", os.getenv("HEIGHT", "1024" if use_sdxl else "768")))
    strength = float(os.getenv("STRENGTH", "0.6"))
    init_image_path = os.getenv("INIT_IMAGE", "")
    mask_image_path = os.getenv("MASK_IMAGE", "")
    use_refiner = bool(int(os.getenv("USE_REFINER", "0"))) and use_sdxl
    refiner_id = os.getenv("MODEL_REFINER", "stabilityai/stable-diffusion-xl-refiner-1.0")
    refine_t = float(os.getenv("REFINE_T", "0.8"))  # fraction for base/refiner split

    out_dir = Path(os.getenv("OUT", "outputs/diffusers_unified"))
    out_dir.mkdir(parents=True, exist_ok=True)

    device, dtype = get_device_and_dtype()
    generator = torch.Generator(device=device).manual_seed(seed)

    txt2img, img2img, inpaint = build_pipelines(model_id, dtype, use_sdxl)
    txt2img = txt2img.to(device)
    img2img = img2img.to(device)
    inpaint = inpaint.to(device)
    for p in (txt2img, img2img, inpaint):
        maybe_enable_memory_opts(p)

    slug = model_id.split("/")[-1].replace(".", "_")

    if task == "txt2img":
        if use_refiner:
            try:
                refiner = maybe_build_refiner(refiner_id, dtype).to(device)
                maybe_enable_memory_opts(refiner)
                latents = txt2img(
                    prompt=prompt,
                    negative_prompt=negative,
                    height=height,
                    width=width,
                    num_inference_steps=steps,
                    guidance_scale=guidance,
                    denoising_end=refine_t,
                    output_type="latent",
                    generator=generator,
                ).images
                image = refiner(
                    prompt=prompt,
                    negative_prompt=negative,
                    image=latents,
                    num_inference_steps=steps,
                    guidance_scale=guidance,
                    denoising_start=refine_t,
                    generator=generator,
                ).images[0]
            except Exception:
                image = txt2img(
                    prompt=prompt,
                    negative_prompt=negative,
                    height=height,
                    width=width,
                    num_inference_steps=steps,
                    guidance_scale=guidance,
                    generator=generator,
                ).images[0]
        else:
            image = txt2img(
                prompt=prompt,
                negative_prompt=negative,
                height=height,
                width=width,
                num_inference_steps=steps,
                guidance_scale=guidance,
                generator=generator,
            ).images[0]
        (out_dir / f"txt2img_{slug}.png").resolve().parent.mkdir(parents=True, exist_ok=True)
        image.save(out_dir / f"txt2img_{slug}.png")

    elif task == "img2img":
        assert init_image_path, "INIT_IMAGE env var is required for img2img"
        init_image = load_image(init_image_path, size=(width, height))
        image = img2img(
            prompt=prompt,
            negative_prompt=negative,
            image=init_image,
            strength=strength,
            num_inference_steps=steps,
            guidance_scale=guidance,
            generator=generator,
        ).images[0]
        image.save(out_dir / f"img2img_{slug}.png")

    elif task == "inpaint":
        assert init_image_path and mask_image_path, "INIT_IMAGE and MASK_IMAGE env vars are required for inpaint"
        init_image = load_image(init_image_path, size=(width, height))
        mask_image = load_mask(mask_image_path, size=(width, height))
        image = inpaint(
            prompt=prompt,
            negative_prompt=negative,
            image=init_image,
            mask_image=mask_image,
            strength=strength,
            num_inference_steps=steps,
            guidance_scale=guidance,
            generator=generator,
        ).images[0]
        image.save(out_dir / f"inpaint_{slug}.png")

    else:
        raise ValueError(f"Unknown TASK: {task}")


if __name__ == "__main__":
    main()



