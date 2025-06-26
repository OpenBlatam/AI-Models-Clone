#!/usr/bin/env python3
"""
🗂️ MODULAR STRUCTURE ORGANIZER - VIDEO AI SYSTEM 2024
======================================================

Script para reorganizar todos los archivos en una estructura modular:
✅ Organización por funcionalidad
✅ Creación de __init__.py en cada módulo
✅ Documentación automática de la estructura
✅ Preservación de archivos importantes
✅ Backup de archivos antes de mover
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Estructura de organización de archivos
FILE_ORGANIZATION = {
    # Core - Archivos principales del sistema
    'core': [
        'models.py',
        'enhanced_models.py', 
        'video_ai_refactored.py',
        '__init__.py'
    ],
    
    # API - Archivos relacionados con APIs y servicios web
    'api': [
        'fastapi_microservice.py',
        'services.py',
        'utils_api.py',
        'utils_batch.py',
        'aws_lambda_handler.py'
    ],
    
    # Optimization - Archivos de optimización y rendimiento
    'optimization': [
        'ultra_performance_optimizers.py',
        'optimized_video_ai.py',
        'optimized_video_ai_ultra.py'
    ],
    
    # Production - Archivos específicos de producción
    'production': [
        'production_api_ultra.py',
        'production_config.py',
        'production_example.py',
        'install_ultra_optimizations.py'
    ],
    
    # Benchmarking - Archivos de testing y benchmarking
    'benchmarking': [
        'benchmark_optimization.py',
        'advanced_benchmark_system.py',
        'test_microservice.py',
        'test_system.py'
    ],
    
    # Config - Archivos de configuración
    'config': [
        'config.py',
        'onyx_config.py',
        'celeryconfig.py',
        'requirements*.txt'
    ],
    
    # Utils - Utilidades y helpers
    'utils': [
        'analytics.py',
        'collaboration.py',
        'compliance.py',
        'extractor_stats.py',
        'langchain_models.py',
        'multimedia.py',
        'review.py',
        'mejoral_watcher.py',
        'state_repository.py',
        'suggestions.py',
        'video_generator.py',
        'web_extract.py'
    ],
    
    # Docs - Documentación
    'docs': [
        '*.md',
        'openapi_examples.yaml'
    ],
    
    # Deployment - Archivos de deployment
    'deployment': [
        'Dockerfile',
        'cloudrun.Dockerfile',
        'docker-compose.yml',
        'kong.yaml',
        'grafana_dashboard.json'
    ],
    
    # Monitoring - Archivos de monitoreo
    'monitoring': [
        'metrics.py',
        'cleanup.py'
    ]
}

class ModularOrganizer:
    """Organizador de estructura modular."""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path('.')
        self.backup_path = self.base_path / 'backup_original'
        self.moved_files = []
        self.errors = []
        
    def create_backup(self):
        """Crear backup de archivos originales."""
        logger.info("📦 Creando backup de archivos originales...")
        
        if self.backup_path.exists():
            shutil.rmtree(self.backup_path)
        
        self.backup_path.mkdir(exist_ok=True)
        
        # Backup de archivos Python principales
        for file_path in self.base_path.glob('*.py'):
            if file_path.is_file():
                shutil.copy2(file_path, self.backup_path / file_path.name)
                logger.info(f"   📄 Backup: {file_path.name}")
        
        # Backup de archivos de configuración
        for pattern in ['*.txt', '*.yml', '*.yaml', '*.json', '*.md']:
            for file_path in self.base_path.glob(pattern):
                if file_path.is_file():
                    shutil.copy2(file_path, self.backup_path / file_path.name)
                    logger.info(f"   📄 Backup: {file_path.name}")
        
        logger.info(f"✅ Backup completado en: {self.backup_path}")
    
    def match_files(self, pattern: str) -> List[Path]:
        """Encontrar archivos que coincidan con el patrón."""
        if '*' in pattern:
            return list(self.base_path.glob(pattern))
        else:
            file_path = self.base_path / pattern
            return [file_path] if file_path.exists() else []
    
    def move_files_to_module(self, module_name: str, file_patterns: List[str]):
        """Mover archivos a un módulo específico."""
        module_path = self.base_path / module_name
        module_path.mkdir(exist_ok=True)
        
        logger.info(f"📁 Organizando módulo: {module_name}")
        
        moved_count = 0
        for pattern in file_patterns:
            matching_files = self.match_files(pattern)
            
            for file_path in matching_files:
                if file_path.is_file() and file_path.parent == self.base_path:
                    try:
                        destination = module_path / file_path.name
                        shutil.move(str(file_path), str(destination))
                        self.moved_files.append((file_path.name, module_name))
                        logger.info(f"   ➡️  {file_path.name} → {module_name}/")
                        moved_count += 1
                    except Exception as e:
                        error_msg = f"Error moviendo {file_path.name}: {e}"
                        self.errors.append(error_msg)
                        logger.error(f"   ❌ {error_msg}")
        
        logger.info(f"   ✅ Archivos movidos al módulo {module_name}: {moved_count}")
        return moved_count
    
    def create_init_files(self):
        """Crear archivos __init__.py para cada módulo."""
        logger.info("📝 Creando archivos __init__.py...")
        
        module_descriptions = {
            'core': 'Modelos y clases principales del sistema de Video AI',
            'api': 'APIs, servicios web y endpoints',
            'optimization': 'Optimizaciones de rendimiento y algoritmos avanzados',
            'production': 'Configuración y archivos específicos de producción',
            'benchmarking': 'Sistemas de testing, benchmarking y validación',
            'config': 'Archivos de configuración del sistema',
            'utils': 'Utilidades, helpers y funciones auxiliares',
            'docs': 'Documentación del sistema',
            'deployment': 'Archivos de deployment y containerización',
            'monitoring': 'Monitoreo, métricas y observabilidad'
        }
        
        for module_name, description in module_descriptions.items():
            module_path = self.base_path / module_name
            if module_path.exists():
                init_file = module_path / '__init__.py'
                
                init_content = f'''"""
{description.upper()}
{'=' * len(description)}

