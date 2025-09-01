#!/usr/bin/env python3
"""
HeyGen AI Demo Launcher

This script allows you to choose and run different HeyGen AI demonstrations:
- Quick Start Ultra Performance Demo
- Refactored Demo with Ultra Performance
- Comprehensive Demo Runner
- Ultra Performance Benchmark
- And more...
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def display_menu():
    """Display the demo selection menu."""
    print("\n" + "=" * 60)
    print("🚀 HeyGen AI Demo Launcher")
    print("=" * 60)
    print("Choose a demo to run:")
    print("1. 🚀 Quick Start Ultra Performance Demo")
    print("2. 🔧 Refactored Demo with Ultra Performance")
    print("3. 🎯 Comprehensive Demo Runner")
    print("4. ⚡ Ultra Performance Benchmark")
    print("5. 🔌 Plugin System Demo")
    print("6. 🧪 Run All Demos")
    print("7. 📋 Check System Requirements")
    print("8. 🔧 Install Dependencies")
    print("9. ❌ Exit")
    print("=" * 60)


def check_system_requirements():
    """Check if the system meets the requirements."""
    print("\n🔍 Checking System Requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check PyTorch
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        print(f"   CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   CUDA Version: {torch.version.cuda}")
            print(f"   GPU Device: {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("❌ PyTorch not installed")
        return False
    
    # Check other key dependencies
    dependencies = [
        ("transformers", "Transformers"),
        ("diffusers", "Diffusers"),
        ("accelerate", "Accelerate"),
        ("gradio", "Gradio")
    ]
    
    for package, name in dependencies:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {name} {version}")
        except ImportError:
            print(f"❌ {name} not installed")
    
    # Check available memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        print(f"✅ System Memory: {memory_gb:.1f} GB")
        
        if memory_gb < 8:
            print("⚠️  Warning: Less than 8GB RAM may cause performance issues")
    except ImportError:
        print("ℹ️  psutil not available - cannot check memory")
    
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n🔧 Installing Dependencies...")
    
    try:
        import subprocess
        
        # Check if pip is available
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("❌ pip not available")
            return False
        
        # Install dependencies from requirements.txt
        requirements_file = Path(__file__).parent / "requirements.txt"
        if requirements_file.exists():
            print("📦 Installing dependencies from requirements.txt...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            print("✅ Dependencies installed successfully")
        else:
            print("❌ requirements.txt not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


async def run_demo(demo_name, script_path):
    """Run a specific demo script."""
    print(f"\n🚀 Running {demo_name}...")
    print(f"📁 Script: {script_path}")
    
    try:
        # Check if script exists
        if not Path(script_path).exists():
            print(f"❌ Script not found: {script_path}")
            return False
        
        # Import and run the demo
        script_dir = Path(script_path).parent
        script_name = Path(script_path).stem
        
        # Add script directory to path
        sys.path.insert(0, str(script_dir))
        
        # Import the demo module
        try:
            if script_name == "quick_start_ultra_performance":
                from quick_start_ultra_performance import main
            elif script_name == "run_refactored_demo":
                from run_refactored_demo import main
            elif script_name == "comprehensive_demo_runner":
                from comprehensive_demo_runner import main
            elif script_name == "ultra_performance_benchmark":
                from ultra_performance_benchmark import main
            else:
                print(f"❌ Unknown demo script: {script_name}")
                return False
            
            # Run the demo
            await main()
            print(f"✅ {demo_name} completed successfully")
            return True
            
        except ImportError as e:
            print(f"❌ Failed to import demo: {e}")
            return False
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to run demo: {e}")
        return False


async def run_all_demos():
    """Run all available demos."""
    print("\n🎯 Running All Demos...")
    
    demos = [
        ("Quick Start Ultra Performance", "quick_start_ultra_performance.py"),
        ("Refactored Demo", "run_refactored_demo.py"),
        ("Comprehensive Demo", "comprehensive_demo_runner.py"),
        ("Ultra Performance Benchmark", "ultra_performance_benchmark.py"),
        ("Plugin System Demo", "plugin_demo.py")
    ]
    
    results = {}
    
    for demo_name, script_name in demos:
        script_path = Path(__file__).parent / script_name
        if script_path.exists():
            print(f"\n{'='*40}")
            print(f"🚀 Running: {demo_name}")
            print(f"{'='*40}")
            
            success = await run_demo(demo_name, script_path)
            results[demo_name] = "✅ Success" if success else "❌ Failed"
        else:
            print(f"⚠️  Script not found: {script_name}")
            results[demo_name] = "⚠️  Not Found"
    
    # Display results summary
    print("\n" + "="*60)
    print("📊 ALL DEMOS RESULTS SUMMARY")
    print("="*60)
    
    for demo_name, result in results.items():
        print(f"{result} {demo_name}")
    
    print("="*60)


async def main():
    """Main launcher function."""
    print("🚀 Welcome to HeyGen AI Demo Launcher!")
    
    while True:
        try:
            display_menu()
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                # Quick Start Ultra Performance Demo
                script_path = Path(__file__).parent / "quick_start_ultra_performance.py"
                await run_demo("Quick Start Ultra Performance Demo", script_path)
                
            elif choice == "2":
                # Refactored Demo
                script_path = Path(__file__).parent / "run_refactored_demo.py"
                await run_demo("Refactored Demo with Ultra Performance", script_path)
                
            elif choice == "3":
                # Comprehensive Demo Runner
                script_path = Path(__file__).parent / "comprehensive_demo_runner.py"
                await run_demo("Comprehensive Demo Runner", script_path)
                
            elif choice == "4":
                # Ultra Performance Benchmark
                script_path = Path(__file__).parent / "ultra_performance_benchmark.py"
                await run_demo("Ultra Performance Benchmark", script_path)
                
            elif choice == "5":
                # Plugin System Demo
                script_path = Path(__file__).parent / "plugin_demo.py"
                await run_demo("Plugin System Demo", script_path)
                
            elif choice == "6":
                # Run All Demos
                await run_all_demos()
                
            elif choice == "7":
                # Check System Requirements
                check_system_requirements()
                
            elif choice == "8":
                # Install Dependencies
                install_dependencies()
                
            elif choice == "9":
                # Exit
                print("\n👋 Goodbye! Thanks for using HeyGen AI Demo Launcher!")
                break
                
            else:
                print("❌ Invalid choice. Please enter a number between 1-9.")
            
            # Ask if user wants to continue
            if choice in ["1", "2", "3", "4", "5", "6"]:
                continue_choice = input("\n🔄 Run another demo? (y/n): ").lower().strip()
                if continue_choice != 'y':
                    print("\n👋 Goodbye! Thanks for using HeyGen AI Demo Launcher!")
                    break
            
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            logger.error(f"Launcher error: {e}")
            
            # Ask if user wants to continue
            continue_choice = input("\n🔄 Continue with launcher? (y/n): ").lower().strip()
            if continue_choice != 'y':
                print("\n👋 Goodbye! Thanks for using HeyGen AI Demo Launcher!")
                break


if __name__ == "__main__":
    try:
        # Run the launcher
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo launcher interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Launcher failed: {e}")
        logger.error(f"Launcher failed: {e}")
        sys.exit(1)
