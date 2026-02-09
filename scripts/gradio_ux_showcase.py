from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Optional

import gradio as gr
import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer


def get_device_and_dtype() -> tuple[str, torch.dtype]:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    use_fp16 = bool(int(os.getenv("FP16", "1"))) and device == "cuda"
    return device, (torch.float16 if use_fp16 else torch.float32)


# ------------------------ LLM ------------------------
@lru_cache(maxsize=1)
def load_lm(model_name: str):
    tok = AutoTokenizer.from_pretrained(model_name)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token or tok.unk_token
    model = AutoModelForCausalLM.from_pretrained(model_name).to(get_device_and_dtype()[0]).eval()
    return tok, model


def llm_generate(
    prompt: str,
    model_name: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    top_k: int,
    do_sample: bool,
    progress: gr.Progress = gr.Progress(track_tqdm=False),
) -> str:
    if not prompt.strip():
        raise gr.Error("Prompt vacío.")
    if not (1 <= max_new_tokens <= 512):
        raise gr.Error("max_new_tokens debe estar entre 1 y 512.")
    tok, model = load_lm(model_name)
    x = tok(prompt, return_tensors="pt").to(get_device_and_dtype()[0])
    with torch.no_grad():
        progress(0.3)
        y = model.generate(
            **x,
            max_new_tokens=int(max_new_tokens),
            do_sample=bool(do_sample),
            temperature=max(0.01, float(temperature)),
            top_p=float(top_p),
            top_k=int(top_k),
            pad_token_id=tok.pad_token_id,
            eos_token_id=tok.eos_token_id,
        )
        progress(0.95)
    return tok.decode(y[0], skip_special_tokens=True)


# --------------------- Diffusers ---------------------
def maybe_enable_mem_opts(pipe):  # type: ignore[no-untyped-def]
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
    return pipe


@lru_cache(maxsize=3)
def load_text2img(model_id: str):  # type: ignore[no-untyped-def]
    device, dtype = get_device_and_dtype()
    use_sdxl = "xl" in model_id.lower() or bool(int(os.getenv("USE_SDXL", "0")))
    if use_sdxl and model_id == "stabilityai/stable-diffusion-2-1":
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    try:
        if use_sdxl:
            from diffusers import StableDiffusionXLPipeline

            pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=dtype)
        else:
            from diffusers import StableDiffusionPipeline

            pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype)
    except Exception as e:
        raise gr.Error(f"No se pudo cargar el modelo: {e}")
    pipe = pipe.to(device)
    return maybe_enable_mem_opts(pipe), device


def t2i_gallery(
    prompt: str,
    negative: str,
    model_id: str,
    steps: int,
    guidance: float,
    width: int,
    height: int,
    seed: int,
    num_images: int,
    style: str,
    progress: gr.Progress = gr.Progress(track_tqdm=False),
) -> List[Image.Image]:
    if not prompt.strip():
        raise gr.Error("Prompt vacío.")
    if not (5 <= steps <= 100):
        raise gr.Error("Steps debe estar entre 5 y 100.")
    if min(width, height) < 256 or max(width, height) > 1536:
        raise gr.Error("Dimensiones fuera de 256-1536.")
    if style == "Photorealistic":
        prompt = f"{prompt}, photo, ultra-detailed, realistic, 50mm lens"
    elif style == "Illustration":
        prompt = f"{prompt}, digital illustration, clean lines, artstation"
    elif style == "Anime":
        prompt = f"{prompt}, anime style, vibrant colors, sharp lines"

    pipe, device = load_text2img(model_id)
    images: List[Image.Image] = []
    for i in range(max(1, min(int(num_images), 6))):
        progress((i + 1) / max(1, num_images))
        gen = torch.Generator(device=device).manual_seed(int(seed) + i)
        img = pipe(
            prompt=prompt,
            negative_prompt=negative or None,
            height=int(height),
            width=int(width),
            num_inference_steps=int(steps),
            guidance_scale=float(guidance),
            generator=gen,
        ).images[0]
        images.append(img)
    return images


# ----------------------- UI -------------------------
def build_ui() -> gr.Blocks:
    default_text_model = os.getenv("TEXT_MODEL", "distilgpt2")
    default_diff_model = os.getenv("DIFF_MODEL", "stabilityai/stable-diffusion-2-1")

    with gr.Blocks(title="UX Showcase: LLM + Diffusers", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        ### Model Showcase
        Diseños amigables para probar capacidades de LLM y Diffusers.
        """)

        with gr.Tabs():
            # LLM tab
            with gr.TabItem("Text Generation"):
                with gr.Row():
                    prompt = gr.Textbox(label="Prompt", lines=6, placeholder="Escribe tu prompt...")
                with gr.Row():
                    model_name = gr.Textbox(label="Model", value=default_text_model)
                with gr.Accordion("Opciones avanzadas", open=False):
                    with gr.Row():
                        max_new = gr.Slider(1, 512, value=128, step=1, label="Max New Tokens")
                        temperature = gr.Slider(0.01, 2.0, value=0.8, step=0.01, label="Temperature")
                    with gr.Row():
                        top_p = gr.Slider(0.1, 1.0, value=0.95, step=0.01, label="Top-p")
                        top_k = gr.Slider(0, 200, value=50, step=1, label="Top-k")
                        do_sample = gr.Checkbox(value=True, label="Sampling")
                out = gr.Textbox(label="Salida", lines=10)
                gr.Examples(
                    examples=[["Escribe una introducción sobre IA responsable."], ["Resume en 3 viñetas los beneficios de PyTorch."]],
                    inputs=[prompt],
                )
                gr.Button("Generar").click(
                    llm_generate,
                    inputs=[prompt, model_name, max_new, temperature, top_p, top_k, do_sample],
                    outputs=out,
                )

            # Diffusers tab
            with gr.TabItem("Text-to-Image Gallery"):
                with gr.Row():
                    t2i_prompt = gr.Textbox(label="Prompt", lines=3, placeholder="Describe la imagen...")
                with gr.Row():
                    t2i_negative = gr.Textbox(label="Negative Prompt", lines=2)
                with gr.Row():
                    diff_model = gr.Textbox(label="Model", value=default_diff_model)
                with gr.Row():
                    steps = gr.Slider(5, 100, value=30, step=1, label="Steps")
                    guidance = gr.Slider(0.0, 15.0, value=7.0, step=0.1, label="Guidance")
                with gr.Row():
                    width = gr.Slider(256, 1024, value=768, step=8, label="Width")
                    height = gr.Slider(256, 1024, value=768, step=8, label="Height")
                with gr.Row():
                    seed = gr.Number(value=42, label="Seed")
                    num_images = gr.Slider(1, 6, value=3, step=1, label="Images")
                    style = gr.Dropdown(["Default", "Photorealistic", "Illustration", "Anime"], value="Default", label="Style")
                gallery = gr.Gallery(label="Resultados", columns=3, height=420)
                gr.Button("Generar Galería").click(
                    t2i_gallery,
                    inputs=[t2i_prompt, t2i_negative, diff_model, steps, guidance, width, height, seed, num_images, style],
                    outputs=gallery,
                )

    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.queue(concurrency_count=2).launch(server_name=os.getenv("HOST", "0.0.0.0"), server_port=int(os.getenv("PORT", "7865")))



