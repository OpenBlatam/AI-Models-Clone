from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

import gradio as gr
import torch
from pydantic import BaseModel, Field, ValidationError, conint, confloat, constr
from transformers import AutoModelForCausalLM, AutoTokenizer


def get_device_and_dtype() -> tuple[str, torch.dtype]:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    use_fp16 = bool(int(os.getenv("FP16", "1"))) and device == "cuda"
    return device, (torch.float16 if use_fp16 else torch.float32)


class LLMRequest(BaseModel):
    prompt: constr(strip_whitespace=True, min_length=1, max_length=4000)
    model_name: constr(strip_whitespace=True, min_length=1) = Field(default="distilgpt2")
    max_new_tokens: conint(ge=1, le=512) = 128
    temperature: confloat(ge=0.01, le=2.0) = 0.8
    top_p: confloat(ge=0.1, le=1.0) = 0.95
    top_k: conint(ge=0, le=200) = 50
    do_sample: bool = True


class T2IRequest(BaseModel):
    prompt: constr(strip_whitespace=True, min_length=1, max_length=600)
    negative: Optional[str] = None
    model_id: constr(strip_whitespace=True, min_length=1) = Field(default="stabilityai/stable-diffusion-2-1")
    steps: conint(ge=5, le=100) = 30
    guidance: confloat(ge=0.0, le=15.0) = 7.0
    width: conint(ge=256, le=1536) = 768
    height: conint(ge=256, le=1536) = 768
    seed: int = 42


@lru_cache(maxsize=1)
def load_lm(model_name: str):
    tok = AutoTokenizer.from_pretrained(model_name)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token or tok.unk_token
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model = model.to(get_device_and_dtype()[0]).eval()
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
    try:
        req = LLMRequest(
            prompt=prompt,
            model_name=model_name,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            do_sample=do_sample,
        )
    except ValidationError as e:
        raise gr.Error(e.errors()[0]["msg"])  # first error message

    tok, model = load_lm(req.model_name)
    device, _ = get_device_and_dtype()
    x = tok(req.prompt, return_tensors="pt").to(device)
    try:
        with torch.no_grad():
            progress(0.3)
            y = model.generate(
                **x,
                max_new_tokens=int(req.max_new_tokens),
                do_sample=bool(req.do_sample),
                temperature=float(req.temperature),
                top_p=float(req.top_p),
                top_k=int(req.top_k),
                pad_token_id=tok.pad_token_id,
                eos_token_id=tok.eos_token_id,
            )
            progress(0.95)
        return tok.decode(y[0], skip_special_tokens=True)
    except RuntimeError as e:
        msg = str(e)
        if "CUDA out of memory" in msg:
            raise gr.Error("GPU sin memoria. Reduce max_new_tokens o usa un modelo más pequeño.")
        raise gr.Error(f"Error de generación: {msg}")
    except Exception as e:
        raise gr.Error(f"Fallo inesperado: {e}")


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


@lru_cache(maxsize=2)
def load_t2i(model_id: str):  # type: ignore[no-untyped-def]
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


def t2i_generate(
    prompt: str,
    negative: str,
    model_id: str,
    steps: int,
    guidance: float,
    width: int,
    height: int,
    seed: int,
    progress: gr.Progress = gr.Progress(track_tqdm=False),
):
    try:
        req = T2IRequest(
            prompt=prompt,
            negative=negative or None,
            model_id=model_id,
            steps=steps,
            guidance=guidance,
            width=width,
            height=height,
            seed=seed,
        )
    except ValidationError as e:
        raise gr.Error(e.errors()[0]["msg"])  # first error

    # enforce multiple-of-8 sizes for better performance
    if req.width % 8 != 0 or req.height % 8 != 0:
        raise gr.Error("Width y Height deben ser múltiplos de 8.")

    pipe, device = load_t2i(req.model_id)
    gen = torch.Generator(device=device).manual_seed(int(req.seed))
    try:
        progress(0.3)
        out = pipe(
            prompt=req.prompt,
            negative_prompt=req.negative,
            height=int(req.height),
            width=int(req.width),
            num_inference_steps=int(req.steps),
            guidance_scale=float(req.guidance),
            generator=gen,
        )
        progress(0.95)
        return out.images[0]
    except RuntimeError as e:
        msg = str(e)
        if "CUDA out of memory" in msg:
            raise gr.Error("GPU sin memoria. Reduce Steps o resolución.")
        raise gr.Error(f"Error de inferencia: {msg}")
    except Exception as e:
        raise gr.Error(f"Fallo inesperado: {e}")


def build_ui() -> gr.Blocks:
    default_text_model = os.getenv("TEXT_MODEL", "distilgpt2")
    default_diff_model = os.getenv("DIFF_MODEL", "stabilityai/stable-diffusion-2-1")

    with gr.Blocks(title="Validación y Manejo de Errores (Gradio)") as demo:
        with gr.Tabs():
            with gr.TabItem("LLM Seguro"):
                prompt = gr.Textbox(label="Prompt", lines=6)
                model = gr.Textbox(label="Model", value=default_text_model)
                max_new = gr.Slider(1, 512, value=128, step=1, label="Max New Tokens")
                temperature = gr.Slider(0.01, 2.0, value=0.8, step=0.01, label="Temperature")
                top_p = gr.Slider(0.1, 1.0, value=0.95, step=0.01, label="Top-p")
                top_k = gr.Slider(0, 200, value=50, step=1, label="Top-k")
                do_sample = gr.Checkbox(value=True, label="Sampling")
                out = gr.Textbox(label="Salida", lines=10)
                gr.Button("Generar").click(
                    llm_generate,
                    inputs=[prompt, model, max_new, temperature, top_p, top_k, do_sample],
                    outputs=out,
                )

            with gr.TabItem("Text-to-Image Seguro"):
                t_prompt = gr.Textbox(label="Prompt", lines=4)
                t_negative = gr.Textbox(label="Negative Prompt", lines=2)
                t_model = gr.Textbox(label="Model", value=default_diff_model)
                steps = gr.Slider(5, 100, value=30, step=1, label="Steps")
                guidance = gr.Slider(0.0, 15.0, value=7.0, step=0.1, label="Guidance")
                width = gr.Slider(256, 1536, value=768, step=8, label="Width")
                height = gr.Slider(256, 1536, value=768, step=8, label="Height")
                seed = gr.Number(value=42, label="Seed")
                img = gr.Image(label="Imagen", type="pil")
                gr.Button("Generar Imagen").click(
                    t2i_generate,
                    inputs=[t_prompt, t_negative, t_model, steps, guidance, width, height, seed],
                    outputs=img,
                )

    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.queue(concurrency_count=2).launch(server_name=os.getenv("HOST", "0.0.0.0"), server_port=int(os.getenv("PORT", "7864")))



