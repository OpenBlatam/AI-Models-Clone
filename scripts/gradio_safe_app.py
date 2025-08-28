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


def guarded_generate(prompt: str, model_name: str, max_new_tokens: int) -> str:
    if not isinstance(prompt, str) or len(prompt.strip()) == 0:
        raise gr.Error("Prompt vacío.")
    if max_new_tokens < 1 or max_new_tokens > 256:
        raise gr.Error("max_new_tokens fuera de rango [1, 256].")
    tok, model = load_text_model(model_name)
    try:
        inputs = tok(prompt, return_tensors="pt").to(get_device())
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=int(max_new_tokens), pad_token_id=tok.pad_token_id)
        return tok.decode(outputs[0], skip_special_tokens=True)
    except RuntimeError as e:
        if "CUDA out of memory" in str(e):
            raise gr.Error("Memoria GPU insuficiente. Reduce max_new_tokens.")
        raise gr.Error(f"Error en generación: {e}")


def build_ui() -> gr.Blocks:
    default_model = os.getenv("TEXT_MODEL", "distilgpt2")
    with gr.Blocks(title="Gradio Safe App") as demo:
        gr.Markdown("## Generación de Texto (Seguro)")
        prompt = gr.Textbox(label="Prompt", lines=5)
        model = gr.Textbox(label="Model", value=default_model)
        max_new = gr.Slider(1, 256, value=64, step=1, label="Max New Tokens")
        out = gr.Textbox(label="Salida", lines=10)
        btn = gr.Button("Generar")
        btn.click(guarded_generate, inputs=[prompt, model, max_new], outputs=out)
    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.launch(server_name=os.getenv("HOST", "0.0.0.0"), server_port=int(os.getenv("PORT", "7862")))



