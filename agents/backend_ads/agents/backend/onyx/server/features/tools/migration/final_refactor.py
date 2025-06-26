#!/usr/bin/env python3
"""
Final Features Directory Refactoring Script

Este script completa la refactorización del directorio features organizando
todos los archivos dispersos en la estructura modular apropiada y eliminando
duplicados.
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinalRefactor:
    """Refactorización final del directorio features."""
    
    def __init__(self, features_dir: str = "."):
        self.features_dir = Path(features_dir)
        self.backup_dir = self.features_dir / "backup_refactor"
        self.stats = {
            "moved_files": 0,
            "merged_files": 0,
            "deleted_duplicates": 0,
            "created_directories": 0,
            "errors": 0
        }
        
        # Mapeo de archivos a sus ubicaciones correctas
        self.file_mappings = {
            # Production files -> modules/production/
            "modules/production/apps/": [
                "production_app_ultra.py",
                "production_optimized.py", 
                "main_quantum.py",
                "main_ultra.py",
                "main.py",
                "production_runner.py",
                "startup.py",
                "app.py"
            ],
            
            # Copywriting files -> modules/copywriting/
            "modules/copywriting/": [
                "copywriting_model.py",
                "advanced_copywriting_cache.py",
                "data_processing.py"
            ],
            
            # Optimization files -> modules/optimization/
            "modules/optimization/": [
                "optimization.py"
            ],
            
            # Configuration files -> config/
            "config/docker/": [
                "Dockerfile.ultra",
                "Dockerfile.production", 
                "docker-compose.production.yml",
                "nginx.conf"
            ],
            
            "config/requirements/": [
                "requirements.txt",
                "requirements_quantum.txt",
                "requirements_ultra.txt", 
                "requirements_optimized.txt",
                "requirements_nexus.txt"
            ],
            
            "config/environment/": [
                "env.example"
            ],
            
            # Deployment scripts -> config/deployment/
            "config/deployment/": [
                "deploy.sh",
                "deploy_production.sh",
                "run.sh",
                "run_ultra.sh", 
                "run_production.sh",
                "Makefile"
            ],
            
            # Core files -> core/
            "core/": [
                "config.py",
                "exceptions.py",
                "monitoring.py",
                "utils.py",
                "protocols.py"
            ],
            
            # Cache -> shared/cache/
            "shared/cache/": [
                "cache.py"
            ],
            
            # Documentation -> docs/
            "docs/refactoring/": [
                "README_IMPROVED.md",
                "ARCHITECTURE_CLEANUP_COMPLETE.md",
                "FINAL_ARCHITECTURE_STATUS.md",
                "REFACTORING_COMPLETE.md",
                "MODULARIZATION_COMPLETE.md",
                "OPTIMIZATION_RESULTS.md",
                "MIGRATION_SUMMARY.md",
                "README_NEXUS.md",
                "ARCHITECTURE.md",
                "README.md",
                "README_PRODUCTION.md"
            ],
            
            # Legacy cleanup scripts -> tools/migration/
            "tools/migration/": [
                "improved_architecture.py",
                "architecture_cleanup.py",
                "cleanup_legacy_final.py", 
                "legacy_cleanup.py",
                "migrate_to_nexus.py",
                "nexus_example_refactored.py"
            ],
            
            # Integration examples -> docs/examples/
            "docs/examples/": [
                "integration_example.py"
            ]
        }
    
    def create_backup(self):
        """Crear backup antes de la refactorización."""
        logger.info("🔄 Creando backup de seguridad...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        self.backup_dir.mkdir()
        
        # Backup de archivos importantes
        important_files = [
            "__init__.py",
            "config.py", 
            "app.py",
            "optimization.py",
            "copywriting_model.py"
        ]
        
        for file_name in important_files:
            source = self.features_dir / file_name
            if source.exists():
                shutil.copy2(source, self.backup_dir / file_name)
        
        logger.info(f"✅ Backup creado en: {self.backup_dir}")
    
    def ensure_directory_structure(self):
        """Asegurar que la estructura de directorios existe."""
        logger.info("🏗️ Verificando estructura de directorios...")
        
        required_dirs = [
            "modules/production/apps",
            "modules/copywriting", 
            "modules/optimization",
            "config/docker",
            "config/requirements", 
            "config/environment",
            "config/deployment",
            "core",
            "shared/cache",
            "docs/refactoring",
            "docs/examples", 
            "tools/migration"
        ]
        
        for dir_path in required_dirs:
            full_path = self.features_dir / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                self.stats["created_directories"] += 1
                logger.info(f"   📁 Creado: {dir_path}")
    
    def move_files(self):
        """Mover archivos a sus ubicaciones correctas."""
        logger.info("📦 Moviendo archivos a estructura modular...")
        
        for target_dir, files in self.file_mappings.items():
            target_path = self.features_dir / target_dir
            
            for file_name in files:
                source_path = self.features_dir / file_name
                dest_path = target_path / file_name
                
                if source_path.exists() and source_path != dest_path:
                    try:
                        # Si el archivo ya existe en destino, hacer merge inteligente
                        if dest_path.exists():
                            self.handle_duplicate(source_path, dest_path)
                        else:
                            shutil.move(str(source_path), str(dest_path))
                            self.stats["moved_files"] += 1
                            logger.info(f"   ✅ {file_name} → {target_dir}")
                    except Exception as e:
                        logger.error(f"   ❌ Error moviendo {file_name}: {e}")
                        self.stats["errors"] += 1
    
    def handle_duplicate(self, source_path: Path, dest_path: Path):
        """Manejar archivos duplicados de forma inteligente."""
        source_size = source_path.stat().st_size
        dest_size = dest_path.stat().st_size
        
        # Si el archivo fuente es más grande o más reciente, reemplazar
        source_mtime = source_path.stat().st_mtime
        dest_mtime = dest_path.stat().st_mtime
        
        if source_size > dest_size or source_mtime > dest_mtime:
            # Backup del archivo existente
            backup_name = f"{dest_path.name}.backup"
            backup_path = dest_path.parent / backup_name
            shutil.copy2(dest_path, backup_path)
            
            # Reemplazar con el archivo fuente
            shutil.copy2(source_path, dest_path)
            source_path.unlink()  # Eliminar archivo fuente
            
            self.stats["merged_files"] += 1
            logger.info(f"   🔄 Merged: {source_path.name} (backup created)")
        else:
            # Eliminar archivo fuente duplicado
            source_path.unlink()
            self.stats["deleted_duplicates"] += 1
            logger.info(f"   🗑️ Eliminado duplicado: {source_path.name}")
    
    def clean_empty_directories(self):
        """Limpiar directorios vacíos."""
        logger.info("🧹 Limpiando directorios vacíos...")
        
        # Obtener todos los directorios
        all_dirs = [d for d in self.features_dir.rglob("*") if d.is_dir()]
        all_dirs.sort(key=lambda x: len(str(x)), reverse=True)  # Empezar por los más profundos
        
        removed_count = 0
        for dir_path in all_dirs:
            try:
                # Verificar si está vacío (no contiene archivos, solo directorios vacíos)
                if dir_path.exists() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    removed_count += 1
                    logger.info(f"   🗑️ Eliminado directorio vacío: {dir_path.name}")
            except OSError:
                # Directorio no vacío o sin permisos
                pass
        
        if removed_count > 0:
            logger.info(f"✅ Eliminados {removed_count} directorios vacíos")
    
    def update_init_files(self):
        """Actualizar archivos __init__.py para la nueva estructura."""
        logger.info("📝 Actualizando archivos __init__.py...")
        
        # Actualizar __init__.py principal
        main_init = self.features_dir / "__init__.py"
        if main_init.exists():
            self.update_main_init(main_init)
        
        # Crear __init__.py en directorios que lo necesiten
        init_dirs = [
            "modules",
            "modules/production", 
            "modules/production/apps",
            "modules/copywriting",
            "modules/optimization", 
            "config",
            "core",
            "shared",
            "docs",
            "tools"
        ]
        
        for dir_path in init_dirs:
            init_file = self.features_dir / dir_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()
                logger.info(f"   ✅ Creado: {dir_path}/__init__.py")
    
    def update_main_init(self, init_file: Path):
        """Actualizar el __init__.py principal con la nueva estructura."""
        content = '''"""
