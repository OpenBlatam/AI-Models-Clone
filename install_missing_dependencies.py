#!/usr/bin/env python3
"""
🚀 Missing Dependencies Installer
Automatically installs missing packages for your diffusion models system
"""

import subprocess
import sys
import importlib
from typing import List, Tuple

class DependencyInstaller:
    """Automated installer for missing dependencies."""
    
    def __init__(self):
        self.missing_core = ['pillow', 'opencv-python', 'scikit-learn']
        self.missing_performance = [
            'xformers', 'optimum', 'onnx', 'onnxruntime-gpu', 
            'GPUtil', 'memory-profiler', 'py-spy'
        ]
        self.missing_advanced = ['mlflow']
        
        # Package display names
        self.package_names = {
            'pillow': 'Pillow (PIL)',
            'opencv-python': 'OpenCV',
            'scikit-learn': 'Scikit-learn',
            'xformers': 'XFormers',
            'optimum': 'Optimum',
            'onnx': 'ONNX',
            'onnxruntime-gpu': 'ONNX Runtime GPU',
            'GPUtil': 'GPUtil',
            'memory-profiler': 'Memory Profiler',
            'py-spy': 'py-spy',
            'mlflow': 'MLflow'
        }

    def check_package(self, package_name: str) -> bool:
        """Check if a package is installed."""
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False

    def install_package(self, package_name: str) -> bool:
        """Install a single package."""
        display_name = self.package_names.get(package_name, package_name)
        print(f"📦 Installing {display_name}...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                print(f"✅ {display_name} installed successfully")
                return True
            else:
                print(f"❌ Failed to install {display_name}")
                print(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout installing {display_name}")
            return False
        except Exception as e:
            print(f"❌ Error installing {display_name}: {e}")
            return False

    def install_from_requirements(self, requirements_file: str) -> bool:
        """Install packages from a requirements file."""
        print(f"📁 Installing from {requirements_file}...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", requirements_file],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode == 0:
                print(f"✅ {requirements_file} installed successfully")
                return True
            else:
                print(f"❌ Failed to install from {requirements_file}")
                print(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout installing from {requirements_file}")
            return False
        except Exception as e:
            print(f"❌ Error installing from {requirements_file}: {e}")
            return False

    def get_missing_packages(self, package_list: List[str]) -> List[str]:
        """Get list of packages that are actually missing."""
        return [pkg for pkg in package_list if not self.check_package(pkg)]

    def install_core_dependencies(self) -> bool:
        """Install missing core dependencies."""
        print("\n🎯 INSTALLING CORE DEPENDENCIES")
        print("=" * 50)
        
        missing = self.get_missing_packages(self.missing_core)
        if not missing:
            print("✅ All core dependencies are already installed!")
            return True
        
        print(f"Found {len(missing)} missing core dependencies")
        
        success_count = 0
        for package in missing:
            if self.install_package(package):
                success_count += 1
        
        print(f"\n📊 Core Dependencies: {success_count}/{len(missing)} installed successfully")
        return success_count == len(missing)

    def install_performance_dependencies(self) -> bool:
        """Install performance optimization dependencies."""
        print("\n🚀 INSTALLING PERFORMANCE DEPENDENCIES")
        print("=" * 50)
        
        # Try to install from requirements file first
        if self.install_from_requirements('requirements_diffusion_models_optimized.txt'):
            return True
        
        # Fallback to individual package installation
        print("⚠️ Requirements file installation failed, trying individual packages...")
        
        missing = self.get_missing_packages(self.missing_performance)
        if not missing:
            print("✅ All performance dependencies are already installed!")
            return True
        
        print(f"Found {len(missing)} missing performance dependencies")
        
        success_count = 0
        for package in missing:
            if self.install_package(package):
                success_count += 1
        
        print(f"\n📊 Performance Dependencies: {success_count}/{len(missing)} installed successfully")
        return success_count == len(missing)

    def install_advanced_dependencies(self) -> bool:
        """Install advanced dependencies."""
        print("\n⚡ INSTALLING ADVANCED DEPENDENCIES")
        print("=" * 50)
        
        # Try to install from requirements file first
        if self.install_from_requirements('advanced_requirements.txt'):
            return True
        
        # Fallback to individual package installation
        print("⚠️ Requirements file installation failed, trying individual packages...")
        
        missing = self.get_missing_packages(self.missing_advanced)
        if not missing:
            print("✅ All advanced dependencies are already installed!")
            return True
        
        print(f"Found {len(missing)} missing advanced dependencies")
        
        success_count = 0
        for package in missing:
            if self.install_package(package):
                success_count += 1
        
        print(f"\n📊 Advanced Dependencies: {success_count}/{len(missing)} installed successfully")
        return success_count == len(missing)

    def install_cuda_support(self) -> bool:
        """Install CUDA support for PyTorch (optional)."""
        print("\n🚀 INSTALLING CUDA SUPPORT (OPTIONAL)")
        print("=" * 50)
        
        print("This will install PyTorch with CUDA support for GPU acceleration.")
        print("Only proceed if you have an NVIDIA GPU with CUDA drivers installed.")
        
        response = input("\nDo you want to install CUDA support? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            try:
                print("📦 Installing PyTorch with CUDA support...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", 
                    "torch", "torchvision", "torchaudio",
                    "--index-url", "https://download.pytorch.org/whl/cu118"
                ], capture_output=True, text=True, timeout=600)
                
                if result.returncode == 0:
                    print("✅ CUDA support installed successfully!")
                    return True
                else:
                    print("❌ Failed to install CUDA support")
                    print(f"Error: {result.stderr}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error installing CUDA support: {e}")
                return False
        else:
            print("⏭️ Skipping CUDA support installation")
            return True

    def run_installation(self):
        """Run the complete installation process."""
        print("🚀 MISSING DEPENDENCIES INSTALLER")
        print("=" * 60)
        print("This script will install missing dependencies for your diffusion models system")
        print("=" * 60)
        
        # Check current status
        print("\n🔍 CHECKING CURRENT STATUS...")
        missing_core = self.get_missing_packages(self.missing_core)
        missing_performance = self.get_missing_packages(self.missing_performance)
        missing_advanced = self.get_missing_packages(self.missing_advanced)
        
        if not any([missing_core, missing_performance, missing_advanced]):
            print("🎉 All dependencies are already installed!")
            return
        
        # Installation summary
        print(f"\n📋 INSTALLATION SUMMARY:")
        print(f"Core Dependencies: {len(missing_core)} missing")
        print(f"Performance Dependencies: {len(missing_performance)} missing")
        print(f"Advanced Dependencies: {len(missing_advanced)} missing")
        
        # Start installation
        print(f"\n🚀 STARTING INSTALLATION...")
        
        # Install core dependencies
        core_success = self.install_core_dependencies()
        
        # Install performance dependencies
        performance_success = self.install_performance_dependencies()
        
        # Install advanced dependencies
        advanced_success = self.install_advanced_dependencies()
        
        # Optional CUDA support
        cuda_success = self.install_cuda_support()
        
        # Final summary
        print("\n" + "=" * 60)
        print("📊 INSTALLATION SUMMARY")
        print("=" * 60)
        print(f"Core Dependencies: {'✅' if core_success else '❌'}")
        print(f"Performance Dependencies: {'✅' if performance_success else '❌'}")
        print(f"Advanced Dependencies: {'✅' if advanced_success else '❌'}")
        print(f"CUDA Support: {'✅' if cuda_success else '⏭️'}")
        
        if all([core_success, performance_success, advanced_success]):
            print("\n🎉 All dependencies installed successfully!")
            print("Your diffusion models system is now fully optimized!")
        else:
            print("\n⚠️ Some dependencies failed to install.")
            print("Check the error messages above and try again.")
        
        print("\n🔍 Run 'py check_dependencies.py' to verify the installation.")

def main():
    """Main function."""
    try:
        installer = DependencyInstaller()
        installer.run_installation()
    except KeyboardInterrupt:
        print("\n\n⚠️ Installation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during installation: {e}")
        print("Please check your Python environment and try again")

if __name__ == "__main__":
    main()
