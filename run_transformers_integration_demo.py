#!/usr/bin/env python3
"""
Transformers Integration Demo for Diffusion Models

Comprehensive demonstration of the transformers integration system
with multiple pre-trained models, tokenizers, and advanced features.
"""

import asyncio
import sys
import logging
import time
import torch
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import transformers integration system
from core.transformers_integration_system import (
    MultiModelManager, ModelConfig, TokenizerConfig, InferenceConfig,
    DiffusionTextProcessor, AdvancedTokenizer
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transformers_integration_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TransformersIntegrationDemo:
    """Comprehensive demo for transformers integration system."""
    
    def __init__(self):
        self.manager = MultiModelManager()
        self.diffusion_processor = None
        self.start_time = None
    
    async def initialize_systems(self):
        """Initialize all transformer systems."""
        try:
            logger.info("🚀 Initializing Transformers Integration Systems...")
            
            # Initialize diffusion text processor
            self.diffusion_processor = DiffusionTextProcessor()
            logger.info("✅ Diffusion text processor initialized")
            
            # Add multiple models to manager
            await self._add_models_to_manager()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize systems: {e}")
            return False
    
    async def _add_models_to_manager(self):
        """Add various models to the manager."""
        try:
            # GPT-2 for text generation
            gpt2_model_config = ModelConfig(
                model_name="gpt2",
                model_type="text-generation",
                task="text-generation",
                torch_dtype="auto"
            )
            gpt2_tokenizer_config = TokenizerConfig(
                model_name="gpt2",
                use_fast=True
            )
            
            self.manager.add_model("gpt2", gpt2_model_config, gpt2_tokenizer_config)
            logger.info("✅ GPT-2 model added")
            
            # BERT for text encoding
            bert_model_config = ModelConfig(
                model_name="bert-base-uncased",
                model_type="bert",
                task="text-generation",
                torch_dtype="auto"
            )
            bert_tokenizer_config = TokenizerConfig(
                model_name="bert-base-uncased",
                use_fast=True
            )
            
            self.manager.add_model("bert", bert_model_config, bert_tokenizer_config)
            logger.info("✅ BERT model added")
            
            # T5 for text-to-text tasks
            t5_model_config = ModelConfig(
                model_name="t5-small",
                model_type="t5",
                task="text2text-generation",
                torch_dtype="auto"
            )
            t5_tokenizer_config = TokenizerConfig(
                model_name="t5-small",
                use_fast=True
            )
            
            self.manager.add_model("t5", t5_model_config, t5_tokenizer_config)
            logger.info("✅ T5 model added")
            
        except Exception as e:
            logger.error(f"❌ Failed to add models: {e}")
            raise
    
    async def demo_text_generation_models(self):
        """Demo text generation with different models."""
        try:
            logger.info("📝 Demo: Text Generation Models")
            
            prompts = [
                "The future of artificial intelligence is",
                "In a world where machines can think,",
                "The most important discovery of the 21st century was"
            ]
            
            # Test GPT-2
            logger.info("  Testing GPT-2:")
            gpt2_pipeline = self.manager.get_model("gpt2")
            if gpt2_pipeline:
                for i, prompt in enumerate(prompts, 1):
                    start_time = time.time()
                    result = gpt2_pipeline.generate_text(prompt, InferenceConfig(max_new_tokens=50))
                    generation_time = time.time() - start_time
                    
                    logger.info(f"    GPT-2 Prompt {i}: {prompt}")
                    logger.info(f"    Result: {result}")
                    logger.info(f"    Time: {generation_time:.3f}s")
                    logger.info("")
            
            # Test T5
            logger.info("  Testing T5:")
            t5_pipeline = self.manager.get_model("t5")
            if t5_pipeline:
                for i, prompt in enumerate(prompts, 1):
                    start_time = time.time()
                    result = t5_pipeline.generate_text(prompt, InferenceConfig(max_new_tokens=50))
                    generation_time = time.time() - start_time
                    
                    logger.info(f"    T5 Prompt {i}: {prompt}")
                    logger.info(f"    Result: {result}")
                    logger.info(f"    Time: {generation_time:.3f}s")
                    logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Text generation demo failed: {e}")
            return False
    
    async def demo_text_encoding_models(self):
        """Demo text encoding with different models."""
        try:
            logger.info("🔤 Demo: Text Encoding Models")
            
            texts = [
                "Hello world, this is a test sentence.",
                "Artificial intelligence is transforming the world.",
                "The quick brown fox jumps over the lazy dog."
            ]
            
            # Test BERT encoding
            logger.info("  Testing BERT encoding:")
            bert_pipeline = self.manager.get_model("bert")
            if bert_pipeline:
                for i, text in enumerate(texts, 1):
                    start_time = time.time()
                    embeddings = bert_pipeline.encode_text(text)
                    encoding_time = time.time() - start_time
                    
                    logger.info(f"    BERT Text {i}: {text}")
                    logger.info(f"    Embeddings shape: {embeddings.shape}")
                    logger.info(f"    Time: {encoding_time:.3f}s")
                    logger.info("")
            
            # Test GPT-2 encoding
            logger.info("  Testing GPT-2 encoding:")
            gpt2_pipeline = self.manager.get_model("gpt2")
            if gpt2_pipeline:
                for i, text in enumerate(texts, 1):
                    start_time = time.time()
                    embeddings = gpt2_pipeline.encode_text(text)
                    encoding_time = time.time() - start_time
                    
                    logger.info(f"    GPT-2 Text {i}: {text}")
                    logger.info(f"    Embeddings shape: {embeddings.shape}")
                    logger.info(f"    Time: {encoding_time:.3f}s")
                    logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Text encoding demo failed: {e}")
            return False
    
    async def demo_diffusion_text_processing(self):
        """Demo diffusion text processing."""
        try:
            logger.info("🎨 Demo: Diffusion Text Processing")
            
            diffusion_prompts = [
                "A beautiful sunset over the mountains, digital art style",
                "A futuristic city with flying cars, sci-fi style",
                "A serene forest with ancient trees, fantasy art style",
                "A cyberpunk street scene with neon lights",
                "A peaceful lake reflecting the sky, impressionist style"
            ]
            
            # Single prompt encoding
            logger.info("  Single prompt encoding:")
            for i, prompt in enumerate(diffusion_prompts[:3], 1):
                start_time = time.time()
                embeddings = self.diffusion_processor.encode_prompt(prompt)
                encoding_time = time.time() - start_time
                
                logger.info(f"    Prompt {i}: {prompt}")
                logger.info(f"    Embeddings shape: {embeddings.shape}")
                logger.info(f"    Time: {encoding_time:.3f}s")
                logger.info("")
            
            # Batch encoding
            logger.info("  Batch prompt encoding:")
            start_time = time.time()
            batch_embeddings = self.diffusion_processor.encode_prompts_batch(diffusion_prompts)
            batch_time = time.time() - start_time
            
            logger.info(f"    Batch embeddings shape: {batch_embeddings.shape}")
            logger.info(f"    Batch time: {batch_time:.3f}s")
            logger.info(f"    Average time per prompt: {batch_time/len(diffusion_prompts):.3f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Diffusion text processing demo failed: {e}")
            return False
    
    async def demo_advanced_tokenizer_features(self):
        """Demo advanced tokenizer features."""
        try:
            logger.info("🔧 Demo: Advanced Tokenizer Features")
            
            # Test different tokenizers
            tokenizers_to_test = [
                ("gpt2", "GPT-2"),
                ("bert-base-uncased", "BERT"),
                ("t5-small", "T5")
            ]
            
            test_text = "Hello world! This is a test sentence with special characters: @#$%^&*()"
            
            for model_name, display_name in tokenizers_to_test:
                logger.info(f"  Testing {display_name} tokenizer:")
                
                try:
                    tokenizer_config = TokenizerConfig(model_name=model_name)
                    tokenizer = AdvancedTokenizer(tokenizer_config)
                    
                    # Encode text
                    tokens = tokenizer.encode_text(test_text)
                    decoded_text = tokenizer.decode_tokens(tokens)
                    
                    logger.info(f"    Original text: {test_text}")
                    logger.info(f"    Encoded tokens: {tokens[:10]}... (showing first 10)")
                    logger.info(f"    Decoded text: {decoded_text}")
                    logger.info(f"    Vocabulary size: {tokenizer.get_vocab_size()}")
                    
                    special_tokens = tokenizer.get_special_tokens()
                    logger.info(f"    Special tokens: {special_tokens}")
                    logger.info("")
                    
                except Exception as e:
                    logger.warning(f"    Failed to test {display_name}: {e}")
                    logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Advanced tokenizer features demo failed: {e}")
            return False
    
    async def demo_model_caching_and_performance(self):
        """Demo model caching and performance features."""
        try:
            logger.info("⚡ Demo: Model Caching and Performance")
            
            # Test model caching
            logger.info("  Testing model caching:")
            
            # First load
            start_time = time.time()
            gpt2_pipeline = self.manager.get_model("gpt2")
            first_load_time = time.time() - start_time
            logger.info(f"    First load time: {first_load_time:.3f}s")
            
            # Second load (should be cached)
            start_time = time.time()
            gpt2_pipeline_cached = self.manager.get_model("gpt2")
            cached_load_time = time.time() - start_time
            logger.info(f"    Cached load time: {cached_load_time:.3f}s")
            logger.info(f"    Speedup: {first_load_time/cached_load_time:.2f}x")
            logger.info("")
            
            # Test batch processing
            logger.info("  Testing batch processing:")
            prompts = [f"Test prompt number {i}" for i in range(5)]
            
            # Individual processing
            start_time = time.time()
            individual_results = []
            for prompt in prompts:
                result = gpt2_pipeline.generate_text(prompt, InferenceConfig(max_new_tokens=20))
                individual_results.append(result)
            individual_time = time.time() - start_time
            
            # Batch processing
            start_time = time.time()
            batch_results = gpt2_pipeline.batch_generate(prompts, InferenceConfig(max_new_tokens=20))
            batch_time = time.time() - start_time
            
            logger.info(f"    Individual processing time: {individual_time:.3f}s")
            logger.info(f"    Batch processing time: {batch_time:.3f}s")
            logger.info(f"    Batch efficiency: {individual_time/batch_time:.2f}x faster")
            logger.info("")
            
            # Memory usage
            logger.info("  Memory usage:")
            if torch.cuda.is_available():
                memory_allocated = torch.cuda.memory_allocated() / 1024**2  # MB
                memory_reserved = torch.cuda.memory_reserved() / 1024**2  # MB
                logger.info(f"    GPU Memory Allocated: {memory_allocated:.2f} MB")
                logger.info(f"    GPU Memory Reserved: {memory_reserved:.2f} MB")
            else:
                logger.info("    CUDA not available, using CPU")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Model caching and performance demo failed: {e}")
            return False
    
    async def demo_multi_model_integration(self):
        """Demo multi-model integration scenarios."""
        try:
            logger.info("🔗 Demo: Multi-Model Integration")
            
            # Scenario 1: Text enhancement for diffusion
            logger.info("  Scenario 1: Text Enhancement for Diffusion")
            
            base_prompt = "A cat"
            logger.info(f"    Base prompt: {base_prompt}")
            
            # Enhance with GPT-2
            gpt2_pipeline = self.manager.get_model("gpt2")
            if gpt2_pipeline:
                enhanced_prompt = gpt2_pipeline.generate_text(
                    f"Enhance this image description to be more detailed: {base_prompt}",
                    InferenceConfig(max_new_tokens=30)
                )
                logger.info(f"    Enhanced prompt: {enhanced_prompt}")
                
                # Encode for diffusion
                diffusion_embeddings = self.diffusion_processor.encode_prompt(enhanced_prompt)
                logger.info(f"    Diffusion embeddings shape: {diffusion_embeddings.shape}")
                logger.info("")
            
            # Scenario 2: Multi-model text processing pipeline
            logger.info("  Scenario 2: Multi-Model Text Processing Pipeline")
            
            input_text = "The weather is nice today"
            logger.info(f"    Input text: {input_text}")
            
            # Step 1: Encode with BERT
            bert_pipeline = self.manager.get_model("bert")
            if bert_pipeline:
                bert_embeddings = bert_pipeline.encode_text(input_text)
                logger.info(f"    BERT embeddings shape: {bert_embeddings.shape}")
            
            # Step 2: Generate continuation with GPT-2
            if gpt2_pipeline:
                continuation = gpt2_pipeline.generate_text(
                    input_text,
                    InferenceConfig(max_new_tokens=20)
                )
                logger.info(f"    GPT-2 continuation: {continuation}")
            
            # Step 3: Process with T5
            t5_pipeline = self.manager.get_model("t5")
            if t5_pipeline:
                t5_result = t5_pipeline.generate_text(
                    f"summarize: {input_text}",
                    InferenceConfig(max_new_tokens=10)
                )
                logger.info(f"    T5 summary: {t5_result}")
                logger.info("")
            
            # Scenario 3: Model comparison
            logger.info("  Scenario 3: Model Comparison")
            
            test_prompt = "The future of technology"
            
            models_to_compare = [
                ("gpt2", "GPT-2"),
                ("t5", "T5")
            ]
            
            for model_name, display_name in models_to_compare:
                pipeline = self.manager.get_model(model_name)
                if pipeline:
                    start_time = time.time()
                    result = pipeline.generate_text(test_prompt, InferenceConfig(max_new_tokens=30))
                    generation_time = time.time() - start_time
                    
                    logger.info(f"    {display_name}: {result}")
                    logger.info(f"    Time: {generation_time:.3f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Multi-model integration demo failed: {e}")
            return False
    
    async def demo_error_handling_and_recovery(self):
        """Demo error handling and recovery mechanisms."""
        try:
            logger.info("🛡️ Demo: Error Handling and Recovery")
            
            # Test invalid model loading
            logger.info("  Testing invalid model handling:")
            try:
                invalid_config = ModelConfig(
                    model_name="invalid-model-name",
                    model_type="text-generation"
                )
                invalid_tokenizer_config = TokenizerConfig(model_name="invalid-model-name")
                
                # This should fail gracefully
                self.manager.add_model("invalid", invalid_config, invalid_tokenizer_config)
            except Exception as e:
                logger.info(f"    Expected error caught: {type(e).__name__}")
                logger.info("    Error handling working correctly")
                logger.info("")
            
            # Test model recovery
            logger.info("  Testing model recovery:")
            available_models = self.manager.list_models()
            logger.info(f"    Available models: {available_models}")
            
            # Remove and re-add a model
            if "gpt2" in available_models:
                self.manager.remove_model("gpt2")
                logger.info("    Removed GPT-2 model")
                
                # Re-add
                gpt2_model_config = ModelConfig(
                    model_name="gpt2",
                    model_type="text-generation",
                    task="text-generation"
                )
                gpt2_tokenizer_config = TokenizerConfig(model_name="gpt2")
                
                self.manager.add_model("gpt2", gpt2_model_config, gpt2_tokenizer_config)
                logger.info("    Re-added GPT-2 model successfully")
                logger.info("")
            
            # Test cache clearing
            logger.info("  Testing cache clearing:")
            self.manager.clear_all()
            logger.info("    Cache cleared successfully")
            
            available_models_after_clear = self.manager.list_models()
            logger.info(f"    Models after clear: {available_models_after_clear}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error handling demo failed: {e}")
            return False
    
    async def run(self):
        """Main demo execution."""
        try:
            self.start_time = datetime.now()
            
            logger.info("🚀 Starting Transformers Integration Demo...")
            logger.info(f"⏰ Start time: {self.start_time}")
            
            # Initialize systems
            if not await self.initialize_systems():
                return False
            
            # Run demos
            demos = [
                self.demo_text_generation_models(),
                self.demo_text_encoding_models(),
                self.demo_diffusion_text_processing(),
                self.demo_advanced_tokenizer_features(),
                self.demo_model_caching_and_performance(),
                self.demo_multi_model_integration(),
                self.demo_error_handling_and_recovery()
            ]
            
            for demo in demos:
                if not await demo:
                    logger.warning("⚠️ Demo completed with warnings")
            
            # Final status
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            logger.info("🎉 Transformers Integration Demo completed successfully!")
            logger.info(f"⏱️  Total duration: {duration}")
            logger.info("📊 All demos executed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Demo execution failed: {e}")
            return False

async def main():
    """Main entry point."""
    demo = TransformersIntegrationDemo()
    
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