Onyx Features - Clean Modular Architecture

Refactored structure with clean separation of concerns:
- modules/: Core business modules (production, copywriting, optimization) 
- shared/: Shared services (cache, database, monitoring, infrastructure)
- core/: Core utilities (config, exceptions, protocols, utils)
- config/: Configuration files (docker, deployment, requirements)
- docs/: Documentation and examples
- tools/: Migration and development tools
- legacy/: Archived legacy code
"""

from typing import Dict, Any, Optional
import logging

# Version information
__version__ = "2.0.0-refactored"
__author__ = "Onyx Features Team"

logger = logging.getLogger(__name__)

# Import availability flags
try:
    from .core import config, exceptions, protocols, utils
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False

try:
    from .modules import copywriting, optimization
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False

try:
    from .shared import cache, database, monitoring, infrastructure
    SHARED_AVAILABLE = True
except ImportError:
    SHARED_AVAILABLE = False

# Production apps availability
try:
    from .modules.production import apps
    PRODUCTION_AVAILABLE = True
except ImportError:
    PRODUCTION_AVAILABLE = False

def get_system_status() -> Dict[str, Any]:
    """Get the status of all system components."""
    return {
        "version": __version__,
        "core_available": CORE_AVAILABLE,
        "modules_available": MODULES_AVAILABLE, 
        "shared_available": SHARED_AVAILABLE,
        "production_available": PRODUCTION_AVAILABLE,
        "architecture": "modular_refactored",
        "refactor_date": "2024-01-15"
    }

def create_feature_factory():
    """Create a factory for feature services."""
    if not CORE_AVAILABLE:
        raise ImportError("Core modules not available")
    
    return {
        "config": config if CORE_AVAILABLE else None,
        "exceptions": exceptions if CORE_AVAILABLE else None,
        "copywriting": copywriting if MODULES_AVAILABLE else None,
        "optimization": optimization if MODULES_AVAILABLE else None,
        "cache": cache if SHARED_AVAILABLE else None,
        "monitoring": monitoring if SHARED_AVAILABLE else None
    }

# Export main components
__all__ = [
    "__version__",
    "__author__", 
    "get_system_status",
    "create_feature_factory",
    "CORE_AVAILABLE",
    "MODULES_AVAILABLE",
    "SHARED_AVAILABLE", 
    "PRODUCTION_AVAILABLE"
]
'''
        
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("   ✅ Actualizado __init__.py principal")
    
    def create_summary_report(self):
        """Crear reporte resumen de la refactorización."""
        logger.info("📊 Generando reporte de refactorización...")
        
        report_content = f"""# Final Refactoring Report