{description}

Estructura del módulo:
"""

# Importaciones automáticas
import os
from pathlib import Path

# Metadata del módulo
__module_name__ = "{module_name}"
__description__ = "{description}"
__version__ = "1.0.0"

# Path del módulo
MODULE_PATH = Path(__file__).parent

# Auto-discovery de archivos Python
__all__ = []
for file_path in MODULE_PATH.glob("*.py"):
    if file_path.name != "__init__.py":
        module_name = file_path.stem
        __all__.append(module_name)

def get_module_info():
    """Obtener información del módulo."""
    return {{
        "name": __module_name__,
        "description": __description__,
        "version": __version__,
        "path": str(MODULE_PATH),
        "files": __all__
    }}

def list_files():
    """Listar archivos en el módulo."""
    return [f.name for f in MODULE_PATH.glob("*.py")]
'''
                
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write(init_content)
                
                logger.info(f"   📝 Creado: {module_name}/__init__.py")
    
    def create_main_init(self):
        """Crear __init__.py principal."""
        logger.info("📝 Creando __init__.py principal...")
        
        main_init_content = '''"""
🚀 ULTRA VIDEO AI SYSTEM - MODULAR ARCHITECTURE
===============================================

Sistema modular ultra-optimizado para procesamiento de video AI.

Módulos disponibles:
- core: Modelos y clases principales
- api: APIs y servicios web
- optimization: Optimizaciones de rendimiento
- production: Configuración de producción
- benchmarking: Testing y benchmarking
- config: Configuración del sistema
- utils: Utilidades y helpers
- docs: Documentación
- deployment: Deployment y containerización
- monitoring: Monitoreo y métricas
"""

__version__ = "2.0.0"
__title__ = "Ultra Video AI System"
__description__ = "Sistema modular ultra-optimizado para procesamiento de video AI"

# Importaciones principales
from pathlib import Path

# Metadata
SYSTEM_PATH = Path(__file__).parent
MODULES = [
    "core",
    "api", 
    "optimization",
    "production",
    "benchmarking",
    "config",
    "utils",
    "docs",
    "deployment",
    "monitoring"
]

def get_system_info():
    """Obtener información del sistema."""
    return {
        "title": __title__,
        "version": __version__,
        "description": __description__,
        "modules": MODULES,
        "path": str(SYSTEM_PATH)
    }

def list_modules():
    """Listar módulos disponibles."""
    available_modules = []
    for module_name in MODULES:
        module_path = SYSTEM_PATH / module_name
        if module_path.exists() and module_path.is_dir():
            available_modules.append({
                "name": module_name,
                "path": str(module_path),
                "files": len(list(module_path.glob("*.py")))
            })
    return available_modules

# Configuración de logging para el sistema
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"🚀 {__title__} v{__version__} - Sistema modular inicializado")
'''
        
        main_init_path = self.base_path / '__init__.py'
        with open(main_init_path, 'w', encoding='utf-8') as f:
            f.write(main_init_content)
        
        logger.info("   ✅ __init__.py principal creado")
    
    def create_structure_documentation(self):
        """Crear documentación de la estructura."""
        logger.info("📚 Creando documentación de la estructura...")
        
        docs_path = self.base_path / 'docs'
        structure_doc = docs_path / 'MODULAR_STRUCTURE.md'
        
        content = f'''# 🗂️ ESTRUCTURA MODULAR - ULTRA VIDEO AI SYSTEM

## Descripción

Sistema reorganizado en estructura modular para mayor mantenibilidad y escalabilidad.

## Estructura de Directorios

```
ai_video/
├── core/                 # Modelos y clases principales
├── api/                  # APIs y servicios web
├── optimization/         # Optimizaciones de rendimiento
├── production/           # Configuración de producción
├── benchmarking/         # Testing y benchmarking
├── config/               # Configuración del sistema
├── utils/                # Utilidades y helpers
├── docs/                 # Documentación
├── deployment/           # Deployment y containerización
├── monitoring/           # Monitoreo y métricas
├── backup_original/      # Backup de archivos originales
└── __init__.py          # Inicialización del sistema
```

## Módulos

### 📦 Core
Contiene los modelos y clases principales del sistema de Video AI.

### 🌐 API
APIs, servicios web, endpoints y utilidades para servicios web.

### ⚡ Optimization  
Optimizaciones de rendimiento, algoritmos avanzados y librerías especializadas.

### 🚀 Production
Configuración y archivos específicos para entorno de producción.

### 🧪 Benchmarking
Sistemas de testing, benchmarking, validación y métricas de rendimiento.

### ⚙️ Config
Archivos de configuración del sistema y variables de entorno.

### 🛠️ Utils
Utilidades, helpers, funciones auxiliares y herramientas de soporte.

### 📚 Docs
Documentación completa del sistema, guías y referencias.

### 🐳 Deployment
Archivos de deployment, containerización (Docker) y orquestación.

### 📊 Monitoring
Monitoreo, métricas, observabilidad y herramientas de diagnóstico.

## Archivos Reorganizados

'''
        
        # Agregar lista de archivos movidos
        for file_name, module_name in sorted(self.moved_files):
            content += f"- `{file_name}` → `{module_name}/`\n"
        
        content += f'''
## Uso

### Importar desde módulos:

```python
# Importar modelos principales
from ai_video.core import models, video_ai_refactored

# Importar optimizaciones
from ai_video.optimization import ultra_performance_optimizers

# Importar APIs
from ai_video.api import fastapi_microservice

# Importar configuración de producción
from ai_video.production import production_config
```

### Obtener información del sistema:

```python
import ai_video

# Información del sistema
info = ai_video.get_system_info()
print(info)

# Listar módulos disponibles
modules = ai_video.list_modules()
for module in modules:
    print(f"Módulo: {{module['name']}} - {{module['files']}} archivos")
```

## Fecha de Reorganización

{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Backup

Los archivos originales se encuentran respaldados en `backup_original/`
'''
        
        with open(structure_doc, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"   📚 Documentación creada: {structure_doc}")
    
    def organize_structure(self):
        """Ejecutar organización completa."""
        logger.info("🗂️ Iniciando reorganización modular del sistema")
        logger.info("=" * 60)
        
        # 1. Crear backup
        self.create_backup()
        
        # 2. Organizar archivos por módulos
        total_moved = 0
        for module_name, file_patterns in FILE_ORGANIZATION.items():
            moved_count = self.move_files_to_module(module_name, file_patterns)
            total_moved += moved_count
        
        # 3. Crear archivos __init__.py
        self.create_init_files()
        self.create_main_init()
        
        # 4. Crear documentación
        self.create_structure_documentation()
        
        # 5. Reporte final
        logger.info("\n" + "=" * 60)
        logger.info("📊 REPORTE DE REORGANIZACIÓN")
        logger.info(f"✅ Archivos movidos: {total_moved}")
        logger.info(f"📁 Módulos creados: {len(FILE_ORGANIZATION)}")
        logger.info(f"❌ Errores: {len(self.errors)}")
        
        if self.errors:
            logger.warning("⚠️ Errores encontrados:")
            for error in self.errors:
                logger.warning(f"   - {error}")
        
        logger.info(f"📦 Backup disponible en: {self.backup_path}")
        logger.info("🎉 Reorganización modular completada!")
        
        return total_moved, len(self.errors)

def main():
    """Función principal."""
    print("🗂️ ORGANIZADOR DE ESTRUCTURA MODULAR")
    print("=" * 50)
    print("Este script reorganizará todos los archivos en una estructura modular.")
    print("Se creará un backup automático antes de mover archivos.")
    print()
    
    # Confirmar ejecución
    response = input("¿Continuar con la reorganización? (y/N): ")
    if response.lower() != 'y':
        print("❌ Reorganización cancelada")
        return
    
    try:
        organizer = ModularOrganizer()
        moved, errors = organizer.organize_structure()
        
        if errors == 0:
            print("\n🎉 ¡Reorganización completada exitosamente!")
            print("📚 Ver docs/MODULAR_STRUCTURE.md para documentación completa")
        else:
            print(f"\n⚠️ Reorganización completada con {errors} errores")
            print("Revisa los logs para más detalles")
            
    except Exception as e:
        logger.error(f"❌ Error durante la reorganización: {e}")
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 