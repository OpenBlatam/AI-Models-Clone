#!/usr/bin/env python3
"""
🚀 Dependency Installation Script for Enhanced AI Model Demos System

This script helps install and verify all dependencies needed for the system.
Run this script to automatically install dependencies and verify your setup.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def print_header():
    """Print a formatted header."""
    print("=" * 80)
    print("🚀 Enhanced AI Model Demos System - Dependency Installer")
    print("=" * 80)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported.")
        print("   Please install Python 3.8 or higher.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible.")
    return True

def check_pip():
    """Check if pip is available."""
    print("📦 Checking pip availability...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip is available.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip is not available.")
        print("   Please install pip first.")
        return False

def upgrade_pip():
    """Upgrade pip to the latest version."""
    print("⬆️  Upgrading pip...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        print("✅ pip upgraded successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Failed to upgrade pip: {e}")
        print("   Continuing with current pip version...")
        return False

def install_requirements(requirements_file):
    """Install requirements from a specific file."""
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file {requirements_file} not found.")
        return False
    
    print(f"📥 Installing dependencies from {requirements_file}...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], 
                      check=True)
        print(f"✅ Dependencies from {requirements_file} installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies from {requirements_file}: {e}")
        return False

def verify_installation():
    """Verify that key packages are installed correctly."""
    print("🔍 Verifying installation...")
    
    key_packages = [
        "torch",
        "gradio", 
        "numpy",
        "plotly",
        "psutil"
    ]
    
    failed_packages = []
    
    for package in key_packages:
        try:
            __import__(package)
            print(f"✅ {package} imported successfully.")
        except ImportError:
            print(f"❌ {package} failed to import.")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️  Some packages failed to import: {', '.join(failed_packages)}")
        return False
    
    print("✅ All key packages imported successfully.")
    return True

def check_gpu_support():
    """Check if GPU support is available."""
    print("🖥️  Checking GPU support...")
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU support available: {gpu_count} GPU(s)")
            print(f"   Primary GPU: {gpu_name}")
            print(f"   CUDA version: {torch.version.cuda}")
        else:
            print("ℹ️  GPU support not available. PyTorch will use CPU.")
        return True
    except ImportError:
        print("❌ PyTorch not available for GPU check.")
        return False

def create_requirements_pinned():
    """Create a pinned requirements file with exact versions."""
    print("📌 Creating pinned requirements file...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"], 
                              capture_output=True, text=True, check=True)
        
        with open("requirements-pinned.txt", "w") as f:
            f.write("# Pinned requirements with exact versions\n")
            f.write("# Generated automatically by install_dependencies.py\n\n")
            f.write(result.stdout)
        
        print("✅ requirements-pinned.txt created successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create pinned requirements: {e}")
        return False

def main():
    """Main installation function."""
    print_header()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # Upgrade pip
    upgrade_pip()
    
    # Determine installation type
    print("\n🎯 Choose installation type:")
    print("1. Production (minimal dependencies)")
    print("2. Development (full system with tools)")
    print("3. Complete (everything)")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice in ["1", "2", "3"]:
            break
        print("Invalid choice. Please enter 1, 2, or 3.")
    
    # Install based on choice
    if choice == "1":
        print("\n🚀 Installing production dependencies...")
        if not install_requirements("requirements-production.txt"):
            print("❌ Production installation failed.")
            sys.exit(1)
    
    elif choice == "2":
        print("\n🚀 Installing development dependencies...")
        if not install_requirements("requirements-production.txt"):
            print("❌ Production dependencies installation failed.")
            sys.exit(1)
        
        if not install_requirements("requirements-development.txt"):
            print("❌ Development dependencies installation failed.")
            sys.exit(1)
    
    elif choice == "3":
        print("\n🚀 Installing complete system...")
        if not install_requirements("requirements-enhanced-system.txt"):
            print("❌ Complete system installation failed.")
            sys.exit(1)
    
    # Verify installation
    print("\n🔍 Verifying installation...")
    if not verify_installation():
        print("❌ Installation verification failed.")
        sys.exit(1)
    
    # Check GPU support
    check_gpu_support()
    
    # Create pinned requirements
    create_requirements_pinned()
    
    # Success message
    print("\n" + "=" * 80)
    print("🎉 Installation completed successfully!")
    print("=" * 80)
    print()
    print("📚 Next steps:")
    print("1. Activate your virtual environment (if using one)")
    print("2. Run the demo: python enhanced_ui_demos_with_validation.py")
    print("3. Check the documentation in DEPENDENCIES_GUIDE.md")
    print()
    print("🔧 If you encounter issues:")
    print("- Check DEPENDENCIES_GUIDE.md for troubleshooting")
    print("- Verify your Python and pip versions")
    print("- Ensure you have the required system dependencies")
    print()
    print("🚀 Happy coding!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Installation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
