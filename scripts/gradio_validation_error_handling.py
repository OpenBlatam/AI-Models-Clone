from __future__ import annotations

import os
import re
import traceback
from functools import lru_cache, wraps
from typing import Optional

import gradio as gr
import torch
from pydantic import BaseModel, Field, ValidationError, field_validator
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


def device_idx() -> int:
    return 0 if torch.cuda.is_available() else -1


def amp_dtype() -> Optional[torch.dtype]:
    if torch.cuda.is_available():
        return torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    return None


class TextGenRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    max_new_tokens: int = Field(80, ge=1, le=512)
    temperature: float = Field(0.9, ge=0.1, le=2.0)
    top_p: float = Field(0.95, ge=0.1, le=1.0)

    @field_validator("prompt")
    @classmethod
    def _sanitize_prompt(cls, v: str) -> str:
        v = v.strip()
        # remove control chars
        v = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", " ", v)
        return v


@lru_cache(maxsize=1)
def load_text_pipeline(model_name: str = "distilgpt2") -> pipeline:
    tok = AutoTokenizer.from_pretrained(model_name)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    gen = pipeline(
        "text-generation",
        model=AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=amp_dtype(),
        ),
        tokenizer=tok,
        device=device_idx(),
    )
    return gen


def safe_handler(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValidationError as ve:
            # show first error
            err = ve.errors()[0]
            loc = ".".join(str(x) for x in err.get("loc", [])) or "input"
            msg = err.get("msg", "Invalid input")
            raise gr.Error(f"{loc}: {msg}")
        except gr.Error:
            raise
        except Exception as e:
            # log traceback for server, show concise user error
            traceback.print_exc()
            raise gr.Error("An unexpected error occurred. Please try again with simpler settings.")
    return wrapper


@safe_handler
def generate_text(prompt: str, max_new_tokens: int, temperature: float, top_p: float) -> str:
    req = TextGenRequest(
        prompt=prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    gen = load_text_pipeline()
    outputs = gen(
        req.prompt,
        max_new_tokens=req.max_new_tokens,
        do_sample=True,
        temperature=req.temperature,
        top_p=req.top_p,
        eos_token_id=gen.tokenizer.eos_token_id,
        pad_token_id=gen.tokenizer.eos_token_id,
    )
    return outputs[0]["generated_text"]


def ui() -> gr.Blocks:
    with gr.Blocks(title="Gradio Validation & Error Handling", theme=gr.themes.Soft()) as demo:
        gr.Markdown("### Robust Input Validation and Error Handling")

        with gr.Row():
            with gr.Column():
                prompt = gr.Textbox(label="Prompt", placeholder="Explain gradient clipping in PyTorch.")
                max_new = gr.Slider(16, 512, 80, step=8, label="Max new tokens")
                temperature = gr.Slider(0.1, 2.0, 0.9, step=0.1, label="Temperature")
                top_p = gr.Slider(0.1, 1.0, 0.95, step=0.05, label="Top-p")
                btn = gr.Button("Generate", variant="primary")
            with gr.Column():
                out = gr.Textbox(label="Generated Text", lines=12)
                tips = gr.Markdown(value="Safe defaults: temperature in [0.1, 2.0], top-p in [0.1, 1.0]. Excessive values may degrade quality.")

        btn.click(generate_text, inputs=[prompt, max_new, temperature, top_p], outputs=[out])

        with gr.Accordion("Notes", open=False):
            gr.Markdown("Validation via Pydantic v2; user-facing errors raised with gr.Error; unexpected exceptions sanitized.")
    return demo


if __name__ == "__main__":
    ui().queue(max_size=64).launch(server_name=os.getenv("HOST", "0.0.0.0"), server_port=int(os.getenv("PORT", "7860")))



