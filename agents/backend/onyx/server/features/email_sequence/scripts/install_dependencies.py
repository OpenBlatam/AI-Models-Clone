#!/usr/bin/env python3
"""
Dependency Installation Script for Email Sequence AI System

This script provides an interactive way to install dependencies with different profiles
and handles common installation issues.
"""

import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path
from typing import List, Dict, Optional


class DependencyInstaller:
    """Manages dependency installation for the Email Sequence AI System."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.system = platform.system().lower()
        self.python_version = sys.version_info
        
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements."""
        if self.python_version < (3, 8):
            print(f"❌ Python {self.python_version.major}.{self.python_version.minor} is not supported.")
            print("Please upgrade to Python 3.8 or higher.")
            return False
        print(f"✅ Python {self.python_version.major}.{self.python_version.minor} is supported.")
        return True
    
    def check_pip(self) -> bool:
        """Check if pip is available and up to date."""
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ pip is available: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError:
            print("❌ pip is not available or not working properly.")
            return False
    
    def upgrade_pip(self) -> bool:
        """Upgrade pip to the latest version."""
        try:
            print("🔄 Upgrading pip...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         check=True, capture_output=True)
            print("✅ pip upgraded successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to upgrade pip: {e}")
            return False
    
    def check_git(self) -> bool:
        """Check if git is available."""
        try:
            result = subprocess.run(["git", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ git is available: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ git is not available. Please install git.")
            return False
    
    def check_cuda(self) -> bool:
        """Check if CUDA is available."""
        try:
            result = subprocess.run(["nvidia-smi"], 
                                  capture_output=True, text=True, check=True)
            print("✅ CUDA is available:")
            print(result.stdout)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  CUDA is not available. GPU features will be disabled.")
            return False
    
    def install_system_dependencies(self) -> bool:
        """Install system-level dependencies."""
        if self.system == "linux":
            return self._install_linux_dependencies()
        elif self.system == "darwin":
            return self._install_macos_dependencies()
        elif self.system == "windows":
            return self._install_windows_dependencies()
        else:
            print(f"⚠️  Unsupported operating system: {self.system}")
            return False
    
    def _install_linux_dependencies(self) -> bool:
        """Install Linux system dependencies."""
        try:
            # Detect package manager
            if os.path.exists("/etc/debian_version"):
                # Debian/Ubuntu
                packages = [
                    "build-essential", "python3-dev", "python3-pip", "python3-venv",
                    "git", "curl", "wget", "unzip", "libssl-dev", "libffi-dev",
                    "libjpeg-dev", "libpng-dev", "libfreetype6-dev", "libxft-dev",
                    "libblas-dev", "liblapack-dev", "libatlas-base-dev", "gfortran"
                ]
                cmd = ["sudo", "apt-get", "update"]
                subprocess.run(cmd, check=True)
                cmd = ["sudo", "apt-get", "install", "-y"] + packages
                subprocess.run(cmd, check=True)
            elif os.path.exists("/etc/redhat-release"):
                # CentOS/RHEL
                packages = [
                    "gcc", "gcc-c++", "python3-devel", "python3-pip", "git",
                    "curl", "wget", "unzip", "openssl-devel", "libffi-devel",
                    "libjpeg-devel", "libpng-devel", "freetype-devel",
                    "blas-devel", "lapack-devel", "atlas-devel", "gcc-gfortran"
                ]
                cmd = ["sudo", "yum", "groupinstall", "-y", "Development Tools"]
                subprocess.run(cmd, check=True)
                cmd = ["sudo", "yum", "install", "-y"] + packages
                subprocess.run(cmd, check=True)
            else:
                print("⚠️  Unsupported Linux distribution. Please install dependencies manually.")
                return False
            
            print("✅ Linux system dependencies installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Linux dependencies: {e}")
            return False
    
    def _install_macos_dependencies(self) -> bool:
        """Install macOS system dependencies."""
        try:
            # Check if Homebrew is installed
            result = subprocess.run(["brew", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("Installing Homebrew...")
                install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                subprocess.run(install_cmd, shell=True, check=True)
            
            packages = [
                "python3", "git", "curl", "wget", "openssl", "pkg-config",
                "libjpeg", "libpng", "freetype", "openblas", "gcc"
            ]
            
            for package in packages:
                print(f"Installing {package}...")
                subprocess.run(["brew", "install", package], check=True)
            
            print("✅ macOS system dependencies installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install macOS dependencies: {e}")
            return False
    
    def _install_windows_dependencies(self) -> bool:
        """Install Windows system dependencies."""
        print("⚠️  Windows dependencies should be installed manually:")
        print("1. Install Visual Studio Build Tools")
        print("2. Install Git for Windows")
        print("3. Install Python from python.org")
        print("4. Install required Visual C++ redistributables")
        return True
    
    def create_virtual_environment(self, env_name: str = "venv") -> bool:
        """Create a virtual environment."""
        try:
            venv_path = self.project_root / env_name
            if venv_path.exists():
                print(f"⚠️  Virtual environment '{env_name}' already exists.")
                return True
            
            print(f"🔄 Creating virtual environment '{env_name}'...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            print(f"✅ Virtual environment created at {venv_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def get_available_profiles(self) -> Dict[str, str]:
        """Get available installation profiles."""
        return {
            "minimal": "Basic functionality with essential dependencies",
            "dev": "Development environment with testing and debugging tools",
            "gpu": "GPU support for accelerated training",
            "distributed": "Distributed training capabilities",
            "cloud": "Cloud integration and deployment",
            "monitoring": "Production monitoring and observability",
            "profiling": "Performance profiling and optimization",
            "optimization": "Hyperparameter optimization tools",
            "nlp": "Advanced NLP and text processing",
            "web": "Web framework support",
            "database": "Database integration",
            "all": "Complete installation with all features"
        }
    
    def install_profile(self, profile: str, upgrade: bool = False) -> bool:
        """Install a specific profile."""
        profiles = self.get_available_profiles()
        
        if profile not in profiles:
            print(f"❌ Unknown profile: {profile}")
            print(f"Available profiles: {', '.join(profiles.keys())}")
            return False
        
        print(f"🔄 Installing profile: {profile}")
        print(f"Description: {profiles[profile]}")
        
        try:
            # Change to project directory
            os.chdir(self.project_root)
            
            # Install command
            cmd = [sys.executable, "-m", "pip", "install", "-e"]
            if upgrade:
                cmd.append("--upgrade")
            
            if profile == "all":
                cmd.append(".[all]")
            else:
                cmd.append(f".[{profile}]")
            
            print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            
            print(f"✅ Profile '{profile}' installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install profile '{profile}': {e}")
            return False
    
    def verify_installation(self, profile: str) -> bool:
        """Verify that the installation was successful."""
        print(f"🔄 Verifying installation for profile: {profile}")
        
        # Basic imports
        basic_modules = ["torch", "transformers", "gradio", "numpy", "pandas"]
        
        for module in basic_modules:
            try:
                __import__(module)
                print(f"✅ {module} imported successfully")
            except ImportError as e:
                print(f"❌ Failed to import {module}: {e}")
                return False
        
        # Profile-specific verifications
        if profile in ["gpu", "all"]:
            try:
                import torch
                if torch.cuda.is_available():
                    print(f"✅ CUDA is available: {torch.cuda.device_count()} GPUs")
                else:
                    print("⚠️  CUDA is not available")
            except ImportError:
                print("❌ PyTorch not available for GPU verification")
        
        if profile in ["profiling", "all"]:
            try:
                import memory_profiler
                import line_profiler
                print("✅ Profiling tools available")
            except ImportError:
                print("❌ Profiling tools not available")
        
        print("✅ Installation verification completed.")
        return True
    
    def interactive_install(self):
        """Run interactive installation."""
        print("🚀 Email Sequence AI System - Interactive Installation")
        print("=" * 60)
        
        # System checks
        if not self.check_python_version():
            return False
        
        if not self.check_pip():
            return False
        
        if not self.upgrade_pip():
            return False
        
        if not self.check_git():
            return False
        
        self.check_cuda()
        
        # System dependencies
        print("\n📦 System Dependencies")
        print("-" * 30)
        install_system = input("Install system dependencies? (y/n): ").lower().startswith('y')
        if install_system:
            if not self.install_system_dependencies():
                print("⚠️  System dependency installation failed. Continuing anyway...")
        
        # Virtual environment
        print("\n🐍 Virtual Environment")
        print("-" * 30)
        create_venv = input("Create virtual environment? (y/n): ").lower().startswith('y')
        if create_venv:
            env_name = input("Environment name (default: venv): ").strip() or "venv"
            if not self.create_virtual_environment(env_name):
                return False
        
        # Profile selection
        print("\n📋 Installation Profiles")
        print("-" * 30)
        profiles = self.get_available_profiles()
        
        for i, (profile, description) in enumerate(profiles.items(), 1):
            print(f"{i:2d}. {profile:<15} - {description}")
        
        while True:
            try:
                choice = input(f"\nSelect profile (1-{len(profiles)}) or 'all': ").strip()
                if choice.lower() == 'all':
                    selected_profile = "all"
                    break
                else:
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(profiles):
                        selected_profile = list(profiles.keys())[choice_idx]
                        break
                    else:
                        print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        # Installation
        print(f"\n🔄 Installing profile: {selected_profile}")
        if not self.install_profile(selected_profile):
            return False
        
        # Verification
        print("\n🔍 Verification")
        print("-" * 30)
        if not self.verify_installation(selected_profile):
            return False
        
        print("\n🎉 Installation completed successfully!")
        print("\nNext steps:")
        print("1. Activate virtual environment: source venv/bin/activate")
        print("2. Run basic demo: python examples/basic_demo.py")
        print("3. Check documentation: docs/")
        
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Install Email Sequence AI System dependencies")
    parser.add_argument("--profile", choices=["minimal", "dev", "gpu", "distributed", "cloud", 
                                            "monitoring", "profiling", "optimization", "nlp", 
                                            "web", "database", "all"],
                       help="Installation profile")
    parser.add_argument("--interactive", action="store_true", 
                       help="Run interactive installation")
    parser.add_argument("--upgrade", action="store_true", 
                       help="Upgrade existing installation")
    parser.add_argument("--verify", action="store_true", 
                       help="Verify installation")
    parser.add_argument("--check-system", action="store_true", 
                       help="Check system requirements")
    
    args = parser.parse_args()
    
    installer = DependencyInstaller()
    
    if args.check_system:
        print("🔍 System Requirements Check")
        print("=" * 40)
        installer.check_python_version()
        installer.check_pip()
        installer.check_git()
        installer.check_cuda()
        return
    
    if args.interactive:
        success = installer.interactive_install()
        sys.exit(0 if success else 1)
    
    if args.profile:
        success = installer.install_profile(args.profile, args.upgrade)
        if args.verify:
            installer.verify_installation(args.profile)
        sys.exit(0 if success else 1)
    
    # Default to interactive mode
    success = installer.interactive_install()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 