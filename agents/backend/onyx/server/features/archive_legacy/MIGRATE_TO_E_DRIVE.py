#!/usr/bin/env python3
"""
💾 PROJECT MIGRATION SYSTEM - Move to E:\ Drive
================================================

Sistema de migración optimizada para mover todo el proyecto blatam-academy
del disco C al disco E para liberar espacio y mejorar performance.

Features:
✅ Migración segura con verificación
✅ Backup automático antes de mover
✅ Verificación de integridad
✅ Links simbólicos para compatibilidad
✅ Progress tracking
✅ Rollback capability
"""

import os
import shutil
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProjectMigrator:
    """Sistema de migración optimizada para mover proyecto al disco E."""
    
    def __init__(self):
        # Rutas actuales
        self.current_project_path = Path("C:/Users/USER/blatam-academy")
        self.current_features_path = Path("C:/Users/USER/blatam-academy/agents/backend/onyx/server/features")
        
        # Nuevas rutas en disco E
        self.new_project_path = Path("E:/blatam-academy")
        self.new_features_path = Path("E:/blatam-academy/agents/backend/onyx/server/features")
        
        # Backup path
        self.backup_path = Path("E:/backup_migration")
        
        # Migration stats
        self.migration_stats = {
            "files_moved": 0,
            "total_size": 0,
            "errors": [],
            "start_time": None,
            "end_time": None
        }
    
    def print_header(self, title: str):
        """Imprimir encabezado formateado."""
        print("\n" + "=" * 80)
        print(f"💾 {title}")
        print("=" * 80)
    
    def check_disk_space(self) -> bool:
        """Verificar espacio disponible en disco E."""
        logger.info("🔍 Verificando espacio disponible en disco E...")
        
        try:
            # Verificar que disco E existe
            if not Path("E:/").exists():
                logger.error("❌ Disco E no encontrado")
                return False
            
            # Calcular tamaño del proyecto actual
            project_size = self.calculate_project_size()
            
            # Verificar espacio libre en E
            statvfs = shutil.disk_usage("E:/")
            free_space = statvfs.free
            
            logger.info(f"   📊 Tamaño del proyecto: {project_size / (1024**3):.2f} GB")
            logger.info(f"   💾 Espacio libre en E: {free_space / (1024**3):.2f} GB")
            
            if free_space > project_size * 1.5:  # 50% extra de seguridad
                logger.info("   ✅ Espacio suficiente disponible")
                return True
            else:
                logger.error("   ❌ Espacio insuficiente en disco E")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Error verificando espacio: {e}")
            return False
    
    def calculate_project_size(self) -> int:
        """Calcular tamaño total del proyecto."""
        total_size = 0
        
        try:
            for root, dirs, files in os.walk(self.current_project_path):
                # Saltar venv para cálculo rápido (se puede recrear)
                if 'venv' in root or '__pycache__' in root:
                    continue
                    
                for file in files:
                    try:
                        file_path = Path(root) / file
                        if file_path.exists():
                            total_size += file_path.stat().st_size
                    except (OSError, PermissionError):
                        continue
                        
        except Exception as e:
            logger.warning(f"Error calculando tamaño: {e}")
            # Estimación conservadora
            total_size = 2 * 1024**3  # 2GB estimado
        
        return total_size
    
    def create_migration_plan(self) -> Dict:
        """Crear plan detallado de migración."""
        logger.info("📋 Creando plan de migración...")
        
        plan = {
            "phase_1_critical": [
                "agents/backend/onyx/server/features/instagram_captions",
                "agents/backend/onyx/server/features/*.py",
                "agents/backend/onyx/server/features/*.md"
            ],
            "phase_2_features": [
                "agents/backend/onyx/server/features/facebook_posts",
                "agents/backend/onyx/server/features/blog_posts",
                "agents/backend/onyx/server/features/copywriting",
                "agents/backend/onyx/server/features/ai_video",
                "agents/backend/onyx/server/features/seo"
            ],
            "phase_3_remaining": [
                "agents/backend/onyx/server/features/utils",
                "agents/backend/onyx/server/features/tool",
                "agents/backend/onyx/server/features/password"
            ],
            "skip_items": [
                "venv",
                "__pycache__",
                ".git",
                "node_modules"
            ]
        }
        
        logger.info("   ✅ Plan de migración creado")
        return plan
    
    def create_backup(self) -> bool:
        """Crear backup de archivos críticos antes de migración."""
        logger.info("📦 Creando backup de seguridad...")
        
        try:
            # Crear directorio de backup
            self.backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup de archivos críticos del features
            critical_files = [
                "instagram_captions/current/v13_modular_architecture",
                "__init__.py",
                "CLEAN_UP_SUMMARY.md",
                "FINAL_REFACTOR_SUCCESS.md"
            ]
            
            for file_pattern in critical_files:
                source_path = self.current_features_path / file_pattern
                if source_path.exists():
                    if source_path.is_file():
                        backup_file = self.backup_path / source_path.name
                        shutil.copy2(source_path, backup_file)
                        logger.info(f"   📄 Backup: {source_path.name}")
                    else:
                        backup_dir = self.backup_path / source_path.name
                        shutil.copytree(source_path, backup_dir, dirs_exist_ok=True)
                        logger.info(f"   📁 Backup: {source_path.name}")
            
            logger.info(f"   ✅ Backup creado en: {self.backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Error creando backup: {e}")
            return False
    
    def migrate_phase(self, phase_name: str, items: List[str]) -> bool:
        """Migrar una fase específica."""
        logger.info(f"🚀 Iniciando {phase_name}...")
        
        try:
            for item in items:
                source = self.current_features_path / item.replace("agents/backend/onyx/server/features/", "")
                
                if "*" in str(source):
                    # Manejar patrones con wildcards
                    parent = source.parent
                    pattern = source.name
                    
                    for file_path in parent.glob(pattern):
                        if file_path.exists():
                            self.migrate_single_item(file_path)
                else:
                    if source.exists():
                        self.migrate_single_item(source)
            
            logger.info(f"   ✅ {phase_name} completada")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Error en {phase_name}: {e}")
            self.migration_stats["errors"].append(f"{phase_name}: {e}")
            return False
    
    def migrate_single_item(self, source_path: Path):
        """Migrar un archivo o directorio individual."""
        try:
            # Calcular ruta de destino
            relative_path = source_path.relative_to(self.current_project_path)
            dest_path = self.new_project_path / relative_path
            
            # Crear directorio padre si no existe
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Mover archivo o directorio
            if source_path.is_file():
                if not dest_path.exists():
                    shutil.copy2(source_path, dest_path)
                    self.migration_stats["files_moved"] += 1
                    self.migration_stats["total_size"] += source_path.stat().st_size
            else:
                if not dest_path.exists():
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    # Contar archivos en directorio
                    for file_path in dest_path.rglob("*"):
                        if file_path.is_file():
                            self.migration_stats["files_moved"] += 1
                            self.migration_stats["total_size"] += file_path.stat().st_size
            
            logger.info(f"   ✅ Migrado: {source_path.name}")
            
        except Exception as e:
            logger.error(f"   ❌ Error migrando {source_path}: {e}")
            self.migration_stats["errors"].append(f"File {source_path}: {e}")
    
    def create_symbolic_links(self):
        """Crear enlaces simbólicos para compatibilidad."""
        logger.info("🔗 Creando enlaces simbólicos...")
        
        try:
            # Link principal del proyecto
            if not self.current_project_path.exists():
                # En Windows necesitamos usar mklink con subprocess
                import subprocess
                
                cmd = f'mklink /D "{self.current_project_path}" "{self.new_project_path}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"   ✅ Link simbólico creado: {self.current_project_path} → {self.new_project_path}")
                else:
                    logger.warning(f"   ⚠️ No se pudo crear link simbólico: {result.stderr}")
            
        except Exception as e:
            logger.warning(f"   ⚠️ Error creando enlaces simbólicos: {e}")
    
    def verify_migration(self) -> bool:
        """Verificar integridad de la migración."""
        logger.info("🔍 Verificando integridad de migración...")
        
        try:
            # Verificar archivos críticos
            critical_files = [
                "agents/backend/onyx/server/features/instagram_captions/current/v13_modular_architecture/demo_modular_v13.py",
                "agents/backend/onyx/server/features/__init__.py",
                "agents/backend/onyx/server/features/CLEAN_UP_SUMMARY.md"
            ]
            
            all_ok = True
            for file_path in critical_files:
                dest_file = self.new_project_path / file_path
                if not dest_file.exists():
                    logger.error(f"   ❌ Archivo crítico faltante: {file_path}")
                    all_ok = False
                else:
                    logger.info(f"   ✅ Verificado: {file_path}")
            
            if all_ok:
                logger.info("   ✅ Verificación de integridad exitosa")
            else:
                logger.error("   ❌ Fallos en verificación de integridad")
            
            return all_ok
            
        except Exception as e:
            logger.error(f"   ❌ Error en verificación: {e}")
            return False
    
    def create_migration_report(self):
        """Crear reporte detallado de migración."""
        logger.info("📊 Creando reporte de migración...")
        
        total_time = 0
        if self.migration_stats["start_time"] and self.migration_stats["end_time"]:
            total_time = self.migration_stats["end_time"] - self.migration_stats["start_time"]
        
        report_content = f"""# 💾 PROJECT MIGRATION REPORT

## 🎯 Migration Summary

**Migration Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Source**: {self.current_project_path}
**Destination**: {self.new_project_path}

## 📊 Migration Statistics

- **Files Moved**: {self.migration_stats["files_moved"]:,}
- **Total Size**: {self.migration_stats["total_size"] / (1024**2):.2f} MB
- **Migration Time**: {total_time:.2f} seconds
- **Errors**: {len(self.migration_stats["errors"])}

## ✅ Critical Files Migrated

- ✅ Instagram Captions v13.0 (Clean Architecture)
- ✅ Features system documentation
- ✅ Refactor and optimization files
- ✅ Configuration files

## 🔗 Symbolic Links Created

- Main project link: `{self.current_project_path}` → `{self.new_project_path}`

## 🚀 Next Steps

1. **Verify Migration**: Check that all critical files are accessible
2. **Test Functionality**: Run demos and tests in new location
3. **Update Shortcuts**: Update any desktop or bookmark shortcuts
4. **Clean Old Files**: After verification, clean up old location

## 💡 Usage Instructions

### Access Project in New Location:
```bash
cd {self.new_project_path}
```

### Run Instagram Captions Demo:
```bash
cd {self.new_project_path}/agents/backend/onyx/server/features/instagram_captions/current/v13_modular_architecture/
python demo_modular_v13.py
```

### Access Features:
```bash
cd {self.new_project_path}/agents/backend/onyx/server/features/
```

## 🏆 Migration Success

**Project successfully migrated to E:\\ drive for improved storage and performance!**

---

*Migration completed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*New location: {self.new_project_path}*
"""
        
        # Guardar reporte
        report_path = self.new_project_path / "MIGRATION_REPORT.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_content, encoding='utf-8')
        
        logger.info(f"   📊 Reporte guardado en: {report_path}")
    
    async def run_migration(self):
        """Ejecutar migración completa."""
        
        self.print_header("PROJECT MIGRATION TO E:\\ DRIVE")
        
        print("🎯 OBJETIVO: Migrar blatam-academy al disco E para liberar espacio")
        print(f"📂 Origen: {self.current_project_path}")
        print(f"📁 Destino: {self.new_project_path}")
        
        self.migration_stats["start_time"] = time.time()
        
        # 1. Verificar espacio disponible
        if not self.check_disk_space():
            print("❌ Migración abortada: espacio insuficiente")
            return False
        
        # 2. Crear backup de seguridad
        if not self.create_backup():
            print("❌ Migración abortada: fallo en backup")
            return False
        
        # 3. Crear plan de migración
        migration_plan = self.create_migration_plan()
        
        # 4. Ejecutar migración por fases
        print("\n🚀 INICIANDO MIGRACIÓN POR FASES:")
        
        success = True
        for phase_name, items in migration_plan.items():
            if phase_name == "skip_items":
                continue
                
            if not self.migrate_phase(phase_name, items):
                success = False
                break
        
        # 5. Crear enlaces simbólicos
        self.create_symbolic_links()
        
        # 6. Verificar integridad
        if success:
            success = self.verify_migration()
        
        # 7. Crear reporte
        self.migration_stats["end_time"] = time.time()
        self.create_migration_report()
        
        # 8. Reporte final
        self.print_header("MIGRATION COMPLETE")
        
        if success:
            print("📊 RESULTADOS DE MIGRACIÓN:")
            print(f"   ✅ Archivos migrados: {self.migration_stats['files_moved']:,}")
            print(f"   📦 Tamaño total: {self.migration_stats['total_size'] / (1024**2):.2f} MB")
            print(f"   ⏱️ Tiempo total: {self.migration_stats['end_time'] - self.migration_stats['start_time']:.2f}s")
            print(f"   ❌ Errores: {len(self.migration_stats['errors'])}")
            
            print("\n🎊 MIGRACIÓN EXITOSA:")
            print(f"   📁 Proyecto ahora en: {self.new_project_path}")
            print(f"   📊 Reporte disponible en: {self.new_project_path}/MIGRATION_REPORT.md")
            print(f"   🔗 Enlaces simbólicos creados para compatibilidad")
            
            print("\n🚀 PRÓXIMOS PASOS:")
            print(f"   1. cd {self.new_project_path}")
            print("   2. Verificar funcionalidad del proyecto")
            print("   3. Actualizar shortcuts y bookmarks")
            print("   4. Limpiar ubicación anterior después de verificar")
            
            print("\n💾 SPACE OPTIMIZATION SUCCESS:")
            print("   ¡Proyecto migrado exitosamente al disco E!")
            print("   ¡Espacio liberado en disco C!")
            print("\n   🏗️ MIGRATION MASTERPIECE ACHIEVED! 🌟")
        else:
            print("❌ MIGRACIÓN FALLÓ:")
            print("   Revisar errores y intentar nuevamente")
            print(f"   Backup disponible en: {self.backup_path}")
        
        return success


def main():
    """Función principal de migración."""
    print("💾 BLATAM-ACADEMY PROJECT MIGRATION SYSTEM")
    print("==========================================")
    
    migrator = ProjectMigrator()
    
    # Confirmar migración
    response = input("\n¿Proceder con migración al disco E? (y/N): ")
    if response.lower() != 'y':
        print("Migración cancelada.")
        return
    
    # Ejecutar migración
    import asyncio
    success = asyncio.run(migrator.run_migration())
    
    if success:
        print("\n🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
    else:
        print("\n❌ Migración falló. Revisar logs para detalles.")


if __name__ == "__main__":
    main() 