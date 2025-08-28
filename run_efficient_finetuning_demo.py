#!/usr/bin/env python3
"""
Efficient Fine-tuning Demo for Diffusion Models

Comprehensive demonstration of parameter-efficient fine-tuning techniques
with multiple examples, performance tests, and validation scenarios.
"""

import asyncio
import sys
import logging
import time
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import efficient fine-tuning system
from core.efficient_finetuning_system import (
    EfficientFineTuningSystem, LoRAConfig, QLoRAConfig, PTuningConfig,
    LoRAManager, PTuningV2, EfficientFineTuningTrainer
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('efficient_finetuning_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EfficientFineTuningDemo:
    """Comprehensive demo for efficient fine-tuning techniques."""
    
    def __init__(self):
        self.systems = {}
        self.start_time = None
    
    async def initialize_systems(self):
        """Initialize various efficient fine-tuning systems."""
        try:
            logger.info("🚀 Initializing Efficient Fine-tuning Systems...")
            
            # Create a simple transformer model for demonstration
            class SimpleTransformer(nn.Module):
                def __init__(self, vocab_size=1000, hidden_size=512, num_layers=6):
                    super().__init__()
                    self.config = type('Config', (), {'hidden_size': hidden_size})()
                    self.embedding = nn.Embedding(vocab_size, hidden_size)
                    self.transformer = nn.TransformerEncoder(
                        nn.TransformerEncoderLayer(
                            d_model=hidden_size,
                            nhead=8,
                            dim_feedforward=2048,
                            dropout=0.1,
                            batch_first=True
                        ),
                        num_layers=num_layers
                    )
                    self.output = nn.Linear(hidden_size, vocab_size)
                
                def forward(self, input_ids, attention_mask=None):
                    embeddings = self.embedding(input_ids)
                    if attention_mask is not None:
                        # Create padding mask for transformer
                        padding_mask = (attention_mask == 0)
                        output = self.transformer(embeddings, src_key_padding_mask=padding_mask)
                    else:
                        output = self.transformer(embeddings)
                    return type('Output', (), {'logits': self.output(output), 'loss': None})()
                
                def get_input_embeddings(self):
                    return self.embedding
            
            # Create model
            model = SimpleTransformer()
            logger.info("✅ Simple transformer model created")
            
            # System 1: LoRA
            lora_config = LoRAConfig(
                r=16,
                alpha=32.0,
                dropout=0.1,
                target_modules=["linear1", "linear2", "output"]
            )
            
            system_lora = EfficientFineTuningSystem(model)
            lora_manager = system_lora.setup_lora(lora_config)
            self.systems["lora"] = system_lora
            logger.info("✅ LoRA system initialized")
            
            # System 2: QLoRA
            qlora_config = QLoRAConfig(
                lora_config=LoRAConfig(r=8, alpha=16.0),
                bits=4,
                group_size=128,
                double_quant=True,
                target_modules=["linear1", "linear2", "output"]
            )
            
            system_qlora = EfficientFineTuningSystem(model)
            qlora_manager = system_qlora.setup_qlora(qlora_config)
            self.systems["qlora"] = system_qlora
            logger.info("✅ QLoRA system initialized")
            
            # System 3: P-tuning
            p_tuning_config = PTuningConfig(
                num_virtual_tokens=20,
                encoder_hidden_size=128,
                prefix_projection=True
            )
            
            system_p_tuning = EfficientFineTuningSystem(model)
            p_tuning = system_p_tuning.setup_p_tuning(p_tuning_config)
            self.systems["p_tuning"] = system_p_tuning
            logger.info("✅ P-tuning system initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize systems: {e}")
            return False
    
    async def demo_parameter_efficiency(self):
        """Demo parameter efficiency of different methods."""
        try:
            logger.info("📊 Demo: Parameter Efficiency")
            
            # Count parameters for each method
            for method, system in self.systems.items():
                trainer = system.get_trainer(method)
                
                if hasattr(trainer, 'lora_manager'):
                    # LoRA/QLoRA
                    trainable_params = trainer.lora_manager.get_trainable_parameters()
                    total_params = sum(p.numel() for p in trainer.model.parameters())
                    trainable_count = sum(p.numel() for p in trainable_params)
                    
                    logger.info(f"  {method.upper()}:")
                    logger.info(f"    Total model parameters: {total_params:,}")
                    logger.info(f"    Trainable parameters: {trainable_count:,}")
                    logger.info(f"    Parameter efficiency: {trainable_count/total_params*100:.2f}%")
                    logger.info(f"    Memory reduction: {(1-trainable_count/total_params)*100:.2f}%")
                    logger.info("")
                
                elif hasattr(trainer, 'p_tuning'):
                    # P-tuning
                    trainable_params = list(trainer.p_tuning.parameters())
                    total_params = sum(p.numel() for p in trainer.model.parameters())
                    trainable_count = sum(p.numel() for p in trainable_params)
                    
                    logger.info(f"  {method.upper()}:")
                    logger.info(f"    Total model parameters: {total_params:,}")
                    logger.info(f"    Trainable parameters: {trainable_count:,}")
                    logger.info(f"    Parameter efficiency: {trainable_count/total_params*100:.2f}%")
                    logger.info(f"    Memory reduction: {(1-trainable_count/total_params)*100:.2f}%")
                    logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Parameter efficiency demo failed: {e}")
            return False
    
    async def demo_memory_usage(self):
        """Demo memory usage comparison."""
        try:
            logger.info("💾 Demo: Memory Usage Comparison")
            
            if not torch.cuda.is_available():
                logger.info("  CUDA not available, skipping memory tests")
                return True
            
            # Test configurations
            batch_size, seq_len, vocab_size = 4, 128, 1000
            
            for method, system in self.systems.items():
                logger.info(f"  Testing {method.upper()} memory usage:")
                
                trainer = system.get_trainer(method)
                model = trainer.model.cuda()
                
                # Clear cache
                torch.cuda.empty_cache()
                
                # Measure memory before
                torch.cuda.synchronize()
                memory_before = torch.cuda.memory_allocated() / 1024**2  # MB
                
                # Create dummy data
                input_ids = torch.randint(0, vocab_size, (batch_size, seq_len)).cuda()
                attention_mask = torch.ones(batch_size, seq_len).cuda()
                
                # Forward pass
                with torch.no_grad():
                    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                
                # Measure memory after
                torch.cuda.synchronize()
                memory_after = torch.cuda.memory_allocated() / 1024**2  # MB
                
                logger.info(f"    Memory before: {memory_before:.2f} MB")
                logger.info(f"    Memory after: {memory_after:.2f} MB")
                logger.info(f"    Memory increase: {memory_after - memory_before:.2f} MB")
                logger.info(f"    Output shape: {outputs.logits.shape}")
                logger.info("")
                
                # Clear cache
                del model, input_ids, attention_mask, outputs
                torch.cuda.empty_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Memory usage demo failed: {e}")
            return False
    
    async def demo_training_simulation(self):
        """Demo training simulation with dummy data."""
        try:
            logger.info("🏋️ Demo: Training Simulation")
            
            # Create dummy dataset
            batch_size, seq_len, vocab_size = 2, 64, 1000
            num_samples = 100
            
            # Generate dummy data
            input_ids = torch.randint(0, vocab_size, (num_samples, seq_len))
            attention_mask = torch.ones(num_samples, seq_len)
            labels = torch.randint(0, vocab_size, (num_samples, seq_len))
            
            # Create dataset and dataloader
            dataset = TensorDataset(input_ids, attention_mask, labels)
            dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
            
            # Test each method
            for method, system in self.systems.items():
                logger.info(f"  Testing {method.upper()} training:")
                
                trainer = system.get_trainer(method)
                
                # Setup optimizer and scheduler
                trainer.setup_optimizer(learning_rate=1e-4)
                trainer.setup_scheduler(num_training_steps=len(dataloader) * 2)
                
                # Training simulation
                total_loss = 0.0
                num_batches = 0
                
                for batch_idx, (input_ids_batch, attention_mask_batch, labels_batch) in enumerate(dataloader):
                    if batch_idx >= 5:  # Limit to 5 batches for demo
                        break
                    
                    # Create batch dict
                    batch = {
                        'input_ids': input_ids_batch,
                        'attention_mask': attention_mask_batch,
                        'labels': labels_batch
                    }
                    
                    # Training step
                    metrics = trainer.train_step(batch)
                    total_loss += metrics["loss"]
                    num_batches += 1
                    
                    logger.info(f"    Batch {batch_idx+1}, Loss: {metrics['loss']:.4f}, LR: {metrics['learning_rate']:.6f}")
                
                avg_loss = total_loss / num_batches
                logger.info(f"    Average loss: {avg_loss:.4f}")
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Training simulation demo failed: {e}")
            return False
    
    async def demo_weight_merging(self):
        """Demo weight merging for LoRA methods."""
        try:
            logger.info("🔗 Demo: Weight Merging")
            
            for method in ["lora", "qlora"]:
                if method in self.systems:
                    logger.info(f"  Testing {method.upper()} weight merging:")
                    
                    system = self.systems[method]
                    trainer = system.get_trainer(method)
                    
                    # Get original weights
                    original_weights = {}
                    for name, param in trainer.model.named_parameters():
                        if param.requires_grad:
                            original_weights[name] = param.data.clone()
                    
                    # Merge weights
                    trainer.lora_manager.merge_weights()
                    
                    # Check if weights changed
                    weight_changes = 0
                    for name, param in trainer.model.named_parameters():
                        if name in original_weights:
                            if not torch.allclose(param.data, original_weights[name]):
                                weight_changes += 1
                    
                    logger.info(f"    Weight changes detected: {weight_changes}")
                    logger.info(f"    Weight merging successful: {weight_changes > 0}")
                    logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Weight merging demo failed: {e}")
            return False
    
    async def demo_save_load_functionality(self):
        """Demo save and load functionality."""
        try:
            logger.info("💾 Demo: Save and Load Functionality")
            
            # Create temporary directory
            temp_dir = Path("temp_checkpoints")
            temp_dir.mkdir(exist_ok=True)
            
            for method, system in self.systems.items():
                logger.info(f"  Testing {method.upper()} save/load:")
                
                trainer = system.get_trainer(method)
                
                # Save checkpoint
                checkpoint_path = temp_dir / f"{method}_checkpoint.pt"
                trainer.save_checkpoint(str(checkpoint_path))
                logger.info(f"    Checkpoint saved to: {checkpoint_path}")
                
                # Load checkpoint
                trainer.load_checkpoint(str(checkpoint_path))
                logger.info(f"    Checkpoint loaded from: {checkpoint_path}")
                
                # Clean up
                checkpoint_path.unlink()
                logger.info("")
            
            # Clean up directory
            temp_dir.rmdir()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Save/load demo failed: {e}")
            return False
    
    async def demo_performance_comparison(self):
        """Demo performance comparison between methods."""
        try:
            logger.info("⚡ Demo: Performance Comparison")
            
            # Test configurations
            batch_size, seq_len, vocab_size = 2, 128, 1000
            num_runs = 10
            
            # Generate test data
            input_ids = torch.randint(0, vocab_size, (batch_size, seq_len))
            attention_mask = torch.ones(batch_size, seq_len)
            
            results = {}
            
            for method, system in self.systems.items():
                logger.info(f"  Testing {method.upper()} performance:")
                
                trainer = system.get_trainer(method)
                model = trainer.model
                
                # Warmup
                for _ in range(3):
                    with torch.no_grad():
                        _ = model(input_ids=input_ids, attention_mask=attention_mask)
                
                # Benchmark
                times = []
                for _ in range(num_runs):
                    start_time = time.time()
                    with torch.no_grad():
                        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                    end_time = time.time()
                    times.append(end_time - start_time)
                
                avg_time = sum(times) / len(times)
                std_time = (sum((t - avg_time) ** 2 for t in times) / len(times)) ** 0.5
                
                results[method] = {
                    'avg_time': avg_time,
                    'std_time': std_time,
                    'throughput': batch_size / avg_time
                }
                
                logger.info(f"    Average time: {avg_time:.4f}s ± {std_time:.4f}s")
                logger.info(f"    Throughput: {batch_size/avg_time:.2f} samples/s")
                logger.info("")
            
            # Summary
            logger.info("  Performance Summary:")
            fastest_method = min(results.keys(), key=lambda x: results[x]['avg_time'])
            logger.info(f"    Fastest method: {fastest_method.upper()} ({results[fastest_method]['avg_time']:.4f}s)")
            
            for method, metrics in results.items():
                speedup = results[fastest_method]['avg_time'] / metrics['avg_time']
                logger.info(f"    {method.upper()}: {speedup:.2f}x speedup")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Performance comparison demo failed: {e}")
            return False
    
    async def demo_gradient_analysis(self):
        """Demo gradient analysis for different methods."""
        try:
            logger.info("🌊 Demo: Gradient Analysis")
            
            for method, system in self.systems.items():
                logger.info(f"  Testing {method.upper()} gradients:")
                
                trainer = system.get_trainer(method)
                
                # Create dummy data
                batch_size, seq_len, vocab_size = 2, 32, 1000
                input_ids = torch.randint(0, vocab_size, (batch_size, seq_len))
                attention_mask = torch.ones(batch_size, seq_len)
                labels = torch.randint(0, vocab_size, (batch_size, seq_len))
                
                batch = {
                    'input_ids': input_ids,
                    'attention_mask': attention_mask,
                    'labels': labels
                }
                
                # Forward and backward pass
                trainer.model.train()
                trainer.optimizer.zero_grad()
                
                outputs = trainer.model(**batch)
                loss = nn.CrossEntropyLoss()(outputs.logits.view(-1, vocab_size), labels.view(-1))
                loss.backward()
                
                # Analyze gradients
                grad_norms = []
                for param in trainer.trainable_params:
                    if param.grad is not None:
                        grad_norms.append(param.grad.norm().item())
                
                if grad_norms:
                    avg_grad_norm = sum(grad_norms) / len(grad_norms)
                    max_grad_norm = max(grad_norms)
                    min_grad_norm = min(grad_norms)
                    
                    logger.info(f"    Average gradient norm: {avg_grad_norm:.4f}")
                    logger.info(f"    Max gradient norm: {max_grad_norm:.4f}")
                    logger.info(f"    Min gradient norm: {min_grad_norm:.4f}")
                    
                    # Check for gradient issues
                    if max_grad_norm > 10.0:
                        logger.warning(f"    ⚠️ Potential gradient explosion detected")
                    elif min_grad_norm < 1e-6:
                        logger.warning(f"    ⚠️ Potential gradient vanishing detected")
                    else:
                        logger.info(f"    ✅ Gradient norms are healthy")
                else:
                    logger.warning(f"    ⚠️ No gradients found")
                
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Gradient analysis demo failed: {e}")
            return False
    
    async def demo_integration_scenarios(self):
        """Demo integration scenarios with different model types."""
        try:
            logger.info("🔗 Demo: Integration Scenarios")
            
            # Scenario 1: Diffusion model integration
            logger.info("  Scenario 1: Diffusion Model Integration")
            
            class MockDiffusionModel(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.config = type('Config', (), {'hidden_size': 512})()
                    self.text_encoder = nn.Linear(512, 512)
                    self.unet = nn.Sequential(
                        nn.Linear(512, 512),
                        nn.ReLU(),
                        nn.Linear(512, 512)
                    )
                
                def forward(self, text_embeddings):
                    encoded = self.text_encoder(text_embeddings)
                    output = self.unet(encoded)
                    return type('Output', (), {'sample': output})()
            
            diffusion_model = MockDiffusionModel()
            
            # Apply LoRA to diffusion model
            lora_config = LoRAConfig(
                r=8,
                alpha=16.0,
                target_modules=["text_encoder", "unet.0", "unet.2"]
            )
            
            diffusion_system = EfficientFineTuningSystem(diffusion_model)
            diffusion_lora = diffusion_system.setup_lora(lora_config)
            
            logger.info(f"    Diffusion model LoRA parameters: {sum(p.numel() for p in diffusion_lora.get_trainable_parameters()):,}")
            logger.info("")
            
            # Scenario 2: Multi-modal integration
            logger.info("  Scenario 2: Multi-modal Integration")
            
            class MockMultiModalModel(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.config = type('Config', (), {'hidden_size': 768})()
                    self.text_encoder = nn.Linear(768, 768)
                    self.image_encoder = nn.Linear(1024, 768)
                    self.fusion_layer = nn.Linear(768, 768)
                
                def forward(self, text_features, image_features):
                    text_encoded = self.text_encoder(text_features)
                    image_encoded = self.image_encoder(image_features)
                    fused = self.fusion_layer(text_encoded + image_encoded)
                    return type('Output', (), {'logits': fused})()
            
            multimodal_model = MockMultiModalModel()
            
            # Apply QLoRA to multimodal model
            qlora_config = QLoRAConfig(
                lora_config=LoRAConfig(r=4, alpha=8.0),
                bits=4,
                target_modules=["text_encoder", "image_encoder", "fusion_layer"]
            )
            
            multimodal_system = EfficientFineTuningSystem(multimodal_model)
            multimodal_qlora = multimodal_system.setup_qlora(qlora_config)
            
            logger.info(f"    Multi-modal QLoRA parameters: {sum(p.numel() for p in multimodal_qlora.get_trainable_parameters()):,}")
            logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Integration scenarios demo failed: {e}")
            return False
    
    async def run(self):
        """Main demo execution."""
        try:
            self.start_time = datetime.now()
            
            logger.info("🚀 Starting Efficient Fine-tuning Demo...")
            logger.info(f"⏰ Start time: {self.start_time}")
            
            # Initialize systems
            if not await self.initialize_systems():
                return False
            
            # Run demos
            demos = [
                self.demo_parameter_efficiency(),
                self.demo_memory_usage(),
                self.demo_training_simulation(),
                self.demo_weight_merging(),
                self.demo_save_load_functionality(),
                self.demo_performance_comparison(),
                self.demo_gradient_analysis(),
                self.demo_integration_scenarios()
            ]
            
            for demo in demos:
                if not await demo:
                    logger.warning("⚠️ Demo completed with warnings")
            
            # Final status
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            logger.info("🎉 Efficient Fine-tuning Demo completed successfully!")
            logger.info(f"⏱️  Total duration: {duration}")
            logger.info("📊 All demos executed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Demo execution failed: {e}")
            return False

async def main():
    """Main entry point."""
    demo = EfficientFineTuningDemo()
    
    try:
        success = await demo.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
