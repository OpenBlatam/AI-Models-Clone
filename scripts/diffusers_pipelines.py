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
    # White = masked area to inpaint; Black = keep
    mask = Image.open(path).convert("L")
    if size is not None:
        mask = mask.resize(size, Image.NEAREST)
    return mask


def build_text2img_pipeline(model_id: str, dtype: torch.dtype, use_sdxl: bool):
    if use_sdxl:
        from diffusers import StableDiffusionXLPipeline

        pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=dtype)
    else:
        from diffusers import StableDiffusionPipeline

        pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype)
    return pipe


def build_img2img_pipeline(model_id: str, dtype: torch.dtype, use_sdxl: bool):
    if use_sdxl:
        from diffusers import StableDiffusionXLImg2ImgPipeline

        pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(model_id, torch_dtype=dtype)
    else:
        from diffusers import StableDiffusionImg2ImgPipeline

        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, torch_dtype=dtype)
    return pipe


def build_inpaint_pipeline(model_id: str, dtype: torch.dtype):
    from diffusers import StableDiffusionInpaintPipeline

    return StableDiffusionInpaintPipeline.from_pretrained(model_id, torch_dtype=dtype)


def main() -> None:
    task = os.getenv("TASK", "txt2img")  # txt2img | img2img | inpaint
    model_id = os.getenv("MODEL_ID", "stabilityai/stable-diffusion-2-1")
    use_sdxl = bool(int(os.getenv("USE_SDXL", "0"))) or "xl" in model_id.lower()
    if use_sdxl and model_id == "stabilityai/stable-diffusion-2-1":
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"

    prompt = os.getenv("PROMPT", "a cinematic photo of a neon cyberpunk alley at night, rain, 50mm")
    negative = os.getenv("NEGATIVE", "lowres, blurry, worst quality, jpeg artifacts")
    steps = int(os.getenv("STEPS", "30"))
    guidance = float(os.getenv("GUIDANCE", "7.0"))
    seed = int(os.getenv("SEED", "1234"))
    width = int(os.getenv("W", os.getenv("WIDTH", "768")))
    height = int(os.getenv("H", os.getenv("HEIGHT", "768")))
    strength = float(os.getenv("STRENGTH", "0.6"))
    init_image_path = os.getenv("INIT_IMAGE", "")
    mask_image_path = os.getenv("MASK_IMAGE", "")
    out_dir = Path(os.getenv("OUT", "outputs/diffusers"))
    out_dir.mkdir(parents=True, exist_ok=True)

    device, dtype = get_device_and_dtype()
    generator = torch.Generator(device=device).manual_seed(seed)

    if task == "txt2img":
        pipe = build_text2img_pipeline(model_id, dtype, use_sdxl).to(device)
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
        image.save(out_dir / f"txt2img_{slug}.png")

    elif task == "img2img":
        assert init_image_path, "INIT_IMAGE env var is required for img2img"
        init_image = load_image(init_image_path, size=(width, height))
        pipe = build_img2img_pipeline(model_id, dtype, use_sdxl).to(device)
        maybe_enable_memory_opts(pipe)
        image = pipe(
            prompt=prompt,
            negative_prompt=negative,
            image=init_image,
            strength=strength,
            num_inference_steps=steps,
            guidance_scale=guidance,
            generator=generator,
        ).images[0]
        slug = model_id.split("/")[-1].replace(".", "_")
        image.save(out_dir / f"img2img_{slug}.png")

    elif task == "inpaint":
        assert init_image_path and mask_image_path, "INIT_IMAGE and MASK_IMAGE env vars are required for inpaint"
        init_image = load_image(init_image_path, size=(width, height))
        mask_image = load_mask(mask_image_path, size=(width, height))
        pipe = build_inpaint_pipeline(model_id, dtype).to(device)
        maybe_enable_memory_opts(pipe)
        image = pipe(
            prompt=prompt,
            negative_prompt=negative,
            image=init_image,
            mask_image=mask_image,
            strength=strength,
            num_inference_steps=steps,
            guidance_scale=guidance,
            generator=generator,
        ).images[0]
        slug = model_id.split("/")[-1].replace(".", "_")
        image.save(out_dir / f"inpaint_{slug}.png")

    else:
        raise ValueError(f"Unknown TASK: {task}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import os
from typing import Optional

import torch
from PIL import Image
from diffusers import (
    StableDiffusionPipeline,
    StableDiffusionImg2ImgPipeline,
    StableDiffusionInpaintPipeline,
    StableDiffusionXLPipeline,
    StableDiffusionXLImg2ImgPipeline,
    StableDiffusionXLInpaintPipeline,
    DPMSolverMultistepScheduler,
)


def get_device_dtype() -> tuple[torch.device, torch.dtype]:
    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")
    dtype = torch.bfloat16 if (device.type == "cuda" and torch.cuda.is_bf16_supported()) else (torch.float16 if device.type == "cuda" else torch.float32)
    return device, dtype


def _post_load(pipe):
    device, _ = get_device_dtype()
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    if device.type == "cuda":
        try:
            pipe.enable_xformers_memory_efficient_attention()
        except Exception:
            pass
        pipe.enable_attention_slicing()
    pipe.to(device)
    return pipe


def load_sd15_txt2img(model_id: str = "runwayml/stable-diffusion-v1-5") -> StableDiffusionPipeline:
    device, dtype = get_device_dtype()
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype, safety_checker=None)
    return _post_load(pipe)


