#!/usr/bin/env python3
"""
Launch Script for Interactive Diffusion Models Gradio Demos
==========================================================

This script launches the interactive Gradio demos for the diffusion models system.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

def main():
    """Main function to launch interactive demos."""
    parser = argparse.ArgumentParser(description="Launch Interactive Diffusion Models Gradio Demos")
    parser.add_argument(
        "--port", 
        type=int, 
        default=7860,
        help="Port to run the demos on"
    )
    parser.add_argument(
        "--share", 
        action="store_true",
        help="Create a public link for the demos"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--demo-type",
        choices=["interactive", "basic", "advanced"],
        default="interactive",
        help="Type of demo to launch"
    )
    
    args = parser.parse_args()
    
    print("🎨 Launching Interactive Diffusion Models Gradio Demos...")
    print(f"Demo Type: {args.demo_type}")
    print(f"Port: {args.port}")
    print(f"Share: {args.share}")
    print(f"Debug: {args.debug}")
    
    try:
        if args.demo_type == "interactive":
            from core.gradio_interactive_demos import create_interactive_demo_interface
            demo = create_interactive_demo_interface()
            print("🚀 Launching Interactive Demo Interface...")
            
        elif args.demo_type == "basic":
            from core.gradio_interface import create_gradio_interface
            demo = create_gradio_interface()
            print("🚀 Launching Basic Gradio Interface...")
            
        elif args.demo_type == "advanced":
            from core.gradio_advanced_components import create_advanced_interface
            demo = create_advanced_interface()
            print("🚀 Launching Advanced Gradio Interface...")
        
        # Launch the demo
        demo.launch(
            server_name="0.0.0.0",
            server_port=args.port,
            share=args.share,
            show_error=args.debug
        )
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required dependencies are installed:")
        print("pip install gradio torch diffusers transformers matplotlib seaborn")
        return 1
        
    except Exception as e:
        print(f"❌ Error launching demos: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
