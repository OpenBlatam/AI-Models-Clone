from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

import torch
from transformers import (
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    DataCollatorForSeq2Seq,
    PreTrainedTokenizerBase,
)


def prepare_tokenizer(model_name: str) -> AutoTokenizer:
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token if tokenizer.eos_token else tokenizer.unk_token
    # For decoder-only LMs, right padding is fine for training. Left padding may be preferred for batched inference.
    tokenizer.padding_side = os.getenv("PADDING_SIDE", "right")
    return tokenizer


def tokenize_texts(
    tokenizer: PreTrainedTokenizerBase,
    texts: Sequence[str],
    *,
    max_length: int,
    truncation: bool = True,
) -> Dict[str, List[List[int]]]:
    encoded = tokenizer(
        list(texts),
        truncation=truncation,
        max_length=max_length,
        padding=False,
        return_attention_mask=True,
        return_token_type_ids=False,
    )
    return {k: list(v) for k, v in encoded.items()}


def pack_for_causal_lm(
    input_id_sequences: Iterable[Sequence[int]],
    *,
    block_size: int,
    pad_token_id: int,
) -> Dict[str, List[List[int]]]:
    # Concatenate all tokens and split into fixed-size blocks to minimize padding.
    flat: List[int] = []
    for seq in input_id_sequences:
        flat.extend(seq)
    # Drop remainder for simplicity. Optionally, pad the tail to block_size.
    total_len = (len(flat) // block_size) * block_size
    flat = flat[:total_len]
    input_blocks = [flat[i : i + block_size] for i in range(0, total_len, block_size)]

    # Labels are the same as inputs for next-token prediction; attention mask is all ones.
    attention = [[1] * block_size for _ in range(len(input_blocks))]
    labels = [list(block) for block in input_blocks]

    if not input_blocks:
        input_blocks = [[pad_token_id] * block_size]
        attention = [[0] * block_size]
        labels = [[-100] * block_size]

    return {
        "input_ids": input_blocks,
        "attention_mask": attention,
        "labels": labels,
    }


@dataclass
class Seq2SeqBatch:
    input_ids: torch.Tensor
    attention_mask: torch.Tensor
    labels: torch.Tensor


def build_causal_lm_collator(tokenizer: PreTrainedTokenizerBase) -> DataCollatorForLanguageModeling:
    # Uses -100 to mask loss on padding per HF convention
    return DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)


def build_seq2seq_collator(tokenizer: PreTrainedTokenizerBase) -> DataCollatorForSeq2Seq:
    return DataCollatorForSeq2Seq(tokenizer=tokenizer, label_pad_token_id=-100, pad_to_multiple_of=8)


def example_usage() -> None:
    # Minimal, dependency-light demo with tiny inputs
    model_name = os.getenv("MODEL", "distilgpt2")
    tokenizer = prepare_tokenizer(model_name)

    # Causal LM: tokenize and pack
    raw_texts = [
        "Transformers are powerful models for sequence transduction.",
        "Tokenization and proper padding significantly affect performance.",
        "Sequence packing reduces padding and improves throughput.",
    ]
    tokenized = tokenize_texts(tokenizer, raw_texts, max_length=int(os.getenv("MAX_LEN", "256")))
    packed = pack_for_causal_lm(tokenized["input_ids"], block_size=int(os.getenv("BLOCK", "128")), pad_token_id=tokenizer.pad_token_id)

    # Convert to tensors for a training step
    input_ids = torch.tensor(packed["input_ids"], dtype=torch.long)
    attention_mask = torch.tensor(packed["attention_mask"], dtype=torch.long)
    labels = torch.tensor(packed["labels"], dtype=torch.long)
    _ = (input_ids, attention_mask, labels)

    # Seq2Seq: demonstrate proper dynamic padding and label masking
    sources = ["Summarize: Transformers improve NLP.", "Summarize: Proper tokenization boosts accuracy."]
    targets = ["Transformers improve NLP.", "Proper tokenization boosts accuracy."]

    inputs = tokenizer(sources, padding=True, truncation=True, max_length=128, return_tensors="pt")
    with tokenizer.as_target_tokenizer():
        labels_enc = tokenizer(targets, padding=True, truncation=True, max_length=64, return_tensors="pt")

    # Replace pad token ids in labels with -100 to ignore in loss
    labels_enc["input_ids"][labels_enc["input_ids"] == tokenizer.pad_token_id] = -100

    batch = Seq2SeqBatch(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        labels=labels_enc["input_ids"],
    )
    _ = batch


