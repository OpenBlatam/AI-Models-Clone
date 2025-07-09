#!/usr/bin/env python3
"""
Transformers Demos Launcher

This script provides easy access to all Transformers-related demos
for the Email Sequence AI System.
"""

import os
import sys
import subprocess
from typing import List, Dict


def print_banner():
    """Print the demo launcher banner."""
    print("🚀 Transformers Demos for Email Sequence AI System")
    print("=" * 60)
    print()


def list_demos() -> List[Dict[str, str]]:
    """List available Transformers demos."""
    demos = [
        {
            "name": "Simple Transformers Demo",
            "file": "examples/simple_transformers_demo.py",
            "description": "Basic Transformers functionality with text generation, sentiment analysis, and summarization"
        },
        {
            "name": "Full Transformers Examples",
            "file": "examples/transformers_examples.py",
            "description": "Comprehensive examples with email sequence generation, categorization, and translation"
        },
        {
            "name": "Gradio Interface",
            "file": "examples/gradio_app.py",
            "description": "Interactive web interface for email sequence generation and analysis"
        },
        {
            "name": "Training Example",
            "file": "examples/training_example.py",
            "description": "Example of training and fine-tuning models for email sequences"
        }
    ]
    return demos


def run_demo(demo_file: str):
    """Run a specific demo."""
    if not os.path.exists(demo_file):
        print(f"❌ Demo file not found: {demo_file}")
        return False
    
    print(f"🎬 Running: {demo_file}")
    print("-" * 40)
    
    try:
        result = subprocess.run([sys.executable, demo_file], capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        return False


def check_transformers_installation():
    """Check if Transformers is properly installed."""
    print("🔍 Checking Transformers installation...")
    
    try:
        import transformers
        print(f"✅ Transformers version: {transformers.__version__}")
        
        # Check available pipelines
        from transformers import pipelines
        print(f"✅ Available pipeline tasks: {len(pipelines.SUPPORTED_TASKS)}")
        
        # Check PyTorch
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"✅ CUDA available: {torch.cuda.is_available()}")
        
        return True
    except ImportError as e:
        print(f"❌ Transformers not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking installation: {e}")
        return False


def main():
    """Main launcher function."""
    print_banner()
    
    # Check installation
    if not check_transformers_installation():
        print("\n❌ Transformers installation check failed.")
        print("Please install Transformers: pip install transformers")
        return
    
    print("\n📋 Available Demos:")
    print("-" * 40)
    
    demos = list_demos()
    for i, demo in enumerate(demos, 1):
        print(f"{i}. {demo['name']}")
        print(f"   {demo['description']}")
        print(f"   File: {demo['file']}")
        print()
    
    # Interactive menu
    while True:
        print("🎯 Select a demo to run:")
        print("1. Simple Transformers Demo")
        print("2. Full Transformers Examples")
        print("3. Gradio Interface")
        print("4. Training Example")
        print("5. Run all demos")
        print("0. Exit")
        
        try:
            choice = input("\nEnter your choice (0-5): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                run_demo("examples/simple_transformers_demo.py")
            elif choice == "2":
                run_demo("examples/transformers_examples.py")
            elif choice == "3":
                run_demo("examples/gradio_app.py")
            elif choice == "4":
                run_demo("examples/training_example.py")
            elif choice == "5":
                print("🚀 Running all demos...")
                for demo in demos:
                    print(f"\n{'='*60}")
                    run_demo(demo['file'])
                    input("\nPress Enter to continue to next demo...")
                print("🎉 All demos completed!")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 0-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main() 