def load_sd15_img2img(model_id: str = "runwayml/stable-diffusion-v1-5") -> StableDiffusionImg2ImgPipeline:
    device, dtype = get_device_dtype()
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, torch_dtype=dtype, safety_checker=None)
    return _post_load(pipe)


def load_sd15_inpaint(model_id: str = "runwayml/stable-diffusion-inpainting") -> StableDiffusionInpaintPipeline:
    device, dtype = get_device_dtype()
    pipe = StableDiffusionInpaintPipeline.from_pretrained(model_id, torch_dtype=dtype, safety_checker=None)
    return _post_load(pipe)


def load_sdxl_txt2img(model_id: str = "stabilityai/stable-diffusion-xl-base-1.0") -> StableDiffusionXLPipeline:
    device, dtype = get_device_dtype()
    pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=dtype)
    return _post_load(pipe)


def load_sdxl_img2img(model_id: str = "stabilityai/stable-diffusion-xl-base-1.0") -> StableDiffusionXLImg2ImgPipeline:
    device, dtype = get_device_dtype()
    pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(model_id, torch_dtype=dtype)
    return _post_load(pipe)


def load_sdxl_inpaint(model_id: str = "diffusers/stable-diffusion-xl-1.0-inpainting-0.1") -> StableDiffusionXLInpaintPipeline:
    device, dtype = get_device_dtype()
    pipe = StableDiffusionXLInpaintPipeline.from_pretrained(model_id, torch_dtype=dtype)
    return _post_load(pipe)


@torch.no_grad()
def txt2img(prompt: str, model: str = "sd15", steps: int = 25, guidance: float = 7.5, width: int = 768, height: int = 768) -> Image.Image:
    if model.lower() == "sdxl":
        pipe = load_sdxl_txt2img()
        with torch.cuda.amp.autocast(enabled=(pipe.device.type == "cuda")):
            result = pipe(prompt=prompt, num_inference_steps=int(steps), guidance_scale=float(guidance), width=int(width), height=int(height))
            return result.images[0]
    else:
        pipe = load_sd15_txt2img()
        with torch.cuda.amp.autocast(enabled=(pipe.device.type == "cuda")):
            result = pipe(prompt=prompt, num_inference_steps=int(steps), guidance_scale=float(guidance), width=int(width), height=int(height))
            return result.images[0]


@torch.no_grad()
def img2img(prompt: str, init_image: Image.Image, strength: float = 0.6, steps: int = 25, guidance: float = 7.5, model: str = "sd15") -> Image.Image:
    if model.lower() == "sdxl":
        pipe = load_sdxl_img2img()
    else:
        pipe = load_sd15_img2img()
    with torch.cuda.amp.autocast(enabled=(pipe.device.type == "cuda")):
        result = pipe(prompt=prompt, image=init_image, strength=float(strength), num_inference_steps=int(steps), guidance_scale=float(guidance))
    return result.images[0]


@torch.no_grad()
def inpaint(prompt: str, image: Image.Image, mask: Image.Image, steps: int = 25, guidance: float = 7.5, model: str = "sd15") -> Image.Image:
    if model.lower() == "sdxl":
        pipe = load_sdxl_inpaint()
    else:
        pipe = load_sd15_inpaint()
    with torch.cuda.amp.autocast(enabled=(pipe.device.type == "cuda")):
        result = pipe(prompt=prompt, image=image, mask_image=mask, num_inference_steps=int(steps), guidance_scale=float(guidance))
    return result.images[0]


def main() -> None:
    ap = argparse.ArgumentParser(description="Diffusers pipelines: SD 1.5 and SDXL")
    ap.add_argument("--task", choices=["txt2img", "img2img", "inpaint"], default="txt2img")
    ap.add_argument("--model", choices=["sd15", "sdxl"], default="sd15")
    ap.add_argument("--prompt", type=str, default="a futuristic cityscape at sunset, cinematic lighting, 8k")
    ap.add_argument("--init-image", type=str, default=None)
    ap.add_argument("--mask", type=str, default=None)
    ap.add_argument("--steps", type=int, default=25)
    ap.add_argument("--guidance", type=float, default=7.5)
    ap.add_argument("--width", type=int, default=768)
    ap.add_argument("--height", type=int, default=768)
    ap.add_argument("--out", type=str, default="outputs/diffusers_result.png")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    if args.task == "txt2img":
        image = txt2img(args.prompt, model=args.model, steps=args.steps, guidance=args.guidance, width=args.width, height=args.height)
    elif args.task == "img2img":
        if not args.init_image:
            raise SystemExit("--init-image is required for img2img")
        init_img = Image.open(args.init_image).convert("RGB")
        image = img2img(args.prompt, init_image=init_img, steps=args.steps, guidance=args.guidance, model=args.model)
    else:
        if not (args.init_image and args.mask):
            raise SystemExit("--init-image and --mask are required for inpaint")
        base = Image.open(args.init_image).convert("RGB")
        mask = Image.open(args.mask).convert("L")
        image = inpaint(args.prompt, image=base, mask=mask, steps=args.steps, guidance=args.guidance, model=args.model)

    image.save(args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()