if __name__ == "__main__":
    example_usage()

from __future__ import annotations

from typing import List, Tuple, Dict

import torch
from torch.utils.data import DataLoader
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoModelForSeq2SeqLM,
    DataCollatorForLanguageModeling,
    DataCollatorForSeq2Seq,
)


def build_causal_lm_packed_dataset(texts: List[str], tokenizer, block_size: int = 512) -> Dataset:
    tokenized = tokenizer(texts, add_special_tokens=True, return_attention_mask=False)
    input_ids: List[int] = []
    for ids in tokenized["input_ids"]:
        input_ids.extend(ids + [tokenizer.eos_token_id])
    # chunk into fixed blocks
    total_len = (len(input_ids) // block_size) * block_size
    input_ids = input_ids[:total_len]
    blocks = [input_ids[i : i + block_size] for i in range(0, total_len, block_size)]
    return Dataset.from_dict({"input_ids": blocks})


def build_seq2seq_dataset(pairs: List[Tuple[str, str]], tokenizer, max_src: int = 256, max_tgt: int = 128) -> Dataset:
    sources, targets = zip(*pairs)
    model_inputs = tokenizer(
        list(sources),
        max_length=max_src,
        truncation=True,
        padding=False,
        return_attention_mask=True,
    )
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            list(targets),
            max_length=max_tgt,
            truncation=True,
            padding=False,
            return_attention_mask=False,
        )
    model_inputs["labels"] = labels["input_ids"]
    return Dataset.from_dict(model_inputs)


def main() -> None:
    device = torch.device("cuda", 0) if torch.cuda.is_available() else torch.device("cpu")

    # Causal LM tokenization (packing into fixed blocks)
    lm_name = "distilgpt2"
    lm_tok = AutoTokenizer.from_pretrained(lm_name)
    if lm_tok.pad_token_id is None:
        lm_tok.pad_token = lm_tok.eos_token
    texts = [
        "Efficient DataLoader uses pin_memory and workers.",
        "Use AMP for mixed precision training on CUDA.",
        "Gradient accumulation simulates large batch sizes.",
    ]
    causal_ds = build_causal_lm_packed_dataset(texts, lm_tok, block_size=128)
    lm_model = AutoModelForCausalLM.from_pretrained(lm_name).to(device)
    causal_collator = DataCollatorForLanguageModeling(lm_tok, mlm=False)
    causal_dl = DataLoader(causal_ds, batch_size=4, shuffle=True, collate_fn=causal_collator)

    batch = next(iter(causal_dl))
    batch = {k: v.to(device) for k, v in batch.items()}
    with torch.no_grad():
        lm_out = lm_model(**batch)
    print({"causal_lm_batch_shape": tuple(batch["input_ids"].shape), "loss": float(lm_out.loss)})

    # Seq2Seq tokenization (source/target with dynamic padding)
    mt_name = "t5-small"
    mt_tok = AutoTokenizer.from_pretrained(mt_name)
    pairs = [
        ("Translate English to German: PyTorch is fast.", "Pytorch ist schnell."),
        ("Translate English to German: Mixed precision is useful.", "Gemischte Präzision ist nützlich."),
    ]
    s2s_ds = build_seq2seq_dataset(pairs, mt_tok, max_src=64, max_tgt=64)
    s2s_model = AutoModelForSeq2SeqLM.from_pretrained(mt_name).to(device)
    s2s_collator = DataCollatorForSeq2Seq(tokenizer=mt_tok, model=s2s_model)
    s2s_dl = DataLoader(s2s_ds, batch_size=2, shuffle=False, collate_fn=s2s_collator)

    batch2 = next(iter(s2s_dl))
    batch2 = {k: v.to(device) for k, v in batch2.items()}
    with torch.no_grad():
        s2s_out = s2s_model(**batch2)
    print({
        "seq2seq_input_shape": tuple(batch2["input_ids"].shape),
        "labels_shape": tuple(batch2["labels"].shape),
        "loss": float(s2s_out.loss),
    })


if __name__ == "__main__":
    main()