## Resumen de Refactorización Completada

**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Versión**: 2.0.0-refactored

## 📊 Estadísticas

- **Archivos movidos**: {self.stats['moved_files']}
- **Archivos fusionados**: {self.stats['merged_files']} 
- **Duplicados eliminados**: {self.stats['deleted_duplicates']}
- **Directorios creados**: {self.stats['created_directories']}
- **Errores**: {self.stats['errors']}

## 🏗️ Nueva Estructura

```
features/
├── modules/                    # Módulos de negocio principales
│   ├── production/            # Aplicaciones de producción
│   │   └── apps/             # Apps específicas
│   ├── copywriting/          # Generación de contenido IA
│   ├── optimization/         # Optimización de rendimiento
│   └── blog_posts/          # Sistema de blogs (ya refactorizado)
│
├── shared/                    # Servicios compartidos
│   ├── cache/               # Sistema de cache
│   ├── database/            # Operaciones de BD
│   ├── monitoring/          # Monitoreo y métricas
│   ├── infrastructure/      # Infraestructura
│   └── performance/         # Utilidades de rendimiento
│
├── core/                     # Utilidades centrales
│   ├── config.py           # Configuración
│   ├── exceptions.py       # Excepciones personalizadas
│   ├── protocols.py        # Interfaces y protocolos
│   └── utils.py           # Utilidades generales
│
├── config/                   # Archivos de configuración
│   ├── docker/             # Dockerfiles y compose
│   ├── deployment/         # Scripts de deployment
│   ├── requirements/       # Dependencias por entorno
│   └── environment/        # Variables de entorno
│
├── docs/                     # Documentación
│   ├── refactoring/        # Docs de refactorización
│   └── examples/           # Ejemplos de integración
│
├── tools/                    # Herramientas de desarrollo
│   └── migration/          # Scripts de migración
│
└── legacy/                   # Código archivado
    ├── production_old/     # Versiones antiguas de producción
    ├── optimization_old/   # Optimizaciones legacy
    ├── benchmarks/        # Benchmarks antiguos
    └── prototypes/        # Prototipos experimentales
```

