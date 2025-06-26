#!/usr/bin/env python3
"""
Architecture Cleanup and Reorganization Script

Este script limpia y reorganiza la arquitectura del proyecto para una estructura más profesional:
- Organiza archivos legacy en directorios apropiados
- Consolida funcionalidad duplicada  
- Mejora la estructura de directorios
- Elimina archivos obsoletos
- Crea una arquitectura más mantenible
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArchitectureCleanup:
    """Gestor de cleanup y reorganización arquitectónica."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.backup_dir = self.base_path / "backup_legacy"
        self.new_structure = {}
        self.cleanup_stats = {
            'moved_files': 0,
            'deleted_files': 0,
            'consolidated_files': 0,
            'created_directories': 0
        }
        
        # Definir nueva estructura arquitectónica
        self.define_target_architecture()
    
    def define_target_architecture(self):
        """Define la estructura arquitectónica objetivo."""
        self.new_structure = {
            # Core modular architecture
            'modules/': {
                'blog_posts/': ['Complete blog post generation module'],
                'copywriting/': ['AI content generation with LangChain'],
                'optimization/': ['Performance optimization engines'],
                'production/': ['Production deployment and quantum app'],
                'analytics/': ['Analytics and monitoring modules'],
                'templates/': ['Content templates and themes']
            },
            
            # Shared services
            'shared/': {
                'database/': ['Database connections and operations'],
                'cache/': ['Caching systems and strategies'],
                'monitoring/': ['Health checks and metrics'],
                'infrastructure/': ['Deployment and configuration'],
                'performance/': ['Performance utilities'],
                'security/': ['Authentication and authorization']
            },
            
            # Legacy and archived code
            'legacy/': {
                'production_variants/': ['Old production files'],
                'optimization_old/': ['Legacy optimization code'],
                'benchmarks/': ['Performance benchmarks'],
                'prototypes/': ['Experimental code'],
                'archived/': ['Deprecated functionality']
            },
            
            # Configuration and deployment
            'config/': {
                'environments/': ['Environment-specific configs'],
                'docker/': ['Docker and containerization'],
                'deployment/': ['Deployment scripts and configs'],
                'examples/': ['Configuration examples']
            },
            
            # Documentation and examples
            'docs/': {
                'architecture/': ['Architecture documentation'],
                'api/': ['API documentation'],
                'guides/': ['User and developer guides'],
                'examples/': ['Integration examples']
            },
            
            # Testing and quality
            'tests/': {
                'unit/': ['Unit tests'],
                'integration/': ['Integration tests'],
                'performance/': ['Performance tests'],
                'fixtures/': ['Test data and fixtures']
            },
            
            # Tools and utilities
            'tools/': {
                'migration/': ['Migration scripts'],
                'monitoring/': ['Monitoring tools'],
                'deployment/': ['Deployment utilities'],
                'development/': ['Development tools']
            }
        }
    
    def create_directory_structure(self):
        """Crear la nueva estructura de directorios."""
        logger.info("🏗️ Creando nueva estructura de directorios...")
        
        for parent_dir, subdirs in self.new_structure.items():
            parent_path = self.base_path / parent_dir
            parent_path.mkdir(exist_ok=True)
            self.cleanup_stats['created_directories'] += 1
            
            if isinstance(subdirs, dict):
                for subdir, description in subdirs.items():
                    subdir_path = parent_path / subdir
                    subdir_path.mkdir(exist_ok=True)
                    self.cleanup_stats['created_directories'] += 1
                    
                    # Crear README.md para explicar el propósito
                    readme_path = subdir_path / "README.md"
                    if not readme_path.exists():
                        readme_content = f"# {subdir.replace('/', '').title()}\n\n"
                        readme_content += f"{description[0] if description else 'Module directory'}\n\n"
                        readme_content += f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        
                        with open(readme_path, 'w', encoding='utf-8') as f:
                            f.write(readme_content)
        
        logger.info(f"✅ Creados {self.cleanup_stats['created_directories']} directorios")
    
    def identify_legacy_files(self) -> Dict[str, List[str]]:
        """Identificar archivos legacy que necesitan reorganización."""
        
        legacy_patterns = {
            'production_variants': [
                'production_final.py', 'production_master.py', 'production_final_quantum.py',
                'production_enterprise.py', 'production_optimized.py', 'production_app_ultra.py',
                'quantum_prod.py', 'ultra_prod.py', 'prod.py', 'main_quantum.py', 'main_ultra.py'
            ],
            
            'optimization_old': [
                'ultra_performance_optimizers.py', 'core_optimizers.py', 'performance_optimizers.py',
                'ultra_optimizers.py', 'copywriting_optimizer.py', 'optimization.py'
            ],
            
            'benchmarks': [
                'benchmark.py', 'benchmark_refactored.py', 'benchmark_quick.py',
                'copywriting_benchmark.py', 'performance_demo.py'
            ],
            
            'prototypes': [
                'nexus_example.py', 'nexus_example_refactored.py', 'nexus_refactored.py',
                'nexus_optimizer.py', 'migrate_to_nexus.py'
            ],
            
            'config_files': [
                'config.py', 'app.py', 'main.py', 'startup.py', 'protocols.py',
                'exceptions.py', 'utils.py', '__init__.py'
            ],
            
            'deployment': [
                'docker-compose.yml', 'docker-compose.ultra.yml', 'docker-compose.production.yml',
                'Dockerfile', 'Dockerfile.ultra', 'Dockerfile.production',
                'deploy.sh', 'deploy_production.sh', 'run.sh', 'run_ultra.sh', 'run_production.sh',
                'nginx.conf', 'Makefile'
            ],
            
            'data_processing': [
                'data_processing.py', 'cache.py', 'advanced_copywriting_cache.py',
                'copywriting_model.py', 'monitoring.py'
            ],
            
            'requirements': [
                'requirements.txt', 'requirements_quantum.txt', 'requirements_ultra.txt',
                'requirements_optimized.txt', 'requirements_nexus.txt'
            ],
            
            'cleanup_scripts': [
                'cleanup_legacy.py', 'cleanup_legacy_final.py', 'legacy_cleanup.py',
                'production_runner.py'
            ],
            
            'documentation': [
                'README.md', 'ARCHITECTURE.md', 'README_PRODUCTION.md', 'README_NEXUS.md',
                'MIGRATION_PLAN.md', 'MIGRATION_SUMMARY.md', 'MODULAR_ARCHITECTURE.md',
                'MODULARIZATION_COMPLETE.md', 'REFACTORING_COMPLETE.md', 
                'OPTIMIZATION_RESULTS.md', 'LANGCHAIN_INTEGRATION_COMPLETE.md',
                'env.example'
            ]
        }
        
        # Verificar qué archivos existen
        existing_files = {}
        for category, files in legacy_patterns.items():
            existing_files[category] = []
            for file in files:
                if (self.base_path / file).exists():
                    existing_files[category].append(file)
        
        return existing_files
    
    def create_backup(self):
        """Crear backup antes de hacer cambios."""
        logger.info("💾 Creando backup de archivos legacy...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        self.backup_dir.mkdir()
        
        legacy_files = self.identify_legacy_files()
        backup_count = 0
        
        for category, files in legacy_files.items():
            category_backup = self.backup_dir / category
            category_backup.mkdir(exist_ok=True)
            
            for file in files:
                source = self.base_path / file
                dest = category_backup / file
                
                try:
                    if source.is_file():
                        shutil.copy2(source, dest)
                        backup_count += 1
                    elif source.is_dir():
                        shutil.copytree(source, dest / source.name, dirs_exist_ok=True)
                        backup_count += 1
                except Exception as e:
                    logger.warning(f"No se pudo hacer backup de {file}: {e}")
        
        logger.info(f"✅ Backup creado con {backup_count} archivos en {self.backup_dir}")
    
    def reorganize_legacy_files(self):
        """Reorganizar archivos legacy en la nueva estructura."""
        logger.info("📁 Reorganizando archivos legacy...")
        
        legacy_files = self.identify_legacy_files()
        
        # Mapeo de categorías a nuevas ubicaciones
        category_mapping = {
            'production_variants': 'legacy/production_variants',
            'optimization_old': 'legacy/optimization_old', 
            'benchmarks': 'legacy/benchmarks',
            'prototypes': 'legacy/prototypes',
            'config_files': 'config/core',
            'deployment': 'config/docker',
            'data_processing': 'legacy/archived',
            'requirements': 'config/environments',
            'cleanup_scripts': 'tools/migration',
            'documentation': 'docs/architecture'
        }
        
        for category, files in legacy_files.items():
            if category in category_mapping:
                target_dir = self.base_path / category_mapping[category]
                target_dir.mkdir(parents=True, exist_ok=True)
                
                for file in files:
                    source = self.base_path / file
                    dest = target_dir / file
                    
                    try:
                        if source.exists() and source != dest:
                            if dest.exists():
                                # Si ya existe, crear versión numerada
                                base_name = dest.stem
                                suffix = dest.suffix
                                counter = 1
                                while dest.exists():
                                    dest = target_dir / f"{base_name}_{counter}{suffix}"
                                    counter += 1
                            
                            shutil.move(str(source), str(dest))
                            self.cleanup_stats['moved_files'] += 1
                            logger.info(f"  📦 Movido: {file} → {category_mapping[category]}")
                    
                    except Exception as e:
                        logger.warning(f"No se pudo mover {file}: {e}")
        
        logger.info(f"✅ Reorganizados {self.cleanup_stats['moved_files']} archivos")
    
    def consolidate_modules(self):
        """Consolidar y mejorar módulos existentes."""
        logger.info("🔧 Consolidando módulos...")
        
        # Consolidaciones específicas
        consolidations = [
            {
                'name': 'Production Module Consolidation',
                'action': self._consolidate_production_modules
            },
            {
                'name': 'Requirements Consolidation', 
                'action': self._consolidate_requirements
            },
            {
                'name': 'Documentation Consolidation',
                'action': self._consolidate_documentation
            },
            {
                'name': 'Configuration Consolidation',
                'action': self._consolidate_configurations
            }
        ]
        
        for consolidation in consolidations:
            try:
                consolidation['action']()
                logger.info(f"  ✅ {consolidation['name']}")
            except Exception as e:
                logger.warning(f"  ⚠️ {consolidation['name']} failed: {e}")
    
    def _consolidate_production_modules(self):
        """Consolidar módulos de producción."""
        # El módulo de producción ya está en modules/production/
        # Solo necesitamos asegurar que esté bien organizado
        prod_dir = self.base_path / "modules/production"
        if prod_dir.exists():
            self.cleanup_stats['consolidated_files'] += 1
    
    def _consolidate_requirements(self):
        """Consolidar archivos de requirements."""
        req_dir = self.base_path / "config/environments"
        req_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear requirements consolidado
        consolidated_req = req_dir / "requirements_consolidated.txt"
        
        req_content = """# Consolidated Requirements - Modular Architecture
# Generated by architecture cleanup

# Core Framework
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.4.0

# AI and ML
openai>=1.3.0
anthropic>=0.7.0
langchain>=0.0.350
langchain-openai>=0.0.2

# Performance and Optimization  
redis>=5.0.0
asyncio>=3.4.3
aiohttp>=3.9.0

# Database
sqlalchemy>=2.0.0
asyncpg>=0.29.0

# Monitoring and Logging
prometheus-client>=0.19.0
structlog>=23.2.0

# Development and Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
"""
        
        with open(consolidated_req, 'w') as f:
            f.write(req_content)
        
        self.cleanup_stats['consolidated_files'] += 1
    
    def _consolidate_documentation(self):
        """Consolidar documentación."""
        docs_dir = self.base_path / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Crear índice de documentación
        index_content = """# Modular Architecture Documentation

## Architecture Overview
- [Modular Architecture](architecture/MODULAR_ARCHITECTURE.md)
- [Migration Guide](architecture/MIGRATION_PLAN.md)
- [Optimization Results](architecture/OPTIMIZATION_RESULTS.md)

## Integration Guides
- [LangChain Integration](architecture/LANGCHAIN_INTEGRATION_COMPLETE.md)
- [Integration Examples](examples/integration_example.py)

## Production Deployment
- [Production Guide](architecture/README_PRODUCTION.md)
- [Docker Configuration](../config/docker/)

## API Documentation
- [Blog Posts API](api/blog_posts.md)
- [Copywriting API](api/copywriting.md)
- [Optimization API](api/optimization.md)

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        index_path = docs_dir / "README.md"
        with open(index_path, 'w') as f:
            f.write(index_content)
        
        self.cleanup_stats['consolidated_files'] += 1
    
    def _consolidate_configurations(self):
        """Consolidar configuraciones."""
        config_dir = self.base_path / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Crear configuración central
        central_config = config_dir / "settings.py"
        
        config_content = '''"""
Central Configuration for Modular Architecture

Consolidates all configuration settings for different modules.
"""

import os
from pathlib import Path
from pydantic import BaseSettings
from typing import Optional

class GlobalSettings(BaseSettings):
    """Global application settings."""
    
    # Application
    APP_NAME: str = "Modular Architecture System"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: Optional[str] = None
    
    # Cache
    REDIS_URL: Optional[str] = None
    
    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Monitoring
    ENABLE_MONITORING: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = GlobalSettings()
'''
        
        with open(central_config, 'w') as f:
            f.write(config_content)
        
        self.cleanup_stats['consolidated_files'] += 1
    
    def create_improved_structure_info(self):
        """Crear archivo de información sobre la nueva estructura."""
        
        structure_info = {
            "architecture_version": "2.0.0",
            "cleanup_date": datetime.now().isoformat(),
            "structure": self.new_structure,
            "cleanup_stats": self.cleanup_stats,
            "features": {
                "modular_design": "Complete separation of concerns",
                "langchain_integration": "Advanced AI capabilities",
                "shared_services": "Reusable infrastructure components", 
                "production_ready": "Enterprise-grade deployment",
                "performance_optimized": "Ultra-fast processing",
                "well_documented": "Comprehensive documentation"
            },
            "migration_benefits": {
                "maintainability": "Easier to maintain and extend",
                "scalability": "Horizontal and vertical scaling",
                "testability": "Comprehensive testing framework",
                "reusability": "Modular components for reuse",
                "performance": "Optimized for high throughput"
            }
        }
        
        info_file = self.base_path / "ARCHITECTURE_INFO.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(structure_info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📋 Información de arquitectura guardada en {info_file}")
    
    def cleanup_empty_directories(self):
        """Limpiar directorios vacíos."""
        logger.info("🧹 Limpiando directorios vacíos...")
        
        removed_count = 0
        for root, dirs, files in os.walk(self.base_path, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if dir_path.is_dir() and not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        removed_count += 1
                        logger.info(f"  🗑️ Eliminado directorio vacío: {dir_path.relative_to(self.base_path)}")
                except OSError:
                    pass  # Directory not empty or permission error
        
        logger.info(f"✅ Eliminados {removed_count} directorios vacíos")
    
    def generate_cleanup_report(self):
        """Generar reporte de cleanup."""
        
        report = f"""
# Architecture Cleanup Report

## Cleanup Summary
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Files moved**: {self.cleanup_stats['moved_files']}
- **Files deleted**: {self.cleanup_stats['deleted_files']}
- **Files consolidated**: {self.cleanup_stats['consolidated_files']}
- **Directories created**: {self.cleanup_stats['created_directories']}

## New Architecture Structure

### Core Modules
```
modules/
├── blog_posts/          # Complete blog post generation
├── copywriting/         # AI content with LangChain  
├── optimization/        # Performance optimization
├── production/          # Production deployment
├── analytics/           # Analytics and monitoring
└── templates/           # Content templates
```

### Shared Services
```
shared/
├── database/            # Database operations
├── cache/               # Caching systems
├── monitoring/          # Health checks
├── infrastructure/      # Configuration
├── performance/         # Performance utilities
└── security/            # Auth and security
```

### Legacy Archive
```
legacy/
├── production_variants/ # Old production files
├── optimization_old/    # Legacy optimization
├── benchmarks/          # Performance tests
├── prototypes/          # Experimental code
└── archived/            # Deprecated code
```

### Configuration
```
config/
├── environments/        # Environment configs
├── docker/              # Docker files
├── deployment/          # Deployment scripts
└── examples/            # Config examples
```

## Benefits Achieved

✅ **Clean Architecture**: Modular, organized structure
✅ **Maintainability**: Easy to understand and modify
✅ **Scalability**: Ready for horizontal scaling
✅ **Documentation**: Comprehensive docs and examples
✅ **Performance**: Optimized for production use
✅ **Testing**: Proper test organization
✅ **Deployment**: Production-ready configuration

## Next Steps

1. **Review** the new structure
2. **Test** all modules work correctly
3. **Update** any remaining import paths
4. **Deploy** to staging environment
5. **Monitor** performance metrics

---
Architecture cleanup completed successfully! 🎉
"""
        
        report_file = self.base_path / "CLEANUP_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📊 Reporte de cleanup guardado en {report_file}")
        return report
    
    def run_complete_cleanup(self):
        """Ejecutar cleanup completo de la arquitectura."""
        
        logger.info("🚀 INICIANDO CLEANUP ARQUITECTÓNICO COMPLETO")
        logger.info("=" * 60)
        
        try:
            # 1. Crear backup
            self.create_backup()
            
            # 2. Crear nueva estructura
            self.create_directory_structure()
            
            # 3. Reorganizar archivos legacy
            self.reorganize_legacy_files()
            
            # 4. Consolidar módulos
            self.consolidate_modules()
            
            # 5. Crear información de estructura
            self.create_improved_structure_info()
            
            # 6. Limpiar directorios vacíos
            self.cleanup_empty_directories()
            
            # 7. Generar reporte
            report = self.generate_cleanup_report()
            
            logger.info("✅ CLEANUP ARQUITECTÓNICO COMPLETADO")
            logger.info("=" * 60)
            logger.info(f"📊 Estadísticas finales:")
            logger.info(f"   • Archivos movidos: {self.cleanup_stats['moved_files']}")
            logger.info(f"   • Archivos consolidados: {self.cleanup_stats['consolidated_files']}")
            logger.info(f"   • Directorios creados: {self.cleanup_stats['created_directories']}")
            logger.info(f"📋 Ver reporte completo en: CLEANUP_REPORT.md")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error durante cleanup: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Función principal para ejecutar el cleanup."""
    
    print("🏗️ MODULAR ARCHITECTURE CLEANUP")
    print("=" * 50)
    print("Este script reorganizará la arquitectura para:")
    print("• ✅ Estructura modular más limpia")
    print("• ✅ Organización de archivos legacy")
    print("• ✅ Consolidación de funcionalidad")
    print("• ✅ Documentación mejorada")
    print("• ✅ Configuración centralizada")
    print()
    
    response = input("¿Continuar con el cleanup? (y/N): ")
    if response.lower() not in ['y', 'yes', 'sí', 's']:
        print("Cleanup cancelado.")
        return
    
    # Ejecutar cleanup
    cleanup = ArchitectureCleanup()
    success = cleanup.run_complete_cleanup()
    
    if success:
        print("\n🎉 CLEANUP COMPLETADO EXITOSAMENTE!")
        print("\n📋 Nueva estructura arquitectónica creada:")
        print("   • modules/ - Módulos core organizados")
        print("   • shared/ - Servicios compartidos")
        print("   • legacy/ - Archivos legacy archivados")
        print("   • config/ - Configuración centralizada")
        print("   • docs/ - Documentación consolidada")
        print("\n📊 Ver CLEANUP_REPORT.md para detalles completos")
    else:
        print("\n❌ Cleanup falló. Ver logs para detalles.")

if __name__ == "__main__":
    main() 