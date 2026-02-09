from __future__ import annotations

import os

from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)
from peft import LoraConfig, PromptTuningConfig, TaskType, get_peft_model


def main() -> None:
    model_name = os.getenv("MODEL", "distilgpt2")
    method = os.getenv("METHOD", "lora").lower()  # "lora" or "prompt"
    out_dir = os.getenv("OUT", "outputs/peft_min")
    steps = int(os.getenv("STEPS", "200"))
    bs = int(os.getenv("BS", "8"))
    accum = int(os.getenv("ACCUM", "2"))
    lr = float(os.getenv("LR", "2e-4"))
    fp16 = bool(int(os.getenv("FP16", "1")))
    bf16 = bool(int(os.getenv("BF16", "0")))

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token or tokenizer.unk_token

    base_model = AutoModelForCausalLM.from_pretrained(model_name)
    if method == "lora":
        peft_cfg = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=8,
            lora_alpha=16,
            lora_dropout=0.05,
            inference_mode=False,
        )
    else:
        peft_cfg = PromptTuningConfig(
            task_type=TaskType.CAUSAL_LM,
            num_virtual_tokens=20,
            prompt_tuning_init="RANDOM",
        )
    model = get_peft_model(base_model, peft_cfg)
    model.print_trainable_parameters()

    ds = load_dataset("wikitext", "wikitext-2-raw-v1")

    def tok(batch):
        return tokenizer(batch["text"], truncation=True, padding=False)

    tokenized = ds.map(tok, batched=True, remove_columns=ds["train"].column_names)
    collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

    args = TrainingArguments(
        output_dir=out_dir,
        per_device_train_batch_size=bs,
        per_device_eval_batch_size=bs,
        gradient_accumulation_steps=accum,
        learning_rate=lr,
        weight_decay=0.01,
        max_steps=steps,
        logging_steps=50,
        evaluation_strategy="steps",
        eval_steps=100,
        save_steps=100,
        save_total_limit=2,
        fp16=fp16,
        bf16=bf16,
        report_to=["tensorboard"],
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized.get("validation"),
        data_collator=collator,
    )
    trainer.train()

    model.save_pretrained(os.path.join(out_dir, f"{method}_adapter"))
    try:
        merged = model.merge_and_unload()
        merged.save_pretrained(os.path.join(out_dir, f"{method}_merged"))
        tokenizer.save_pretrained(os.path.join(out_dir, f"{method}_merged"))
    except Exception:
        pass


if __name__ == "__main__":
    main()



