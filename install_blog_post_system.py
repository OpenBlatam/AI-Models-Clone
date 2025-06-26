#!/usr/bin/env python3
"""
INSTALADOR AUTOMÁTICO - Sistema de Blog Posts de Onyx
======================================================

Script de instalación automática para el sistema de blog posts.
Instala dependencias, configura el entorno y verifica la instalación.

Uso:
    python install_blog_post_system.py
    python install_blog_post_system.py --full
    python install_blog_post_system.py --dev
"""

import asyncio
import os
import sys
import subprocess
import logging
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BlogPostSystemInstaller:
    """Instalador del sistema de blog posts"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.install_log = []
        
    def log_step(self, message: str, success: bool = True):
        """Registrar paso de instalación"""
        status = "✅" if success else "❌"
        log_message = f"{status} {message}"
        print(log_message)
        logger.info(message)
        
        self.install_log.append({
            "message": message,
            "success": success,
            "timestamp": time.time()
        })
    
    def run_command(self, command: List[str], description: str) -> bool:
        """Ejecutar comando del sistema"""
        try:
            self.log_step(f"Ejecutando: {description}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout:
                logger.debug(f"STDOUT: {result.stdout}")
            
            self.log_step(f"Completado: {description}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_step(f"Error en: {description} - {e}", False)
            if e.stderr:
                logger.error(f"STDERR: {e.stderr}")
            return False
        except Exception as e:
            self.log_step(f"Error inesperado en: {description} - {e}", False)
            return False
    
    def check_python_version(self) -> bool:
        """Verificar versión de Python"""
        self.log_step("Verificando versión de Python...")
        
        version = sys.version_info
        required_major, required_minor = 3, 8
        
        if version.major >= required_major and version.minor >= required_minor:
            self.log_step(f"Python {version.major}.{version.minor}.{version.micro} ✓")
            return True
        else:
            self.log_step(
                f"Python {version.major}.{version.minor} es demasiado antiguo. "
                f"Se requiere Python {required_major}.{required_minor}+", 
                False
            )
            return False
    
    def check_pip(self) -> bool:
        """Verificar que pip está disponible"""
        self.log_step("Verificando pip...")
        
        try:
            import pip
            self.log_step("pip está disponible ✓")
            return True
        except ImportError:
            try:
                subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
                self.log_step("pip está disponible via módulo ✓")
                return True
            except subprocess.CalledProcessError:
                self.log_step("pip no está disponible", False)
                return False
    
    def install_core_dependencies(self) -> bool:
        """Instalar dependencias core"""
        self.log_step("Instalando dependencias core...")
        
        core_deps = [
            "aiohttp>=3.8.0",
            "asyncio-compat>=0.1.0", 
            "dataclasses>=0.6",
            "typing-extensions>=4.0.0",
            "httpx>=0.24.0",
            "python-dateutil>=2.8.0"
        ]
        
        for dep in core_deps:
            success = self.run_command(
                [sys.executable, "-m", "pip", "install", dep],
                f"Instalando {dep}"
            )
            if not success:
                return False
        
        return True
    
    def install_recommended_dependencies(self) -> bool:
        """Instalar dependencias recomendadas"""
        self.log_step("Instalando dependencias recomendadas...")
        
        recommended_deps = [
            "langchain>=0.1.0",
            "langchain-community>=0.0.10",
            "orjson>=3.8.0",
            "blake3>=0.3.0",
            "lz4>=4.0.0",
            "pydantic>=2.0.0",
            "structlog>=23.0.0",
            "rich>=13.0.0"
        ]
        
        for dep in recommended_deps:
            success = self.run_command(
                [sys.executable, "-m", "pip", "install", dep],
                f"Instalando {dep}"
            )
            # No fallar si estas dependencias fallan
            if not success:
                self.log_step(f"Advertencia: No se pudo instalar {dep}", False)
        
        return True
    
    def install_full_dependencies(self) -> bool:
        """Instalar todas las dependencias desde requirements.txt"""
        self.log_step("Instalando todas las dependencias...")
        
        requirements_file = self.script_dir / "requirements.txt"
        
        if not requirements_file.exists():
            self.log_step("requirements.txt no encontrado", False)
            return False
        
        return self.run_command(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            "Instalando desde requirements.txt"
        )
    
    def install_dev_dependencies(self) -> bool:
        """Instalar dependencias de desarrollo"""
        self.log_step("Instalando dependencias de desarrollo...")
        
        dev_deps = [
            "pytest>=7.2.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0"
        ]
        
        for dep in dev_deps:
            success = self.run_command(
                [sys.executable, "-m", "pip", "install", dep],
                f"Instalando {dep}"
            )
            if not success:
                self.log_step(f"Advertencia: No se pudo instalar {dep}", False)
        
        return True
    
    def create_env_file(self) -> bool:
        """Crear archivo .env de ejemplo"""
        self.log_step("Creando archivo .env de ejemplo...")
        
        env_file = self.script_dir / ".env.example"
        
        env_content = """# =============================================
