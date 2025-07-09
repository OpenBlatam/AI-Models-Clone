#!/usr/bin/env python3
"""
Product Description Generator - Main Entry Point
===============================================

Run the product description generator in different modes:
- API service
- Gradio interface  
- CLI tool
- Demo mode
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from core.generator import ProductDescriptionGenerator
from core.config import ProductDescriptionConfig, ECOMMERCE_CONFIG, LUXURY_CONFIG, TECHNICAL_CONFIG
from api.service import ProductDescriptionService
from api.gradio_interface import create_gradio_app

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_demo():
    """Run demo generation examples."""
    print("🛍️ Product Description Generator - Demo Mode")
    print("=" * 50)
    
    # Initialize generator
    config = ProductDescriptionConfig()
    generator = ProductDescriptionGenerator(config)
    
    print("Initializing AI model... (this may take a moment)")
    await generator.initialize()
    print("✅ Model initialized!")
    
    # Demo products
    demo_products = [
        {
            "product_name": "Wireless Bluetooth Headphones",
            "features": ["Active noise cancellation", "30-hour battery", "Premium leather", "Quick charge"],
            "category": "electronics",
            "brand": "TechPro",
            "style": "professional",
            "tone": "friendly"
        },
        {
            "product_name": "Luxury Silk Scarf",
            "features": ["100% pure silk", "Hand-rolled edges", "Designer pattern", "Gift packaging"],
            "category": "clothing",
            "brand": "LuxeStyle",
            "style": "luxury",
            "tone": "sophisticated"
        },
        {
            "product_name": "Gaming Mechanical Keyboard",
            "features": ["Cherry MX switches", "RGB backlighting", "Programmable keys", "USB-C connectivity"],
            "category": "electronics",
            "brand": "GameForce",
            "style": "technical",
            "tone": "enthusiastic"
        }
    ]
    
    # Generate descriptions
    for i, product in enumerate(demo_products, 1):
        print(f"\n📝 Demo {i}: {product['product_name']}")
        print("-" * 40)
        
        results = generator.generate(**product)
        
        result = results[0]
        print(f"✨ Generated Description:")
        print(f"{result['description']}")
        print(f"\n📊 Metrics:")
        print(f"   Quality Score: {result['quality_score']:.2f}")
        print(f"   SEO Score: {result['seo_score']:.2f}")
        print(f"   Word Count: {result['metadata']['word_count']}")
        print(f"   Style: {result['metadata']['style']}")
        print(f"   Tone: {result['metadata']['tone']}")
    
    # Show statistics
    stats = generator.get_stats()
    print(f"\n📈 Generator Statistics:")
    print(f"   Total Generations: {stats['total_generations']}")
    print(f"   Average Time: {stats['avg_time_per_generation']:.2f}s")
    print(f"   Cache Hit Rate: {stats['cache_hit_rate']:.2%}")
    
    print("\n🎉 Demo completed!")


def run_cli():
    """Run CLI mode for single generation with guard clauses."""
    print("🛍️ Product Description Generator - CLI Mode")
    print("=" * 50)
    
    # Get user input
    product_name = input("Product Name: ")
    
    # Guard clause: Validate product name
    if not product_name or not product_name.strip():
        print("❌ Error: Product name cannot be empty")
        return
    
    features_input = input("Features (comma-separated): ")
    features = [f.strip() for f in features_input.split(',') if f.strip()]
    
    # Guard clause: Validate features
    if not features:
        print("❌ Error: At least one feature is required")
        return
    
    category = input("Category (default: general): ") or "general"
    brand = input("Brand (default: unknown): ") or "unknown"
    style = input("Style [professional/casual/luxury/technical/creative] (default: professional): ") or "professional"
    tone = input("Tone [friendly/formal/enthusiastic/informative/persuasive] (default: friendly): ") or "friendly"
    
    # Guard clause: Validate style
    valid_styles = ["professional", "casual", "luxury", "technical", "creative"]
    if style not in valid_styles:
        print(f"❌ Error: Invalid style. Must be one of: {', '.join(valid_styles)}")
        return
    
    # Guard clause: Validate tone
    valid_tones = ["friendly", "formal", "enthusiastic", "informative", "persuasive"]
    if tone not in valid_tones:
        print(f"❌ Error: Invalid tone. Must be one of: {', '.join(valid_tones)}")
        return
    
    async def generate():
        # Initialize generator
        config = ProductDescriptionConfig()
        generator = ProductDescriptionGenerator(config)
        
        print("\nInitializing AI model...")
        await generator.initialize()
        print("✅ Model ready!")
        
        # Generate
        print("🤖 Generating description...")
        results = generator.generate(
            product_name=product_name,
            features=features,
            category=category,
            brand=brand,
            style=style,
            tone=tone,
            num_variations=2
        )
        
        # Display results
        print("\n✨ Generated Descriptions:")
        print("=" * 50)
        
        for i, result in enumerate(results, 1):
            print(f"\n📝 Variation {i}:")
            print(f"{result['description']}")
            print(f"\n📊 Metrics:")
            print(f"   Quality: {result['quality_score']:.2f}/1.0")
            print(f"   SEO: {result['seo_score']:.2f}/1.0")
            print(f"   Words: {result['metadata']['word_count']}")
    
    asyncio.run(generate())


def run_api(host="0.0.0.0", port=8000):
    """Run API service with guard clauses."""
    # Guard clause: Validate host
    if not host or not host.strip():
        print("❌ Error: Host cannot be empty")
        return
    
    # Guard clause: Validate port range
    if port < 1 or port > 65535:
        print("❌ Error: Port must be between 1 and 65535")
        return
    
    print(f"🚀 Starting Product Description API on {host}:{port}")
    
    service = ProductDescriptionService()
    service.run(host=host, port=port)


def run_gradio(share=False, port=7860):
    """Run Gradio interface with guard clauses."""
    # Guard clause: Validate port range
    if port < 1 or port > 65535:
        print("❌ Error: Port must be between 1 and 65535")
        return
    
    print(f"🎮 Starting Gradio Interface on port {port}")
    
    app = create_gradio_app()
    app.launch(share=share, server_port=port)


def main():
    """Main entry point with guard clauses."""
    parser = argparse.ArgumentParser(
        description="Product Description Generator - AI-powered product descriptions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py demo                    # Run demo mode
  python main.py cli                     # Run CLI mode
  python main.py api                     # Start API service
  python main.py gradio                  # Start Gradio interface
  python main.py api --port 8080         # API on custom port
  python main.py gradio --share          # Gradio with public sharing
        """
    )
    
    parser.add_argument(
        "mode",
        choices=["demo", "cli", "api", "gradio"],
        help="Run mode"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for API service (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for API service (default: 8000) or Gradio (default: 7860)"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="Enable public sharing for Gradio interface"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Guard clause: Validate port range
    if args.port < 1 or args.port > 65535:
        print("❌ Error: Port must be between 1 and 65535")
        return
    
    # Guard clause: Validate host
    if not args.host or not args.host.strip():
        print("❌ Error: Host cannot be empty")
        return
    
    # Setup debug logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run selected mode
    try:
        if args.mode == "demo":
            asyncio.run(run_demo())
        elif args.mode == "cli":
            run_cli()
        elif args.mode == "api":
            run_api(host=args.host, port=args.port)
        elif args.mode == "gradio":
            gradio_port = args.port if args.port != 8000 else 7860
            run_gradio(share=args.share, port=gradio_port)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 