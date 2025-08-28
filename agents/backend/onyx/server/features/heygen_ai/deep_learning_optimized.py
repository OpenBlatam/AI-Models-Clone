#!/usr/bin/env python3
"""
Optimized Deep Learning Module
=============================

Production-ready deep learning implementation with:
- PyTorch optimization and multi-GPU training
- Transformers library integration
- Diffusion models with Diffusers
- Gradio interface for demos
- Comprehensive error handling and logging
"""

import os
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from torch.cuda.amp import autocast, GradScaler
from torch.nn.parallel import DataParallel, DistributedDataParallel
from torch.utils.tensorboard import SummaryWriter

import transformers
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForCausalLM,
    TrainingArguments, Trainer, DataCollatorWithPadding,
    get_linear_schedule_with_warmup, get_cosine_schedule_with_warmup
)

import diffusers
from diffusers import (
    StableDiffusionPipeline, StableDiffusionXLPipeline,
    DDIMScheduler, DDPMScheduler, EulerDiscreteScheduler,
    AutoencoderKL, UNet2DConditionModel
)

import gradio as gr
import numpy as np
from tqdm import tqdm
import wandb

# =============================================================================
# Optimized Constants and Configuration
# =============================================================================

@dataclass
class TrainingConfig:
    """Optimized training configuration."""
    # Model settings
    model_name: str = "gpt2"
    max_length: int = 512
    batch_size: int = 8
    gradient_accumulation_steps: int = 4
    
    # Training settings
    learning_rate: float = 2e-5
    num_epochs: int = 3
    warmup_steps: int = 100
    weight_decay: float = 0.01
    
    # Optimization settings
    use_mixed_precision: bool = True
    use_gradient_clipping: bool = True
    max_grad_norm: float = 1.0
    
    # Hardware settings
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    num_gpus: int = torch.cuda.device_count()
    
    # Logging settings
    logging_steps: int = 100
    save_steps: int = 1000
    eval_steps: int = 500
    
    # Paths
    output_dir: str = "./outputs"
    cache_dir: str = "./cache"

# =============================================================================
# Optimized Model Architectures
# =============================================================================

class OptimizedTransformerModel(nn.Module):
    """Optimized transformer model with performance enhancements."""
    
    def __init__(self, model_name: str, num_labels: int = 2):
        super().__init__()
        self.config = TrainingConfig()
        
        # Load pre-trained model
        self.transformer = AutoModel.from_pretrained(
            model_name,
            cache_dir=self.config.cache_dir,
            torch_dtype=torch.float16 if self.config.use_mixed_precision else torch.float32
        )
        
        # Classification head
        self.classifier = nn.Linear(self.transformer.config.hidden_size, num_labels)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize model weights for optimal performance."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, input_ids, attention_mask=None, labels=None):
        """Forward pass with optimization."""
        outputs = self.transformer(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=False,
            return_dict=True
        )
        
        pooled_output = outputs.pooler_output
        logits = self.classifier(pooled_output)
        
        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, logits.size(-1)), labels.view(-1))
        
        return {"loss": loss, "logits": logits} if loss is not None else {"logits": logits}

class OptimizedDiffusionModel:
    """Optimized diffusion model wrapper."""
    
    def __init__(self, model_name: str = "runwayml/stable-diffusion-v1-5"):
        self.config = TrainingConfig()
        self.device = self.config.device
        
        # Load pipeline with optimizations
        self.pipeline = StableDiffusionPipeline.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.config.use_mixed_precision else torch.float32,
            cache_dir=self.config.cache_dir
        )
        
        # Optimize for inference
        self.pipeline = self.pipeline.to(self.device)
        if self.config.use_mixed_precision:
            self.pipeline.enable_attention_slicing()
            self.pipeline.enable_vae_slicing()
    
    def generate_image(self, prompt: str, num_inference_steps: int = 50) -> torch.Tensor:
        """Generate image with optimized inference."""
        try:
            with autocast(enabled=self.config.use_mixed_precision):
                image = self.pipeline(
                    prompt=prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=7.5
                ).images[0]
            
            return image
        except Exception as e:
            logging.error(f"Image generation failed: {e}")
            raise

# =============================================================================
# Optimized Data Loading
# =============================================================================

