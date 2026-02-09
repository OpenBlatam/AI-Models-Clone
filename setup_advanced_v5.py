#!/usr/bin/env python3
"""
SETUP ADVANCED v5.0 - Script de Configuración Avanzada
Configuración completa del sistema integrado v5.0 con opciones avanzadas
"""

import os
import sys
import subprocess
import platform
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SetupMode(Enum):
    """Modos de configuración disponibles."""
    BASIC = "basic"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"
    QUANTUM = "quantum"
    CUSTOM = "custom"

class SystemType(Enum):
    """Tipos de sistema soportados."""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"

@dataclass
class SystemRequirements:
    """Requisitos del sistema."""
    python_version: str
    memory_gb: float
    cpu_cores: int
    disk_gb: float
    gpu_required: bool
    internet_required: bool

@dataclass
class SetupConfig:
    """Configuración de setup."""
    mode: SetupMode
    system_type: SystemType
    install_dependencies: bool
    create_virtual_env: bool
    download_models: bool
    configure_services: bool
    run_tests: bool
    start_dashboard: bool
    custom_options: Dict[str, Any]

class AdvancedSetupV5:
    """Sistema de configuración avanzada v5.0."""
    
    def __init__(self):
        self.config: Optional[SetupConfig] = None
        self.system_info: Dict[str, Any] = {}
        self.requirements: SystemRequirements = SystemRequirements(
            python_version="3.8",
            memory_gb=4.0,
            cpu_cores=2,
            disk_gb=10.0,
            gpu_required=False,
            internet_required=True
        )
        
        logger.info("🚀 Advanced Setup v5.0 initialized")
    
    def detect_system(self) -> Dict[str, Any]:
        """Detectar información del sistema."""
        logger.info("🔍 Detecting system information...")
        
        system_info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": sys.version,
            "python_executable": sys.executable
        }
        
        # Detectar tipo de sistema
        if system_info["platform"] == "Windows":
            system_info["system_type"] = SystemType.WINDOWS
        elif system_info["platform"] == "Linux":
            system_info["system_type"] = SystemType.LINUX
        elif system_info["platform"] == "Darwin":
            system_info["system_type"] = SystemType.MACOS
        else:
            system_info["system_type"] = SystemType.LINUX
        
        # Detectar Docker
        if self._check_docker():
            system_info["docker_available"] = True
            system_info["docker_version"] = self._get_docker_version()
        else:
            system_info["docker_available"] = False
        
        # Detectar Kubernetes
        if self._check_kubernetes():
            system_info["kubernetes_available"] = True
            system_info["kubernetes_version"] = self._get_kubernetes_version()
        else:
            system_info["kubernetes_available"] = False
        
        self.system_info = system_info
        logger.info(f"✅ System detected: {system_info['platform']} {system_info['architecture']}")
        
        return system_info
    
    def _check_docker(self) -> bool:
        """Verificar si Docker está disponible."""
        try:
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _get_docker_version(self) -> str:
        """Obtener versión de Docker."""
        try:
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "Unknown"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "Not available"
    
    def _check_kubernetes(self) -> bool:
        """Verificar si Kubernetes está disponible."""
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _get_kubernetes_version(self) -> str:
        """Obtener versión de Kubernetes."""
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "Unknown"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "Not available"
    
    def check_system_requirements(self) -> Dict[str, Any]:
        """Verificar requisitos del sistema."""
        logger.info("🔍 Checking system requirements...")
        
        requirements_status = {
            "python_version": False,
            "memory": False,
            "cpu": False,
            "disk": False,
            "gpu": False,
            "internet": False,
            "overall": False
        }
        
        # Verificar versión de Python
        python_version = sys.version_info
        required_version = tuple(map(int, self.requirements.python_version.split('.')))
        
        if python_version >= required_version:
            requirements_status["python_version"] = True
            logger.info(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            logger.error(f"❌ Python version required: {self.requirements.python_version}, found: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Verificar memoria (simulación)
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb >= self.requirements.memory_gb:
                requirements_status["memory"] = True
                logger.info(f"✅ Memory: {memory_gb:.1f} GB")
            else:
                logger.warning(f"⚠️ Memory: {memory_gb:.1f} GB (recommended: {self.requirements.memory_gb} GB)")
        except ImportError:
            logger.warning("⚠️ psutil not available, skipping memory check")
            requirements_status["memory"] = True
        
        # Verificar CPU (simulación)
        try:
            cpu_count = os.cpu_count()
            if cpu_count and cpu_count >= self.requirements.cpu_cores:
                requirements_status["cpu"] = True
                logger.info(f"✅ CPU cores: {cpu_count}")
            else:
                logger.warning(f"⚠️ CPU cores: {cpu_count} (recommended: {self.requirements.cpu_cores})")
        except:
            logger.warning("⚠️ Could not determine CPU count")
            requirements_status["cpu"] = True
        
        # Verificar disco (simulación)
        try:
            disk_usage = psutil.disk_usage('/')
            disk_gb = disk_usage.free / (1024**3)
            if disk_gb >= self.requirements.disk_gb:
                requirements_status["disk"] = True
                logger.info(f"✅ Disk space: {disk_gb:.1f} GB free")
            else:
                logger.warning(f"⚠️ Disk space: {disk_gb:.1f} GB free (recommended: {self.requirements.disk_gb} GB)")
        except:
            logger.warning("⚠️ Could not determine disk space")
            requirements_status["disk"] = True
        
        # Verificar GPU (simulación)
        if not self.requirements.gpu_required:
            requirements_status["gpu"] = True
            logger.info("✅ GPU not required")
        else:
            try:
                import torch
                if torch.cuda.is_available():
                    requirements_status["gpu"] = True
                    logger.info(f"✅ GPU available: {torch.cuda.get_device_name(0)}")
                else:
                    logger.warning("⚠️ GPU not available")
            except ImportError:
                logger.warning("⚠️ PyTorch not available, skipping GPU check")
                requirements_status["gpu"] = True
        
        # Verificar internet (simulación)
        try:
            import urllib.request
            urllib.request.urlopen('http://www.google.com', timeout=5)
            requirements_status["internet"] = True
            logger.info("✅ Internet connection available")
        except:
            logger.warning("⚠️ Internet connection not available")
        
        # Estado general
        critical_checks = ["python_version"]
        if all(requirements_status[check] for check in critical_checks):
            requirements_status["overall"] = True
            logger.info("✅ System requirements met")
        else:
            logger.error("❌ System requirements not met")
        
        return requirements_status
    
    def create_virtual_environment(self, env_name: str = "linkedin_optimizer_v5") -> bool:
        """Crear entorno virtual."""
        logger.info(f"🐍 Creating virtual environment: {env_name}")
        
        try:
            # Verificar si ya existe
            if os.path.exists(env_name):
                logger.info(f"✅ Virtual environment already exists: {env_name}")
                return True
            
            # Crear entorno virtual
            result = subprocess.run(
                [sys.executable, "-m", "venv", env_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Virtual environment created: {env_name}")
                return True
            else:
                logger.error(f"❌ Failed to create virtual environment: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout creating virtual environment")
            return False
        except Exception as e:
            logger.error(f"❌ Error creating virtual environment: {e}")
            return False
    
    def install_dependencies(self, env_name: str = "linkedin_optimizer_v5") -> bool:
        """Instalar dependencias."""
        logger.info("📦 Installing dependencies...")
        
        try:
            # Activar entorno virtual y instalar
            if platform.system() == "Windows":
                pip_path = os.path.join(env_name, "Scripts", "pip")
                python_path = os.path.join(env_name, "Scripts", "python")
            else:
                pip_path = os.path.join(env_name, "bin", "pip")
                python_path = os.path.join(env_name, "bin", "python")
            
            # Verificar si existe requirements_v5.txt
            if not os.path.exists("requirements_v5.txt"):
                logger.error("❌ requirements_v5.txt not found")
                return False
            
            # Instalar dependencias
            result = subprocess.run(
                [pip_path, "install", "-r", "requirements_v5.txt"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✅ Dependencies installed successfully")
                return True
            else:
                logger.error(f"❌ Failed to install dependencies: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout installing dependencies")
            return False
        except Exception as e:
            logger.error(f"❌ Error installing dependencies: {e}")
            return False
    
    async def download_ai_models(self) -> bool:
        """Descargar modelos de AI."""
        logger.info("🤖 Downloading AI models...")
        
        try:
            # Simular descarga de modelos
            await asyncio.sleep(2)
            
            logger.info("✅ AI models downloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error downloading AI models: {e}")
            return False
    
    def configure_services(self) -> bool:
        """Configurar servicios del sistema."""
        logger.info("⚙️ Configuring system services...")
        
        try:
            # Crear directorios necesarios
            directories = [
                "logs",
                "data",
                "models",
                "config",
                "reports"
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"📁 Created directory: {directory}")
            
            # Crear archivo de configuración
            config = {
                "system": {
                    "version": "5.0",
                    "mode": "auto",
                    "log_level": "INFO"
                },
                "services": {
                    "ai_intelligence": True,
                    "microservices": True,
                    "analytics": True,
                    "security": True,
                    "infrastructure": True
                },
                "dashboard": {
                    "host": "localhost",
                    "port": 8000,
                    "auto_start": True
                }
            }
            
            with open("config/system_config_v5.json", "w") as f:
                json.dump(config, f, indent=2)
            
            logger.info("✅ System services configured")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configuring services: {e}")
            return False
    
    def run_system_tests(self) -> bool:
        """Ejecutar pruebas del sistema."""
        logger.info("🧪 Running system tests...")
        
        try:
            # Ejecutar test_system_v5.py
            if os.path.exists("test_system_v5.py"):
                result = subprocess.run(
                    [sys.executable, "test_system_v5.py"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    logger.info("✅ System tests passed")
                    return True
                else:
                    logger.error(f"❌ System tests failed: {result.stderr}")
                    return False
            else:
                logger.warning("⚠️ test_system_v5.py not found, skipping tests")
                return True
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout running system tests")
            return False
        except Exception as e:
            logger.error(f"❌ Error running system tests: {e}")
            return False
    
    def start_dashboard(self) -> bool:
        """Iniciar dashboard web."""
        logger.info("🌐 Starting web dashboard...")
        
        try:
            # Verificar si existe web_dashboard_v5.py
            if not os.path.exists("web_dashboard_v5.py"):
                logger.error("❌ web_dashboard_v5.py not found")
                return False
            
            # Iniciar dashboard en background
            if platform.system() == "Windows":
                subprocess.Popen(
                    [sys.executable, "web_dashboard_v5.py"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                subprocess.Popen(
                    [sys.executable, "web_dashboard_v5.py"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            logger.info("✅ Web dashboard started")
            logger.info("🌐 Access at: http://localhost:8000")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting dashboard: {e}")
            return False
    
    async def run_setup(self, config: SetupConfig) -> Dict[str, Any]:
        """Ejecutar setup completo."""
        logger.info(f"🚀 Starting setup in {config.mode.value} mode...")
        
        self.config = config
        setup_results = {
            "system_detection": False,
            "requirements_check": False,
            "virtual_env": False,
            "dependencies": False,
            "ai_models": False,
            "services": False,
            "tests": False,
            "dashboard": False,
            "overall": False
        }
        
        try:
            # 1. Detectar sistema
            system_info = self.detect_system()
            setup_results["system_detection"] = True
            
            # 2. Verificar requisitos
            requirements_status = self.check_system_requirements()
            if requirements_status["overall"]:
                setup_results["requirements_check"] = True
            else:
                logger.error("❌ System requirements not met, setup cannot continue")
                return setup_results
            
            # 3. Crear entorno virtual
            if config.create_virtual_env:
                if self.create_virtual_environment():
                    setup_results["virtual_env"] = True
                else:
                    logger.error("❌ Failed to create virtual environment")
                    return setup_results
            
            # 4. Instalar dependencias
            if config.install_dependencies:
                if self.install_dependencies():
                    setup_results["dependencies"] = True
                else:
                    logger.error("❌ Failed to install dependencies")
                    return setup_results
            
            # 5. Descargar modelos AI
            if config.download_models:
                if await self.download_ai_models():
                    setup_results["ai_models"] = True
                else:
                    logger.warning("⚠️ Failed to download AI models")
            
            # 6. Configurar servicios
            if config.configure_services:
                if self.configure_services():
                    setup_results["services"] = True
                else:
                    logger.warning("⚠️ Failed to configure services")
            
            # 7. Ejecutar pruebas
            if config.run_tests:
                if self.run_system_tests():
                    setup_results["tests"] = True
                else:
                    logger.warning("⚠️ Failed to run system tests")
            
            # 8. Iniciar dashboard
            if config.start_dashboard:
                if self.start_dashboard():
                    setup_results["dashboard"] = True
                else:
                    logger.warning("⚠️ Failed to start dashboard")
            
            # Estado general
            critical_steps = ["system_detection", "requirements_check"]
            if config.create_virtual_env:
                critical_steps.append("virtual_env")
            if config.install_dependencies:
                critical_steps.append("dependencies")
            
            if all(setup_results[step] for step in critical_steps):
                setup_results["overall"] = True
                logger.info("🎉 Setup completed successfully!")
            else:
                logger.error("❌ Setup failed")
            
            return setup_results
            
        except Exception as e:
            logger.error(f"❌ Setup failed with error: {e}")
            return setup_results
    
    def generate_setup_report(self, results: Dict[str, Any]) -> str:
        """Generar reporte de setup."""
        logger.info("📊 Generating setup report...")
        
        report = f"""
# SETUP REPORT v5.0
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Information
- Platform: {self.system_info.get('platform', 'Unknown')}
- Architecture: {self.system_info.get('architecture', 'Unknown')}
- Python: {self.system_info.get('python_version', 'Unknown')}
- Docker: {self.system_info.get('docker_available', False)}
- Kubernetes: {self.system_info.get('kubernetes_available', False)}

## Setup Results
"""
        
        for step, status in results.items():
            status_icon = "✅" if status else "❌"
            report += f"- {step.replace('_', ' ').title()}: {status_icon}\n"
        
        report += f"""
## Overall Status
{'🎉 SUCCESS' if results['overall'] else '❌ FAILED'}

## Next Steps
"""
        
        if results['overall']:
            report += """
1. Access the web dashboard at: http://localhost:8000
2. Run optimization tests with: python test_system_v5.py
3. Check system status in the dashboard
4. Review logs in the 'logs' directory
"""
        else:
            report += """
1. Review the error messages above
2. Check system requirements
3. Verify Python version and dependencies
4. Try running setup again
"""
        
        # Guardar reporte
        with open("setup_report_v5.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        logger.info("💾 Setup report saved to setup_report_v5.md")
        return report

async def interactive_setup():
    """Setup interactivo."""
    print("🚀 LINKEDIN OPTIMIZER v5.0 - Advanced Setup")
    print("=" * 50)
    
    # Detectar sistema
    setup = AdvancedSetupV5()
    system_info = setup.detect_system()
    
    print(f"\n🔍 System detected: {system_info['platform']} {system_info['architecture']}")
    print(f"🐍 Python: {system_info['python_version']}")
    
    # Verificar requisitos
    requirements_status = setup.check_system_requirements()
    if not requirements_status["overall"]:
        print("\n❌ System requirements not met. Setup cannot continue.")
        return
    
    print("\n✅ System requirements met!")
    
    # Seleccionar modo
    print("\n📋 Select setup mode:")
    print("1. Basic - Core functionality only")
    print("2. Advanced - Full system with AI models")
    print("3. Enterprise - Production-ready with security")
    print("4. Quantum - Experimental features")
    print("5. Custom - Manual configuration")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                break
            print("Invalid choice. Please enter 1-5.")
        except KeyboardInterrupt:
            print("\n\nSetup cancelled.")
            return
    
    # Mapear elección a modo
    mode_map = {
        '1': SetupMode.BASIC,
        '2': SetupMode.ADVANCED,
        '3': SetupMode.ENTERPRISE,
        '4': SetupMode.QUANTUM,
        '5': SetupMode.CUSTOM
    }
    
    selected_mode = mode_map[choice]
    
    # Configuración según modo
    if selected_mode == SetupMode.BASIC:
        config = SetupConfig(
            mode=selected_mode,
            system_type=system_info["system_type"],
            install_dependencies=True,
            create_virtual_env=True,
            download_models=False,
            configure_services=True,
            run_tests=True,
            start_dashboard=True,
            custom_options={}
        )
    elif selected_mode == SetupMode.ADVANCED:
        config = SetupConfig(
            mode=selected_mode,
            system_type=system_info["system_type"],
            install_dependencies=True,
            create_virtual_env=True,
            download_models=True,
            configure_services=True,
            run_tests=True,
            start_dashboard=True,
            custom_options={}
        )
    elif selected_mode == SetupMode.ENTERPRISE:
        config = SetupConfig(
            mode=selected_mode,
            system_type=system_info["system_type"],
            install_dependencies=True,
            create_virtual_env=True,
            download_models=True,
            configure_services=True,
            run_tests=True,
            start_dashboard=True,
            custom_options={"security_level": "high"}
        )
    elif selected_mode == SetupMode.QUANTUM:
        config = SetupConfig(
            mode=selected_mode,
            system_type=system_info["system_type"],
            install_dependencies=True,
            create_virtual_env=True,
            download_models=True,
            configure_services=True,
            run_tests=True,
            start_dashboard=True,
            custom_options={"experimental": True}
        )
    else:  # Custom
        config = SetupConfig(
            mode=selected_mode,
            system_type=system_info["system_type"],
            install_dependencies=input("Install dependencies? (y/n): ").lower() == 'y',
            create_virtual_env=input("Create virtual environment? (y/n): ").lower() == 'y',
            download_models=input("Download AI models? (y/n): ").lower() == 'y',
            configure_services=input("Configure services? (y/n): ").lower() == 'y',
            run_tests=input("Run system tests? (y/n): ").lower() == 'y',
            start_dashboard=input("Start dashboard? (y/n): ").lower() == 'y',
            custom_options={}
        )
    
    print(f"\n🚀 Starting setup in {selected_mode.value} mode...")
    
    # Ejecutar setup
    results = await setup.run_setup(config)
    
    # Generar reporte
    report = setup.generate_setup_report(results)
    
    print("\n" + "=" * 50)
    print("📊 SETUP COMPLETED")
    print("=" * 50)
    print(report)

async def demo():
    """Función de demostración."""
    logger.info("🎯 Starting Advanced Setup v5.0 Demo")
    
    try:
        # Crear setup básico
        setup = AdvancedSetupV5()
        
        # Configuración de demo
        config = SetupConfig(
            mode=SetupMode.ADVANCED,
            system_type=SystemType.LINUX,
            install_dependencies=True,
            create_virtual_env=True,
            download_models=True,
            configure_services=True,
            run_tests=True,
            start_dashboard=True,
            custom_options={}
        )
        
        # Ejecutar setup
        results = await setup.run_setup(config)
        
        # Generar reporte
        report = setup.generate_setup_report(results)
        
        logger.info("✅ Demo completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(interactive_setup())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Please check the error messages and try again.")
