#!/usr/bin/env python3
"""
🔍 Dependency Checker for Diffusion Models System
Comprehensive analysis of your Python environment and installed packages
"""

import sys
import subprocess
import importlib
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class DependencyChecker:
    """Comprehensive dependency checker for the diffusion models system."""
    
    def __init__(self):
        self.python_version = sys.version_info
        self.platform_info = platform.platform()
        self.arch_info = platform.architecture()
        self.machine_info = platform.machine()
        
        # Core dependencies to check
        self.core_deps = {
            'torch': 'PyTorch',
            'torchvision': 'TorchVision',
            'torchaudio': 'TorchAudio',
            'transformers': 'Transformers',
            'diffusers': 'Diffusers',
            'accelerate': 'Accelerate',
            'gradio': 'Gradio',
            'numpy': 'NumPy',
            'matplotlib': 'Matplotlib',
            'pillow': 'Pillow (PIL)',
            'opencv-python': 'OpenCV',
            'scipy': 'SciPy',
            'scikit-learn': 'Scikit-learn'
        }
        
        # Performance optimization dependencies
        self.performance_deps = {
            'xformers': 'XFormers',
            'optimum': 'Optimum',
            'onnx': 'ONNX',
            'onnxruntime-gpu': 'ONNX Runtime GPU',
            'psutil': 'psutil',
            'GPUtil': 'GPUtil',
            'memory-profiler': 'Memory Profiler',
            'py-spy': 'py-spy'
        }
        
        # Advanced dependencies
        self.advanced_deps = {
            'fastapi': 'FastAPI',
            'uvicorn': 'Uvicorn',
            'numba': 'Numba',
            'cython': 'Cython',
            'redis': 'Redis',
            'tensorboard': 'TensorBoard',
            'wandb': 'Weights & Biases',
            'mlflow': 'MLflow'
        }

    def print_header(self):
        """Print the checker header."""
        print("=" * 80)
        print("🔍 DEPENDENCY CHECKER FOR DIFFUSION MODELS SYSTEM")
        print("=" * 80)
        print(f"Platform: {self.platform_info}")
        print(f"Architecture: {self.arch_info[0]} ({self.arch_info[1]})")
        print(f"Machine: {self.machine_info}")
        print(f"Python: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        print("=" * 80)

    def check_python_version(self) -> bool:
        """Check if Python version meets minimum requirements."""
        min_version = (3, 8)
        current_version = (self.python_version.major, self.python_version.minor)
        
        if current_version >= min_version:
            print(f"✅ Python {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro} - OK")
            return True
        else:
            print(f"❌ Python {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro} - Requires Python 3.8+")
            return False

    def check_package(self, package_name: str, display_name: str) -> Tuple[bool, Optional[str]]:
        """Check if a specific package is installed and get its version."""
        try:
            module = importlib.import_module(package_name)
            version = getattr(module, '__version__', 'Unknown version')
            return True, version
        except ImportError:
            return False, None

    def check_dependencies(self, deps: Dict[str, str], category: str) -> Dict[str, Tuple[bool, Optional[str]]]:
        """Check a category of dependencies."""
        print(f"\n📦 {category.upper()} DEPENDENCIES:")
        print("-" * 50)
        
        results = {}
        for package, display_name in deps.items():
            installed, version = self.check_package(package, display_name)
            results[package] = (installed, version)
            
            if installed:
                print(f"✅ {display_name}: {version}")
            else:
                print(f"❌ {display_name}: Not installed")
        
        return results

    def check_cuda_availability(self) -> Dict[str, bool]:
        """Check CUDA availability and PyTorch CUDA support."""
        print(f"\n🚀 CUDA & GPU SUPPORT:")
        print("-" * 50)
        
        cuda_info = {}
        
        # Check if PyTorch is installed
        torch_available = importlib.util.find_spec('torch') is not None
        
        if torch_available:
            try:
                import torch
                cuda_info['torch_cuda_available'] = torch.cuda.is_available()
                cuda_info['torch_cuda_version'] = torch.version.cuda if torch.cuda.is_available() else None
                cuda_info['torch_device_count'] = torch.cuda.device_count() if torch.cuda.is_available() else 0
                
                if torch.cuda.is_available():
                    print(f"✅ PyTorch CUDA: Available (CUDA {torch.version.cuda})")
                    print(f"✅ GPU Devices: {torch.cuda.device_count()}")
                    if torch.cuda.device_count() > 0:
                        print(f"✅ Current Device: {torch.cuda.get_device_name(0)}")
                else:
                    print("❌ PyTorch CUDA: Not available")
                    
            except Exception as e:
                print(f"⚠️ PyTorch CUDA check failed: {e}")
                cuda_info['torch_cuda_available'] = False
        else:
            print("❌ PyTorch: Not installed")
            cuda_info['torch_cuda_available'] = False
        
        # Check system CUDA
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ NVIDIA Driver: Available")
                cuda_info['nvidia_driver'] = True
            else:
                print("❌ NVIDIA Driver: Not available")
                cuda_info['nvidia_driver'] = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ NVIDIA Driver: Not available")
            cuda_info['nvidia_driver'] = False
        
        return cuda_info

    def check_requirements_files(self) -> List[str]:
        """Check which requirements files are available."""
        print(f"\n📁 AVAILABLE REQUIREMENTS FILES:")
        print("-" * 50)
        
        available_files = []
        requirements_files = [
            'requirements.txt',
            'requirements_diffusion_models_optimized.txt',
            'advanced_requirements.txt',
            'requirements-ultra-optimized-quantum-neural.txt'
        ]
        
        for req_file in requirements_files:
            if Path(req_file).exists():
                print(f"✅ {req_file}")
                available_files.append(req_file)
            else:
                print(f"❌ {req_file}")
        
        return available_files

    def generate_installation_guide(self, core_results: Dict, performance_results: Dict, 
                                   advanced_results: Dict, cuda_info: Dict) -> None:
        """Generate installation recommendations based on current state."""
        print(f"\n🔧 INSTALLATION RECOMMENDATIONS:")
        print("-" * 50)
        
        # Count missing packages
        missing_core = sum(1 for installed, _ in core_results.values() if not installed)
        missing_performance = sum(1 for installed, _ in performance_results.values() if not installed)
        missing_advanced = sum(1 for installed, _ in advanced_results.values() if not installed)
        
        if missing_core == 0:
            print("✅ Core dependencies are complete!")
            print("   You can now run basic diffusion models functionality.")
        else:
            print(f"⚠️ {missing_core} core dependencies missing")
            print("   Install with: pip install -r requirements.txt")
        
        if missing_performance == 0:
            print("✅ Performance optimization dependencies are complete!")
            print("   You have access to advanced performance features.")
        else:
            print(f"⚠️ {missing_performance} performance dependencies missing")
            print("   Install with: pip install -r requirements_diffusion_models_optimized.txt")
        
        if missing_advanced == 0:
            print("✅ Advanced dependencies are complete!")
            print("   You have access to enterprise-level features.")
        else:
            print(f"⚠️ {missing_advanced} advanced dependencies missing")
            print("   Install with: pip install -r advanced_requirements.txt")
        
        # CUDA recommendations
        if not cuda_info.get('torch_cuda_available', False):
            print("\n🚨 CUDA RECOMMENDATIONS:")
            if not cuda_info.get('nvidia_driver', False):
                print("   - Install NVIDIA drivers for your GPU")
            print("   - Install PyTorch with CUDA support:")
            print("     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")

    def run_comprehensive_check(self):
        """Run the complete dependency check."""
        self.print_header()
        
        # Check Python version
        python_ok = self.check_python_version()
        
        if not python_ok:
            print("\n❌ Please upgrade Python to version 3.8 or higher")
            return
        
        # Check dependencies
        core_results = self.check_dependencies(self.core_deps, "Core")
        performance_results = self.check_dependencies(self.performance_deps, "Performance")
        advanced_results = self.check_dependencies(self.advanced_deps, "Advanced")
        
        # Check CUDA
        cuda_info = self.check_cuda_availability()
        
        # Check requirements files
        available_files = self.check_requirements_files()
        
        # Generate recommendations
        self.generate_installation_guide(core_results, performance_results, advanced_results, cuda_info)
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print("-" * 50)
        total_core = len(self.core_deps)
        total_performance = len(self.performance_deps)
        total_advanced = len(self.advanced_deps)
        
        installed_core = sum(1 for installed, _ in core_results.values() if installed)
        installed_performance = sum(1 for installed, _ in performance_results.values() if installed)
        installed_advanced = sum(1 for installed, _ in advanced_results.values() if installed)
        
        print(f"Core Dependencies: {installed_core}/{total_core} ({installed_core/total_core*100:.1f}%)")
        print(f"Performance Dependencies: {installed_performance}/{total_performance} ({installed_performance/total_performance*100:.1f}%)")
        print(f"Advanced Dependencies: {installed_advanced}/{total_advanced} ({installed_advanced/total_advanced*100:.1f}%)")
        
        if cuda_info.get('torch_cuda_available', False):
            print(f"GPU Support: ✅ Available ({cuda_info.get('torch_device_count', 0)} devices)")
        else:
            print("GPU Support: ❌ Not available")
        
        print(f"\n🎯 Ready for: ", end="")
        if installed_core == total_core:
            print("Basic diffusion models ✅")
        if installed_performance == total_performance:
            print("Performance optimization ✅")
        if installed_advanced == total_advanced:
            print("Advanced features ✅")
        
        print("\n" + "=" * 80)

def main():
    """Main function to run the dependency checker."""
    try:
        checker = DependencyChecker()
        checker.run_comprehensive_check()
    except KeyboardInterrupt:
        print("\n\n⚠️ Check interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during dependency check: {e}")
        print("Please check your Python environment and try again")

if __name__ == "__main__":
    main()
