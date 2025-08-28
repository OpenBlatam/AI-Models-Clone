from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Tuple

import gradio as gr
import numpy as np
import torch
import torch.nn as nn
from PIL import Image


def get_device_and_dtype() -> tuple[str, torch.dtype]:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    use_fp16 = bool(int(os.getenv("FP16", "1"))) and device == "cuda"
    return device, (torch.float16 if use_fp16 else torch.float32)


class TinyMLP(nn.Module):
    def __init__(self, in_dim: int, hidden: int, classes: int) -> None:
        super().__init__()
        self.net = nn.Sequential(nn.Linear(in_dim, hidden), nn.ReLU(), nn.Linear(hidden, classes))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


@lru_cache(maxsize=1)
def load_classifier() -> tuple[TinyMLP, str, int, int]:
    device, _ = get_device_and_dtype()
    in_dim = int(os.getenv("CLS_IN", "16"))
    hidden = int(os.getenv("CLS_HID", "64"))
    classes = int(os.getenv("CLS_CLASSES", "4"))
    model = TinyMLP(in_dim, hidden, classes).to(device)
    model.eval()
    torch.manual_seed(0)
    # Randomly initialize; for demo we won't train. Probabilities still sum to 1.
    return model, device, in_dim, classes


def classify_vector(vec_text: str) -> dict:
    model, device, in_dim, classes = load_classifier()
    try:
        values = [float(x.strip()) for x in vec_text.split(",") if x.strip()]
    except Exception:
        raise gr.Error("Vector inválido. Usa números separados por coma.")
    if len(values) != in_dim:
        raise gr.Error(f"Se esperaban {in_dim} elementos, recibidos {len(values)}")
    x = torch.tensor(values, dtype=torch.float32, device=device).unsqueeze(0)
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=-1).squeeze(0).cpu().numpy().tolist()
    pred = int(np.argmax(probs))
    return {"pred": pred, "probs": {str(i): float(p) for i, p in enumerate(probs)}}


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
    try:
        pipe.enable_attention_slicing()
        pipe.enable_vae_slicing()
    except Exception:
        pass
    return pipe, device


def t2i_gallery(prompt: str, negative: str, model_id: str, steps: int, guidance: float, width: int, height: int, seed: int, count: int) -> List[Image.Image]:
    if not prompt.strip():
        raise gr.Error("Prompt vacío.")
    count = max(1, min(int(count), 6))
    pipe, device = load_t2i_pipeline(model_id)
    g = torch.Generator(device=device).manual_seed(int(seed))
    images: List[Image.Image] = []
    for i in range(count):
        out = pipe(
            prompt=prompt,
            negative_prompt=negative or None,
            height=int(height),
            width=int(width),
            num_inference_steps=int(steps),
            guidance_scale=float(guidance),
            generator=g,
        )
        images.append(out.images[0])
    return images


def build_ui() -> gr.Blocks:
    default_diffusion_model = os.getenv("DIFF_MODEL", "stabilityai/stable-diffusion-2-1")
    with gr.Blocks(title="Gradio Showcase: Classification + Text-to-Image") as demo:
        gr.Markdown("## Demos Interactivos")
        with gr.Tabs():
            with gr.TabItem("Clasificador (Vector)"):
                gr.Markdown("Ingresa un vector de longitud fija (coma separada)")
                vec = gr.Textbox(label="Vector (ej: 0.1, -0.2, ...)")
                out = gr.JSON(label="Predicción y Probabilidades")
                btn = gr.Button("Clasificar")
                btn.click(classify_vector, inputs=[vec], outputs=[out])

            with gr.TabItem("Text-to-Image (Galería)"):
                prompt = gr.Textbox(label="Prompt", lines=3)
                negative = gr.Textbox(label="Negative Prompt", lines=2)
                model_id = gr.Textbox(label="Model", value=default_diffusion_model)
                with gr.Row():
                    steps = gr.Slider(5, 75, value=25, step=1, label="Steps")
                    guidance = gr.Slider(0.0, 15.0, value=7.0, step=0.1, label="Guidance")
                with gr.Row():
                    width = gr.Slider(256, 1024, value=768, step=8, label="Width")
                    height = gr.Slider(256, 1024, value=768, step=8, label="Height")
                with gr.Row():
                    seed = gr.Number(value=123, label="Seed")
                    count = gr.Slider(1, 6, value=3, step=1, label="Images")
                gallery = gr.Gallery(label="Resultados", columns=3, height=400)
                gen = gr.Button("Generar")
                gen.click(t2i_gallery, inputs=[prompt, negative, model_id, steps, guidance, width, height, seed, count], outputs=gallery)
    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.queue(concurrency_count=2).launch(server_name=os.getenv("HOST", "0.0.0.0"), server_port=int(os.getenv("PORT", "7861")))



