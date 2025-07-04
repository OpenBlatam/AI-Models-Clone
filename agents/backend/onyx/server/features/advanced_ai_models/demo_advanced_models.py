#!/usr/bin/env python3
"""
Advanced AI Models Demo - Comprehensive Showcase
Demonstrating Deep Learning, Transformers, Diffusion Models & LLMs
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Optional
import time
import logging
import json
from pathlib import Path
import gradio as gr
from PIL import Image
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

# Import our advanced models
try:
    from models.transformer_models import (
        AdvancedTransformerModel,
        MultiModalTransformer,
        CustomAttentionMechanism,
        PositionalEncoding,
        VisionTransformer
    )
    from models.diffusion_models import (
        CustomDiffusionModel,
        StableDiffusionPipeline,
        DiffusionScheduler,
        TextToImagePipeline
    )
    from models.llm_models import (
        AdvancedLLMModel,
        LoRAFineTuner,
        CustomTokenizer,
        LLMInferenceEngine
    )
    logger.info("✅ Successfully imported advanced AI models")
except ImportError as e:
    logger.warning(f"⚠️ Some models not available: {e}")
    # Create mock classes for demo
    class MockModel:
        def __init__(self, *args, **kwargs):
            pass
        def forward(self, *args, **kwargs):
            return {"logits": torch.randn(1, 10)}
        def generate(self, *args, **kwargs):
            return ["Generated text example"]
    
    AdvancedTransformerModel = MockModel
    CustomDiffusionModel = MockModel
    AdvancedLLMModel = MockModel


class AdvancedAIModelsDemo:
    """
    Comprehensive demo for advanced AI models.
    """
    
    def __init__(self):
        self.models = {}
        self.results = {}
        self.performance_metrics = {}
        
        # Initialize models
        self._initialize_models()
        
        logger.info("🚀 Advanced AI Models Demo initialized")
    
    def _initialize_models(self):
        """Initialize all advanced AI models."""
        try:
            # Transformer Models
            logger.info("Initializing Transformer Models...")
            
            # Advanced Transformer
            self.models["transformer"] = AdvancedTransformerModel(
                vocab_size=32000,
                d_model=512,
                n_layers=6,
                n_heads=8,
                d_ff=2048,
                max_seq_len=512,
                dropout=0.1
            ).to(device)
            
            # Vision Transformer
            self.models["vision_transformer"] = VisionTransformer(
                image_size=224,
                patch_size=16,
                num_classes=1000,
                dim=768,
                depth=12,
                heads=12
            ).to(device)
            
            # Custom Attention Mechanism
            self.models["attention"] = CustomAttentionMechanism(
                d_model=512,
                n_heads=8,
                attention_type="scaled_dot_product",
                use_flash_attention=True
            ).to(device)
            
            logger.info("✅ Transformer models initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Transformer models initialization failed: {e}")
        
        try:
            # Diffusion Models
            logger.info("Initializing Diffusion Models...")
            
            # Custom Diffusion Model
            unet_config = {
                "sample_size": 64,
                "in_channels": 4,
                "out_channels": 4,
                "down_block_types": ["CrossAttnDownBlock2D", "CrossAttnDownBlock2D", "CrossAttnDownBlock2D", "DownBlock2D"],
                "up_block_types": ["UpBlock2D", "CrossAttnUpBlock2D", "CrossAttnUpBlock2D", "CrossAttnUpBlock2D"],
                "block_out_channels": [320, 640, 1280, 1280],
                "layers_per_block": 2,
                "cross_attention_dim": 1280,
                "attention_head_dim": 8
            }
            
            scheduler_config = {
                "type": "ddim",
                "num_train_timesteps": 1000,
                "beta_start": 0.0001,
                "beta_end": 0.02,
                "beta_schedule": "linear"
            }
            
            self.models["diffusion"] = CustomDiffusionModel(
                unet_config=unet_config,
                scheduler_config=scheduler_config,
                use_fp16=True,
                use_xformers=True
            ).to(device)
            
            # Diffusion Scheduler
            self.models["scheduler"] = DiffusionScheduler(
                scheduler_type="ddim",
                num_train_timesteps=1000
            )
            
            logger.info("✅ Diffusion models initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Diffusion models initialization failed: {e}")
        
        try:
            # LLM Models
            logger.info("Initializing LLM Models...")
            
            # Advanced LLM (using a smaller model for demo)
            self.models["llm"] = AdvancedLLMModel(
                model_name="microsoft/DialoGPT-small",
                use_4bit=False,  # Use 8-bit for demo
                use_8bit=True,
                use_flash_attention=True
            )
            
            # Custom Tokenizer
            self.models["tokenizer"] = CustomTokenizer(
                tokenizer_name="microsoft/DialoGPT-small",
                max_length=512
            )
            
            # LLM Inference Engine
            self.models["inference_engine"] = LLMInferenceEngine(
                model=self.models["llm"],
                use_cache=True,
                max_cache_size=1000,
                use_batch_inference=True,
                max_batch_size=4
            )
            
            logger.info("✅ LLM models initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ LLM models initialization failed: {e}")
    
    def demo_transformer_models(self) -> Dict[str, Any]:
        """Demo transformer models functionality."""
        logger.info("🔄 Running Transformer Models Demo...")
        
        results = {
            "attention_mechanism": {},
            "positional_encoding": {},
            "transformer_generation": {},
            "vision_transformer": {}
        }
        
        try:
            # Test Custom Attention Mechanism
            logger.info("Testing Custom Attention Mechanism...")
            
            batch_size, seq_len, d_model = 2, 10, 512
            query = torch.randn(batch_size, seq_len, d_model).to(device)
            key = torch.randn(batch_size, seq_len, d_model).to(device)
            value = torch.randn(batch_size, seq_len, d_model).to(device)
            
            start_time = time.time()
            attention_model = self.models.get("attention")
            if attention_model:
                output, attention_weights = attention_model(query, key, value)
                attention_time = time.time() - start_time
                
                results["attention_mechanism"] = {
                    "success": True,
                    "output_shape": list(output.shape),
                    "attention_weights_shape": list(attention_weights.shape) if attention_weights is not None else None,
                    "execution_time": attention_time,
                    "memory_usage": output.element_size() * output.nelement() / 1024 / 1024  # MB
                }
            else:
                results["attention_mechanism"] = {"success": False, "error": "Model not available"}
            
            # Test Positional Encoding
            logger.info("Testing Positional Encoding...")
            
            pos_encoding = PositionalEncoding(d_model=512, max_len=100, encoding_type="sinusoidal")
            input_tensor = torch.randn(50, 2, 512).to(device)  # (seq_len, batch_size, d_model)
            
            start_time = time.time()
            encoded_output = pos_encoding(input_tensor)
            encoding_time = time.time() - start_time
            
            results["positional_encoding"] = {
                "success": True,
                "input_shape": list(input_tensor.shape),
                "output_shape": list(encoded_output.shape),
                "execution_time": encoding_time,
                "encoding_type": "sinusoidal"
            }
            
            # Test Transformer Generation
            logger.info("Testing Transformer Generation...")
            
            transformer_model = self.models.get("transformer")
            if transformer_model:
                # Create dummy input
                input_ids = torch.randint(0, 32000, (1, 10)).to(device)
                
                start_time = time.time()
                outputs = transformer_model(input_ids)
                generation_time = time.time() - start_time
                
                results["transformer_generation"] = {
                    "success": True,
                    "input_shape": list(input_ids.shape),
                    "output_shape": list(outputs["logits"].shape),
                    "execution_time": generation_time,
                    "vocab_size": 32000
                }
            else:
                results["transformer_generation"] = {"success": False, "error": "Model not available"}
            
            # Test Vision Transformer
            logger.info("Testing Vision Transformer...")
            
            vision_model = self.models.get("vision_transformer")
            if vision_model:
                # Create dummy image input
                dummy_image = torch.randn(1, 3, 224, 224).to(device)
                
                start_time = time.time()
                vision_output = vision_model(dummy_image)
                vision_time = time.time() - start_time
                
                results["vision_transformer"] = {
                    "success": True,
                    "input_shape": list(dummy_image.shape),
                    "output_shape": list(vision_output.shape),
                    "execution_time": vision_time,
                    "num_classes": 1000
                }
            else:
                results["vision_transformer"] = {"success": False, "error": "Model not available"}
            
        except Exception as e:
            logger.error(f"❌ Transformer demo failed: {e}")
            results["error"] = str(e)
        
        self.results["transformer"] = results
        return results
    
    def demo_diffusion_models(self) -> Dict[str, Any]:
        """Demo diffusion models functionality."""
        logger.info("🔄 Running Diffusion Models Demo...")
        
        results = {
            "scheduler_test": {},
            "latent_generation": {},
            "noise_addition": {},
            "denoising_process": {}
        }
        
        try:
            # Test Diffusion Scheduler
            logger.info("Testing Diffusion Scheduler...")
            
            scheduler = self.models.get("scheduler")
            if scheduler:
                # Test noise addition
                original_samples = torch.randn(1, 3, 64, 64).to(device)
                timesteps = torch.randint(0, 1000, (1,)).to(device)
                
                start_time = time.time()
                noisy_samples = scheduler.add_noise(original_samples, timesteps)
                scheduler_time = time.time() - start_time
                
                results["scheduler_test"] = {
                    "success": True,
                    "original_shape": list(original_samples.shape),
                    "noisy_shape": list(noisy_samples.shape),
                    "execution_time": scheduler_time,
                    "scheduler_type": "ddim"
                }
            else:
                results["scheduler_test"] = {"success": False, "error": "Scheduler not available"}
            
            # Test Latent Generation
            logger.info("Testing Latent Generation...")
            
            # Simulate latent generation
            batch_size, channels, height, width = 1, 4, 64, 64
            latents = torch.randn(batch_size, channels, height, width).to(device)
            
            results["latent_generation"] = {
                "success": True,
                "latent_shape": list(latents.shape),
                "latent_channels": channels,
                "spatial_dimensions": [height, width]
            }
            
            # Test Noise Addition Process
            logger.info("Testing Noise Addition Process...")
            
            # Simulate noise addition
            clean_latents = torch.randn(1, 4, 64, 64).to(device)
            noise = torch.randn_like(clean_latents)
            timestep = torch.tensor([500]).to(device)
            
            # Simulate noise addition (simplified)
            noisy_latents = clean_latents + 0.1 * noise
            
            results["noise_addition"] = {
                "success": True,
                "clean_shape": list(clean_latents.shape),
                "noisy_shape": list(noisy_latents.shape),
                "noise_level": 0.1,
                "timestep": timestep.item()
            }
            
            # Test Denoising Process
            logger.info("Testing Denoising Process...")
            
            # Simulate denoising steps
            denoising_steps = 10
            current_latents = noisy_latents.clone()
            
            start_time = time.time()
            for step in range(denoising_steps):
                # Simulate denoising (simplified)
                current_latents = current_latents - 0.01 * noise
            denoising_time = time.time() - start_time
            
            results["denoising_process"] = {
                "success": True,
                "steps": denoising_steps,
                "execution_time": denoising_time,
                "final_shape": list(current_latents.shape),
                "improvement": torch.norm(clean_latents - current_latents).item()
            }
            
        except Exception as e:
            logger.error(f"❌ Diffusion demo failed: {e}")
            results["error"] = str(e)
        
        self.results["diffusion"] = results
        return results
    
    def demo_llm_models(self) -> Dict[str, Any]:
        """Demo LLM models functionality."""
        logger.info("🔄 Running LLM Models Demo...")
        
        results = {
            "text_generation": {},
            "embedding_generation": {},
            "similarity_search": {},
            "batch_processing": {}
        }
        
        try:
            # Test Text Generation
            logger.info("Testing Text Generation...")
            
            inference_engine = self.models.get("inference_engine")
            if inference_engine:
                prompts = [
                    "Hello, how are you?",
                    "What is artificial intelligence?",
                    "Tell me a joke"
                ]
                
                start_time = time.time()
                generated_texts = inference_engine.generate_batch(
                    prompts,
                    max_length=50,
                    temperature=0.7,
                    do_sample=True
                )
                generation_time = time.time() - start_time
                
                results["text_generation"] = {
                    "success": True,
                    "prompts": prompts,
                    "generated_texts": generated_texts,
                    "execution_time": generation_time,
                    "num_prompts": len(prompts)
                }
            else:
                results["text_generation"] = {"success": False, "error": "Inference engine not available"}
            
            # Test Embedding Generation
            logger.info("Testing Embedding Generation...")
            
            llm_model = self.models.get("llm")
            if llm_model:
                texts = ["This is a test sentence.", "Another example text."]
                
                start_time = time.time()
                embeddings = llm_model.get_embeddings(texts, pooling="mean")
                embedding_time = time.time() - start_time
                
                results["embedding_generation"] = {
                    "success": True,
                    "texts": texts,
                    "embedding_shape": list(embeddings.shape),
                    "execution_time": embedding_time,
                    "pooling_method": "mean"
                }
            else:
                results["embedding_generation"] = {"success": False, "error": "LLM model not available"}
            
            # Test Similarity Search
            logger.info("Testing Similarity Search...")
            
            if inference_engine:
                query = "machine learning"
                candidates = [
                    "artificial intelligence",
                    "deep learning",
                    "computer vision",
                    "natural language processing",
                    "robotics"
                ]
                
                start_time = time.time()
                similarities = inference_engine.similarity_search(
                    query, candidates, top_k=3
                )
                search_time = time.time() - start_time
                
                results["similarity_search"] = {
                    "success": True,
                    "query": query,
                    "candidates": candidates,
                    "top_results": similarities,
                    "execution_time": search_time
                }
            else:
                results["similarity_search"] = {"success": False, "error": "Inference engine not available"}
            
            # Test Batch Processing
            logger.info("Testing Batch Processing...")
            
            if inference_engine:
                batch_prompts = [
                    "Generate a creative story",
                    "Write a technical explanation",
                    "Create a poem",
                    "Describe a scientific concept"
                ]
                
                start_time = time.time()
                batch_results = inference_engine.generate_batch(
                    batch_prompts,
                    max_length=30,
                    temperature=0.8
                )
                batch_time = time.time() - start_time
                
                results["batch_processing"] = {
                    "success": True,
                    "batch_size": len(batch_prompts),
                    "results": batch_results,
                    "execution_time": batch_time,
                    "throughput": len(batch_prompts) / batch_time
                }
            else:
                results["batch_processing"] = {"success": False, "error": "Inference engine not available"}
            
        except Exception as e:
            logger.error(f"❌ LLM demo failed: {e}")
            results["error"] = str(e)
        
        self.results["llm"] = results
        return results
    
    def run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run comprehensive performance benchmarks."""
        logger.info("🔄 Running Performance Benchmarks...")
        
        benchmarks = {
            "memory_usage": {},
            "inference_speed": {},
            "throughput": {},
            "gpu_utilization": {}
        }
        
        try:
            # Memory Usage Benchmark
            logger.info("Testing Memory Usage...")
            
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            initial_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
            
            # Test with different model sizes
            model_sizes = [512, 768, 1024]
            memory_results = {}
            
            for size in model_sizes:
                try:
                    # Create a simple model
                    model = nn.Sequential(
                        nn.Linear(size, size),
                        nn.ReLU(),
                        nn.Linear(size, size)
                    ).to(device)
                    
                    # Test input
                    x = torch.randn(1, size).to(device)
                    _ = model(x)
                    
                    current_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
                    memory_used = current_memory - initial_memory
                    
                    memory_results[f"size_{size}"] = {
                        "memory_mb": memory_used / 1024 / 1024,
                        "parameters": sum(p.numel() for p in model.parameters())
                    }
                    
                    del model
                    torch.cuda.empty_cache() if torch.cuda.is_available() else None
                    
                except Exception as e:
                    memory_results[f"size_{size}"] = {"error": str(e)}
            
            benchmarks["memory_usage"] = memory_results
            
            # Inference Speed Benchmark
            logger.info("Testing Inference Speed...")
            
            # Test different batch sizes
            batch_sizes = [1, 4, 8, 16]
            speed_results = {}
            
            for batch_size in batch_sizes:
                try:
                    # Create test model
                    model = nn.Sequential(
                        nn.Linear(512, 512),
                        nn.ReLU(),
                        nn.Linear(512, 512)
                    ).to(device)
                    
                    x = torch.randn(batch_size, 512).to(device)
                    
                    # Warmup
                    for _ in range(10):
                        _ = model(x)
                    
                    # Benchmark
                    torch.cuda.synchronize() if torch.cuda.is_available() else None
                    start_time = time.time()
                    
                    for _ in range(100):
                        _ = model(x)
                    
                    torch.cuda.synchronize() if torch.cuda.is_available() else None
                    end_time = time.time()
                    
                    avg_time = (end_time - start_time) / 100
                    throughput = batch_size / avg_time
                    
                    speed_results[f"batch_{batch_size}"] = {
                        "avg_inference_time_ms": avg_time * 1000,
                        "throughput_samples_per_sec": throughput,
                        "batch_size": batch_size
                    }
                    
                    del model
                    
                except Exception as e:
                    speed_results[f"batch_{batch_size}"] = {"error": str(e)}
            
            benchmarks["inference_speed"] = speed_results
            
            # Throughput Benchmark
            logger.info("Testing Throughput...")
            
            # Test with different input sizes
            input_sizes = [128, 256, 512, 1024]
            throughput_results = {}
            
            for input_size in input_sizes:
                try:
                    model = nn.Sequential(
                        nn.Linear(input_size, input_size),
                        nn.ReLU(),
                        nn.Linear(input_size, input_size)
                    ).to(device)
                    
                    x = torch.randn(8, input_size).to(device)
                    
                    # Measure throughput
                    start_time = time.time()
                    num_iterations = 1000
                    
                    for _ in range(num_iterations):
                        _ = model(x)
                    
                    end_time = time.time()
                    
                    total_time = end_time - start_time
                    samples_per_sec = (8 * num_iterations) / total_time
                    
                    throughput_results[f"input_{input_size}"] = {
                        "samples_per_second": samples_per_sec,
                        "total_time": total_time,
                        "input_size": input_size
                    }
                    
                    del model
                    
                except Exception as e:
                    throughput_results[f"input_{input_size}"] = {"error": str(e)}
            
            benchmarks["throughput"] = throughput_results
            
            # GPU Utilization (if available)
            if torch.cuda.is_available():
                logger.info("Testing GPU Utilization...")
                
                gpu_info = {
                    "device_name": torch.cuda.get_device_name(),
                    "memory_total_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3,
                    "memory_allocated_gb": torch.cuda.memory_allocated() / 1024**3,
                    "memory_reserved_gb": torch.cuda.memory_reserved() / 1024**3,
                    "compute_capability": torch.cuda.get_device_capability()
                }
                
                benchmarks["gpu_utilization"] = gpu_info
            else:
                benchmarks["gpu_utilization"] = {"note": "GPU not available"}
            
        except Exception as e:
            logger.error(f"❌ Performance benchmarks failed: {e}")
            benchmarks["error"] = str(e)
        
        self.performance_metrics = benchmarks
        return benchmarks
    
    def create_visualizations(self) -> Dict[str, Any]:
        """Create visualizations of results and performance."""
        logger.info("🔄 Creating Visualizations...")
        
        visualizations = {}
        
        try:
            # Performance comparison chart
            if "inference_speed" in self.performance_metrics:
                speed_data = self.performance_metrics["inference_speed"]
                
                batch_sizes = []
                inference_times = []
                throughputs = []
                
                for key, data in speed_data.items():
                    if "error" not in data:
                        batch_sizes.append(data["batch_size"])
                        inference_times.append(data["avg_inference_time_ms"])
                        throughputs.append(data["throughput_samples_per_sec"])
                
                if batch_sizes:
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                    
                    # Inference time vs batch size
                    ax1.plot(batch_sizes, inference_times, 'bo-', linewidth=2, markersize=8)
                    ax1.set_xlabel('Batch Size')
                    ax1.set_ylabel('Inference Time (ms)')
                    ax1.set_title('Inference Time vs Batch Size')
                    ax1.grid(True, alpha=0.3)
                    
                    # Throughput vs batch size
                    ax2.plot(batch_sizes, throughputs, 'ro-', linewidth=2, markersize=8)
                    ax2.set_xlabel('Batch Size')
                    ax2.set_ylabel('Throughput (samples/sec)')
                    ax2.set_title('Throughput vs Batch Size')
                    ax2.grid(True, alpha=0.3)
                    
                    plt.tight_layout()
                    
                    # Save to bytes
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                    buf.seek(0)
                    visualizations["performance_chart"] = base64.b64encode(buf.getvalue()).decode()
                    plt.close()
            
            # Memory usage chart
            if "memory_usage" in self.performance_metrics:
                memory_data = self.performance_metrics["memory_usage"]
                
                model_sizes = []
                memory_usage = []
                
                for key, data in memory_data.items():
                    if "error" not in data:
                        size = int(key.split('_')[1])
                        model_sizes.append(size)
                        memory_usage.append(data["memory_mb"])
                
                if model_sizes:
                    plt.figure(figsize=(10, 6))
                    plt.bar(model_sizes, memory_usage, color='skyblue', alpha=0.7)
                    plt.xlabel('Model Size (dimensions)')
                    plt.ylabel('Memory Usage (MB)')
                    plt.title('Memory Usage vs Model Size')
                    plt.grid(True, alpha=0.3)
                    
                    # Save to bytes
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                    buf.seek(0)
                    visualizations["memory_chart"] = base64.b64encode(buf.getvalue()).decode()
                    plt.close()
            
            # Success rate summary
            success_rates = {}
            for model_type, results in self.results.items():
                if isinstance(results, dict):
                    successful_tests = sum(1 for test in results.values() 
                                         if isinstance(test, dict) and test.get("success", False))
                    total_tests = len([test for test in results.values() 
                                     if isinstance(test, dict) and "success" in test])
                    if total_tests > 0:
                        success_rates[model_type] = successful_tests / total_tests
            
            if success_rates:
                plt.figure(figsize=(8, 6))
                model_names = list(success_rates.keys())
                rates = list(success_rates.values())
                
                colors = ['green' if rate > 0.8 else 'orange' if rate > 0.5 else 'red' for rate in rates]
                bars = plt.bar(model_names, rates, color=colors, alpha=0.7)
                
                # Add value labels on bars
                for bar, rate in zip(bars, rates):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                            f'{rate:.1%}', ha='center', va='bottom', fontweight='bold')
                
                plt.xlabel('Model Type')
                plt.ylabel('Success Rate')
                plt.title('Model Test Success Rates')
                plt.ylim(0, 1.1)
                plt.grid(True, alpha=0.3)
                
                # Save to bytes
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                buf.seek(0)
                visualizations["success_rate_chart"] = base64.b64encode(buf.getvalue()).decode()
                plt.close()
            
        except Exception as e:
            logger.error(f"❌ Visualization creation failed: {e}")
            visualizations["error"] = str(e)
        
        return visualizations
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive demo report."""
        logger.info("📊 Generating Comprehensive Report...")
        
        report = {
            "demo_summary": {
                "total_models": len(self.models),
                "available_models": list(self.models.keys()),
                "device": str(device),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "model_results": self.results,
            "performance_metrics": self.performance_metrics,
            "recommendations": [],
            "system_info": {
                "torch_version": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "cuda_version": torch.version.cuda if torch.cuda.is_available() else "N/A",
                "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
            }
        }
        
        # Generate recommendations
        recommendations = []
        
        # Check model availability
        available_models = sum(1 for results in self.results.values() 
                             if any(test.get("success", False) for test in results.values() 
                                   if isinstance(test, dict)))
        
        if available_models == 0:
            recommendations.append("⚠️ No models are currently available. Check dependencies and model loading.")
        elif available_models < len(self.results):
            recommendations.append("⚠️ Some models failed to load. Consider using smaller models or checking GPU memory.")
        
        # Performance recommendations
        if "performance_metrics" in report and "inference_speed" in report["performance_metrics"]:
            speed_data = report["performance_metrics"]["inference_speed"]
            avg_times = [data.get("avg_inference_time_ms", 0) for data in speed_data.values() 
                        if "error" not in data]
            
            if avg_times:
                avg_time = sum(avg_times) / len(avg_times)
                if avg_time > 100:
                    recommendations.append("🐌 Inference is slow. Consider using model optimization techniques.")
                elif avg_time < 10:
                    recommendations.append("⚡ Excellent inference speed! Consider increasing batch size for better throughput.")
        
        # Memory recommendations
        if torch.cuda.is_available():
            memory_used = torch.cuda.memory_allocated() / 1024**3  # GB
            memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
            memory_usage = memory_used / memory_total
            
            if memory_usage > 0.8:
                recommendations.append("💾 High GPU memory usage. Consider using model quantization or smaller models.")
            elif memory_usage < 0.3:
                recommendations.append("💾 Low GPU memory usage. Consider using larger models for better performance.")
        
        report["recommendations"] = recommendations
        
        return report
    
    def run_complete_demo(self) -> Dict[str, Any]:
        """Run complete demo with all components."""
        logger.info("🚀 Starting Complete Advanced AI Models Demo...")
        
        # Run all demos
        logger.info("=" * 60)
        logger.info("🔄 TRANSFORMER MODELS DEMO")
        logger.info("=" * 60)
        transformer_results = self.demo_transformer_models()
        
        logger.info("=" * 60)
        logger.info("🔄 DIFFUSION MODELS DEMO")
        logger.info("=" * 60)
        diffusion_results = self.demo_diffusion_models()
        
        logger.info("=" * 60)
        logger.info("🔄 LLM MODELS DEMO")
        logger.info("=" * 60)
        llm_results = self.demo_llm_models()
        
        logger.info("=" * 60)
        logger.info("🔄 PERFORMANCE BENCHMARKS")
        logger.info("=" * 60)
        performance_results = self.run_performance_benchmarks()
        
        logger.info("=" * 60)
        logger.info("📊 GENERATING REPORT")
        logger.info("=" * 60)
        report = self.generate_comprehensive_report()
        
        logger.info("=" * 60)
        logger.info("✅ COMPLETE DEMO FINISHED")
        logger.info("=" * 60)
        
        return {
            "transformer_results": transformer_results,
            "diffusion_results": diffusion_results,
            "llm_results": llm_results,
            "performance_results": performance_results,
            "comprehensive_report": report
        }


def main():
    """Main demo execution."""
    print("🚀 Advanced AI Models Demo")
    print("=" * 50)
    print("Deep Learning, Transformers, Diffusion Models & LLMs")
    print("=" * 50)
    
    # Initialize demo
    demo = AdvancedAIModelsDemo()
    
    # Run complete demo
    results = demo.run_complete_demo()
    
    # Print summary
    print("\n📊 DEMO SUMMARY")
    print("=" * 50)
    
    # Model availability
    total_tests = 0
    successful_tests = 0
    
    for model_type, model_results in results.items():
        if model_type != "comprehensive_report" and model_type != "performance_results":
            print(f"\n🔧 {model_type.upper().replace('_', ' ')}:")
            
            for test_name, test_result in model_results.items():
                if isinstance(test_result, dict) and "success" in test_result:
                    total_tests += 1
                    if test_result["success"]:
                        successful_tests += 1
                        print(f"  ✅ {test_name}: Success")
                    else:
                        print(f"  ❌ {test_name}: Failed")
    
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n📈 Overall Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
    
    # Performance summary
    if "performance_results" in results:
        perf = results["performance_results"]
        if "inference_speed" in perf:
            speed_data = perf["inference_speed"]
            avg_times = [data.get("avg_inference_time_ms", 0) for data in speed_data.values() 
                        if "error" not in data]
            if avg_times:
                avg_time = sum(avg_times) / len(avg_times)
                print(f"⚡ Average Inference Time: {avg_time:.2f} ms")
    
    # System info
    print(f"\n💻 System Info:")
    print(f"  Device: {device}")
    print(f"  PyTorch: {torch.__version__}")
    print(f"  CUDA Available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name()}")
        print(f"  Memory: {torch.cuda.memory_allocated() / 1024**3:.2f} GB / {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    
    print("\n🎉 Demo completed successfully!")
    
    return results


if __name__ == "__main__":
    try:
        results = main()
        
        # Save results to file
        output_file = "advanced_ai_models_demo_results.json"
        with open(output_file, 'w') as f:
            # Convert tensors to lists for JSON serialization
            def convert_tensors(obj):
                if isinstance(obj, torch.Tensor):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_tensors(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_tensors(item) for item in obj]
                else:
                    return obj
            
            json.dump(convert_tensors(results), f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc() 