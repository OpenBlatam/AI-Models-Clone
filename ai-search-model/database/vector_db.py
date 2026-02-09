"""
Vector Database - Base de datos vectorial
Maneja el almacenamiento y recuperación de documentos y embeddings
"""

import asyncio
import logging
import json
import sqlite3
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os
import pickle
import hashlib

logger = logging.getLogger(__name__)

class VectorDatabase:
    """
    Base de datos vectorial para almacenar documentos y sus embeddings
    Utiliza SQLite para metadatos y archivos pickle para embeddings
    """
    
    def __init__(self, db_path: str = "vector_database.db", embeddings_path: str = "embeddings.pkl"):
        self.db_path = db_path
        self.embeddings_path = embeddings_path
        self.connection = None
        self.embeddings_cache = {}
        self.is_initialized = False
        
    async def initialize(self):
        """Inicializar la base de datos"""
        try:
            logger.info("Inicializando Vector Database...")
            
            # Crear conexión a SQLite
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            # Crear tablas
            await self._create_tables()
            
            # Cargar embeddings existentes
            await self._load_embeddings()
            
            self.is_initialized = True
            logger.info("Vector Database inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error al inicializar Vector Database: {e}")
            raise
    
    async def _create_tables(self):
        """Crear tablas de la base de datos"""
        try:
            cursor = self.connection.cursor()
            
            # Tabla de documentos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    original_content TEXT,
                    document_type TEXT DEFAULT 'text',
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    content_length INTEGER,
                    word_count INTEGER
                )
            """)
            
            # Tabla de embeddings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    document_id TEXT PRIMARY KEY,
                    embedding_hash TEXT NOT NULL,
                    embedding_dimension INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (document_id)
                )
            """)
            
            # Tabla de índices
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_index (
                    document_id TEXT,
                    keyword TEXT,
                    frequency INTEGER,
                    position INTEGER,
                    FOREIGN KEY (document_id) REFERENCES documents (document_id)
                )
            """)
            
            # Crear índices para mejorar rendimiento
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_title ON documents (title)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_type ON documents (document_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_created ON documents (created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_keyword ON search_index (keyword)")
            
            self.connection.commit()
            logger.info("Tablas de base de datos creadas correctamente")
            
        except Exception as e:
            logger.error(f"Error al crear tablas: {e}")
            raise
    
    async def _load_embeddings(self):
        """Cargar embeddings desde archivo"""
        try:
            if os.path.exists(self.embeddings_path):
                with open(self.embeddings_path, 'rb') as f:
                    self.embeddings_cache = pickle.load(f)
                logger.info(f"Embeddings cargados: {len(self.embeddings_cache)} documentos")
            else:
                self.embeddings_cache = {}
                logger.info("No se encontraron embeddings existentes")
                
        except Exception as e:
            logger.error(f"Error al cargar embeddings: {e}")
            self.embeddings_cache = {}
    
    async def _save_embeddings(self):
        """Guardar embeddings en archivo"""
        try:
            with open(self.embeddings_path, 'wb') as f:
                pickle.dump(self.embeddings_cache, f)
            logger.info("Embeddings guardados correctamente")
            
        except Exception as e:
            logger.error(f"Error al guardar embeddings: {e}")
    
    async def add_document(self, document: Dict[str, Any]) -> str:
        """Agregar documento a la base de datos"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            document_id = document["document_id"]
            logger.info(f"Agregando documento: {document_id}")
            
            cursor = self.connection.cursor()
            
            # Insertar documento
            cursor.execute("""
                INSERT OR REPLACE INTO documents 
                (document_id, title, content, original_content, document_type, 
                 metadata, content_length, word_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document_id,
                document["title"],
                document["content"],
                document.get("original_content", document["content"]),
                document.get("document_type", "text"),
                json.dumps(document.get("metadata", {})),
                document.get("content_length", len(document["content"])),
                document.get("word_count", len(document["content"].split()))
            ))
            
            # Actualizar timestamp
            cursor.execute("""
                UPDATE documents 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE document_id = ?
            """, (document_id,))
            
            self.connection.commit()
            
            logger.info(f"Documento agregado exitosamente: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Error al agregar documento: {e}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Obtener documento por ID"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM documents WHERE document_id = ?", (document_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "document_id": row["document_id"],
                    "title": row["title"],
                    "content": row["content"],
                    "original_content": row["original_content"],
                    "document_type": row["document_type"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "content_length": row["content_length"],
                    "word_count": row["word_count"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error al obtener documento: {e}")
            return None
    
    async def delete_document(self, document_id: str) -> bool:
        """Eliminar documento de la base de datos"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            cursor = self.connection.cursor()
            
            # Eliminar de todas las tablas
            cursor.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))
            cursor.execute("DELETE FROM embeddings WHERE document_id = ?", (document_id,))
            cursor.execute("DELETE FROM search_index WHERE document_id = ?", (document_id,))
            
            # Eliminar de cache de embeddings
            if document_id in self.embeddings_cache:
                del self.embeddings_cache[document_id]
                await self._save_embeddings()
            
            self.connection.commit()
            
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Documento eliminado: {document_id}")
            else:
                logger.warning(f"Documento no encontrado para eliminar: {document_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error al eliminar documento: {e}")
            return False
    
    async def list_documents(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Listar documentos con paginación"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT document_id, title, document_type, created_at, content_length, word_count
                FROM documents 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = cursor.fetchall()
            documents = []
            
            for row in rows:
                documents.append({
                    "document_id": row["document_id"],
                    "title": row["title"],
                    "document_type": row["document_type"],
                    "created_at": row["created_at"],
                    "content_length": row["content_length"],
                    "word_count": row["word_count"]
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error al listar documentos: {e}")
            return []
    
    async def count_documents(self) -> int:
        """Contar total de documentos"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            count = cursor.fetchone()[0]
            
            return count
            
        except Exception as e:
            logger.error(f"Error al contar documentos: {e}")
            return 0
    
    async def search_documents(
        self, 
        query: str, 
        limit: int = 10, 
        document_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Buscar documentos por texto"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            cursor = self.connection.cursor()
            
            # Construir consulta SQL
            sql = """
                SELECT document_id, title, content, document_type, created_at
                FROM documents 
                WHERE (title LIKE ? OR content LIKE ?)
            """
            params = [f"%{query}%", f"%{query}%"]
            
            if document_type:
                sql += " AND document_type = ?"
                params.append(document_type)
            
            sql += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            documents = []
            for row in rows:
                documents.append({
                    "document_id": row["document_id"],
                    "title": row["title"],
                    "content": row["content"],
                    "document_type": row["document_type"],
                    "created_at": row["created_at"]
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error en búsqueda de documentos: {e}")
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de la base de datos"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            cursor = self.connection.cursor()
            
            # Estadísticas generales
            cursor.execute("SELECT COUNT(*) FROM documents")
            total_documents = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM embeddings")
            total_embeddings = cursor.fetchone()[0]
            
            # Estadísticas por tipo
            cursor.execute("""
                SELECT document_type, COUNT(*) as count 
                FROM documents 
                GROUP BY document_type
            """)
            type_stats = {row["document_type"]: row["count"] for row in cursor.fetchall()}
            
            # Estadísticas de contenido
            cursor.execute("SELECT AVG(content_length), AVG(word_count) FROM documents")
            avg_stats = cursor.fetchone()
            
            # Tamaño de la base de datos
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            embeddings_size = os.path.getsize(self.embeddings_path) if os.path.exists(self.embeddings_path) else 0
            
            return {
                "total_documents": total_documents,
                "total_embeddings": total_embeddings,
                "documents_by_type": type_stats,
                "average_content_length": avg_stats[0] or 0,
                "average_word_count": avg_stats[1] or 0,
                "database_size_bytes": db_size,
                "embeddings_size_bytes": embeddings_size,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {}
    
    async def close(self):
        """Cerrar conexión a la base de datos"""
        try:
            if self.connection:
                self.connection.close()
                logger.info("Conexión a base de datos cerrada")
        except Exception as e:
            logger.error(f"Error al cerrar base de datos: {e}")
    
    async def backup_database(self, backup_path: str):
        """Crear respaldo de la base de datos"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Respaldar base de datos SQLite
            backup_db_path = f"{backup_path}_db.db"
            if os.path.exists(self.db_path):
                import shutil
                shutil.copy2(self.db_path, backup_db_path)
            
            # Respaldar embeddings
            backup_embeddings_path = f"{backup_path}_embeddings.pkl"
            if os.path.exists(self.embeddings_path):
                import shutil
                shutil.copy2(self.embeddings_path, backup_embeddings_path)
            
            logger.info(f"Respaldo creado en: {backup_path}")
            
        except Exception as e:
            logger.error(f"Error al crear respaldo: {e}")
            raise



























