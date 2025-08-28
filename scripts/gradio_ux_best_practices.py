from __future__ import annotations

import os
from functools import lru_cache

import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def get_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


@lru_cache(maxsize=1)
def load_text_model(model_name: str):
    tok = AutoTokenizer.from_pretrained(model_name)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token or tok.unk_token
    model = AutoModelForCausalLM.from_pretrained(model_name).to(get_device()).eval()
    return tok, model


def generate(prompt: str, max_new_tokens: int, temperature: float, top_p: float, model_name: str, progress=gr.Progress(track_tqdm=False)) -> str:
    if not prompt.strip():
        gr.Warning("El prompt está vacío; generando con un mensaje por defecto.")
        prompt = "Hola, mundo."
    tok, model = load_text_model(model_name)
    inputs = tok(prompt, return_tensors="pt").to(get_device())
    with torch.no_grad():
        progress(0.2)
        out = model.generate(
            **inputs,
            max_new_tokens=int(max_new_tokens),
            temperature=max(0.01, float(temperature)),
            top_p=float(top_p),
            do_sample=True,
            pad_token_id=tok.pad_token_id,
            eos_token_id=tok.eos_token_id,
        )
        progress(0.95)
    return tok.decode(out[0], skip_special_tokens=True)


def build_ui() -> gr.Blocks:
    default_model = os.getenv("TEXT_MODEL", "distilgpt2")
    with gr.Blocks(title="Gradio UX Best Practices") as demo:
        gr.Markdown("## UX Patterns: Defaults, Feedback, Progress, and Validation")
        with gr.Group():
            prompt = gr.Textbox(label="Prompt", lines=5, placeholder="Escribe algo...")
            with gr.Row():
                max_new = gr.Slider(1, 256, value=64, step=1, label="Max New Tokens")
                temperature = gr.Slider(0.01, 2.0, value=0.8, step=0.01, label="Temperature")
                top_p = gr.Slider(0.1, 1.0, value=0.95, step=0.01, label="Top-p")
            model = gr.Textbox(label="Model", value=default_model)
            btn = gr.Button("Generar")
            out = gr.Textbox(label="Salida", lines=10)
        btn.click(generate, inputs=[prompt, max_new, temperature, top_p, model], outputs=out)
    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.queue(concurrency_count=2).launch(server_name=os.getenv("HOST", "0.0.0.0"), server_port=int(os.getenv("PORT", "7863")))



