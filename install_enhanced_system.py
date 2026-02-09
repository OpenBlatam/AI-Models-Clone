#!/usr/bin/env python3
"""
Enhanced SEO System - Automated Installation Script
Sets up the complete system with dependency management and verification
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_banner():
    """Print installation banner."""
    print("=" * 80)
    print("🚀 Enhanced SEO System - Automated Installation")
    print("=" * 80)
    print("Setting up production-ready SEO optimization system")
    print("=" * 80)
    print()

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ required.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def check_system_info():
    """Display system information."""
    print("\n💻 System Information:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    print(f"   Python: {sys.executable}")
    print(f"   Working Directory: {os.getcwd()}")

def check_pip():
    """Check if pip is available."""
    print("\n📦 Checking pip availability...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ pip available: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip not available")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("\n📥 Installing dependencies...")
    
    # Check if requirements file exists
    requirements_file = "requirements_enhanced.txt"
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file {requirements_file} not found")
        return False
    
    try:
        # Install dependencies
        print("   Installing from requirements_enhanced.txt...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ], check=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def install_optional_dependencies():
    """Install optional development dependencies."""
    print("\n🔧 Installing optional development dependencies...")
    
    optional_packages = [
        "pytest", "pytest-cov", "black", "isort", "flake8", "mypy"
    ]
    
    for package in optional_packages:
        try:
            print(f"   Installing {package}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=True, capture_output=True)
            print(f"   ✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"   ⚠️  {package} installation failed (optional)")

def verify_installation():
    """Verify that all components are properly installed."""
    print("\n🔍 Verifying installation...")
    
    # Check core packages
    core_packages = [
        "torch", "transformers", "gradio", "numpy", "pandas", "psutil"
    ]
    
    missing_packages = []
    for package in core_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        return False
    
    return True

def run_basic_tests():
    """Run basic functionality tests."""
    print("\n🧪 Running basic tests...")
    
    try:
        # Run the simple test script
        result = subprocess.run([
            sys.executable, "test_simple.py"
        ], capture_output=True, text=True, check=True)
        
        print("✅ Basic tests passed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Basic tests failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Errors: {e.stderr}")
        return False

def create_launch_scripts():
    """Create convenient launch scripts."""
    print("\n📝 Creating launch scripts...")
    
    # Create Windows batch file
    if platform.system() == "Windows":
        batch_content = """@echo off
echo Starting Enhanced SEO System...
python launch_enhanced_system.py %*
pause
"""
        with open("launch_enhanced.bat", "w") as f:
            f.write(batch_content)
        print("   ✅ launch_enhanced.bat created")
    
    # Create Unix shell script
    shell_content = """#!/bin/bash
echo "Starting Enhanced SEO System..."
python3 launch_enhanced_system.py "$@"
"""
    with open("launch_enhanced.sh", "w") as f:
        f.write(shell_content)
    
    # Make shell script executable on Unix systems
    if platform.system() != "Windows":
        os.chmod("launch_enhanced.sh", 0o755)
    
    print("   ✅ launch_enhanced.sh created")

def print_post_installation_info():
    """Print post-installation information."""
    print("\n🎉 Installation Complete!")
    print("=" * 50)
    
    print("\n🚀 Launch Options:")
    if platform.system() == "Windows":
        print("   • Double-click: launch_enhanced.bat")
        print("   • Command line: python launch_enhanced_system.py")
    else:
        print("   • Shell script: ./launch_enhanced.sh")
        print("   • Command line: python3 launch_enhanced_system.py")
    
    print("\n🔧 Development Mode:")
    print("   python launch_enhanced_system.py --dev")
    
    print("\n🏭 Production Mode:")
    print("   python launch_enhanced_system.py --production")
    
    print("\n🧪 Run Tests:")
    print("   python launch_enhanced_system.py --run-tests")
    
    print("\n📊 Web Interface:")
    print("   http://localhost:7860")
    
    print("\n📚 Documentation:")
    print("   README_ENHANCED.md")
    
    print("\n💡 Next Steps:")
    print("   1. Launch the system using one of the options above")
    print("   2. Access the web interface at http://localhost:7860")
    print("   3. Explore the monitoring dashboard and performance charts")
    print("   4. Test with your own SEO content")
    print("   5. Customize configuration for your specific needs")

def main():
    """Main installation function."""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    check_system_info()
    
    if not check_pip():
        print("❌ pip is required for installation")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install core dependencies")
        sys.exit(1)
    
    # Install optional dependencies
    install_optional_dependencies()
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        sys.exit(1)
    
    # Run tests
    if not run_basic_tests():
        print("❌ Basic tests failed")
        sys.exit(1)
    
    # Create launch scripts
    create_launch_scripts()
    
    # Print post-installation info
    print_post_installation_info()
    
    print("\n" + "=" * 80)
    print("🎉 Enhanced SEO System is ready for use!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed with error: {e}")
        sys.exit(1)