# ONYX BLOG POST SYSTEM - Environment Variables
# =============================================

# OpenRouter API (REQUIRED)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Onyx Integration (OPTIONAL)
ONYX_API_KEY=your_onyx_api_key_here
ONYX_BASE_URL=http://localhost:8080

# Cache Configuration
REDIS_URL=redis://localhost:6379
ENABLE_CACHE=true
CACHE_TTL=3600

# Database (for Onyx integration)
DATABASE_URL=postgresql://user:password@localhost:5432/onyx

# Performance Settings
MAX_CONCURRENT_REQUESTS=10
REQUESTS_PER_MINUTE=60
TOKENS_PER_MINUTE=100000

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# Security
ENABLE_CONTENT_FILTERING=true
MAX_COST_PER_REQUEST=1.0
DAILY_COST_LIMIT=50.0

# =============================================
# INSTRUCTIONS:
# 1. Copy this file to .env
# 2. Fill in your actual API keys
# 3. Adjust settings as needed
# =============================================
"""
        
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            self.log_step("Archivo .env.example creado ✓")
            return True
            
        except Exception as e:
            self.log_step(f"Error creando .env.example: {e}", False)
            return False
    
    def create_config_file(self) -> bool:
        """Crear archivo de configuración de ejemplo"""
        self.log_step("Creando archivo de configuración...")
        
        config_file = self.script_dir / "config.example.json"
        
        config_content = {
            "environment": "development",
            "openrouter": {
                "app_name": "onyx-blog-post",
                "default_model": "openai/gpt-4-turbo",
                "timeout": 60,
                "max_retries": 3,
                "requests_per_minute": 60,
                "tokens_per_minute": 100000,
                "enable_cost_tracking": True,
                "max_cost_per_request": 1.0,
                "daily_cost_limit": 50.0
            },
            "onyx_integration": {
                "enable_onyx_integration": True,
                "use_onyx_database": True,
                "store_blog_posts": True,
                "require_user_authentication": False,
                "enable_user_quotas": True,
                "default_user_quota": 10
            },
            "blog_defaults": {
                "blog_type": "technical",
                "tone": "professional",
                "length": "medium",
                "language": "es",
                "include_seo": True,
                "min_quality_score": 7.0
            },
            "cache": {
                "enable_cache": True,
                "cache_ttl": 3600,
                "max_cache_size": 1000,
                "enable_memory_cache": True,
                "enable_redis_cache": False
            },
            "performance": {
                "max_concurrent_requests": 10,
                "request_timeout": 120,
                "enable_metrics": True,
                "enable_benchmarking": True
            },
            "security": {
                "enable_content_filtering": True,
                "max_content_length": 50000,
                "user_rate_limit": 100,
                "strict_input_validation": True
            }
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_content, f, indent=2, ensure_ascii=False)
            
            self.log_step("Archivo config.example.json creado ✓")
            return True
            
        except Exception as e:
            self.log_step(f"Error creando config.example.json: {e}", False)
            return False
    
    async def test_installation(self) -> bool:
        """Probar la instalación"""
        self.log_step("Probando instalación...")
        
        try:
            # Importar el sistema
            from . import BlogPostSystem, create_blog_post_system
            
            # Crear sistema de prueba
            system = create_blog_post_system(
                api_key="test-key",
                environment="development"
            )
            
            # Verificar componentes básicos
            config = system.get_config_summary()
            self.log_step("Sistema inicializado correctamente ✓")
            
            # Verificar funcionalidades básicas
            models = await system.get_available_models()
            self.log_step(f"Modelos disponibles: {len(models)} ✓")
            
            # Verificar análisis de texto
            analysis = await system.analyze_text(
                text="Este es un texto de prueba para verificar el análisis.",
                keywords=["prueba", "análisis"]
            )
            self.log_step("Análisis de texto funcional ✓")
            
            # Verificar validación
            validation = await system.validate_content(
                topic="Tema de prueba",
                keywords=["prueba"]
            )
            self.log_step("Validación de contenido funcional ✓")
            
            # Cerrar sistema
            await system.close()
            self.log_step("Sistema cerrado correctamente ✓")
            
            return True
            
        except ImportError as e:
            self.log_step(f"Error de importación: {e}", False)
            return False
        except Exception as e:
            self.log_step(f"Error en test: {e}", False)
            return False
    
    def show_installation_summary(self):
        """Mostrar resumen de instalación"""
        print("\n" + "="*60)
        print("📋 RESUMEN DE INSTALACIÓN")
        print("="*60)
        
        successful_steps = [log for log in self.install_log if log["success"]]
        failed_steps = [log for log in self.install_log if not log["success"]]
        
        print(f"✅ Pasos exitosos: {len(successful_steps)}")
        print(f"❌ Pasos fallidos: {len(failed_steps)}")
        
        if failed_steps:
            print(f"\n⚠️  Errores encontrados:")
            for step in failed_steps:
                print(f"   - {step['message']}")
        
        print(f"\n📦 Sistema de Blog Posts:")
        print(f"   - Directorio: {self.script_dir}")
        print(f"   - Archivos de configuración creados")
        print(f"   - Dependencias instaladas")
        
        if len(failed_steps) == 0:
            print(f"\n🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")
            print(f"   El sistema de blog posts está listo para usar.")
        else:
            print(f"\n⚠️  INSTALACIÓN COMPLETADA CON ADVERTENCIAS")
            print(f"   Revisa los errores y considera instalar dependencias manualmente.")
    
    def show_next_steps(self):
        """Mostrar próximos pasos"""
        print("\n" + "="*60)
        print("🚀 PRÓXIMOS PASOS")
        print("="*60)
        print("1. Configurar API key de OpenRouter:")
        print("   - Copia .env.example a .env")
        print("   - Agrega tu OPENROUTER_API_KEY")
        print("")
        print("2. Probar el sistema:")
        print("   python demo_blog_post_system.py")
        print("")
        print("3. Usar en tu código:")
        print("   from onyx.server.features.blog_post import BlogPostSystem")
        print("   system = BlogPostSystem(api_key='tu-api-key')")
        print("")
        print("4. Configuración avanzada:")
        print("   - Revisa config.example.json")
        print("   - Configura Redis para cache (opcional)")
        print("   - Configura base de datos Onyx (opcional)")
        print("")
        print("📚 Documentación completa en README.md")
        print("="*60)
    
    async def install(self, mode: str = "core"):
        """Ejecutar instalación completa"""
        print("🚀 INSTALADOR DEL SISTEMA DE BLOG POSTS DE ONYX")
        print("="*60)
        print(f"Modo de instalación: {mode.upper()}")
        print("="*60)
        
        # Verificaciones básicas
        if not self.check_python_version():
            return False
        
        if not self.check_pip():
            return False
        
        # Instalación según modo
        success = True
        
        if mode in ["core", "recommended", "full", "dev"]:
            success &= self.install_core_dependencies()
        
        if mode in ["recommended", "full", "dev"]:
            success &= self.install_recommended_dependencies()
        
        if mode == "full":
            success &= self.install_full_dependencies()
        
        if mode == "dev":
            success &= self.install_dev_dependencies()
        
        # Crear archivos de configuración
        self.create_env_file()
        self.create_config_file()
        
        # Test de instalación
        if success:
            test_success = await self.test_installation()
            if not test_success:
                success = False
        
        # Mostrar resumen
        self.show_installation_summary()
        
        if success:
            self.show_next_steps()
        
        return success

async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Instalador del Sistema de Blog Posts de Onyx"
    )
    parser.add_argument(
        "--mode", 
        choices=["core", "recommended", "full", "dev"],
        default="recommended",
        help="Modo de instalación (default: recommended)"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Instalación completa (equivale a --mode full)"
    )
    parser.add_argument(
        "--dev",
        action="store_true", 
        help="Instalación para desarrollo (equivale a --mode dev)"
    )
    
    args = parser.parse_args()
    
    # Determinar modo
    if args.full:
        mode = "full"
    elif args.dev:
        mode = "dev"
    else:
        mode = args.mode
    
    # Ejecutar instalación
    installer = BlogPostSystemInstaller()
    success = await installer.install(mode)
    
    # Exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main()) 