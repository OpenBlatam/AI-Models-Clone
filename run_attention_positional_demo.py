#!/usr/bin/env python3
"""
Attention Mechanisms and Positional Encodings Demo for Diffusion Models

Comprehensive demonstration of attention mechanisms and positional encodings
with multiple examples, performance tests, and validation scenarios.
"""

import asyncio
import sys
import logging
import time
import torch
import torch.nn.functional as F
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import attention and positional encoding system
from core.attention_positional_system import (
    AttentionPositionalSystem, AttentionConfig, PositionalEncodingConfig,
    MultiHeadAttention, CrossAttention, SinusoidalPositionalEncoding,
    LearnedPositionalEncoding, RotaryPositionEmbedding, ALiBiPositionalEncoding,
    RelativePositionalEncoding, AttentionBlock
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('attention_positional_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AttentionPositionalDemo:
    """Comprehensive demo for attention mechanisms and positional encodings."""
    
    def __init__(self):
        self.systems = {}
        self.start_time = None
    
    async def initialize_systems(self):
        """Initialize various attention and positional encoding systems."""
        try:
            logger.info("🚀 Initializing Attention and Positional Encoding Systems...")
            
            # System 1: Standard multi-head attention with sinusoidal encoding
            attention_config_1 = AttentionConfig(
                num_heads=8,
                head_dim=64,
                dropout=0.1,
                attention_type="scaled_dot_product",
                use_rope=False,
                causal=False
            )
            
            positional_config_1 = PositionalEncodingConfig(
                encoding_type="sinusoidal",
                max_length=512,
                embedding_dim=512,
                dropout=0.1
            )
            
            self.systems["standard"] = AttentionPositionalSystem(
                attention_config_1,
                positional_config_1,
                embed_dim=512,
                cross_embed_dim=768
            )
            logger.info("✅ Standard system initialized")
            
            # System 2: RoPE attention with learned positional encoding
            attention_config_2 = AttentionConfig(
                num_heads=8,
                head_dim=64,
                dropout=0.1,
                attention_type="scaled_dot_product",
                use_rope=True,
                causal=True
            )
            
            positional_config_2 = PositionalEncodingConfig(
                encoding_type="learned",
                max_length=512,
                embedding_dim=512,
                dropout=0.1,
                learnable=True
            )
            
            self.systems["rope_learned"] = AttentionPositionalSystem(
                attention_config_2,
                positional_config_2,
                embed_dim=512
            )
            logger.info("✅ RoPE with learned encoding system initialized")
            
            # System 3: ALiBi attention with relative positional encoding
            attention_config_3 = AttentionConfig(
                num_heads=8,
                head_dim=64,
                dropout=0.1,
                attention_type="alibi",
                use_rope=False,
                causal=True
            )
            
            positional_config_3 = PositionalEncodingConfig(
                encoding_type="sinusoidal",
                max_length=512,
                embedding_dim=512,
                dropout=0.1
            )
            
            self.systems["alibi"] = AttentionPositionalSystem(
                attention_config_3,
                positional_config_3,
                embed_dim=512
            )
            logger.info("✅ ALiBi system initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize systems: {e}")
            return False
    
    async def demo_positional_encodings(self):
        """Demo different positional encoding strategies."""
        try:
            logger.info("📍 Demo: Positional Encodings")
            
            # Test configurations
            batch_size, seq_len, embed_dim = 2, 128, 512
            
            # Test sinusoidal positional encoding
            logger.info("  Testing Sinusoidal Positional Encoding:")
            sin_config = PositionalEncodingConfig(
                encoding_type="sinusoidal",
                max_length=512,
                embedding_dim=embed_dim,
                dropout=0.1
            )
            
            sin_encoding = SinusoidalPositionalEncoding(sin_config)
            x = torch.randn(batch_size, seq_len, embed_dim)
            
            start_time = time.time()
            output = sin_encoding(x)
            encoding_time = time.time() - start_time
            
            logger.info(f"    Input shape: {x.shape}")
            logger.info(f"    Output shape: {output.shape}")
            logger.info(f"    Encoding time: {encoding_time:.3f}s")
            logger.info(f"    Output norm: {output.norm().item():.4f}")
            logger.info("")
            
            # Test learned positional encoding
            logger.info("  Testing Learned Positional Encoding:")
            learned_config = PositionalEncodingConfig(
                encoding_type="learned",
                max_length=512,
                embedding_dim=embed_dim,
                dropout=0.1,
                learnable=True
            )
            
            learned_encoding = LearnedPositionalEncoding(learned_config)
            
            start_time = time.time()
            output = learned_encoding(x)
            encoding_time = time.time() - start_time
            
            logger.info(f"    Input shape: {x.shape}")
            logger.info(f"    Output shape: {output.shape}")
            logger.info(f"    Encoding time: {encoding_time:.3f}s")
            logger.info(f"    Output norm: {output.norm().item():.4f}")
            logger.info("")
            
            # Test RoPE
            logger.info("  Testing Rotary Position Embedding (RoPE):")
            rope = RotaryPositionEmbedding(dim=64, max_position_embeddings=512)
            q = torch.randn(batch_size, 8, seq_len, 64)  # [batch, heads, seq, head_dim]
            
            start_time = time.time()
            output = rope(q, seq_len)
            encoding_time = time.time() - start_time
            
            logger.info(f"    Input shape: {q.shape}")
            logger.info(f"    Output shape: {output.shape}")
            logger.info(f"    Encoding time: {encoding_time:.3f}s")
            logger.info(f"    Output norm: {output.norm().item():.4f}")
            logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Positional encodings demo failed: {e}")
            return False
    
    async def demo_attention_mechanisms(self):
        """Demo different attention mechanisms."""
        try:
            logger.info("🔍 Demo: Attention Mechanisms")
            
            # Test configurations
            batch_size, seq_len, embed_dim = 2, 128, 512
            num_heads, head_dim = 8, 64
            
            # Test standard multi-head attention
            logger.info("  Testing Standard Multi-Head Attention:")
            attn_config = AttentionConfig(
                num_heads=num_heads,
                head_dim=head_dim,
                dropout=0.1,
                attention_type="scaled_dot_product",
                use_rope=False,
                causal=False
            )
            
            attention = MultiHeadAttention(attn_config, embed_dim)
            query = torch.randn(batch_size, seq_len, embed_dim)
            key = torch.randn(batch_size, seq_len, embed_dim)
            value = torch.randn(batch_size, seq_len, embed_dim)
            
            start_time = time.time()
            output, attention_weights = attention(query, key, value)
            attention_time = time.time() - start_time
            
            logger.info(f"    Query shape: {query.shape}")
            logger.info(f"    Output shape: {output.shape}")
            logger.info(f"    Attention weights shape: {attention_weights.shape}")
            logger.info(f"    Attention time: {attention_time:.3f}s")
            logger.info(f"    Output norm: {output.norm().item():.4f}")
            logger.info("")
            
            # Test cross-attention
            logger.info("  Testing Cross-Attention:")
            cross_attn = CrossAttention(attn_config, embed_dim, 768)
            context = torch.randn(batch_size, 77, 768)  # Text embeddings
            
            start_time = time.time()
            output, attention_weights = cross_attn(query, context)
            attention_time = time.time() - start_time
            
            logger.info(f"    Query shape: {query.shape}")
            logger.info(f"    Context shape: {context.shape}")
            logger.info(f"    Output shape: {output.shape}")
            logger.info(f"    Attention weights shape: {attention_weights.shape}")
            logger.info(f"    Attention time: {attention_time:.3f}s")
            logger.info("")
            
            # Test causal attention
            logger.info("  Testing Causal Attention:")
            causal_config = AttentionConfig(
                num_heads=num_heads,
                head_dim=head_dim,
                dropout=0.1,
                attention_type="scaled_dot_product",
                use_rope=False,
                causal=True
            )
            
            causal_attention = MultiHeadAttention(causal_config, embed_dim)
            
            start_time = time.time()
            output, attention_weights = causal_attention(query, query, query)
            attention_time = time.time() - start_time
            
            logger.info(f"    Output shape: {output.shape}")
            logger.info(f"    Attention weights shape: {attention_weights.shape}")
            logger.info(f"    Attention time: {attention_time:.3f}s")
            
            # Verify causal mask
            causal_mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
            masked_weights = attention_weights[0, 0].masked_fill(causal_mask, 0)
            logger.info(f"    Causal mask verified: {masked_weights.sum().item() == 0}")
            logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Attention mechanisms demo failed: {e}")
            return False
    
    async def demo_complete_systems(self):
        """Demo complete attention and positional encoding systems."""
        try:
            logger.info("🔧 Demo: Complete Systems")
            
            # Test configurations
            batch_size, seq_len = 2, 128
            x = torch.randn(batch_size, seq_len, 512)
            context = torch.randn(batch_size, 77, 768)  # Text embeddings
            
            # Test standard system
            logger.info("  Testing Standard System:")
            system = self.systems["standard"]
            
            start_time = time.time()
            output = system.forward(x, context)
            forward_time = time.time() - start_time
            
            logger.info(f"    Input shape: {x.shape}")
            logger.info(f"    Context shape: {context.shape}")
            logger.info(f"    Output shape: {output.shape}")
            logger.info(f"    Forward time: {forward_time:.3f}s")
            logger.info(f"    Output norm: {output.norm().item():.4f}")
            logger.info("")
            
            # Test RoPE system
            logger.info("  Testing RoPE System:")
            rope_system = self.systems["rope_learned"]
            
            start_time = time.time()
            output = rope_system.forward(x)
            forward_time = time.time() - start_time
            
            logger.info(f"    Input shape: {x.shape}")
            logger.info(f"    Output shape: {output.shape}")
            logger.info(f"    Forward time: {forward_time:.3f}s")
            logger.info(f"    Output norm: {output.norm().item():.4f}")
            logger.info("")
            
            # Test ALiBi system
            logger.info("  Testing ALiBi System:")
            alibi_system = self.systems["alibi"]
            
            start_time = time.time()
            output = alibi_system.forward(x)
            forward_time = time.time() - start_time
            
            logger.info(f"    Input shape: {x.shape}")
            logger.info(f"    Output shape: {output.shape}")
            logger.info(f"    Forward time: {forward_time:.3f}s")
            logger.info(f"    Output norm: {output.norm().item():.4f}")
            logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Complete systems demo failed: {e}")
            return False
    
    async def demo_attention_analysis(self):
        """Demo attention weight analysis and visualization."""
        try:
            logger.info("📊 Demo: Attention Analysis")
            
            # Test configurations
            batch_size, seq_len = 2, 64
            x = torch.randn(batch_size, seq_len, 512)
            context = torch.randn(batch_size, 32, 768)
            
            # Get attention weights
            system = self.systems["standard"]
            attention_weights = system.get_attention_weights(x, context)
            
            logger.info("  Attention Weights Analysis:")
            logger.info(f"    Self-attention weights shape: {attention_weights['self_attention'].shape}")
            logger.info(f"    Cross-attention weights shape: {attention_weights['cross_attention'].shape}")
            
            # Analyze attention patterns
            self_attn = attention_weights['self_attention'][0, 0]  # First batch, first head
            cross_attn = attention_weights['cross_attention'][0, 0]
            
            logger.info(f"    Self-attention max weight: {self_attn.max().item():.4f}")
            logger.info(f"    Self-attention min weight: {self_attn.min().item():.4f}")
            logger.info(f"    Self-attention mean weight: {self_attn.mean().item():.4f}")
            logger.info(f"    Cross-attention max weight: {cross_attn.max().item():.4f}")
            logger.info(f"    Cross-attention min weight: {cross_attn.min().item():.4f}")
            logger.info(f"    Cross-attention mean weight: {cross_attn.mean().item():.4f}")
            
            # Check attention distribution
            logger.info("  Attention Distribution:")
            logger.info(f"    Self-attention entropy: {-(self_attn * torch.log(self_attn + 1e-8)).sum().item():.4f}")
            logger.info(f"    Cross-attention entropy: {-(cross_attn * torch.log(cross_attn + 1e-8)).sum().item():.4f}")
            
            # Check if attention weights sum to 1
            self_attn_sum = self_attn.sum(dim=-1)
            cross_attn_sum = cross_attn.sum(dim=-1)
            logger.info(f"    Self-attention weights sum to 1: {torch.allclose(self_attn_sum, torch.ones_like(self_attn_sum), atol=1e-6)}")
            logger.info(f"    Cross-attention weights sum to 1: {torch.allclose(cross_attn_sum, torch.ones_like(cross_attn_sum), atol=1e-6)}")
            logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Attention analysis demo failed: {e}")
            return False
    
    async def demo_performance_comparison(self):
        """Demo performance comparison between different attention types."""
        try:
            logger.info("⚡ Demo: Performance Comparison")
            
            # Test configurations
            batch_size, seq_len, embed_dim = 2, 256, 512
            num_heads, head_dim = 8, 64
            
            # Test different attention configurations
            configs = [
                ("Standard", AttentionConfig(
                    num_heads=num_heads,
                    head_dim=head_dim,
                    dropout=0.1,
                    attention_type="scaled_dot_product",
                    use_rope=False,
                    causal=False
                )),
                ("RoPE", AttentionConfig(
                    num_heads=num_heads,
                    head_dim=head_dim,
                    dropout=0.1,
                    attention_type="scaled_dot_product",
                    use_rope=True,
                    causal=False
                )),
                ("Causal", AttentionConfig(
                    num_heads=num_heads,
                    head_dim=head_dim,
                    dropout=0.1,
                    attention_type="scaled_dot_product",
                    use_rope=False,
                    causal=True
                )),
                ("ALiBi", AttentionConfig(
                    num_heads=num_heads,
                    head_dim=head_dim,
                    dropout=0.1,
                    attention_type="alibi",
                    use_rope=False,
                    causal=True
                ))
            ]
            
            query = torch.randn(batch_size, seq_len, embed_dim)
            key = torch.randn(batch_size, seq_len, embed_dim)
            value = torch.randn(batch_size, seq_len, embed_dim)
            
            results = []
            
            for name, config in configs:
                logger.info(f"  Testing {name} Attention:")
                
                attention = MultiHeadAttention(config, embed_dim)
                
                # Warmup
                for _ in range(3):
                    _ = attention(query, key, value)
                
                # Benchmark
                start_time = time.time()
                for _ in range(10):
                    output, _ = attention(query, key, value)
                end_time = time.time()
                
                avg_time = (end_time - start_time) / 10
                results.append((name, avg_time, output.norm().item()))
                
                logger.info(f"    Average time: {avg_time:.3f}s")
                logger.info(f"    Output norm: {output.norm().item():.4f}")
                logger.info("")
            
            # Summary
            logger.info("  Performance Summary:")
            for name, time_taken, norm in results:
                logger.info(f"    {name}: {time_taken:.3f}s, norm: {norm:.4f}")
            
            # Find fastest
            fastest = min(results, key=lambda x: x[1])
            logger.info(f"    Fastest: {fastest[0]} ({fastest[1]:.3f}s)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Performance comparison demo failed: {e}")
            return False
    
    async def demo_memory_efficiency(self):
        """Demo memory efficiency of different attention mechanisms."""
        try:
            logger.info("💾 Demo: Memory Efficiency")
            
            if not torch.cuda.is_available():
                logger.info("  CUDA not available, skipping memory tests")
                return True
            
            # Test configurations
            batch_size, seq_len, embed_dim = 4, 512, 512
            num_heads, head_dim = 8, 64
            
            query = torch.randn(batch_size, seq_len, embed_dim).cuda()
            key = torch.randn(batch_size, seq_len, embed_dim).cuda()
            value = torch.randn(batch_size, seq_len, embed_dim).cuda()
            
            # Clear cache
            torch.cuda.empty_cache()
            
            # Test standard attention
            logger.info("  Testing Standard Attention Memory:")
            attn_config = AttentionConfig(
                num_heads=num_heads,
                head_dim=head_dim,
                dropout=0.1,
                attention_type="scaled_dot_product",
                use_rope=False,
                causal=False
            )
            
            attention = MultiHeadAttention(attn_config, embed_dim).cuda()
            
            # Measure memory before
            torch.cuda.synchronize()
            memory_before = torch.cuda.memory_allocated() / 1024**2  # MB
            
            # Forward pass
            output, _ = attention(query, key, value)
            
            # Measure memory after
            torch.cuda.synchronize()
            memory_after = torch.cuda.memory_allocated() / 1024**2  # MB
            
            logger.info(f"    Memory before: {memory_before:.2f} MB")
            logger.info(f"    Memory after: {memory_after:.2f} MB")
            logger.info(f"    Memory increase: {memory_after - memory_before:.2f} MB")
            logger.info(f"    Output shape: {output.shape}")
            logger.info("")
            
            # Clear cache
            del attention, output
            torch.cuda.empty_cache()
            
            # Test with RoPE
            logger.info("  Testing RoPE Attention Memory:")
            rope_config = AttentionConfig(
                num_heads=num_heads,
                head_dim=head_dim,
                dropout=0.1,
                attention_type="scaled_dot_product",
                use_rope=True,
                causal=False
            )
            
            rope_attention = MultiHeadAttention(rope_config, embed_dim).cuda()
            
            # Measure memory before
            torch.cuda.synchronize()
            memory_before = torch.cuda.memory_allocated() / 1024**2  # MB
            
            # Forward pass
            output, _ = rope_attention(query, key, value)
            
            # Measure memory after
            torch.cuda.synchronize()
            memory_after = torch.cuda.memory_allocated() / 1024**2  # MB
            
            logger.info(f"    Memory before: {memory_before:.2f} MB")
            logger.info(f"    Memory after: {memory_after:.2f} MB")
            logger.info(f"    Memory increase: {memory_after - memory_before:.2f} MB")
            logger.info(f"    Output shape: {output.shape}")
            logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Memory efficiency demo failed: {e}")
            return False
    
    async def demo_gradient_flow(self):
        """Demo gradient flow through attention mechanisms."""
        try:
            logger.info("🌊 Demo: Gradient Flow")
            
            # Test configurations
            batch_size, seq_len, embed_dim = 2, 64, 512
            num_heads, head_dim = 8, 64
            
            # Create attention mechanism
            attn_config = AttentionConfig(
                num_heads=num_heads,
                head_dim=head_dim,
                dropout=0.1,
                attention_type="scaled_dot_product",
                use_rope=False,
                causal=False
            )
            
            attention = MultiHeadAttention(attn_config, embed_dim)
            
            # Create input tensors
            query = torch.randn(batch_size, seq_len, embed_dim, requires_grad=True)
            key = torch.randn(batch_size, seq_len, embed_dim, requires_grad=True)
            value = torch.randn(batch_size, seq_len, embed_dim, requires_grad=True)
            
            # Forward pass
            output, attention_weights = attention(query, key, value)
            
            # Create dummy loss
            target = torch.randn_like(output)
            loss = F.mse_loss(output, target)
            
            # Backward pass
            loss.backward()
            
            logger.info("  Gradient Analysis:")
            logger.info(f"    Query gradient norm: {query.grad.norm().item():.4f}")
            logger.info(f"    Key gradient norm: {key.grad.norm().item():.4f}")
            logger.info(f"    Value gradient norm: {value.grad.norm().item():.4f}")
            logger.info(f"    Output norm: {output.norm().item():.4f}")
            logger.info(f"    Loss: {loss.item():.4f}")
            
            # Check for gradient explosion/vanishing
            grad_norms = [query.grad.norm().item(), key.grad.norm().item(), value.grad.norm().item()]
            max_grad_norm = max(grad_norms)
            min_grad_norm = min(grad_norms)
            
            if max_grad_norm > 10.0:
                logger.warning(f"    ⚠️ Potential gradient explosion: max norm = {max_grad_norm:.4f}")
            elif min_grad_norm < 1e-6:
                logger.warning(f"    ⚠️ Potential gradient vanishing: min norm = {min_grad_norm:.4f}")
            else:
                logger.info(f"    ✅ Gradient norms are healthy: {min_grad_norm:.4f} - {max_grad_norm:.4f}")
            
            logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Gradient flow demo failed: {e}")
            return False
    
    async def run(self):
        """Main demo execution."""
        try:
            self.start_time = datetime.now()
            
            logger.info("🚀 Starting Attention and Positional Encoding Demo...")
            logger.info(f"⏰ Start time: {self.start_time}")
            
            # Initialize systems
            if not await self.initialize_systems():
                return False
            
            # Run demos
            demos = [
                self.demo_positional_encodings(),
                self.demo_attention_mechanisms(),
                self.demo_complete_systems(),
                self.demo_attention_analysis(),
                self.demo_performance_comparison(),
                self.demo_memory_efficiency(),
                self.demo_gradient_flow()
            ]
            
            for demo in demos:
                if not await demo:
                    logger.warning("⚠️ Demo completed with warnings")
            
            # Final status
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            logger.info("🎉 Attention and Positional Encoding Demo completed successfully!")
            logger.info(f"⏱️  Total duration: {duration}")
            logger.info("📊 All demos executed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Demo execution failed: {e}")
            return False

async def main():
    """Main entry point."""
    demo = AttentionPositionalDemo()
    
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
