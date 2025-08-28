#!/usr/bin/env python3
"""
Advanced Training Script for HeyGen AI Machine Learning Module
Implements modern training workflows with PyTorch, Transformers, and optimizations
"""

import os
import sys
import yaml
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torch.cuda.amp import autocast, GradScaler
from torch.nn.parallel import DataParallel, DistributedDataParallel
import torch.distributed as dist

from transformers import (
    AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer,
    DataCollatorForLanguageModeling, get_cosine_schedule_with_warmup
)

from ultra_optimized_ml import (
    ModelConfig, CustomDataset, AdvancedTextModel, 
    AdvancedTrainer, DiffusionModelManager
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise

def setup_device(config: Dict[str, Any]) -> torch.device:
    """Setup device for training."""
    if config['hardware']['device'] == 'auto':
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(config['hardware']['device'])
    
    logger.info(f"Using device: {device}")
    if device.type == 'cuda':
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"CUDA version: {torch.version.cuda}")
        logger.info(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    return device

def setup_distributed_training(config: Dict[str, Any]) -> bool:
    """Setup distributed training if enabled."""
    if config['hardware']['distributed_training']:
        if 'RANK' in os.environ and 'WORLD_SIZE' in os.environ:
            rank = int(os.environ['RANK'])
            world_size = int(os.environ['WORLD_SIZE'])
            dist.init_process_group(backend='nccl', rank=rank, world_size=world_size)
            logger.info(f"Distributed training initialized: rank {rank}, world size {world_size}")
            return True
        else:
            logger.warning("Distributed training requested but environment variables not set")
            return False
    return False

def create_model(config: Dict[str, Any], device: torch.device) -> nn.Module:
    """Create and initialize the model."""
    model_config = config['model']
    
    if model_config['name'] == 'custom':
        # Use custom advanced text model
        model = AdvancedTextModel(
            vocab_size=model_config['vocab_size'],
            d_model=model_config['d_model'],
            n_heads=model_config['n_heads'],
            n_layers=model_config['n_layers']
        )
        logger.info("Created custom AdvancedTextModel")
    else:
        # Use pre-trained model from Hugging Face
        model = AutoModelForCausalLM.from_pretrained(
            model_config['name'],
            torch_dtype=torch.float16 if device.type == 'cuda' else torch.float32,
            low_cpu_mem_usage=True
        )
        logger.info(f"Loaded pre-trained model: {model_config['name']}")
    
    # Apply optimizations
    if config['optimization']['gradient_checkpointing']:
        model.gradient_checkpointing_enable()
        logger.info("Enabled gradient checkpointing")
    
    if config['optimization']['compile_model'] and hasattr(torch, 'compile'):
        model = torch.compile(model)
        logger.info("Model compiled with torch.compile")
    
    return model

def create_tokenizer(config: Dict[str, Any]):
    """Create tokenizer for the model."""
    model_name = config['model']['name']
    
    if model_name == 'custom':
        # For custom model, create a basic tokenizer
        from transformers import GPT2Tokenizer
        tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        tokenizer.pad_token = tokenizer.eos_token
        logger.info("Created GPT2 tokenizer for custom model")
    else:
        # Use model-specific tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        logger.info(f"Loaded tokenizer for {model_name}")
    
    return tokenizer

def prepare_data(config: Dict[str, Any], tokenizer) -> tuple[DataLoader, DataLoader, DataLoader]:
    """Prepare training, validation, and test dataloaders."""
    data_config = config['data']
    
    # Load sample data (replace with your actual data loading logic)
    sample_texts = [
        "This is a sample text for training the language model.",
        "Another example of text data for the dataset.",
        "The model will learn from these text samples.",
        # Add more sample texts here
    ] * 100  # Repeat to create more samples
    
    # Create dataset
    dataset = CustomDataset(sample_texts, tokenizer, data_config['max_length'])
    
    # Split dataset
    total_size = len(dataset)
    train_size = int(data_config['train_split'] * total_size)
    val_size = int(data_config['val_split'] * total_size)
    test_size = total_size - train_size - val_size
    
    train_dataset, val_dataset, test_dataset = random_split(
        dataset, [train_size, val_size, test_size]
    )
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=True,
        num_workers=config['hardware']['num_workers'],
        pin_memory=config['hardware']['pin_memory']
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=False,
        num_workers=config['hardware']['num_workers'],
        pin_memory=config['hardware']['pin_memory']
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=False,
        num_workers=config['hardware']['num_workers'],
        pin_memory=config['hardware']['pin_memory']
    )
    
    logger.info(f"Data prepared: {len(train_dataset)} train, {len(val_dataset)} val, {len(test_dataset)} test")
    return train_loader, val_loader, test_loader

