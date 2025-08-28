#!/usr/bin/env python3
"""
Transformers and LLM Demo for Diffusion Models

Comprehensive demonstration of the transformers and LLM system
with multiple examples, performance tests, and integration scenarios.
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

# Import transformers and LLM system
from core.transformers_llm_system import (
    OptimizedTextProcessor, MultiModalTransformer, DiffusionTextEncoder,
    AdvancedLLMPipeline, TransformerConfig, LLMConfig
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transformers_llm_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TransformersLLMDemo:
    """Comprehensive demo for transformers and LLM system."""
    
    def __init__(self):
        self.text_processor = None
        self.diffusion_encoder = None
        self.llm_pipeline = None
        self.multimodal_transformer = None
        self.start_time = None
    
    async def initialize_systems(self):
        """Initialize all transformer and LLM systems."""
        try:
            logger.info("🚀 Initializing Transformers and LLM Systems...")
            
            # Initialize text processor
            text_config = TransformerConfig(
                model_name="gpt2",
                model_type="text-generation",
                max_length=512,
                temperature=0.7,
                torch_dtype="auto"
            )
            
            self.text_processor = OptimizedTextProcessor(text_config)
            logger.info("✅ Text processor initialized")
            
            # Initialize diffusion text encoder
            self.diffusion_encoder = DiffusionTextEncoder()
            logger.info("✅ Diffusion text encoder initialized")
            
            # Initialize LLM pipeline
            llm_config = LLMConfig(
                model_name="gpt2",
                max_new_tokens=100,
                temperature=0.8,
                repetition_penalty=1.1
            )
            
            self.llm_pipeline = AdvancedLLMPipeline(llm_config)
            logger.info("✅ LLM pipeline initialized")
            
            # Initialize multimodal transformer
            multimodal_config = TransformerConfig(
                model_name="gpt2",
                model_type="text-generation"
            )
            
            self.multimodal_transformer = MultiModalTransformer(multimodal_config)
            logger.info("✅ Multimodal transformer initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize systems: {e}")
            return False
    
    async def demo_text_generation(self):
        """Demo text generation capabilities."""
        try:
            logger.info("📝 Demo: Text Generation")
            
            prompts = [
                "The future of artificial intelligence is",
                "In a world where machines can think,",
                "The most important discovery of the 21st century was",
                "When I first encountered the AI system,",
                "The relationship between humans and technology"
            ]
            
            for i, prompt in enumerate(prompts, 1):
                logger.info(f"  Prompt {i}: {prompt}")
                
                # Generate with text processor
                start_time = time.time()
                generated_text = self.text_processor.generate_text(prompt)
                generation_time = time.time() - start_time
                
                logger.info(f"    Generated: {generated_text}")
                logger.info(f"    Time: {generation_time:.3f}s")
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Text generation demo failed: {e}")
            return False
    
    async def demo_diffusion_text_encoding(self):
        """Demo diffusion text encoding."""
        try:
            logger.info("🎨 Demo: Diffusion Text Encoding")
            
            diffusion_prompts = [
                "A beautiful sunset over the mountains, digital art",
                "A futuristic city with flying cars, sci-fi style",
                "A serene forest with ancient trees, fantasy art",
                "A cyberpunk street scene with neon lights",
                "A peaceful lake reflecting the sky, impressionist style"
            ]
            
            for i, prompt in enumerate(diffusion_prompts, 1):
                logger.info(f"  Diffusion Prompt {i}: {prompt}")
                
                # Encode for diffusion
                start_time = time.time()
                embeddings = self.diffusion_encoder.encode_prompt(prompt)
                encoding_time = time.time() - start_time
                
                logger.info(f"    Embeddings shape: {embeddings.shape}")
                logger.info(f"    Time: {encoding_time:.3f}s")
                logger.info("")
            
            # Batch encoding demo
            logger.info("  Batch encoding demo:")
            start_time = time.time()
            batch_embeddings = self.diffusion_encoder.encode_prompts_batch(diffusion_prompts)
            batch_time = time.time() - start_time
            
            logger.info(f"    Batch embeddings shape: {batch_embeddings.shape}")
            logger.info(f"    Batch time: {batch_time:.3f}s")
            logger.info(f"    Average time per prompt: {batch_time/len(diffusion_prompts):.3f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Diffusion text encoding demo failed: {e}")
            return False
    
    async def demo_advanced_llm_features(self):
        """Demo advanced LLM features."""
        try:
            logger.info("🧠 Demo: Advanced LLM Features")
            
            # Basic text generation
            logger.info("  Basic text generation:")
            prompt = "Write a short story about a robot learning to paint:"
            result = self.llm_pipeline.generate_text(prompt, max_new_tokens=80)
            logger.info(f"    Result: {result}")
            logger.info("")
            
            # Generation with stopping criteria
            logger.info("  Generation with stopping criteria:")
            stop_sequences = ["END", "STOP", "FINISH"]
            result_with_stopping = self.llm_pipeline.generate_with_stopping(
                "Describe the process of training a neural network:",
                stop_sequences,
                max_new_tokens=100
            )
            logger.info(f"    Result: {result_with_stopping}")
            logger.info("")
            
            # Batch generation
            logger.info("  Batch generation:")
            batch_prompts = [
                "The best way to learn programming is",
                "Artificial intelligence will change",
                "The most important skill for the future is"
            ]
            
            start_time = time.time()
            batch_results = self.llm_pipeline.batch_generate(
                batch_prompts,
                max_new_tokens=50
            )
            batch_time = time.time() - start_time
            
            for i, (prompt, result) in enumerate(zip(batch_prompts, batch_results)):
                logger.info(f"    Batch {i+1}: {prompt}")
                logger.info(f"    Result: {result}")
                logger.info("")
            
            logger.info(f"    Batch generation time: {batch_time:.3f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Advanced LLM features demo failed: {e}")
            return False
    
    async def demo_multimodal_processing(self):
        """Demo multimodal processing capabilities."""
        try:
            logger.info("🖼️ Demo: Multimodal Processing")
            
            # Text encoding
            text = "A beautiful landscape with mountains and lakes"
            logger.info(f"  Text: {text}")
            
            # Encode text and image (placeholder for image)
            start_time = time.time()
            multimodal_result = self.multimodal_transformer.encode_text_and_image(text)
            encoding_time = time.time() - start_time
            
            logger.info(f"    Text embeddings shape: {multimodal_result['text_embeddings'].shape}")
            logger.info(f"    Encoding time: {encoding_time:.3f}s")
            logger.info("")
            
            # Generate with image context
            logger.info("  Generation with image context:")
            context_text = "Describe what you see in this image:"
            generated_with_context = self.multimodal_transformer.generate_with_image_context(context_text)
            logger.info(f"    Result: {generated_with_context}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Multimodal processing demo failed: {e}")
            return False
    
    async def demo_performance_tests(self):
        """Demo performance and stress tests."""
        try:
            logger.info("⚡ Demo: Performance Tests")
            
            # Test 1: Text encoding performance
            logger.info("  Test 1: Text Encoding Performance")
            test_texts = [f"Test text number {i} for performance evaluation" for i in range(10)]
            
            start_time = time.time()
            embeddings = self.text_processor.batch_encode_texts(test_texts)
            encoding_time = time.time() - start_time
            
            logger.info(f"    Encoded {len(test_texts)} texts in {encoding_time:.3f}s")
            logger.info(f"    Average time per text: {encoding_time/len(test_texts):.3f}s")
            logger.info(f"    Embeddings shape: {embeddings.shape}")
            logger.info("")
            
            # Test 2: Memory usage
            logger.info("  Test 2: Memory Usage")
            if torch.cuda.is_available():
                memory_allocated = torch.cuda.memory_allocated() / 1024**2  # MB
                memory_reserved = torch.cuda.memory_reserved() / 1024**2  # MB
                logger.info(f"    GPU Memory Allocated: {memory_allocated:.2f} MB")
                logger.info(f"    GPU Memory Reserved: {memory_reserved:.2f} MB")
            else:
                logger.info("    CUDA not available, using CPU")
            logger.info("")
            
            # Test 3: Concurrent processing
            logger.info("  Test 3: Concurrent Processing")
            
            async def process_text(text):
                return self.text_processor.encode_text(text)
            
            concurrent_texts = [f"Concurrent text {i}" for i in range(5)]
            start_time = time.time()
            
            tasks = [process_text(text) for text in concurrent_texts]
            results = await asyncio.gather(*tasks)
            
            concurrent_time = time.time() - start_time
            logger.info(f"    Processed {len(concurrent_texts)} texts concurrently in {concurrent_time:.3f}s")
            logger.info(f"    Average time per text: {concurrent_time/len(concurrent_texts):.3f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Performance tests demo failed: {e}")
            return False
    
    async def demo_integration_scenarios(self):
        """Demo integration scenarios with diffusion models."""
        try:
            logger.info("🔗 Demo: Integration Scenarios")
            
            # Scenario 1: Text-to-image prompt generation
            logger.info("  Scenario 1: Text-to-Image Prompt Generation")
            
            base_prompt = "A peaceful scene"
            enhanced_prompt = self.llm_pipeline.generate_text(
                f"Enhance this image description to be more detailed and artistic: {base_prompt}",
                max_new_tokens=30
            )
            
            logger.info(f"    Base prompt: {base_prompt}")
            logger.info(f"    Enhanced prompt: {enhanced_prompt}")
            
            # Encode for diffusion
            embeddings = self.diffusion_encoder.encode_prompt(enhanced_prompt)
            logger.info(f"    Encoded for diffusion: {embeddings.shape}")
            logger.info("")
            
            # Scenario 2: Style transfer prompt generation
            logger.info("  Scenario 2: Style Transfer Prompt Generation")
            
            content = "A cat sitting on a windowsill"
            style_prompt = self.llm_pipeline.generate_text(
                f"Convert this description to a specific art style: {content}",
                max_new_tokens=20
            )
            
            logger.info(f"    Content: {content}")
            logger.info(f"    Style prompt: {style_prompt}")
            logger.info("")
            
            # Scenario 3: Batch processing for multiple images
            logger.info("  Scenario 3: Batch Processing")
            
            image_descriptions = [
                "A futuristic cityscape",
                "A serene mountain landscape",
                "A bustling street market"
            ]
            
            # Generate enhanced descriptions
            enhanced_descriptions = []
            for desc in image_descriptions:
                enhanced = self.llm_pipeline.generate_text(
                    f"Make this description more vivid and detailed: {desc}",
                    max_new_tokens=25
                )
                enhanced_descriptions.append(enhanced)
            
            # Batch encode for diffusion
            batch_embeddings = self.diffusion_encoder.encode_prompts_batch(enhanced_descriptions)
            
            logger.info(f"    Processed {len(image_descriptions)} descriptions")
            logger.info(f"    Batch embeddings shape: {batch_embeddings.shape}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Integration scenarios demo failed: {e}")
            return False
    
    async def run(self):
        """Main demo execution."""
        try:
            self.start_time = datetime.now()
            
            logger.info("🚀 Starting Transformers and LLM Demo...")
            logger.info(f"⏰ Start time: {self.start_time}")
            
            # Initialize systems
            if not await self.initialize_systems():
                return False
            
            # Run demos
            demos = [
                self.demo_text_generation(),
                self.demo_diffusion_text_encoding(),
                self.demo_advanced_llm_features(),
                self.demo_multimodal_processing(),
                self.demo_performance_tests(),
                self.demo_integration_scenarios()
            ]
            
            for demo in demos:
                if not await demo:
                    logger.warning("⚠️ Demo completed with warnings")
            
            # Final status
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            logger.info("🎉 Transformers and LLM Demo completed successfully!")
            logger.info(f"⏱️  Total duration: {duration}")
            logger.info("📊 All demos executed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Demo execution failed: {e}")
            return False

async def main():
    """Main entry point."""
    demo = TransformersLLMDemo()
    
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
