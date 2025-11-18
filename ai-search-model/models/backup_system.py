"""
Backup System - Sistema de Backup y Recuperación
Sistema automatizado de backup, versionado y recuperación de datos
"""

import asyncio
import logging
import json
import shutil
import gzip
import tarfile
import zipfile
import hashlib
import os
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import schedule
import threading
import time
import uuid
from pathlib import Path
import aiofiles
import aiofiles.os

logger = logging.getLogger(__name__)

class BackupType(Enum):
    """Tipos de backup"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    DATABASE_ONLY = "database_only"
    FILES_ONLY = "files_only"

class BackupStatus(Enum):
    """Estados de backup"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RestoreStatus(Enum):
    """Estados de restauración"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class BackupConfig:
    """Configuración de backup"""
    id: str
    name: str
    description: str
    backup_type: BackupType
    source_paths: List[str]
    destination_path: str
    schedule_cron: str
    retention_days: int
    compression: bool = True
    encryption: bool = False
    encryption_key: Optional[str] = None
    enabled: bool = True
    created_at: str = None
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()

@dataclass
class BackupRecord:
    """Registro de backup"""
    id: str
    config_id: str
    backup_type: BackupType
    status: BackupStatus
    started_at: str
    completed_at: Optional[str] = None
    file_path: Optional[str] = None
    file_size: int = 0
    checksum: Optional[str] = None
    error_message: Optional[str] = None
    source_files_count: int = 0
    source_size: int = 0
    compression_ratio: float = 0.0
    
    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.now(timezone.utc).isoformat()

@dataclass
class RestoreRecord:
    """Registro de restauración"""
    id: str
    backup_id: str
    status: RestoreStatus
    started_at: str
    completed_at: Optional[str] = None
    target_path: Optional[str] = None
    restored_files_count: int = 0
    restored_size: int = 0
    error_message: Optional[str] = None

class BackupSystem:
    """
    Sistema de backup y recuperación automatizado
    """
    
    def __init__(self, base_backup_path: str = "./backups"):
        self.base_backup_path = Path(base_backup_path)
        self.base_backup_path.mkdir(exist_ok=True)
        
        # Almacenamiento
        self.backup_configs: Dict[str, BackupConfig] = {}
        self.backup_records: List[BackupRecord] = []
        self.restore_records: List[RestoreRecord] = []
        
        # Configuraciones
        self.config = {
            "max_concurrent_backups": 3,
            "default_retention_days": 30,
            "compression_level": 6,
            "chunk_size": 1024 * 1024,  # 1MB
            "verify_backups": True,
            "cleanup_old_backups": True
        }
        
        # Scheduler
        self.scheduler_thread = None
        self.is_running = False
        
        # Base de datos de metadatos
        self.metadata_db_path = self.base_backup_path / "backup_metadata.db"
        
        # Inicializar configuraciones por defecto
        self._initialize_default_configs()
    
    async def initialize(self):
        """Inicializar sistema de backup"""
        try:
            logger.info("Inicializando sistema de backup...")
            
            # Crear directorio base
            self.base_backup_path.mkdir(exist_ok=True)
            
            # Inicializar base de datos de metadatos
            await self._initialize_metadata_db()
            
            # Cargar configuraciones guardadas
            await self._load_backup_configs()
            
            # Cargar registros de backup
            await self._load_backup_records()
            
            # Iniciar scheduler
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_worker, daemon=True)
            self.scheduler_thread.start()
            
            logger.info("Sistema de backup inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando sistema de backup: {e}")
            raise
    
    async def _initialize_metadata_db(self):
        """Inicializar base de datos de metadatos"""
        try:
            conn = sqlite3.connect(str(self.metadata_db_path))
            cursor = conn.cursor()
            
            # Crear tablas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backup_configs (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    backup_type TEXT NOT NULL,
                    source_paths TEXT NOT NULL,
                    destination_path TEXT NOT NULL,
                    schedule_cron TEXT,
                    retention_days INTEGER,
                    compression BOOLEAN,
                    encryption BOOLEAN,
                    encryption_key TEXT,
                    enabled BOOLEAN,
                    created_at TEXT,
                    last_run TEXT,
                    next_run TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backup_records (
                    id TEXT PRIMARY KEY,
                    config_id TEXT NOT NULL,
                    backup_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    checksum TEXT,
                    error_message TEXT,
                    source_files_count INTEGER,
                    source_size INTEGER,
                    compression_ratio REAL,
                    FOREIGN KEY (config_id) REFERENCES backup_configs (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS restore_records (
                    id TEXT PRIMARY KEY,
                    backup_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    target_path TEXT,
                    restored_files_count INTEGER,
                    restored_size INTEGER,
                    error_message TEXT,
                    FOREIGN KEY (backup_id) REFERENCES backup_records (id)
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("Base de datos de metadatos inicializada")
            
        except Exception as e:
            logger.error(f"Error inicializando base de datos de metadatos: {e}")
            raise
    
    def _initialize_default_configs(self):
        """Inicializar configuraciones de backup por defecto"""
        try:
            # Backup completo del sistema
            full_backup_config = BackupConfig(
                id="full_system_backup",
                name="Full System Backup",
                description="Backup completo del sistema incluyendo base de datos y archivos",
                backup_type=BackupType.FULL,
                source_paths=[
                    "./ai_search.db",
                    "./vector_embeddings.db",
                    "./documents",
                    "./models",
                    "./logs"
                ],
                destination_path=str(self.base_backup_path / "full"),
                schedule_cron="0 2 * * *",  # Diario a las 2 AM
                retention_days=7
            )
            self.backup_configs[full_backup_config.id] = full_backup_config
            
            # Backup incremental de documentos
            incremental_backup_config = BackupConfig(
                id="documents_incremental",
                name="Documents Incremental Backup",
                description="Backup incremental de documentos",
                backup_type=BackupType.INCREMENTAL,
                source_paths=["./documents"],
                destination_path=str(self.base_backup_path / "incremental"),
                schedule_cron="0 */6 * * *",  # Cada 6 horas
                retention_days=14
            )
            self.backup_configs[incremental_backup_config.id] = incremental_backup_config
            
            # Backup de solo base de datos
            db_backup_config = BackupConfig(
                id="database_only",
                name="Database Only Backup",
                description="Backup solo de la base de datos",
                backup_type=BackupType.DATABASE_ONLY,
                source_paths=["./ai_search.db", "./vector_embeddings.db"],
                destination_path=str(self.base_backup_path / "database"),
                schedule_cron="0 */2 * * *",  # Cada 2 horas
                retention_days=30
            )
            self.backup_configs[db_backup_config.id] = db_backup_config
            
            logger.info("Configuraciones de backup por defecto inicializadas")
            
        except Exception as e:
            logger.error(f"Error inicializando configuraciones por defecto: {e}")
    
    async def _load_backup_configs(self):
        """Cargar configuraciones de backup desde la base de datos"""
        try:
            conn = sqlite3.connect(str(self.metadata_db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM backup_configs")
            rows = cursor.fetchall()
            
            for row in rows:
                config = BackupConfig(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    backup_type=BackupType(row[3]),
                    source_paths=json.loads(row[4]),
                    destination_path=row[5],
                    schedule_cron=row[6],
                    retention_days=row[7],
                    compression=bool(row[8]),
                    encryption=bool(row[9]),
                    encryption_key=row[10],
                    enabled=bool(row[11]),
                    created_at=row[12],
                    last_run=row[13],
                    next_run=row[14]
                )
                self.backup_configs[config.id] = config
            
            conn.close()
            logger.info(f"Cargadas {len(self.backup_configs)} configuraciones de backup")
            
        except Exception as e:
            logger.error(f"Error cargando configuraciones de backup: {e}")
    
    async def _load_backup_records(self):
        """Cargar registros de backup desde la base de datos"""
        try:
            conn = sqlite3.connect(str(self.metadata_db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM backup_records ORDER BY started_at DESC LIMIT 1000")
            rows = cursor.fetchall()
            
            for row in rows:
                record = BackupRecord(
                    id=row[0],
                    config_id=row[1],
                    backup_type=BackupType(row[2]),
                    status=BackupStatus(row[3]),
                    started_at=row[4],
                    completed_at=row[5],
                    file_path=row[6],
                    file_size=row[7],
                    checksum=row[8],
                    error_message=row[9],
                    source_files_count=row[10],
                    source_size=row[11],
                    compression_ratio=row[12]
                )
                self.backup_records.append(record)
            
            conn.close()
            logger.info(f"Cargados {len(self.backup_records)} registros de backup")
            
        except Exception as e:
            logger.error(f"Error cargando registros de backup: {e}")
    
    def _scheduler_worker(self):
        """Worker thread para el scheduler"""
        while self.is_running:
            try:
                # Verificar configuraciones programadas
                for config in self.backup_configs.values():
                    if not config.enabled:
                        continue
                    
                    if config.schedule_cron:
                        # Verificar si es hora de ejecutar
                        if self._should_run_backup(config):
                            # Ejecutar backup en un hilo separado
                            asyncio.run_coroutine_threadsafe(
                                self.run_backup(config.id),
                                asyncio.get_event_loop()
                            )
                
                time.sleep(60)  # Verificar cada minuto
                
            except Exception as e:
                logger.error(f"Error en scheduler worker: {e}")
                time.sleep(60)
    
    def _should_run_backup(self, config: BackupConfig) -> bool:
        """Verificar si un backup debe ejecutarse"""
        try:
            if not config.schedule_cron:
                return False
            
            # Implementación simple de verificación de cron
            # En producción, usaría una librería como croniter
            now = datetime.now()
            
            # Verificar si el último backup fue hace más de 24 horas
            if config.last_run:
                last_run = datetime.fromisoformat(config.last_run)
                if now - last_run < timedelta(hours=23):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verificando programación de backup: {e}")
            return False
    
    async def create_backup_config(self, name: str, description: str,
                                 backup_type: BackupType, source_paths: List[str],
                                 destination_path: str, schedule_cron: str = None,
                                 retention_days: int = None) -> BackupConfig:
        """Crear nueva configuración de backup"""
        try:
            config_id = str(uuid.uuid4())
            
            config = BackupConfig(
                id=config_id,
                name=name,
                description=description,
                backup_type=backup_type,
                source_paths=source_paths,
                destination_path=destination_path,
                schedule_cron=schedule_cron,
                retention_days=retention_days or self.config["default_retention_days"]
            )
            
            # Guardar en base de datos
            await self._save_backup_config(config)
            
            # Agregar a configuraciones activas
            self.backup_configs[config_id] = config
            
            logger.info(f"Configuración de backup creada: {name}")
            return config
            
        except Exception as e:
            logger.error(f"Error creando configuración de backup: {e}")
            raise
    
    async def _save_backup_config(self, config: BackupConfig):
        """Guardar configuración de backup en la base de datos"""
        try:
            conn = sqlite3.connect(str(self.metadata_db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO backup_configs 
                (id, name, description, backup_type, source_paths, destination_path,
                 schedule_cron, retention_days, compression, encryption, encryption_key,
                 enabled, created_at, last_run, next_run)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                config.id, config.name, config.description, config.backup_type.value,
                json.dumps(config.source_paths), config.destination_path,
                config.schedule_cron, config.retention_days, config.compression,
                config.encryption, config.encryption_key, config.enabled,
                config.created_at, config.last_run, config.next_run
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error guardando configuración de backup: {e}")
            raise
    
    async def run_backup(self, config_id: str) -> BackupRecord:
        """Ejecutar backup"""
        try:
            if config_id not in self.backup_configs:
                raise ValueError(f"Configuración de backup no encontrada: {config_id}")
            
            config = self.backup_configs[config_id]
            
            # Crear registro de backup
            backup_id = str(uuid.uuid4())
            backup_record = BackupRecord(
                id=backup_id,
                config_id=config_id,
                backup_type=config.backup_type,
                status=BackupStatus.RUNNING,
                started_at=datetime.now(timezone.utc).isoformat()
            )
            
            self.backup_records.append(backup_record)
            
            try:
                # Ejecutar backup según el tipo
                if config.backup_type == BackupType.FULL:
                    await self._run_full_backup(config, backup_record)
                elif config.backup_type == BackupType.INCREMENTAL:
                    await self._run_incremental_backup(config, backup_record)
                elif config.backup_type == BackupType.DATABASE_ONLY:
                    await self._run_database_backup(config, backup_record)
                elif config.backup_type == BackupType.FILES_ONLY:
                    await self._run_files_backup(config, backup_record)
                
                # Marcar como completado
                backup_record.status = BackupStatus.COMPLETED
                backup_record.completed_at = datetime.now(timezone.utc).isoformat()
                
                # Actualizar configuración
                config.last_run = backup_record.completed_at
                await self._save_backup_config(config)
                
                # Guardar registro
                await self._save_backup_record(backup_record)
                
                logger.info(f"Backup completado: {config.name}")
                
            except Exception as e:
                backup_record.status = BackupStatus.FAILED
                backup_record.error_message = str(e)
                backup_record.completed_at = datetime.now(timezone.utc).isoformat()
                await self._save_backup_record(backup_record)
                raise
            
            return backup_record
            
        except Exception as e:
            logger.error(f"Error ejecutando backup: {e}")
            raise
    
    async def _run_full_backup(self, config: BackupConfig, backup_record: BackupRecord):
        """Ejecutar backup completo"""
        try:
            # Crear directorio de destino
            backup_dir = Path(config.destination_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear archivo de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"full_backup_{timestamp}.tar.gz"
            backup_path = backup_dir / backup_filename
            
            # Crear archivo comprimido
            with tarfile.open(backup_path, "w:gz") as tar:
                total_files = 0
                total_size = 0
                
                for source_path in config.source_paths:
                    source = Path(source_path)
                    if source.exists():
                        if source.is_file():
                            tar.add(source, arcname=source.name)
                            total_files += 1
                            total_size += source.stat().st_size
                        elif source.is_dir():
                            for file_path in source.rglob("*"):
                                if file_path.is_file():
                                    tar.add(file_path, arcname=file_path.relative_to(source.parent))
                                    total_files += 1
                                    total_size += file_path.stat().st_size
            
            # Calcular checksum
            checksum = await self._calculate_checksum(backup_path)
            
            # Actualizar registro
            backup_record.file_path = str(backup_path)
            backup_record.file_size = backup_path.stat().st_size
            backup_record.checksum = checksum
            backup_record.source_files_count = total_files
            backup_record.source_size = total_size
            backup_record.compression_ratio = total_size / backup_record.file_size if backup_record.file_size > 0 else 0
            
        except Exception as e:
            logger.error(f"Error en backup completo: {e}")
            raise
    
    async def _run_incremental_backup(self, config: BackupConfig, backup_record: BackupRecord):
        """Ejecutar backup incremental"""
        try:
            # Obtener último backup para comparar
            last_backup = None
            for record in reversed(self.backup_records):
                if (record.config_id == config.id and 
                    record.status == BackupStatus.COMPLETED):
                    last_backup = record
                    break
            
            # Crear directorio de destino
            backup_dir = Path(config.destination_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear archivo de backup incremental
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"incremental_backup_{timestamp}.tar.gz"
            backup_path = backup_dir / backup_filename
            
            # Determinar archivos modificados desde el último backup
            modified_files = []
            if last_backup:
                last_backup_time = datetime.fromisoformat(last_backup.started_at)
                for source_path in config.source_paths:
                    source = Path(source_path)
                    if source.exists():
                        for file_path in source.rglob("*"):
                            if file_path.is_file():
                                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                                if file_mtime > last_backup_time:
                                    modified_files.append(file_path)
            else:
                # Si no hay backup anterior, incluir todos los archivos
                for source_path in config.source_paths:
                    source = Path(source_path)
                    if source.exists():
                        for file_path in source.rglob("*"):
                            if file_path.is_file():
                                modified_files.append(file_path)
            
            # Crear archivo comprimido con archivos modificados
            with tarfile.open(backup_path, "w:gz") as tar:
                total_files = 0
                total_size = 0
                
                for file_path in modified_files:
                    tar.add(file_path, arcname=file_path.relative_to(Path.cwd()))
                    total_files += 1
                    total_size += file_path.stat().st_size
            
            # Calcular checksum
            checksum = await self._calculate_checksum(backup_path)
            
            # Actualizar registro
            backup_record.file_path = str(backup_path)
            backup_record.file_size = backup_path.stat().st_size
            backup_record.checksum = checksum
            backup_record.source_files_count = total_files
            backup_record.source_size = total_size
            backup_record.compression_ratio = total_size / backup_record.file_size if backup_record.file_size > 0 else 0
            
        except Exception as e:
            logger.error(f"Error en backup incremental: {e}")
            raise
    
    async def _run_database_backup(self, config: BackupConfig, backup_record: BackupRecord):
        """Ejecutar backup de solo base de datos"""
        try:
            # Crear directorio de destino
            backup_dir = Path(config.destination_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear archivo de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"database_backup_{timestamp}.sql.gz"
            backup_path = backup_dir / backup_filename
            
            # Hacer backup de cada base de datos
            total_files = 0
            total_size = 0
            
            with gzip.open(backup_path, 'wt') as gz_file:
                for source_path in config.source_paths:
                    source = Path(source_path)
                    if source.exists() and source.suffix == '.db':
                        # Hacer dump de la base de datos SQLite
                        conn = sqlite3.connect(str(source))
                        for line in conn.iterdump():
                            gz_file.write(line + '\n')
                        conn.close()
                        
                        total_files += 1
                        total_size += source.stat().st_size
            
            # Calcular checksum
            checksum = await self._calculate_checksum(backup_path)
            
            # Actualizar registro
            backup_record.file_path = str(backup_path)
            backup_record.file_size = backup_path.stat().st_size
            backup_record.checksum = checksum
            backup_record.source_files_count = total_files
            backup_record.source_size = total_size
            backup_record.compression_ratio = total_size / backup_record.file_size if backup_record.file_size > 0 else 0
            
        except Exception as e:
            logger.error(f"Error en backup de base de datos: {e}")
            raise
    
    async def _run_files_backup(self, config: BackupConfig, backup_record: BackupRecord):
        """Ejecutar backup de solo archivos"""
        try:
            # Similar a backup completo pero solo archivos
            await self._run_full_backup(config, backup_record)
            
        except Exception as e:
            logger.error(f"Error en backup de archivos: {e}")
            raise
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calcular checksum SHA256 de un archivo"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculando checksum: {e}")
            return ""
    
    async def _save_backup_record(self, backup_record: BackupRecord):
        """Guardar registro de backup en la base de datos"""
        try:
            conn = sqlite3.connect(str(self.metadata_db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO backup_records 
                (id, config_id, backup_type, status, started_at, completed_at,
                 file_path, file_size, checksum, error_message, source_files_count,
                 source_size, compression_ratio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                backup_record.id, backup_record.config_id, backup_record.backup_type.value,
                backup_record.status.value, backup_record.started_at, backup_record.completed_at,
                backup_record.file_path, backup_record.file_size, backup_record.checksum,
                backup_record.error_message, backup_record.source_files_count,
                backup_record.source_size, backup_record.compression_ratio
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error guardando registro de backup: {e}")
    
    async def restore_backup(self, backup_id: str, target_path: str) -> RestoreRecord:
        """Restaurar backup"""
        try:
            # Buscar registro de backup
            backup_record = None
            for record in self.backup_records:
                if record.id == backup_id:
                    backup_record = record
                    break
            
            if not backup_record:
                raise ValueError(f"Backup no encontrado: {backup_id}")
            
            if backup_record.status != BackupStatus.COMPLETED:
                raise ValueError(f"Backup no completado: {backup_record.status}")
            
            # Crear registro de restauración
            restore_id = str(uuid.uuid4())
            restore_record = RestoreRecord(
                id=restore_id,
                backup_id=backup_id,
                status=RestoreStatus.RUNNING,
                started_at=datetime.now(timezone.utc).isoformat(),
                target_path=target_path
            )
            
            self.restore_records.append(restore_record)
            
            try:
                # Restaurar archivos
                await self._restore_files(backup_record, target_path, restore_record)
                
                # Marcar como completado
                restore_record.status = RestoreStatus.COMPLETED
                restore_record.completed_at = datetime.now(timezone.utc).isoformat()
                
                logger.info(f"Restauración completada: {backup_id}")
                
            except Exception as e:
                restore_record.status = RestoreStatus.FAILED
                restore_record.error_message = str(e)
                restore_record.completed_at = datetime.now(timezone.utc).isoformat()
                raise
            
            return restore_record
            
        except Exception as e:
            logger.error(f"Error restaurando backup: {e}")
            raise
    
    async def _restore_files(self, backup_record: BackupRecord, target_path: str, 
                           restore_record: RestoreRecord):
        """Restaurar archivos desde backup"""
        try:
            backup_path = Path(backup_record.file_path)
            target = Path(target_path)
            
            if not backup_path.exists():
                raise ValueError(f"Archivo de backup no encontrado: {backup_path}")
            
            # Crear directorio de destino
            target.mkdir(parents=True, exist_ok=True)
            
            # Restaurar según el tipo de archivo
            if backup_path.suffix == '.gz' and 'tar' in backup_path.name:
                # Archivo tar.gz
                with tarfile.open(backup_path, "r:gz") as tar:
                    tar.extractall(target)
                    restore_record.restored_files_count = len(tar.getnames())
            elif backup_path.suffix == '.gz' and 'sql' in backup_path.name:
                # Archivo SQL comprimido
                with gzip.open(backup_path, 'rt') as gz_file:
                    sql_content = gz_file.read()
                
                # Ejecutar SQL en la base de datos de destino
                db_path = target / "restored_database.db"
                conn = sqlite3.connect(str(db_path))
                conn.executescript(sql_content)
                conn.close()
                
                restore_record.restored_files_count = 1
            
            # Calcular tamaño restaurado
            restore_record.restored_size = sum(
                f.stat().st_size for f in target.rglob("*") if f.is_file()
            )
            
        except Exception as e:
            logger.error(f"Error restaurando archivos: {e}")
            raise
    
    async def cleanup_old_backups(self):
        """Limpiar backups antiguos"""
        try:
            current_time = datetime.now(timezone.utc)
            cleaned_count = 0
            
            for config in self.backup_configs.values():
                cutoff_time = current_time - timedelta(days=config.retention_days)
                
                # Buscar backups antiguos para esta configuración
                old_backups = []
                for record in self.backup_records:
                    if (record.config_id == config.id and 
                        record.status == BackupStatus.COMPLETED and
                        datetime.fromisoformat(record.started_at) < cutoff_time):
                        old_backups.append(record)
                
                # Eliminar archivos y registros
                for backup in old_backups:
                    if backup.file_path and Path(backup.file_path).exists():
                        Path(backup.file_path).unlink()
                    
                    self.backup_records.remove(backup)
                    cleaned_count += 1
            
            logger.info(f"Limpiados {cleaned_count} backups antiguos")
            
        except Exception as e:
            logger.error(f"Error limpiando backups antiguos: {e}")
    
    async def get_backup_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema de backup"""
        try:
            total_configs = len(self.backup_configs)
            active_configs = len([c for c in self.backup_configs.values() if c.enabled])
            total_backups = len(self.backup_records)
            successful_backups = len([b for b in self.backup_records if b.status == BackupStatus.COMPLETED])
            failed_backups = len([b for b in self.backup_records if b.status == BackupStatus.FAILED])
            
            # Calcular tamaño total de backups
            total_backup_size = sum(b.file_size for b in self.backup_records if b.file_size)
            
            # Últimos backups
            recent_backups = sorted(
                [b for b in self.backup_records if b.status == BackupStatus.COMPLETED],
                key=lambda x: x.started_at,
                reverse=True
            )[:5]
            
            return {
                "total_configs": total_configs,
                "active_configs": active_configs,
                "total_backups": total_backups,
                "successful_backups": successful_backups,
                "failed_backups": failed_backups,
                "total_backup_size": total_backup_size,
                "recent_backups": [asdict(b) for b in recent_backups],
                "is_running": self.is_running,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de backup: {e}")
            return {}
    
    async def shutdown(self):
        """Cerrar sistema de backup"""
        try:
            self.is_running = False
            
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=5)
            
            logger.info("Sistema de backup cerrado")
            
        except Exception as e:
            logger.error(f"Error cerrando sistema de backup: {e}")


























