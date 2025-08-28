from __future__ import annotations

import os
from typing import List

import torch
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer


def get_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_tokenizer(model_name: str) -> AutoTokenizer:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token or tokenizer.unk_token
    return tokenizer


@torch.no_grad()
def encode_texts(texts: List[str], model_name: str = "distilbert-base-uncased", max_length: int = 256) -> torch.Tensor:
    tokenizer = load_tokenizer(model_name)
    encoder = AutoModel.from_pretrained(model_name).to(get_device()).eval()
    batch = tokenizer(texts, padding=True, truncation=True, max_length=max_length, return_tensors="pt").to(get_device())
    outputs = encoder(**batch).last_hidden_state  # [B, T, H]
    mask = batch["attention_mask"].unsqueeze(-1)  # [B, T, 1]
    pooled = (outputs * mask).sum(dim=1) / mask.sum(dim=1).clamp_min(1)
    return pooled  # [B, H]


@torch.no_grad()
def generate_texts(
    prompts: List[str],
    model_name: str = "distilgpt2",
    max_new_tokens: int = 64,
    temperature: float = 0.8,
    top_p: float = 0.95,
    top_k: int = 50,
) -> List[str]:
    tokenizer = load_tokenizer(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(get_device()).eval()
    batch = tokenizer(prompts, padding=True, truncation=True, max_length=256, return_tensors="pt").to(get_device())
    outputs = model.generate(
        **batch,
        max_new_tokens=int(max_new_tokens),
        do_sample=True,
        temperature=max(0.01, float(temperature)),
        top_p=float(top_p),
        top_k=int(top_k),
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    return [tokenizer.decode(ids, skip_special_tokens=True) for ids in outputs]


if __name__ == "__main__":
    embs = encode_texts(["Transformers provide transfer learning.", "Embeddings represent semantics."])
    print("embeddings_shape", list(embs.shape))
    texts = generate_texts(["Hello, world!", "In a future where AI"], max_new_tokens=32)
    print("\n".join(texts))



