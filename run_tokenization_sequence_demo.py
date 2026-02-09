#!/usr/bin/env python3
"""
Tokenization and Sequence Handling Demo for Diffusion Models

Comprehensive demonstration of tokenization and sequence handling
with multiple examples, performance tests, and validation scenarios.
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

# Import tokenization and sequence system
from core.tokenization_sequence_system import (
    TokenizationSequenceSystem, TokenizerConfig, SequenceConfig, TextProcessingConfig,
    TokenizerType, SequenceStrategy
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tokenization_sequence_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TokenizationSequenceDemo:
    """Comprehensive demo for tokenization and sequence handling."""
    
    def __init__(self):
        self.system = TokenizationSequenceSystem()
        self.start_time = None
    
    async def initialize_systems(self):
        """Initialize various tokenization and sequence systems."""
        try:
            logger.info("🚀 Initializing Tokenization and Sequence Systems...")
            
            # System 1: CLIP for Stable Diffusion
            clip_tokenizer_config = TokenizerConfig(
                model_name="openai/clip-vit-base-patch32",
                tokenizer_type=TokenizerType.CLIP,
                max_length=77,
                padding="max_length",
                truncation="longest_first"
            )
            
            clip_sequence_config = SequenceConfig(
                strategy=SequenceStrategy.TRUNCATE,
                max_length=77,
                padding_side="right",
                truncation_side="right"
            )
            
            clip_text_config = TextProcessingConfig(
                lowercase=False,
                remove_extra_whitespace=True,
                normalize_unicode=True,
                custom_filters=["artistic_style", "diffusion_optimized"],
                max_words=20,
                min_words=1
            )
            
            clip_processor = self.system.add_processor(
                "clip", clip_tokenizer_config, clip_sequence_config, clip_text_config
            )
            logger.info("✅ CLIP processor initialized")
            
            # System 2: T5 for Stable Diffusion XL
            t5_tokenizer_config = TokenizerConfig(
                model_name="t5-base",
                tokenizer_type=TokenizerType.T5,
                max_length=77,
                padding="max_length",
                truncation="longest_first"
            )
            
            t5_sequence_config = SequenceConfig(
                strategy=SequenceStrategy.TRUNCATE,
                max_length=77,
                padding_side="right",
                truncation_side="right"
            )
            
            t5_text_config = TextProcessingConfig(
                lowercase=False,
                remove_extra_whitespace=True,
                normalize_unicode=True,
                max_words=20,
                min_words=1
            )
            
            t5_processor = self.system.add_processor(
                "t5", t5_tokenizer_config, t5_sequence_config, t5_text_config
            )
            logger.info("✅ T5 processor initialized")
            
            # System 3: GPT-2 for text generation
            gpt2_tokenizer_config = TokenizerConfig(
                model_name="gpt2",
                tokenizer_type=TokenizerType.GPT2,
                max_length=512,
                padding="max_length",
                truncation="longest_first"
            )
            
            gpt2_sequence_config = SequenceConfig(
                strategy=SequenceStrategy.CHUNK,
                max_length=512,
                chunk_size=512,
                overlap=50,
                padding_side="right",
                truncation_side="right"
            )
            
            gpt2_text_config = TextProcessingConfig(
                lowercase=False,
                remove_extra_whitespace=True,
                normalize_unicode=True,
                max_words=100,
                min_words=1
            )
            
            gpt2_processor = self.system.add_processor(
                "gpt2", gpt2_tokenizer_config, gpt2_sequence_config, gpt2_text_config
            )
            logger.info("✅ GPT-2 processor initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize systems: {e}")
            return False
    
    async def demo_text_preprocessing(self):
        """Demo text preprocessing capabilities."""
        try:
            logger.info("📝 Demo: Text Preprocessing")
            
            test_texts = [
                "A beautiful sunset over the mountains, digital art style",
                "A futuristic city with flying cars, sci-fi style",
                "A serene forest with ancient trees, fantasy art style",
                "High quality, detailed, sharp focus portrait",
                "Blurry, low quality, pixelated image",
                "A cat sitting on a windowsill, looking out at the rain",
                "An astronaut riding a horse on Mars, digital art",
                "A cyberpunk street scene with neon lights and flying cars"
            ]
            
            # Test different preprocessing configurations
            configs = [
                ("Basic", TextProcessingConfig()),
                ("Artistic", TextProcessingConfig(
                    custom_filters=["artistic_style", "diffusion_optimized"]
                )),
                ("Aggressive", TextProcessingConfig(
                    lowercase=True,
                    remove_punctuation=True,
                    remove_numbers=True,
                    custom_filters=["artistic_style", "diffusion_optimized"]
                ))
            ]
            
            for config_name, config in configs:
                logger.info(f"  Testing {config_name} preprocessing:")
                
                from core.tokenization_sequence_system import TextPreprocessor
                preprocessor = TextPreprocessor(config)
                
                for i, text in enumerate(test_texts[:3], 1):
                    processed = preprocessor.process(text)
                    logger.info(f"    Text {i}: {text}")
                    logger.info(f"    Processed: {processed}")
                    logger.info(f"    Length change: {len(text)} -> {len(processed)}")
                    logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Text preprocessing demo failed: {e}")
            return False
    
    async def demo_tokenization_methods(self):
        """Demo different tokenization methods."""
        try:
            logger.info("🔤 Demo: Tokenization Methods")
            
            test_prompts = [
                "A beautiful sunset over the mountains",
                "A futuristic city with flying cars",
                "A serene forest with ancient trees"
            ]
            
            processors = ["clip", "t5", "gpt2"]
            
            for processor_name in processors:
                logger.info(f"  Testing {processor_name.upper()} tokenization:")
                
                processor = self.system.get_processor(processor_name)
                if not processor:
                    continue
                
                for i, prompt in enumerate(test_prompts, 1):
                    # Process prompt
                    result = processor.process_prompt(prompt)
                    
                    logger.info(f"    Prompt {i}: {prompt}")
                    logger.info(f"    Processed text: {result['text']}")
                    logger.info(f"    Token count: {result['token_count']}")
                    logger.info(f"    Input IDs shape: {result['input_ids'].shape}")
                    logger.info(f"    Attention mask shape: {result['attention_mask'].shape}")
                    
                    # Decode tokens back
                    decoded = processor.tokenizer.decode_tokens(result['input_ids'])
                    logger.info(f"    Decoded: {decoded}")
                    logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Tokenization methods demo failed: {e}")
            return False
    
    async def demo_sequence_handling(self):
        """Demo different sequence handling strategies."""
        try:
            logger.info("📏 Demo: Sequence Handling Strategies")
            
            # Create a long text for testing
            long_text = """
            This is a very long text that will be used to test different sequence handling strategies.
            It contains multiple sentences and should be long enough to demonstrate truncation, padding,
            sliding windows, and chunking. The text includes various types of content such as descriptions,
            technical terms, and artistic expressions. We want to see how different strategies handle
            this long sequence and what the results look like.
            """ * 3  # Repeat to make it longer
            
            from core.tokenization_sequence_system import SequenceHandler, SequenceConfig
            
            strategies = [
                ("Truncate", SequenceStrategy.TRUNCATE),
                ("Pad", SequenceStrategy.PAD),
                ("Slide", SequenceStrategy.SLIDE),
                ("Chunk", SequenceStrategy.CHUNK)
            ]
            
            # Tokenize the text first
            processor = self.system.get_processor("gpt2")
            if not processor:
                logger.warning("GPT-2 processor not available, skipping sequence handling demo")
                return True
            
            tokens = processor.tokenizer.encode_text(long_text)
            logger.info(f"  Original text tokens: {len(tokens)}")
            
            for strategy_name, strategy in strategies:
                logger.info(f"  Testing {strategy_name} strategy:")
                
                config = SequenceConfig(
                    strategy=strategy,
                    max_length=50,
                    chunk_size=100,
                    overlap=20,
                    stride=10
                )
                
                handler = SequenceHandler(config)
                sequences = handler.handle_sequence(tokens)
                
                logger.info(f"    Number of sequences: {len(sequences)}")
                for i, seq in enumerate(sequences[:3], 1):  # Show first 3
                    logger.info(f"    Sequence {i} length: {len(seq)}")
                    logger.info(f"    Sequence {i} tokens: {seq[:10]}...")  # Show first 10 tokens
                
                # Create attention masks
                masks = handler.create_attention_mask(sequences)
                logger.info(f"    Attention masks created: {len(masks)}")
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Sequence handling demo failed: {e}")
            return False
    
    async def demo_batch_processing(self):
        """Demo batch processing capabilities."""
        try:
            logger.info("📦 Demo: Batch Processing")
            
            test_prompts = [
                "A beautiful sunset over the mountains, digital art style",
                "A futuristic city with flying cars, sci-fi style",
                "A serene forest with ancient trees, fantasy art style",
                "A cyberpunk street scene with neon lights",
                "A peaceful lake reflecting the sky, impressionist style",
                "A steampunk airship flying through clouds",
                "A magical forest with glowing mushrooms",
                "A desert landscape with ancient ruins"
            ]
            
            processors = ["clip", "t5"]
            
            for processor_name in processors:
                logger.info(f"  Testing {processor_name.upper()} batch processing:")
                
                processor = self.system.get_processor(processor_name)
                if not processor:
                    continue
                
                # Process batch
                start_time = time.time()
                batch_result = processor.process_prompts_batch(test_prompts)
                batch_time = time.time() - start_time
                
                logger.info(f"    Batch processing time: {batch_time:.3f}s")
                logger.info(f"    Input IDs shape: {batch_result['input_ids'].shape}")
                logger.info(f"    Attention mask shape: {batch_result['attention_mask'].shape}")
                logger.info(f"    Number of texts: {len(batch_result['texts'])}")
                logger.info(f"    Token counts: {batch_result['token_counts']}")
                
                # Compare with individual processing
                start_time = time.time()
                individual_results = []
                for prompt in test_prompts:
                    result = processor.process_prompt(prompt)
                    individual_results.append(result)
                individual_time = time.time() - start_time
                
                logger.info(f"    Individual processing time: {individual_time:.3f}s")
                logger.info(f"    Speedup: {individual_time/batch_time:.2f}x")
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Batch processing demo failed: {e}")
            return False
    
    async def demo_prompt_analysis(self):
        """Demo prompt analysis capabilities."""
        try:
            logger.info("🔍 Demo: Prompt Analysis")
            
            test_prompts = [
                "A beautiful sunset over the mountains, digital art style, high quality, detailed",
                "A futuristic city with flying cars, sci-fi style, sharp focus",
                "A serene forest with ancient trees, fantasy art style, atmospheric lighting",
                "A cyberpunk street scene with neon lights, rain, moody atmosphere",
                "A peaceful lake reflecting the sky, impressionist style, soft colors"
            ]
            
            processor = self.system.get_processor("clip")
            if not processor:
                logger.warning("CLIP processor not available, skipping prompt analysis demo")
                return True
            
            for i, prompt in enumerate(test_prompts, 1):
                logger.info(f"  Analyzing prompt {i}:")
                
                analysis = processor.analyze_prompt(prompt)
                
                logger.info(f"    Original length: {analysis['original_length']}")
                logger.info(f"    Processed length: {analysis['processed_length']}")
                logger.info(f"    Word count: {analysis['word_count']}")
                logger.info(f"    Token count: {analysis['token_count']}")
                logger.info(f"    Avg tokens per word: {analysis['avg_tokens_per_word']:.2f}")
                logger.info(f"    Unique words: {analysis['unique_words']}")
                logger.info(f"    Unique tokens: {analysis['unique_tokens']}")
                logger.info(f"    Special tokens: {analysis['special_tokens']}")
                
                # Show most common words and tokens
                top_words = analysis['word_distribution'].most_common(5)
                top_tokens = analysis['token_distribution'].most_common(5)
                
                logger.info(f"    Top words: {top_words}")
                logger.info(f"    Top tokens: {top_tokens}")
                logger.info(f"    Processed text: {analysis['processed_text']}")
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Prompt analysis demo failed: {e}")
            return False
    
    async def demo_text_encoding(self):
        """Demo text encoding for diffusion models."""
        try:
            logger.info("🎨 Demo: Text Encoding for Diffusion")
            
            test_prompts = [
                "A beautiful sunset over the mountains, digital art style",
                "A futuristic city with flying cars, sci-fi style",
                "A serene forest with ancient trees, fantasy art style"
            ]
            
            processors = ["clip", "t5"]
            
            for processor_name in processors:
                logger.info(f"  Testing {processor_name.upper()} text encoding:")
                
                processor = self.system.get_processor(processor_name)
                if not processor:
                    continue
                
                if processor.text_encoder is None:
                    logger.info(f"    Text encoder not available for {processor_name}")
                    continue
                
                # Single prompt encoding
                start_time = time.time()
                embeddings = processor.encode_prompt(test_prompts[0])
                single_time = time.time() - start_time
                
                logger.info(f"    Single prompt encoding time: {single_time:.3f}s")
                logger.info(f"    Embeddings shape: {embeddings.shape}")
                logger.info(f"    Embeddings dtype: {embeddings.dtype}")
                logger.info(f"    Embeddings device: {embeddings.device}")
                
                # Batch encoding
                start_time = time.time()
                batch_embeddings = processor.encode_prompts_batch(test_prompts)
                batch_time = time.time() - start_time
                
                logger.info(f"    Batch encoding time: {batch_time:.3f}s")
                logger.info(f"    Batch embeddings shape: {batch_embeddings.shape}")
                logger.info(f"    Speedup: {single_time * len(test_prompts) / batch_time:.2f}x")
                
                # Embedding statistics
                logger.info(f"    Embedding mean: {embeddings.mean().item():.4f}")
                logger.info(f"    Embedding std: {embeddings.std().item():.4f}")
                logger.info(f"    Embedding min: {embeddings.min().item():.4f}")
                logger.info(f"    Embedding max: {embeddings.max().item():.4f}")
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Text encoding demo failed: {e}")
            return False
    
    async def demo_performance_comparison(self):
        """Demo performance comparison between different processors."""
        try:
            logger.info("⚡ Demo: Performance Comparison")
            
            test_prompts = [
                "A beautiful sunset over the mountains, digital art style",
                "A futuristic city with flying cars, sci-fi style",
                "A serene forest with ancient trees, fantasy art style",
                "A cyberpunk street scene with neon lights",
                "A peaceful lake reflecting the sky, impressionist style"
            ]
            
            processors = ["clip", "t5", "gpt2"]
            results = {}
            
            for processor_name in processors:
                logger.info(f"  Testing {processor_name.upper()} performance:")
                
                processor = self.system.get_processor(processor_name)
                if not processor:
                    continue
                
                # Processing time
                start_time = time.time()
                batch_result = processor.process_prompts_batch(test_prompts)
                processing_time = time.time() - start_time
                
                # Tokenization time
                start_time = time.time()
                for prompt in test_prompts:
                    processor.tokenizer.encode_text(prompt)
                tokenization_time = time.time() - start_time
                
                # Memory usage (approximate)
                input_ids_size = batch_result['input_ids'].numel() * batch_result['input_ids'].element_size()
                attention_mask_size = batch_result['attention_mask'].numel() * batch_result['attention_mask'].element_size()
                total_memory = (input_ids_size + attention_mask_size) / 1024  # KB
                
                results[processor_name] = {
                    'processing_time': processing_time,
                    'tokenization_time': tokenization_time,
                    'total_memory_kb': total_memory,
                    'avg_tokens': sum(batch_result['token_counts']) / len(batch_result['token_counts'])
                }
                
                logger.info(f"    Processing time: {processing_time:.3f}s")
                logger.info(f"    Tokenization time: {tokenization_time:.3f}s")
                logger.info(f"    Memory usage: {total_memory:.2f} KB")
                logger.info(f"    Average tokens: {results[processor_name]['avg_tokens']:.1f}")
                logger.info("")
            
            # Summary
            logger.info("  Performance Summary:")
            fastest_processor = min(results.keys(), key=lambda x: results[x]['processing_time'])
            logger.info(f"    Fastest processor: {fastest_processor.upper()}")
            
            for processor_name, metrics in results.items():
                speedup = results[fastest_processor]['processing_time'] / metrics['processing_time']
                logger.info(f"    {processor_name.upper()}: {speedup:.2f}x speedup")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Performance comparison demo failed: {e}")
            return False
    
    async def demo_error_handling(self):
        """Demo error handling and edge cases."""
        try:
            logger.info("🛡️ Demo: Error Handling")
            
            processor = self.system.get_processor("clip")
            if not processor:
                logger.warning("CLIP processor not available, skipping error handling demo")
                return True
            
            # Test edge cases
            edge_cases = [
                "",  # Empty string
                "   ",  # Whitespace only
                "A" * 1000,  # Very long text
                "A beautiful sunset over the mountains, digital art style, high quality, detailed, sharp focus, professional photography, 8k resolution, masterpiece, trending on artstation",
                "A cat",  # Very short text
                "A beautiful sunset over the mountains, digital art style, high quality, detailed, sharp focus, professional photography, 8k resolution, masterpiece, trending on artstation, " * 10  # Repeated text
            ]
            
            for i, text in enumerate(edge_cases, 1):
                logger.info(f"  Testing edge case {i}:")
                logger.info(f"    Input: {text[:50]}{'...' if len(text) > 50 else ''}")
                
                try:
                    result = processor.process_prompt(text)
                    logger.info(f"    ✅ Success: {result['token_count']} tokens")
                except Exception as e:
                    logger.info(f"    ❌ Error: {type(e).__name__}: {str(e)}")
                
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error handling demo failed: {e}")
            return False
    
    async def demo_integration_scenarios(self):
        """Demo integration scenarios with diffusion models."""
        try:
            logger.info("🔗 Demo: Integration Scenarios")
            
            # Scenario 1: Stable Diffusion prompt processing
            logger.info("  Scenario 1: Stable Diffusion Prompt Processing")
            
            sd_prompts = [
                "A beautiful sunset over the mountains, digital art style, high quality, detailed",
                "A futuristic city with flying cars, sci-fi style, sharp focus, professional",
                "A serene forest with ancient trees, fantasy art style, atmospheric lighting"
            ]
            
            clip_processor = self.system.get_processor("clip")
            if clip_processor:
                # Process prompts
                batch_result = clip_processor.process_prompts_batch(sd_prompts)
                
                logger.info(f"    Processed {len(batch_result['texts'])} prompts")
                logger.info(f"    Input IDs shape: {batch_result['input_ids'].shape}")
                logger.info(f"    Average tokens: {sum(batch_result['token_counts']) / len(batch_result['token_counts']):.1f}")
                
                # Encode for diffusion
                if clip_processor.text_encoder:
                    embeddings = clip_processor.encode_prompts_batch(sd_prompts)
                    logger.info(f"    Text embeddings shape: {embeddings.shape}")
                    logger.info(f"    Ready for diffusion model")
                logger.info("")
            
            # Scenario 2: Multi-modal text processing
            logger.info("  Scenario 2: Multi-modal Text Processing")
            
            multimodal_texts = [
                "A cat sitting on a windowsill",
                "A dog running in a park",
                "A bird flying over the ocean"
            ]
            
            # Process with different tokenizers
            for processor_name in ["clip", "t5"]:
                processor = self.system.get_processor(processor_name)
                if processor:
                    result = processor.process_prompts_batch(multimodal_texts)
                    logger.info(f"    {processor_name.upper()}: {result['input_ids'].shape}")
            
            logger.info("")
            
            # Scenario 3: Text generation preprocessing
            logger.info("  Scenario 3: Text Generation Preprocessing")
            
            generation_texts = [
                "The future of artificial intelligence is",
                "In a world where machines can think,",
                "The most important discovery of the 21st century was"
            ]
            
            gpt2_processor = self.system.get_processor("gpt2")
            if gpt2_processor:
                result = gpt2_processor.process_prompts_batch(generation_texts)
                logger.info(f"    GPT-2 processing: {result['input_ids'].shape}")
                logger.info(f"    Ready for text generation")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Integration scenarios demo failed: {e}")
            return False
    
    async def run(self):
        """Main demo execution."""
        try:
            self.start_time = datetime.now()
            
            logger.info("🚀 Starting Tokenization and Sequence Handling Demo...")
            logger.info(f"⏰ Start time: {self.start_time}")
            
            # Initialize systems
            if not await self.initialize_systems():
                return False
            
            # Run demos
            demos = [
                self.demo_text_preprocessing(),
                self.demo_tokenization_methods(),
                self.demo_sequence_handling(),
                self.demo_batch_processing(),
                self.demo_prompt_analysis(),
                self.demo_text_encoding(),
                self.demo_performance_comparison(),
                self.demo_error_handling(),
                self.demo_integration_scenarios()
            ]
            
            for demo in demos:
                if not await demo:
                    logger.warning("⚠️ Demo completed with warnings")
            
            # Final status
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            logger.info("🎉 Tokenization and Sequence Handling Demo completed successfully!")
            logger.info(f"⏱️  Total duration: {duration}")
            logger.info("📊 All demos executed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Demo execution failed: {e}")
            return False

async def main():
    """Main entry point."""
    demo = TokenizationSequenceDemo()
    
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