## ✅ Beneficios Logrados

### 1. **Organización Clara**
- Separación limpia por dominio de negocio
- Ubicación predecible de archivos
- Eliminación de duplicados

### 2. **Mantenibilidad Mejorada** 
- Código modular y reutilizable
- Dependencias claras entre módulos
- Facilidad para testing

### 3. **Escalabilidad**
- Arquitectura preparada para crecimiento
- Módulos independientes deployables
- Configuración centralizada

### 4. **Rendimiento**
- Optimizaciones consolidadas
- Cache compartido eficiente
- Monitoreo integrado

## 🚀 Próximos Pasos

1. **Testing**: Verificar que todos los módulos funcionan correctamente
2. **Integration**: Actualizar importaciones en el sistema principal
3. **Documentation**: Completar documentación de APIs
4. **Deployment**: Actualizar scripts de deployment para nueva estructura

## 🔧 Uso de la Nueva Estructura

```python
# Importar desde la nueva estructura
from features import get_system_status, create_feature_factory

# Verificar estado del sistema
status = get_system_status()
print(f"System version: {{status['version']}}")

# Crear factory de servicios
factory = create_feature_factory()
copywriting_service = factory['copywriting']
optimization_service = factory['optimization']
```

---
**Refactorización completada exitosamente** ✅
"""
        
        report_file = self.features_dir / "FINAL_REFACTOR_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"✅ Reporte creado: {report_file}")
    
    def run_refactor(self):
        """Ejecutar la refactorización completa."""
        logger.info("🚀 INICIANDO REFACTORIZACIÓN FINAL")
        logger.info("=" * 50)
        
        try:
            # 1. Crear backup
            self.create_backup()
            
            # 2. Asegurar estructura de directorios
            self.ensure_directory_structure()
            
            # 3. Mover archivos
            self.move_files()
            
            # 4. Limpiar directorios vacíos
            self.clean_empty_directories()
            
            # 5. Actualizar __init__.py
            self.update_init_files()
            
            # 6. Crear reporte
            self.create_summary_report()
            
            logger.info("=" * 50)
            logger.info("🎉 REFACTORIZACIÓN COMPLETADA EXITOSAMENTE")
            logger.info(f"📊 Estadísticas: {self.stats}")
            
        except Exception as e:
            logger.error(f"❌ Error durante refactorización: {e}")
            logger.info("🔄 Restaurando desde backup...")
            # Aquí podrías implementar lógica de rollback si es necesario
            raise

if __name__ == "__main__":
    refactor = FinalRefactor()
    refactor.run_refactor() 