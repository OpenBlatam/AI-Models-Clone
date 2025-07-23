#!/usr/bin/env python3
"""
Advanced AI System Runner

Simple script to run the advanced AI system with deep learning, transformers, 
diffusion models, and LLMs.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Run the Advanced AI System."""
    try:
        from advanced_ai_system import AdvancedAISystem, AdvancedAIConfig
        
        print("🚀 Starting Advanced AI System...")
        print("Deep Learning, Transformers, Diffusion Models, and LLMs")
        
        # Create configuration
        config = AdvancedAIConfig()
        
        # Create and initialize system
        ai_system = AdvancedAISystem(config)
        
        if ai_system.initialize():
            print("✅ Advanced AI System initialized successfully")
            
            # Show system status
            status = ai_system.get_system_status()
            print("\n📊 System Status:")
            print(f"  LLM Models Loaded: {status['llm_models_loaded']}")
            print(f"  Diffusion Pipelines: {status['diffusion_pipelines_loaded']}")
            print(f"  CUDA Available: {status['cuda_available']}")
            print(f"  CUDA Devices: {status['cuda_device_count']}")
            
            # Launch Gradio interface
            print("\n🌐 Launching Gradio interface on http://localhost:7860")
            print("Press Ctrl+C to stop the server")
            
            ai_system.launch_interface(
                share=False,
                server_name="0.0.0.0",
                server_port=7860,
                show_error=True
            )
            
        else:
            print("❌ Failed to initialize Advanced AI System")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Advanced AI System...")
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Please install required dependencies:")
        print("pip install -r advanced_ai_requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 