class OptimizedDataset(Dataset):
    """Optimized dataset with caching and preprocessing."""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Pre-tokenize for performance
        self.encodings = self._preprocess_data()
    
    def _preprocess_data(self) -> List[Dict[str, torch.Tensor]]:
        """Preprocess and cache tokenized data."""
        encodings = []
        
        for text, label in tqdm(zip(self.texts, self.labels), desc="Preprocessing data"):
            encoding = self.tokenizer(
                text,
                truncation=True,
                padding="max_length",
                max_length=self.max_length,
                return_tensors="pt"
            )
            
            encoding["labels"] = torch.tensor(label)
            encodings.append(encoding)
        
        return encodings
    
    def __len__(self) -> int:
        return len(self.encodings)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        return self.encodings[idx]

def create_optimized_dataloader(
    dataset: Dataset,
    batch_size: int,
    num_workers: int = 4,
    pin_memory: bool = True
) -> DataLoader:
    """Create optimized DataLoader with performance settings."""
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=True,
        persistent_workers=True if num_workers > 0 else False
    )

# =============================================================================
# Optimized Training Loop
# =============================================================================

class OptimizedTrainer:
    """Production-ready trainer with comprehensive optimizations."""
    
    def __init__(self, model: nn.Module, config: TrainingConfig):
        self.model = model
        self.config = config
        self.device = config.device
        
        # Move model to device
        self.model = self.model.to(self.device)
        
        # Multi-GPU setup
        if self.config.num_gpus > 1:
            self.model = DataParallel(self.model)
        
        # Optimizer and scheduler
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay
        )
        
        # Mixed precision training
        self.scaler = GradScaler() if config.use_mixed_precision else None
        
        # Logging
        self.writer = SummaryWriter(log_dir=config.output_dir)
        self.global_step = 0
        
        # Metrics tracking
        self.train_losses = []
        self.val_losses = []
    
    def train_epoch(
        self,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader] = None
    ) -> Dict[str, float]:
        """Train for one epoch with optimizations."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        progress_bar = tqdm(train_loader, desc="Training")
        
        for batch_idx, batch in enumerate(progress_bar):
            # Move batch to device
            batch = {k: v.to(self.device) for k, v in batch.items()}
            
            # Forward pass with mixed precision
            with autocast(enabled=self.config.use_mixed_precision):
                outputs = self.model(**batch)
                loss = outputs["loss"]
                loss = loss / self.config.gradient_accumulation_steps
            
            # Backward pass
            if self.config.use_mixed_precision:
                self.scaler.scale(loss).backward()
            else:
                loss.backward()
            
            # Gradient accumulation
            if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                # Gradient clipping
                if self.config.use_gradient_clipping:
                    if self.config.use_mixed_precision:
                        self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(
                        self.model.parameters(),
                        self.config.max_grad_norm
                    )
                
                # Optimizer step
                if self.config.use_mixed_precision:
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    self.optimizer.step()
                
                self.optimizer.zero_grad()
                self.global_step += 1
            
            # Update metrics
            total_loss += loss.item() * self.config.gradient_accumulation_steps
            num_batches += 1
            
            # Update progress bar
            progress_bar.set_postfix({
                "loss": f"{loss.item():.4f}",
                "avg_loss": f"{total_loss / num_batches:.4f}"
            })
            
            # Logging
            if self.global_step % self.config.logging_steps == 0:
                self._log_metrics({
                    "train_loss": loss.item(),
                    "learning_rate": self.optimizer.param_groups[0]["lr"]
                })
        
        avg_loss = total_loss / num_batches
        self.train_losses.append(avg_loss)
        
        # Validation
        val_metrics = {}
        if val_loader is not None:
            val_metrics = self.evaluate(val_loader)
        
        return {
            "train_loss": avg_loss,
            **val_metrics
        }
    
    def evaluate(self, val_loader: DataLoader) -> Dict[str, float]:
        """Evaluate model with optimizations."""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Evaluating"):
                batch = {k: v.to(self.device) for k, v in batch.items()}
                
                with autocast(enabled=self.config.use_mixed_precision):
                    outputs = self.model(**batch)
                    loss = outputs["loss"]
                
                total_loss += loss.item()
                num_batches += 1
        
        avg_loss = total_loss / num_batches
        self.val_losses.append(avg_loss)
        
        return {"val_loss": avg_loss}
    
    def _log_metrics(self, metrics: Dict[str, float]):
        """Log metrics to tensorboard and wandb."""
        for key, value in metrics.items():
            self.writer.add_scalar(key, value, self.global_step)
        
        if wandb.run is not None:
            wandb.log(metrics, step=self.global_step)
    
    def save_checkpoint(self, epoch: int, metrics: Dict[str, float]):
        """Save model checkpoint with metadata."""
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scaler_state_dict": self.scaler.state_dict() if self.scaler else None,
            "metrics": metrics,
            "config": self.config
        }
        
        checkpoint_path = Path(self.config.output_dir) / f"checkpoint_epoch_{epoch}.pt"
        torch.save(checkpoint, checkpoint_path)
        logging.info(f"Checkpoint saved: {checkpoint_path}")

# =============================================================================
# Optimized Inference
# =============================================================================

class OptimizedInference:
    """Optimized inference pipeline."""
    
    def __init__(self, model_path: str, config: TrainingConfig):
        self.config = config
        self.device = config.device
        
        # Load model
        self.model = OptimizedTransformerModel(config.model_name)
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
    
    def predict(self, text: str) -> Dict[str, Any]:
        """Make prediction with optimization."""
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=self.config.max_length,
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Inference
            with torch.no_grad():
                with autocast(enabled=self.config.use_mixed_precision):
                    outputs = self.model(**inputs)
                    logits = outputs["logits"]
                    probabilities = F.softmax(logits, dim=-1)
                    predictions = torch.argmax(logits, dim=-1)
            
            return {
                "predictions": predictions.cpu().numpy(),
                "probabilities": probabilities.cpu().numpy(),
                "logits": logits.cpu().numpy()
            }
        
        except Exception as e:
            logging.error(f"Inference failed: {e}")
            raise

# =============================================================================
# Gradio Interface
# =============================================================================

class OptimizedGradioInterface:
    """Production-ready Gradio interface."""
    
    def __init__(self, inference_model: OptimizedInference, diffusion_model: OptimizedDiffusionModel):
        self.inference_model = inference_model
        self.diffusion_model = diffusion_model
    
    def create_interface(self) -> gr.Interface:
        """Create optimized Gradio interface."""
        
        def text_classification(text: str) -> Dict[str, Any]:
            """Text classification endpoint."""
            try:
                results = self.inference_model.predict(text)
                return {
                    "prediction": int(results["predictions"][0]),
                    "confidence": float(results["probabilities"][0].max()),
                    "probabilities": results["probabilities"][0].tolist()
                }
            except Exception as e:
                return {"error": str(e)}
        
        def image_generation(prompt: str, num_steps: int = 50) -> np.ndarray:
            """Image generation endpoint."""
            try:
                image = self.diffusion_model.generate_image(prompt, num_steps)
                return np.array(image)
            except Exception as e:
                logging.error(f"Image generation failed: {e}")
                return None
        
        # Create interface
        interface = gr.Interface(
            fn=[text_classification, image_generation],
            inputs=[
                gr.Textbox(label="Text for classification"),
                gr.Textbox(label="Prompt for image generation"),
                gr.Slider(minimum=10, maximum=100, value=50, step=10, label="Inference steps")
            ],
            outputs=[
                gr.JSON(label="Classification Results"),
                gr.Image(label="Generated Image")
            ],
            title="Optimized AI Model Interface",
            description="Text classification and image generation with production optimizations",
            examples=[
                ["This is a positive review", "A beautiful sunset over mountains", 50],
                ["This product is terrible", "A futuristic city skyline", 30]
            ]
        )
        
        return interface

# =============================================================================
# Main Training Function
# =============================================================================

def main():
    """Main training function with comprehensive optimizations."""
    
    # Initialize logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Configuration
    config = TrainingConfig()
    
    # Initialize wandb
    wandb.init(project="optimized-deep-learning", config=config.__dict__)
    
    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Create model
        model = OptimizedTransformerModel(config.model_name)
        
        # Create trainer
        trainer = OptimizedTrainer(model, config)
        
        # Training loop
        for epoch in range(config.num_epochs):
            logging.info(f"Starting epoch {epoch + 1}/{config.num_epochs}")
            
            # Train
            metrics = trainer.train_epoch(None)  # Add your dataloaders here
            
            # Save checkpoint
            trainer.save_checkpoint(epoch, metrics)
            
            logging.info(f"Epoch {epoch + 1} completed. Metrics: {metrics}")
        
        # Create inference model
        inference_model = OptimizedInference(
            str(Path(config.output_dir) / "checkpoint_epoch_0.pt"),
            config
        )
        
        # Create diffusion model
        diffusion_model = OptimizedDiffusionModel()
        
        # Create Gradio interface
        interface = OptimizedGradioInterface(inference_model, diffusion_model)
        gradio_app = interface.create_interface()
        
        # Launch interface
        gradio_app.launch(share=True)
        
    except Exception as e:
        logging.error(f"Training failed: {e}")
        raise
    finally:
        wandb.finish()

if __name__ == "__main__":
    main()