def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    config: Dict[str, Any],
    device: torch.device,
    output_dir: str
) -> None:
    """Train the model using the advanced trainer."""
    
    # Create model config for trainer
    trainer_config = ModelConfig(
        model_name=config['model']['name'],
        max_length=config['model']['max_length'],
        batch_size=config['training']['batch_size'],
        learning_rate=config['training']['learning_rate'],
        num_epochs=config['training']['num_epochs'],
        warmup_steps=config['training']['warmup_steps'],
        gradient_accumulation_steps=config['training']['gradient_accumulation_steps'],
        max_grad_norm=config['training']['max_grad_norm'],
        weight_decay=config['training']['weight_decay'],
        fp16=config['training']['fp16']
    )
    
    # Initialize trainer
    trainer = AdvancedTrainer(model, trainer_config)
    
    # Training loop
    best_val_loss = float('inf')
    patience_counter = 0
    
    for epoch in range(config['training']['num_epochs']):
        logger.info(f"Starting epoch {epoch + 1}/{config['training']['num_epochs']}")
        
        # Training
        train_loss = trainer.train_epoch(train_loader, epoch + 1)
        
        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = input_ids.clone()
                
                outputs = model(input_ids, attention_mask)
                loss = nn.CrossEntropyLoss(ignore_index=-100)(
                    outputs.view(-1, outputs.size(-1)), labels.view(-1)
                )
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        logger.info(f"Epoch {epoch + 1} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
        
        # Save checkpoint
        if config['logging']['save_checkpoints']:
            checkpoint_path = os.path.join(
                output_dir, 
                f"checkpoint_epoch_{epoch + 1}_loss_{val_loss:.4f}.pt"
            )
            trainer.save_checkpoint(epoch + 1, val_loss, checkpoint_path)
        
        # Early stopping
        if config['advanced']['early_stopping']:
            if val_loss < best_val_loss - config['advanced']['early_stopping_threshold']:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                best_model_path = os.path.join(output_dir, "best_model.pt")
                trainer.save_checkpoint(epoch + 1, val_loss, best_model_path)
            else:
                patience_counter += 1
                
            if patience_counter >= config['advanced']['early_stopping_patience']:
                logger.info(f"Early stopping triggered after {epoch + 1} epochs")
                break
    
    logger.info("Training completed!")

def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train HeyGen AI ML models")
    parser.add_argument(
        "--config", 
        type=str, 
        default="ml_config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--output_dir", 
        type=str, 
        default="outputs",
        help="Output directory for models and logs"
    )
    parser.add_argument(
        "--resume", 
        type=str, 
        default=None,
        help="Path to checkpoint to resume training from"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Load configuration
    config = load_config(args.config)
    
    # Setup device and distributed training
    device = setup_device(config)
    is_distributed = setup_distributed_training(config)
    
    # Create model
    model = create_model(config, device)
    
    # Create tokenizer
    tokenizer = create_tokenizer(config)
    
    # Prepare data
    train_loader, val_loader, test_loader = prepare_data(config, tokenizer)
    
    # Resume training if checkpoint provided
    if args.resume and os.path.exists(args.resume):
        logger.info(f"Resuming training from checkpoint: {args.resume}")
        checkpoint = torch.load(args.resume, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        logger.info("Checkpoint loaded successfully")
    
    # Train model
    train_model(model, train_loader, val_loader, config, device, str(output_dir))
    
    # Save final model and tokenizer
    final_model_path = output_dir / "final_model"
    final_model_path.mkdir(exist_ok=True)
    
    if hasattr(model, 'save_pretrained'):
        model.save_pretrained(final_model_path)
        tokenizer.save_pretrained(final_model_path)
        logger.info(f"Final model saved to {final_model_path}")
    else:
        torch.save(model.state_dict(), final_model_path / "model.pt")
        logger.info(f"Final model saved to {final_model_path / 'model.pt'}")

if __name__ == "__main__":
    main()
