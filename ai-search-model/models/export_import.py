"""
Export/Import System - Sistema de Exportación e Importación
Maneja la exportación e importación de datos del sistema
"""

import asyncio
import logging
import json
import csv
import zipfile
import tempfile
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from io import StringIO, BytesIO

logger = logging.getLogger(__name__)

class ExportImportSystem:
    """
    Sistema de exportación e importación de datos del sistema de búsqueda IA
    """
    
    def __init__(self):
        self.supported_formats = ['json', 'csv', 'zip', 'xlsx']
        self.export_metadata = {}
        
    async def export_documents(self, documents: List[Dict[str, Any]], 
                             format_type: str = 'json',
                             include_embeddings: bool = False,
                             output_path: Optional[str] = None) -> Dict[str, Any]:
        """Exportar documentos en diferentes formatos"""
        try:
            logger.info(f"Exportando {len(documents)} documentos en formato {format_type}")
            
            if not documents:
                return {"error": "No hay documentos para exportar"}
            
            # Preparar datos para exportación
            export_data = self._prepare_documents_for_export(documents, include_embeddings)
            
            # Crear archivo de salida
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"documents_export_{timestamp}.{format_type}"
            
            # Exportar según formato
            if format_type == 'json':
                result = await self._export_to_json(export_data, output_path)
            elif format_type == 'csv':
                result = await self._export_to_csv(export_data, output_path)
            elif format_type == 'zip':
                result = await self._export_to_zip(export_data, output_path)
            elif format_type == 'xlsx':
                result = await self._export_to_excel(export_data, output_path)
            else:
                return {"error": f"Formato no soportado: {format_type}"}
            
            # Agregar metadatos de exportación
            result["export_metadata"] = {
                "export_date": datetime.now().isoformat(),
                "total_documents": len(documents),
                "format": format_type,
                "include_embeddings": include_embeddings,
                "file_size": os.path.getsize(output_path) if os.path.exists(output_path) else 0
            }
            
            logger.info(f"Exportación completada: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error exportando documentos: {e}")
            return {"error": str(e)}
    
    async def export_search_results(self, search_results: List[Dict[str, Any]], 
                                  format_type: str = 'json',
                                  output_path: Optional[str] = None) -> Dict[str, Any]:
        """Exportar resultados de búsqueda"""
        try:
            logger.info(f"Exportando {len(search_results)} resultados de búsqueda")
            
            if not search_results:
                return {"error": "No hay resultados para exportar"}
            
            # Preparar datos
            export_data = {
                "search_results": search_results,
                "export_info": {
                    "total_results": len(search_results),
                    "export_date": datetime.now().isoformat(),
                    "query_info": search_results[0].get("query_info", {}) if search_results else {}
                }
            }
            
            # Crear archivo de salida
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"search_results_export_{timestamp}.{format_type}"
            
            # Exportar según formato
            if format_type == 'json':
                result = await self._export_to_json(export_data, output_path)
            elif format_type == 'csv':
                result = await self._export_to_csv(export_data["search_results"], output_path)
            else:
                return {"error": f"Formato no soportado para resultados: {format_type}"}
            
            logger.info(f"Exportación de resultados completada: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error exportando resultados: {e}")
            return {"error": str(e)}
    
    async def export_system_backup(self, vector_db, search_engine, 
                                 output_path: Optional[str] = None) -> Dict[str, Any]:
        """Crear respaldo completo del sistema"""
        try:
            logger.info("Creando respaldo completo del sistema...")
            
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"system_backup_{timestamp}.zip"
            
            with tempfile.TemporaryDirectory() as temp_dir:
                backup_files = []
                
                # 1. Exportar documentos
                documents = await vector_db.list_documents(limit=10000)
                if documents:
                    doc_export = await self.export_documents(
                        documents, 
                        format_type='json',
                        output_path=os.path.join(temp_dir, "documents.json")
                    )
                    if "output_path" in doc_export:
                        backup_files.append(doc_export["output_path"])
                
                # 2. Exportar estadísticas
                stats = await vector_db.get_statistics()
                stats_file = os.path.join(temp_dir, "statistics.json")
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, indent=2, ensure_ascii=False)
                backup_files.append(stats_file)
                
                # 3. Exportar configuración del motor de búsqueda
                engine_stats = search_engine.get_statistics()
                engine_file = os.path.join(temp_dir, "search_engine.json")
                with open(engine_file, 'w', encoding='utf-8') as f:
                    json.dump(engine_stats, f, indent=2, ensure_ascii=False)
                backup_files.append(engine_file)
                
                # 4. Crear archivo de metadatos del respaldo
                backup_metadata = {
                    "backup_date": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "total_documents": len(documents) if documents else 0,
                    "files_included": [os.path.basename(f) for f in backup_files],
                    "system_info": {
                        "database_stats": stats,
                        "search_engine_stats": engine_stats
                    }
                }
                
                metadata_file = os.path.join(temp_dir, "backup_metadata.json")
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_metadata, f, indent=2, ensure_ascii=False)
                backup_files.append(metadata_file)
                
                # 5. Crear archivo ZIP
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in backup_files:
                        if os.path.exists(file_path):
                            zipf.write(file_path, os.path.basename(file_path))
                
                result = {
                    "success": True,
                    "output_path": output_path,
                    "backup_metadata": backup_metadata,
                    "file_size": os.path.getsize(output_path)
                }
                
                logger.info(f"Respaldo del sistema creado: {output_path}")
                return result
                
        except Exception as e:
            logger.error(f"Error creando respaldo del sistema: {e}")
            return {"error": str(e)}
    
    async def import_documents(self, file_path: str, document_processor, vector_db) -> Dict[str, Any]:
        """Importar documentos desde archivo"""
        try:
            logger.info(f"Importando documentos desde: {file_path}")
            
            if not os.path.exists(file_path):
                return {"error": "Archivo no encontrado"}
            
            # Determinar formato por extensión
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.json':
                result = await self._import_from_json(file_path, document_processor, vector_db)
            elif file_ext == '.csv':
                result = await self._import_from_csv(file_path, document_processor, vector_db)
            elif file_ext == '.zip':
                result = await self._import_from_zip(file_path, document_processor, vector_db)
            else:
                return {"error": f"Formato de archivo no soportado: {file_ext}"}
            
            logger.info(f"Importación completada: {result.get('total_imported', 0)} documentos")
            return result
            
        except Exception as e:
            logger.error(f"Error importando documentos: {e}")
            return {"error": str(e)}
    
    async def import_system_backup(self, backup_path: str, vector_db, search_engine) -> Dict[str, Any]:
        """Restaurar sistema desde respaldo"""
        try:
            logger.info(f"Restaurando sistema desde respaldo: {backup_path}")
            
            if not os.path.exists(backup_path):
                return {"error": "Archivo de respaldo no encontrado"}
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extraer archivo ZIP
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(temp_dir)
                
                # Leer metadatos del respaldo
                metadata_file = os.path.join(temp_dir, "backup_metadata.json")
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        backup_metadata = json.load(f)
                else:
                    backup_metadata = {}
                
                # Restaurar documentos
                documents_file = os.path.join(temp_dir, "documents.json")
                if os.path.exists(documents_file):
                    with open(documents_file, 'r', encoding='utf-8') as f:
                        documents_data = json.load(f)
                    
                    # Procesar documentos
                    imported_count = 0
                    failed_count = 0
                    
                    for doc_data in documents_data.get("documents", []):
                        try:
                            # Recrear documento
                            processed_doc = await document_processor.process_document(
                                title=doc_data["title"],
                                content=doc_data["content"],
                                metadata=doc_data.get("metadata", {}),
                                document_type=doc_data.get("document_type", "text")
                            )
                            
                            # Agregar a base de datos
                            await vector_db.add_document(processed_doc)
                            imported_count += 1
                            
                        except Exception as e:
                            logger.error(f"Error restaurando documento: {e}")
                            failed_count += 1
                    
                    result = {
                        "success": True,
                        "total_imported": imported_count,
                        "total_failed": failed_count,
                        "backup_metadata": backup_metadata,
                        "restore_date": datetime.now().isoformat()
                    }
                    
                    logger.info(f"Restauración completada: {imported_count} documentos restaurados")
                    return result
                else:
                    return {"error": "Archivo de documentos no encontrado en el respaldo"}
                    
        except Exception as e:
            logger.error(f"Error restaurando sistema: {e}")
            return {"error": str(e)}
    
    def _prepare_documents_for_export(self, documents: List[Dict[str, Any]], 
                                    include_embeddings: bool = False) -> Dict[str, Any]:
        """Preparar documentos para exportación"""
        try:
            export_data = {
                "export_info": {
                    "export_date": datetime.now().isoformat(),
                    "total_documents": len(documents),
                    "include_embeddings": include_embeddings,
                    "version": "1.0.0"
                },
                "documents": []
            }
            
            for doc in documents:
                doc_export = {
                    "document_id": doc.get("document_id"),
                    "title": doc.get("title"),
                    "content": doc.get("content"),
                    "document_type": doc.get("document_type", "text"),
                    "metadata": doc.get("metadata", {}),
                    "created_at": doc.get("created_at"),
                    "updated_at": doc.get("updated_at"),
                    "content_length": doc.get("content_length"),
                    "word_count": doc.get("word_count")
                }
                
                if include_embeddings and "embedding" in doc:
                    doc_export["embedding"] = doc["embedding"]
                
                export_data["documents"].append(doc_export)
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error preparando documentos para exportación: {e}")
            return {"error": str(e)}
    
    async def _export_to_json(self, data: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """Exportar a formato JSON"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            return {
                "success": True,
                "output_path": output_path,
                "format": "json"
            }
            
        except Exception as e:
            logger.error(f"Error exportando a JSON: {e}")
            return {"error": str(e)}
    
    async def _export_to_csv(self, data: Union[Dict, List], output_path: str) -> Dict[str, Any]:
        """Exportar a formato CSV"""
        try:
            if isinstance(data, dict) and "documents" in data:
                documents = data["documents"]
            elif isinstance(data, list):
                documents = data
            else:
                return {"error": "Formato de datos no válido para CSV"}
            
            if not documents:
                return {"error": "No hay documentos para exportar"}
            
            # Crear DataFrame
            df = pd.DataFrame(documents)
            
            # Seleccionar columnas principales
            csv_columns = ['document_id', 'title', 'content', 'document_type', 'created_at']
            available_columns = [col for col in csv_columns if col in df.columns]
            
            df_export = df[available_columns]
            
            # Exportar a CSV
            df_export.to_csv(output_path, index=False, encoding='utf-8')
            
            return {
                "success": True,
                "output_path": output_path,
                "format": "csv",
                "columns_exported": available_columns
            }
            
        except Exception as e:
            logger.error(f"Error exportando a CSV: {e}")
            return {"error": str(e)}
    
    async def _export_to_zip(self, data: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """Exportar a formato ZIP"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Crear archivos individuales
                files_created = []
                
                # 1. Archivo principal de documentos
                docs_file = os.path.join(temp_dir, "documents.json")
                with open(docs_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                files_created.append(docs_file)
                
                # 2. Archivo de metadatos
                metadata = {
                    "export_date": datetime.now().isoformat(),
                    "total_documents": len(data.get("documents", [])),
                    "format": "zip",
                    "files_included": ["documents.json", "metadata.json"]
                }
                
                metadata_file = os.path.join(temp_dir, "metadata.json")
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                files_created.append(metadata_file)
                
                # 3. Crear archivo ZIP
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in files_created:
                        zipf.write(file_path, os.path.basename(file_path))
                
                return {
                    "success": True,
                    "output_path": output_path,
                    "format": "zip",
                    "files_included": len(files_created)
                }
                
        except Exception as e:
            logger.error(f"Error exportando a ZIP: {e}")
            return {"error": str(e)}
    
    async def _export_to_excel(self, data: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """Exportar a formato Excel"""
        try:
            if "documents" not in data:
                return {"error": "Formato de datos no válido para Excel"}
            
            documents = data["documents"]
            if not documents:
                return {"error": "No hay documentos para exportar"}
            
            # Crear DataFrame
            df = pd.DataFrame(documents)
            
            # Crear archivo Excel con múltiples hojas
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Hoja principal con documentos
                df_main = df[['document_id', 'title', 'content', 'document_type', 'created_at']].copy()
                df_main.to_excel(writer, sheet_name='Documents', index=False)
                
                # Hoja con estadísticas
                stats_data = {
                    'Metric': ['Total Documents', 'Export Date', 'Average Content Length'],
                    'Value': [
                        len(documents),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        df['content_length'].mean() if 'content_length' in df.columns else 0
                    ]
                }
                df_stats = pd.DataFrame(stats_data)
                df_stats.to_excel(writer, sheet_name='Statistics', index=False)
                
                # Hoja con metadatos
                if 'metadata' in df.columns:
                    metadata_list = []
                    for idx, row in df.iterrows():
                        if row['metadata']:
                            for key, value in row['metadata'].items():
                                metadata_list.append({
                                    'document_id': row['document_id'],
                                    'metadata_key': key,
                                    'metadata_value': str(value)
                                })
                    
                    if metadata_list:
                        df_metadata = pd.DataFrame(metadata_list)
                        df_metadata.to_excel(writer, sheet_name='Metadata', index=False)
            
            return {
                "success": True,
                "output_path": output_path,
                "format": "xlsx",
                "sheets_created": ["Documents", "Statistics", "Metadata"]
            }
            
        except Exception as e:
            logger.error(f"Error exportando a Excel: {e}")
            return {"error": str(e)}
    
    async def _import_from_json(self, file_path: str, document_processor, vector_db) -> Dict[str, Any]:
        """Importar desde archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = data.get("documents", [])
            imported_count = 0
            failed_count = 0
            
            for doc_data in documents:
                try:
                    processed_doc = await document_processor.process_document(
                        title=doc_data["title"],
                        content=doc_data["content"],
                        metadata=doc_data.get("metadata", {}),
                        document_type=doc_data.get("document_type", "text")
                    )
                    
                    await vector_db.add_document(processed_doc)
                    imported_count += 1
                    
                except Exception as e:
                    logger.error(f"Error importando documento: {e}")
                    failed_count += 1
            
            return {
                "success": True,
                "total_imported": imported_count,
                "total_failed": failed_count,
                "format": "json"
            }
            
        except Exception as e:
            logger.error(f"Error importando desde JSON: {e}")
            return {"error": str(e)}
    
    async def _import_from_csv(self, file_path: str, document_processor, vector_db) -> Dict[str, Any]:
        """Importar desde archivo CSV"""
        try:
            df = pd.read_csv(file_path)
            
            required_columns = ['title', 'content']
            if not all(col in df.columns for col in required_columns):
                return {"error": f"Columnas requeridas no encontradas: {required_columns}"}
            
            imported_count = 0
            failed_count = 0
            
            for index, row in df.iterrows():
                try:
                    metadata = {}
                    for col in df.columns:
                        if col not in required_columns and pd.notna(row[col]):
                            metadata[col.lower()] = str(row[col])
                    
                    processed_doc = await document_processor.process_document(
                        title=str(row['title']),
                        content=str(row['content']),
                        metadata=metadata,
                        document_type="text"
                    )
                    
                    await vector_db.add_document(processed_doc)
                    imported_count += 1
                    
                except Exception as e:
                    logger.error(f"Error importando fila {index + 1}: {e}")
                    failed_count += 1
            
            return {
                "success": True,
                "total_imported": imported_count,
                "total_failed": failed_count,
                "format": "csv"
            }
            
        except Exception as e:
            logger.error(f"Error importando desde CSV: {e}")
            return {"error": str(e)}
    
    async def _import_from_zip(self, file_path: str, document_processor, vector_db) -> Dict[str, Any]:
        """Importar desde archivo ZIP"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(file_path, 'r') as zipf:
                    zipf.extractall(temp_dir)
                
                # Buscar archivo de documentos
                documents_file = os.path.join(temp_dir, "documents.json")
                if os.path.exists(documents_file):
                    return await self._import_from_json(documents_file, document_processor, vector_db)
                else:
                    return {"error": "Archivo de documentos no encontrado en el ZIP"}
                    
        except Exception as e:
            logger.error(f"Error importando desde ZIP: {e}")
            return {"error": str(e)}



























