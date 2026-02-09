from __future__ import annotations

import os
from functools import lru_cache
from typing import Tuple

import gradio as gr
import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer


def get_device_and_dtype() -> tuple[str, torch.dtype]:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    use_fp16 = bool(int(os.getenv("FP16", "1"))) and device == "cuda"
    return device, (torch.float16 if use_fp16 else torch.float32)


@lru_cache(maxsize=1)
def load_text_model(model_name: str) -> tuple[AutoTokenizer, AutoModelForCausalLM, str]:
    device, dtype = get_device_and_dtype()
    tok = AutoTokenizer.from_pretrained(model_name)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token or tok.unk_token
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model = model.to(device)
    model.eval()
    return tok, model, device


def generate_text(
    prompt: str,
    model_name: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    top_k: int,
    do_sample: bool,
    progress: gr.Progress = gr.Progress(track_tqdm=False),
) -> str:
    if not isinstance(prompt, str) or len(prompt.strip()) == 0:
        raise gr.Error("Prompt vacío.")
    if max_new_tokens <= 0 or max_new_tokens > 1024:
        raise gr.Error("max_new_tokens inválido.")
    tok, model, device = load_text_model(model_name)
    inputs = tok(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        progress(0.2)
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=max(0.01, float(temperature)),
            top_p=float(top_p),
            top_k=int(top_k),
            pad_token_id=tok.pad_token_id,
            eos_token_id=tok.eos_token_id,
        )
        progress(0.9)
    text = tok.decode(outputs[0], skip_special_tokens=True)
    return text


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


@lru_cache(maxsize=2)
def load_t2i_pipeline(model_id: str):  # type: ignore[no-untyped-def]
    device, dtype = get_device_and_dtype()
    use_sdxl = bool(int(os.getenv("USE_SDXL", "0"))) or "xl" in model_id.lower()
    if use_sdxl and model_id == "stabilityai/stable-diffusion-2-1":
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    if use_sdxl:
        from diffusers import StableDiffusionXLPipeline

        pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=dtype)
    else:
        from diffusers import StableDiffusionPipeline

        pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype)
    pipe = pipe.to(device)
    maybe_enable_memory_opts(pipe)
    return pipe, device


def txt2img(
    prompt: str,
    negative: str,
    model_id: str,
    steps: int,
    guidance: float,
    width: int,
    height: int,
    seed: int,
    progress: gr.Progress = gr.Progress(track_tqdm=False),
) -> Image.Image:
    if not isinstance(prompt, str) or len(prompt.strip()) == 0:
        raise gr.Error("Prompt vacío.")
    if steps < 1 or steps > 150:
        raise gr.Error("Número de pasos inválido.")
    if min(width, height) < 256 or max(width, height) > 1536:
        raise gr.Error("Dimensiones fuera de rango.")
    pipe, device = load_t2i_pipeline(model_id)
    g = torch.Generator(device=device).manual_seed(int(seed))
    progress(0.2)
    out = pipe(
        prompt=prompt,
        negative_prompt=negative or None,
        height=int(height),
        width=int(width),
        num_inference_steps=int(steps),
        guidance_scale=float(guidance),
        generator=g,
    )
    progress(0.95)
    return out.images[0]


def build_ui() -> gr.Blocks:
    default_text_model = os.getenv("TEXT_MODEL", "distilgpt2")
    default_diffusion_model = os.getenv("DIFF_MODEL", "stabilityai/stable-diffusion-2-1")

    with gr.Blocks(title="Gradio Integration: LLM + Diffusers") as demo:
        gr.Markdown("## LLM Text Generation y Text-to-Image")

        with gr.Tabs():
            with gr.TabItem("Text Generation"):
                with gr.Row():
                    prompt_in = gr.Textbox(label="Prompt", lines=6, placeholder="Escribe tu prompt...")
                with gr.Row():
                    model_dd = gr.Textbox(label="Model", value=default_text_model)
                with gr.Row():
                    max_new = gr.Slider(1, 256, value=64, step=1, label="Max New Tokens")
                    temperature = gr.Slider(0.01, 2.0, value=0.8, step=0.01, label="Temperature")
                with gr.Row():
                    top_p = gr.Slider(0.1, 1.0, value=0.95, step=0.01, label="Top-p")
                    top_k = gr.Slider(0, 100, value=50, step=1, label="Top-k")
                    do_sample = gr.Checkbox(value=True, label="Sampling")
                out_text = gr.Textbox(label="Salida", lines=10)
                btn_gen = gr.Button("Generar Texto")
                btn_gen.click(
                    fn=generate_text,
                    inputs=[prompt_in, model_dd, max_new, temperature, top_p, top_k, do_sample],
                    outputs=out_text,
                )

            with gr.TabItem("Text-to-Image"):
                with gr.Row():
                    t2i_prompt = gr.Textbox(label="Prompt", lines=4)
                with gr.Row():
                    t2i_negative = gr.Textbox(label="Negative Prompt", lines=2)
                with gr.Row():
                    model_id = gr.Textbox(label="Model", value=default_diffusion_model)
                with gr.Row():
                    steps = gr.Slider(5, 75, value=25, step=1, label="Steps")
                    guidance = gr.Slider(0.0, 15.0, value=7.0, step=0.1, label="Guidance")
                with gr.Row():
                    width = gr.Slider(256, 1024, value=768, step=8, label="Width")
                    height = gr.Slider(256, 1024, value=768, step=8, label="Height")
                with gr.Row():
                    seed = gr.Number(value=42, label="Seed")
                img_out = gr.Image(label="Imagen", type="pil")
                btn_img = gr.Button("Generar Imagen")
                btn_img.click(
                    fn=txt2img,
                    inputs=[t2i_prompt, t2i_negative, model_id, steps, guidance, width, height, seed],
                    outputs=img_out,
                )

    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.queue(concurrency_count=2).launch(server_name=os.getenv("HOST", "0.0.0.0"), server_port=int(os.getenv("PORT", "7860")))



