#!/usr/bin/env python3
"""
🧠 ENHANCED NLP SYSTEM DEMO v4.0.0
====================================

Comprehensive demonstration of the enhanced NLP system with:
- Latest models (Gemini, Claude 3.5, Mistral, Llama 3)
- Advanced reasoning (Chain-of-Thought, Tree-of-Thoughts, ReAct)
- Domain-specific processing (Legal, Medical, Financial, Scientific)
- Multimodal capabilities (Text, Image, Audio)
- Real-time processing
- Interactive features
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import our enhanced NLP system
from enhanced_nlp_system import (
    EnhancedNLPEngine,
    EnhancedNLPConfig,
    EnhancedModelType,
    ReasoningType,
    DomainType,
    create_enhanced_nlp_engine,
    get_enhanced_nlp_capabilities
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# 🎯 DEMO CONFIGURATION
# =============================================================================

def create_demo_config() -> EnhancedNLPConfig:
    """Create configuration for demo."""
    return EnhancedNLPConfig(
        # Model Configuration
        primary_model=EnhancedModelType.GEMINI_PRO,
        fallback_model=EnhancedModelType.GPT_3_5_TURBO,
        reasoning_type=ReasoningType.CHAIN_OF_THOUGHT,
        domain_type=DomainType.GENERAL,
        
        # API Keys (set your keys here)
        gemini_api_key=None,  # Set your Gemini API key
        anthropic_api_key=None,  # Set your Anthropic API key
        openai_api_key=None,  # Set your OpenAI API key
        cohere_api_key=None,  # Set your Cohere API key
        
        # Performance
        max_concurrent_requests=10,
        enable_caching=True,
        enable_batching=True,
        batch_size=32,
        enable_quantization=True,
        enable_distributed=False,
        
        # Features
        enable_multimodal=True,
        enable_real_time=True,
        enable_interactive=True,
        enable_domain_specific=True,
        enable_advanced_reasoning=True,
        
        # Languages
        supported_languages=["en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko"],
        enable_multilingual=True,
        auto_detect_language=True
    )

# =============================================================================
# 🚀 DEMO FUNCTIONS
# =============================================================================

async def demo_basic_generation(nlp_engine: EnhancedNLPEngine):
    """Demo basic text generation."""
    print("\n" + "="*60)
    print("🚀 BASIC TEXT GENERATION DEMO")
    print("="*60)
    
    prompt = "Explain quantum computing in simple terms"
    
    print(f"📝 Prompt: {prompt}")
    print("🔄 Generating response...")
    
    start_time = time.time()
    result = await nlp_engine.enhanced_generate(prompt)
    generation_time = time.time() - start_time
    
    print(f"✅ Generated in {generation_time:.2f}s")
    print(f"🤖 Model: {result['model']}")
    print(f"🧠 Reasoning: {result['reasoning_type']}")
    print(f"🎯 Domain: {result['domain']}")
    print(f"⏱️ Response time: {result['response_time_ms']:.0f}ms")
    print(f"📄 Content: {result['content'][:200]}...")
    
    return result

async def demo_advanced_reasoning(nlp_engine: EnhancedNLPEngine):
    """Demo advanced reasoning techniques."""
    print("\n" + "="*60)
    print("🧠 ADVANCED REASONING DEMO")
    print("="*60)
    
    prompt = "Solve this math problem: If a train travels 120 km in 2 hours, what is its average speed?"
    
    reasoning_types = [
        ReasoningType.CHAIN_OF_THOUGHT,
        ReasoningType.TREE_OF_THOUGHTS,
        ReasoningType.REACT,
        ReasoningType.SELF_CONSISTENCY
    ]
    
    for reasoning_type in reasoning_types:
        print(f"\n🔍 Testing {reasoning_type.value.upper()}:")
        print(f"📝 Prompt: {prompt}")
        
        start_time = time.time()
        result = await nlp_engine.enhanced_generate(
            prompt,
            reasoning_type=reasoning_type,
            model=EnhancedModelType.GEMINI_PRO
        )
        generation_time = time.time() - start_time
        
        print(f"✅ Generated in {generation_time:.2f}s")
        print(f"🧠 Reasoning: {result['reasoning_type']}")
        print(f"📄 Content: {result['content'][:300]}...")

async def demo_domain_specific(nlp_engine: EnhancedNLPEngine):
    """Demo domain-specific processing."""
    print("\n" + "="*60)
    print("🎯 DOMAIN-SPECIFIC PROCESSING DEMO")
    print("="*60)
    
    domains = [
        (DomainType.LEGAL, "Analyze this contract clause: 'The party shall not disclose confidential information.'"),
        (DomainType.MEDICAL, "Explain the symptoms of diabetes in simple terms."),
        (DomainType.FINANCIAL, "What are the key factors to consider when investing in stocks?"),
        (DomainType.SCIENTIFIC, "Explain the process of photosynthesis."),
        (DomainType.CODE, "Review this Python code: def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"),
        (DomainType.SOCIAL_MEDIA, "Analyze this tweet: 'Just launched our new AI product! #AI #Innovation'")
    ]
    
    for domain, prompt in domains:
        print(f"\n🎯 {domain.value.upper()} DOMAIN:")
        print(f"📝 Prompt: {prompt}")
        
        start_time = time.time()
        result = await nlp_engine.enhanced_generate(
            prompt,
            domain=domain,
            model=EnhancedModelType.GEMINI_PRO
        )
        generation_time = time.time() - start_time
        
        print(f"✅ Generated in {generation_time:.2f}s")
        print(f"🎯 Domain: {result['domain']}")
        print(f"📄 Content: {result['content'][:200]}...")

async def demo_multimodal_processing(nlp_engine: EnhancedNLPEngine):
    """Demo multimodal processing."""
    print("\n" + "="*60)
    print("🌐 MULTIMODAL PROCESSING DEMO")
    print("="*60)
    
    # Text-only processing
    text = "This is a sample text for multimodal analysis."
    images = ["sample_image.jpg"]  # Placeholder
    audio = "sample_audio.wav"  # Placeholder
    
    print("📝 Processing text-only content...")
    result = await nlp_engine.process_multimodal(text)
    print(f"✅ Text analysis: {result['text_analysis']}")
    
    print("\n🖼️ Processing text + images...")
    result = await nlp_engine.process_multimodal(text, images=images)
    print(f"✅ Image analysis: {result['image_analysis']}")
    
    print("\n🎵 Processing text + audio...")
    result = await nlp_engine.process_multimodal(text, audio=audio)
    print(f"✅ Audio analysis: {result['audio_analysis']}")

async def demo_real_time_processing(nlp_engine: EnhancedNLPEngine):
    """Demo real-time processing."""
    print("\n" + "="*60)
    print("⚡ REAL-TIME PROCESSING DEMO")
    print("="*60)
    
    text_streams = [
        "I love this product! It's amazing!",
        "This service is terrible, I'm very disappointed.",
        "The new AI features are quite impressive and useful."
    ]
    
    processing_types = ["sentiment", "entities", "keywords"]
    
    for text in text_streams:
        print(f"\n📝 Processing: {text}")
        
        for processing_type in processing_types:
            start_time = time.time()
            result = await nlp_engine.process_real_time(text, processing_type)
            processing_time = time.time() - start_time
            
            print(f"⚡ {processing_type.upper()}: {result.get(processing_type, 'N/A')} ({processing_time:.3f}s)")

async def demo_model_comparison(nlp_engine: EnhancedNLPEngine):
    """Demo different model capabilities."""
    print("\n" + "="*60)
    print("🤖 MODEL COMPARISON DEMO")
    print("="*60)
    
    prompt = "Write a short poem about artificial intelligence"
    
    models = [
        EnhancedModelType.GEMINI_PRO,
        EnhancedModelType.GPT_3_5_TURBO,
        EnhancedModelType.CLAUDE_3_5_SONNET
    ]
    
    for model in models:
        print(f"\n🤖 Testing {model.value}:")
        print(f"📝 Prompt: {prompt}")
        
        try:
            start_time = time.time()
            result = await nlp_engine.enhanced_generate(
                prompt,
                model=model,
                reasoning_type=ReasoningType.ZERO_SHOT
            )
            generation_time = time.time() - start_time
            
            print(f"✅ Generated in {generation_time:.2f}s")
            print(f"⏱️ Response time: {result['response_time_ms']:.0f}ms")
            print(f"📄 Content: {result['content'][:150]}...")
            
        except Exception as e:
            print(f"❌ Error with {model.value}: {e}")

async def demo_performance_metrics(nlp_engine: EnhancedNLPEngine):
    """Demo performance metrics and statistics."""
    print("\n" + "="*60)
    print("📊 PERFORMANCE METRICS DEMO")
    print("="*60)
    
    # Get comprehensive statistics
    stats = nlp_engine.get_enhanced_stats()
    
    print("📈 SYSTEM STATISTICS:")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   LLM calls: {stats['llm_calls']}")
    print(f"   Embedding calls: {stats['embedding_calls']}")
    print(f"   Cache hits: {stats['cache_hits']}")
    print(f"   Average response time: {stats['avg_response_time']:.0f}ms")
    
    print("\n🤖 MODELS USED:")
    for model in stats['models_used']:
        print(f"   - {model}")
    
    print("\n🧠 REASONING TECHNIQUES:")
    for reasoning in stats['reasoning_used']:
        print(f"   - {reasoning}")
    
    print("\n🎯 DOMAINS PROCESSED:")
    for domain in stats['domains_processed']:
        print(f"   - {domain}")
    
    print("\n🔧 CAPABILITIES:")
    for capability, available in stats['capabilities'].items():
        status = "✅" if available else "❌"
        print(f"   {status} {capability}")
    
    print("\n📊 CACHE STATISTICS:")
    cache_stats = stats['cache_stats']
    print(f"   General cache size: {cache_stats['general_cache_size']}")
    print(f"   Embedding cache size: {cache_stats['embedding_cache_size']}")
    print(f"   Cache hit rate: {cache_stats['cache_hit_rate']:.1f}%")

async def demo_interactive_conversation(nlp_engine: EnhancedNLPEngine):
    """Demo interactive conversation capabilities."""
    print("\n" + "="*60)
    print("💬 INTERACTIVE CONVERSATION DEMO")
    print("="*60)
    
    conversation_history = []
    
    # Simulate a conversation
    messages = [
        "Hello! I'm interested in learning about machine learning.",
        "What are the main types of machine learning?",
        "Can you explain deep learning in simple terms?",
        "What are some practical applications of AI?"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n👤 User {i}: {message}")
        
        # Add context from conversation history
        context = "\n".join(conversation_history[-3:])  # Last 3 messages
        full_prompt = f"{context}\n\nUser: {message}\nAssistant:"
        
        start_time = time.time()
        result = await nlp_engine.enhanced_generate(
            full_prompt,
            reasoning_type=ReasoningType.CHAIN_OF_THOUGHT,
            model=EnhancedModelType.GEMINI_PRO
        )
        generation_time = time.time() - start_time
        
        response = result['content']
        print(f"🤖 Assistant: {response}")
        print(f"⏱️ Response time: {result['response_time_ms']:.0f}ms")
        
        # Update conversation history
        conversation_history.append(f"User: {message}")
        conversation_history.append(f"Assistant: {response}")

async def demo_error_handling(nlp_engine: EnhancedNLPEngine):
    """Demo error handling and fallback mechanisms."""
    print("\n" + "="*60)
    print("🛡️ ERROR HANDLING DEMO")
    print("="*60)
    
    # Test with invalid model
    print("🧪 Testing fallback mechanism...")
    
    try:
        result = await nlp_engine.enhanced_generate(
            "This is a test prompt",
            model=EnhancedModelType.GPT_4_TURBO,  # This might not be available
            reasoning_type=ReasoningType.ZERO_SHOT
        )
        print(f"✅ Success: {result['model']}")
        
    except Exception as e:
        print(f"❌ Error caught: {e}")
        print("🔄 Attempting fallback...")
        
        try:
            result = await nlp_engine.enhanced_generate(
                "This is a test prompt",
                model=EnhancedModelType.GPT_3_5_TURBO,  # Fallback model
                reasoning_type=ReasoningType.ZERO_SHOT
            )
            print(f"✅ Fallback successful: {result['model']}")
            
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")

# =============================================================================
# 🚀 MAIN DEMO FUNCTION
# =============================================================================

async def run_comprehensive_demo():
    """Run comprehensive NLP system demo."""
    print("🧠 ENHANCED NLP SYSTEM DEMO v4.0.0")
    print("="*60)
    
    # Check capabilities
    print("🔍 Checking system capabilities...")
    capabilities = get_enhanced_nlp_capabilities()
    available_capabilities = [cap for cap, available in capabilities.items() if available]
    print(f"✅ Available capabilities: {len(available_capabilities)}")
    for cap in available_capabilities:
        print(f"   - {cap}")
    
    # Create configuration
    config = create_demo_config()
    
    # Initialize NLP engine
    print("\n🚀 Initializing Enhanced NLP Engine...")
    try:
        nlp_engine = await create_enhanced_nlp_engine(config)
        print("✅ Enhanced NLP Engine initialized successfully!")
        
    except Exception as e:
        print(f"❌ Failed to initialize NLP engine: {e}")
        print("💡 Make sure to set your API keys in the configuration")
        return
    
    # Run demos
    try:
        # Basic generation demo
        await demo_basic_generation(nlp_engine)
        
        # Advanced reasoning demo
        await demo_advanced_reasoning(nlp_engine)
        
        # Domain-specific demo
        await demo_domain_specific(nlp_engine)
        
        # Multimodal processing demo
        await demo_multimodal_processing(nlp_engine)
        
        # Real-time processing demo
        await demo_real_time_processing(nlp_engine)
        
        # Model comparison demo
        await demo_model_comparison(nlp_engine)
        
        # Interactive conversation demo
        await demo_interactive_conversation(nlp_engine)
        
        # Error handling demo
        await demo_error_handling(nlp_engine)
        
        # Performance metrics demo
        await demo_performance_metrics(nlp_engine)
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
    
    finally:
        print("\n🎉 Demo completed!")
        print("📊 Final statistics:")
        stats = nlp_engine.get_enhanced_stats()
        print(f"   Total requests: {stats['total_requests']}")
        print(f"   Average response time: {stats['avg_response_time']:.0f}ms")
        print(f"   Cache hit rate: {stats['cache_stats']['cache_hit_rate']:.1f}%")

# =============================================================================
# 🎯 USAGE EXAMPLES
# =============================================================================

async def example_legal_analysis():
    """Example: Legal document analysis."""
    print("\n📋 LEGAL ANALYSIS EXAMPLE")
    print("="*40)
    
    config = EnhancedNLPConfig(
        primary_model=EnhancedModelType.GEMINI_PRO,
        domain_type=DomainType.LEGAL,
        reasoning_type=ReasoningType.CHAIN_OF_THOUGHT
    )
    
    nlp_engine = await create_enhanced_nlp_engine(config)
    
    contract_text = """
    This Agreement is entered into between Company A and Company B.
    The term of this agreement shall be 12 months from the effective date.
    Either party may terminate this agreement with 30 days written notice.
    """
    
    result = await nlp_engine.enhanced_generate(
        f"Analyze this contract and identify key terms, obligations, and potential risks:\n\n{contract_text}",
        domain=DomainType.LEGAL
    )
    
    print(f"📄 Analysis: {result['content'][:300]}...")

async def example_medical_diagnosis():
    """Example: Medical text analysis."""
    print("\n🏥 MEDICAL ANALYSIS EXAMPLE")
    print("="*40)
    
    config = EnhancedNLPConfig(
        primary_model=EnhancedModelType.CLAUDE_3_5_SONNET,
        domain_type=DomainType.MEDICAL,
        reasoning_type=ReasoningType.CHAIN_OF_THOUGHT
    )
    
    nlp_engine = await create_enhanced_nlp_engine(config)
    
    symptoms = "Patient reports fatigue, increased thirst, frequent urination, and blurred vision."
    
    result = await nlp_engine.enhanced_generate(
        f"Based on these symptoms, what could be the possible diagnosis and what tests should be recommended?\n\nSymptoms: {symptoms}",
        domain=DomainType.MEDICAL
    )
    
    print(f"🏥 Analysis: {result['content'][:300]}...")

async def example_financial_analysis():
    """Example: Financial market analysis."""
    print("\n💰 FINANCIAL ANALYSIS EXAMPLE")
    print("="*40)
    
    config = EnhancedNLPConfig(
        primary_model=EnhancedModelType.GPT_4_TURBO,
        domain_type=DomainType.FINANCIAL,
        reasoning_type=ReasoningType.TREE_OF_THOUGHTS
    )
    
    nlp_engine = await create_enhanced_nlp_engine(config)
    
    market_data = "Tech stocks are showing volatility due to interest rate concerns. AI companies are performing well."
    
    result = await nlp_engine.enhanced_generate(
        f"Analyze this market information and provide investment insights:\n\n{market_data}",
        domain=DomainType.FINANCIAL
    )
    
    print(f"💰 Analysis: {result['content'][:300]}...")

async def example_scientific_research():
    """Example: Scientific paper analysis."""
    print("\n🔬 SCIENTIFIC RESEARCH EXAMPLE")
    print("="*40)
    
    config = EnhancedNLPConfig(
        primary_model=EnhancedModelType.GEMINI_PRO,
        domain_type=DomainType.SCIENTIFIC,
        reasoning_type=ReasoningType.CHAIN_OF_THOUGHT
    )
    
    nlp_engine = await create_enhanced_nlp_engine(config)
    
    research_abstract = """
    This study investigates the application of transformer models in natural language processing.
    We propose a novel architecture that improves performance by 15% on benchmark datasets.
    Our approach combines attention mechanisms with hierarchical structures.
    """
    
    result = await nlp_engine.enhanced_generate(
        f"Analyze this research abstract and identify key contributions, methodology, and potential impact:\n\n{research_abstract}",
        domain=DomainType.SCIENTIFIC
    )
    
    print(f"🔬 Analysis: {result['content'][:300]}...")

# =============================================================================
# 🚀 MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("🧠 Enhanced NLP System Demo")
    print("="*60)
    
    # Run comprehensive demo
    asyncio.run(run_comprehensive_demo())
    
    # Run specific examples
    print("\n" + "="*60)
    print("📚 SPECIFIC EXAMPLES")
    print("="*60)
    
    asyncio.run(example_legal_analysis())
    asyncio.run(example_medical_diagnosis())
    asyncio.run(example_financial_analysis())
    asyncio.run(example_scientific_research())
    
    print("\n🎉 All demos and examples completed!")
    print("💡 To use this system in production:")
    print("   1. Set your API keys in the configuration")
    print("   2. Choose appropriate models for your use case")
    print("   3. Configure domain-specific processing")
    print("   4. Enable advanced reasoning techniques")
    print("   5. Monitor performance metrics") 