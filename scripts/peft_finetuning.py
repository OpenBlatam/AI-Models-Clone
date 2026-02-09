from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Optional

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

try:
    from peft import LoraConfig, PromptTuningConfig, TaskType, get_peft_model, PeftModel
except Exception as e:  # pragma: no cover
    raise RuntimeError("peft is required: pip install peft") from e


@dataclass
class FinetuneCfg:
    model_name: str = "distilgpt2"
    dataset_name: str = "wikitext"
    dataset_config: str = "wikitext-2-raw-v1"
    method: str = "lora"  # lora | prompt
    output_dir: str = "outputs/peft"
    max_steps: int = 200
    warmup_steps: int = 20
    lr: float = 2e-4
    weight_decay: float = 0.01
    batch_size: int = 8
    grad_accum: int = 2
    fp16: bool = True
    bf16: bool = False
    save_steps: int = 100
    logging_steps: int = 10
    seed: int = 42
    # LoRA
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: Optional[str] = None  # comma separated, e.g. c_attn,c_proj
    # Prompt Tuning
    prompt_tuning_num_tokens: int = 20


def build_peft_model(cfg: FinetuneCfg, base: AutoModelForCausalLM) -> PeftModel:
    if cfg.method.lower() == "lora":
        target_modules = None
        if cfg.target_modules:
            target_modules = [m.strip() for m in cfg.target_modules.split(",") if m.strip()]
        lora = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=cfg.lora_r,
            lora_alpha=cfg.lora_alpha,
            lora_dropout=cfg.lora_dropout,
            target_modules=target_modules,
        )
        return get_peft_model(base, lora)
    elif cfg.method.lower() in {"prompt", "prompt_tuning"}:
        pt = PromptTuningConfig(
            task_type=TaskType.CAUSAL_LM,
            prompt_tuning_init="RANDOM",
            num_virtual_tokens=cfg.prompt_tuning_num_tokens,
        )
        return get_peft_model(base, pt)
    else:
        raise ValueError(f"Unknown method: {cfg.method}")


def main() -> None:
    ap = argparse.ArgumentParser(description="PEFT LoRA / Prompt Tuning fine-tuning")
    ap.add_argument("--model", type=str, default="distilgpt2")
    ap.add_argument("--dataset", type=str, default="wikitext")
    ap.add_argument("--dataset-config", type=str, default="wikitext-2-raw-v1")
    ap.add_argument("--method", type=str, default="lora")
    ap.add_argument("--out", type=str, default="outputs/peft")
    ap.add_argument("--max-steps", type=int, default=200)
    ap.add_argument("--warmup-steps", type=int, default=20)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--weight-decay", type=float, default=0.01)
    ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--accum", type=int, default=2)
    ap.add_argument("--fp16", action="store_true")
    ap.add_argument("--bf16", action="store_true")
    ap.add_argument("--save-steps", type=int, default=100)
    ap.add_argument("--logging-steps", type=int, default=10)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--lora-alpha", type=int, default=32)
    ap.add_argument("--lora-dropout", type=float, default=0.05)
    ap.add_argument("--target-modules", type=str, default="")
    ap.add_argument("--prompt-tokens", type=int, default=20)
    args = ap.parse_args()

    cfg = FinetuneCfg(
        model_name=args.model,
        dataset_name=args.dataset,
        dataset_config=args.dataset_config,
        method=args.method,
        output_dir=args.out,
        max_steps=args.max_steps,
        warmup_steps=args.warmup_steps,
        lr=args.lr,
        weight_decay=args.weight_decay,
        batch_size=args.bs,
        grad_accum=args.accum,
        fp16=args.fp16,
        bf16=args.bf16,
        save_steps=args.save_steps,
        logging_steps=args.logging_steps,
        seed=args.seed,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=(args.target_modules or None),
        prompt_tuning_num_tokens=args.prompt_tokens,
    )

    tok = AutoTokenizer.from_pretrained(cfg.model_name)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token

    base = AutoModelForCausalLM.from_pretrained(cfg.model_name)
    model = build_peft_model(cfg, base)
    model.print_trainable_parameters()

    ds = load_dataset(cfg.dataset_name, cfg.dataset_config)
    def tokenize_fn(batch):
        return tok(batch["text"], truncation=True, padding=False)
    tokenized = ds.map(tokenize_fn, batched=True, num_proc=1, remove_columns=ds["train"].column_names)

    collator = DataCollatorForLanguageModeling(tok, mlm=False)

    training_args = TrainingArguments(
        output_dir=cfg.output_dir,
        per_device_train_batch_size=cfg.batch_size,
        per_device_eval_batch_size=cfg.batch_size,
        gradient_accumulation_steps=cfg.grad_accum,
        learning_rate=cfg.lr,
        weight_decay=cfg.weight_decay,
        warmup_steps=cfg.warmup_steps,
        max_steps=cfg.max_steps,
        evaluation_strategy="steps",
        eval_steps=cfg.logging_steps,
        logging_steps=cfg.logging_steps,
        save_steps=cfg.save_steps,
        save_total_limit=2,
        fp16=cfg.fp16,
        bf16=cfg.bf16,
        dataloader_num_workers=2,
        report_to=["tensorboard"],
        seed=cfg.seed,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized.get("validation", None),
        data_collator=collator,
    )

    trainer.train()

    os.makedirs(cfg.output_dir, exist_ok=True)
    # save PEFT adapters
    model.save_pretrained(os.path.join(cfg.output_dir, f"{cfg.method}_adapter"))

    # optionally merge and save full model
    try:
        merged = model.merge_and_unload()
        merged.save_pretrained(os.path.join(cfg.output_dir, f"{cfg.method}_merged"))
        tok.save_pretrained(os.path.join(cfg.output_dir, f"{cfg.method}_merged"))
    except Exception:
        pass


if __name__ == "__main__":
    main()



