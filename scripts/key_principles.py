from __future__ import annotations

import textwrap


def main() -> None:
    print(
        textwrap.dedent(
            """
            project:
              name: my_project
              seed: 42
            conventions:
              - concise_technical_code
              - OOP_for_models
              - functional_data_pipelines
              - gpu_amp_when_available
              - descriptive_variable_names
              - pep8
            structure:
              src: [models, data, training, evaluation, utils]
              scripts: [training, profiling, demos, project_init]
              config: [train.yaml]
              checkpoints: true
              experiments: true
            training:
              features:
                - amp
                - grad_accumulation
                - grad_clipping
                - lr_scheduling
                - early_stopping
                - tensorboard_wandb
            transformers:
              - correct_tokenization
              - masking_and_padding
              - efficient_finetuning_lora_prompt
            diffusion:
              - sdxl_sd15_pipelines
              - schedulers_and_samplers
              - memory_optimizations
            mlops:
              - yaml_configs
              - experiment_tracking
              - checkpointing
              - version_control
            """
        ).strip()
    )


if __name__ == "__main__":
    main()

from __future__ import annotations

import sys
import yaml


KEY_PRINCIPLES = {
    "general": [
        "Concise, correct, and production-oriented code",
        "OOP for models; functional for data pipelines",
        "PEP8 style; descriptive variable names",
        "Determinism when needed: seeds and reproducibility",
    ],
    "deep_learning": [
        "Custom nn.Module architectures with clear forward APIs",
        "Proper weight init (Kaiming/Xavier/Orthogonal) and normalization",
        "Appropriate loss functions per task (CE/BCE/Dice/Huber)",
        "Optimizers: AdamW/SGD with correct weight decay and schedulers",
    ],
    "transformers_llms": [
        "Use HuggingFace Transformers (Auto* classes) and datasets",
        "Correct attention masking and positional encodings (RoPE/Sinusoidal)",
        "Efficient finetuning (LoRA/PEFT, prompt-tuning) when applicable",
        "Correct tokenization, packing, padding, truncation",
    ],
    "diffusion_models": [
        "Use Diffusers pipelines (SD 1.5/SDXL) with appropriate schedulers",
        "Understand forward/reverse diffusion, noise schedules, UNet blocks",
        "Choose samplers (DDPM/DDIM/DPMSolver) per quality/speed targets",
        "Safe memory configs (fp16/bf16, xformers, attention slicing)",
    ],
    "training_evaluation": [
        "Efficient DataLoader (pin_memory, workers, prefetch, persistent)",
        "Train/val/test splits; K-Fold when needed",
        "Early stopping; LR warmup + cosine/one-cycle; gradient clipping",
        "Task-appropriate metrics with clear logging",
    ],
    "gradio_integration": [
        "Lazy model loading; clear UX; validated inputs",
        "Use gr.Error/gr.Warning for user-facing failures",
        "Non-blocking handlers for heavy inference",
    ],
    "error_debugging": [
        "Try/except around IO/inference; structured logging",
        "torch.autograd.set_detect_anomaly for debugging only",
        "NaN/Inf guards; nan_to_num; isfinite checks",
    ],
    "performance_optimization": [
        "AMP (fp16/bf16), gradient accumulation, channels_last",
        "torch.compile when stable; enable TF32 on Ampere+",
        "DDP or Accelerate for multi-GPU; correct DistributedSampler",
        "Profile data vs compute; optimize hotspots first",
    ],
    "dependencies": [
        "torch, torchvision, transformers, diffusers, accelerate, safetensors",
        "numpy, datasets, scikit-learn, pillow, tqdm",
        "tensorboard, wandb, gradio, pyyaml",
    ],
    "conventions": [
        "Config-driven (YAML) hyperparameters and settings",
        "Experiment tracking + checkpointing with top-K monitor",
        "CI for lint/tests; version control required",
        "Modular project layout: data/models/training/eval/utils",
    ],
}


def main() -> None:
    yaml.safe_dump(KEY_PRINCIPLES, sys.stdout, sort_keys=True, allow_unicode=True)


if __name__ == "__main__":
    main()


