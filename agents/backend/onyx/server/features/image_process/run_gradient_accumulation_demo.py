#!/usr/bin/env python3
"""
Gradient Accumulation Demo Launcher

This script launches the gradient accumulation demo for large batch sizes.
"""

import sys
import logging
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("🚀 Launching Gradient Accumulation Demo...")
    
    try:
        from gradient_accumulation_demo import main as run_demo
        
        print("✅ Demo module imported successfully")
        print("🎯 Starting gradient accumulation demonstration...")
        
        # Run the demo
        run_demo()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required modules are available:")
        print("- advanced_diffusion_system.py")
        print("- gradient_accumulation_demo.py")
        print("- Required dependencies: torch, gradio, matplotlib, numpy")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
