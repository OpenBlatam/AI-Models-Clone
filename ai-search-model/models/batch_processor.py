"""
Batch Processor - Procesador por Lotes
Maneja el procesamiento eficiente de grandes cantidades de documentos
"""

import asyncio
import logging
import os
import json
import csv
import zipfile
import tempfile
from typing import List, Dict, Any, Optional, Callable, Union
from datetime import datetime
from pathlib import Path
import aiofiles
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import mimetypes

logger = logging.getLogger(__name__)

class BatchProcessor:
    """
    Procesador por lotes para manejar grandes volúmenes de documentos
    de manera eficiente con procesamiento paralelo
    """
    
    def __init__(self, max_workers: int = 4, batch_size: int = 100):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.processed_count = 0
        self.failed_count = 0
        self.progress_callback = None
        
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """Establecer callback para reportar progreso"""
        self.progress_callback = callback
    
    async def process_file_batch(self, file_paths: List[str], document_processor, vector_db) -> Dict[str, Any]:
        """Procesar lote de archivos"""
        try:
            logger.info(f"Procesando lote de {len(file_paths)} archivos...")
            
            results = {
                "successful": [],
                "failed": [],
                "total_processed": 0,
                "total_failed": 0,
                "processing_time": 0
            }
            
            start_time = datetime.now()
            
            # Procesar archivos en paralelo
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Crear tareas
                tasks = []
                for file_path in file_paths:
                    task = executor.submit(
                        self._process_single_file, 
                        file_path, 
                        document_processor, 
                        vector_db
                    )
                    tasks.append(task)
                
                # Procesar resultados conforme se completan
                for i, task in enumerate(as_completed(tasks)):
                    try:
                        result = task.result()
                        if result["success"]:
                            results["successful"].append(result)
                            self.processed_count += 1
                        else:
                            results["failed"].append(result)
                            self.failed_count += 1
                        
                        # Reportar progreso
                        if self.progress_callback:
                            progress = ((i + 1) / len(tasks)) * 100
                            self.progress_callback(
                                i + 1, 
                                len(tasks), 
                                f"Procesando archivo {i + 1} de {len(tasks)}"
                            )
                            
                    except Exception as e:
                        logger.error(f"Error procesando tarea: {e}")
                        results["failed"].append({
                            "file_path": "unknown",
                            "error": str(e),
                            "success": False
                        })
                        self.failed_count += 1
            
            end_time = datetime.now()
            results["processing_time"] = (end_time - start_time).total_seconds()
            results["total_processed"] = len(results["successful"])
            results["total_failed"] = len(results["failed"])
            
            logger.info(f"Lote procesado: {results['total_processed']} exitosos, {results['total_failed']} fallidos")
            return results
            
        except Exception as e:
            logger.error(f"Error procesando lote de archivos: {e}")
            return {"error": str(e)}
    
    def _process_single_file(self, file_path: str, document_processor, vector_db) -> Dict[str, Any]:
        """Procesar un archivo individual"""
        try:
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                return {
                    "file_path": file_path,
                    "success": False,
                    "error": "Archivo no encontrado"
                }
            
            # Determinar tipo de archivo
            file_type = self._detect_file_type(file_path)
            
            # Leer contenido del archivo
            content = self._read_file_content(file_path, file_type)
            
            if not content:
                return {
                    "file_path": file_path,
                    "success": False,
                    "error": "No se pudo leer el contenido del archivo"
                }
            
            # Extraer metadatos del archivo
            metadata = self._extract_file_metadata(file_path, content)
            
            # Procesar documento
            processed_doc = asyncio.run(document_processor.process_document(
                title=metadata["title"],
                content=content,
                metadata=metadata,
                document_type=file_type
            ))
            
            # Guardar en base de datos
            document_id = asyncio.run(vector_db.add_document(processed_doc))
            
            return {
                "file_path": file_path,
                "document_id": document_id,
                "success": True,
                "metadata": metadata,
                "content_length": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error procesando archivo {file_path}: {e}")
            return {
                "file_path": file_path,
                "success": False,
                "error": str(e)
            }
    
    def _detect_file_type(self, file_path: str) -> str:
        """Detectar tipo de archivo"""
        try:
            # Obtener extensión
            ext = Path(file_path).suffix.lower()
            
            # Mapeo de extensiones a tipos
            type_mapping = {
                '.txt': 'text',
                '.md': 'markdown',
                '.markdown': 'markdown',
                '.html': 'html',
                '.htm': 'html',
                '.json': 'json',
                '.csv': 'csv',
                '.xml': 'xml',
                '.rtf': 'rtf'
            }
            
            return type_mapping.get(ext, 'text')
            
        except Exception as e:
            logger.error(f"Error detectando tipo de archivo {file_path}: {e}")
            return 'text'
    
    def _read_file_content(self, file_path: str, file_type: str) -> str:
        """Leer contenido del archivo"""
        try:
            # Determinar encoding
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    return content
                except UnicodeDecodeError:
                    continue
            
            # Si falla con todos los encodings, usar modo binario
            with open(file_path, 'rb') as f:
                content = f.read()
                return content.decode('utf-8', errors='ignore')
                
        except Exception as e:
            logger.error(f"Error leyendo archivo {file_path}: {e}")
            return ""
    
    def _extract_file_metadata(self, file_path: str, content: str) -> Dict[str, Any]:
        """Extraer metadatos del archivo"""
        try:
            file_path_obj = Path(file_path)
            file_stats = file_path_obj.stat()
            
            metadata = {
                "title": file_path_obj.stem,
                "filename": file_path_obj.name,
                "file_path": str(file_path_obj),
                "file_size": file_stats.st_size,
                "created_at": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                "file_extension": file_path_obj.suffix,
                "batch_processed": True
            }
            
            # Agregar metadatos específicos del tipo de archivo
            if file_path_obj.suffix.lower() == '.json':
                try:
                    json_data = json.loads(content)
                    if isinstance(json_data, dict):
                        metadata["json_keys"] = list(json_data.keys())
                except:
                    pass
            
            elif file_path_obj.suffix.lower() == '.csv':
                try:
                    # Leer primeras líneas para detectar estructura
                    lines = content.split('\n')[:5]
                    if lines:
                        metadata["csv_headers"] = lines[0].split(',')
                        metadata["csv_rows_preview"] = len([l for l in lines[1:] if l.strip()])
                except:
                    pass
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extrayendo metadatos de {file_path}: {e}")
            return {"title": Path(file_path).stem, "batch_processed": True}
    
    async def process_directory(self, directory_path: str, document_processor, vector_db, 
                              file_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Procesar todos los archivos de un directorio"""
        try:
            logger.info(f"Procesando directorio: {directory_path}")
            
            if not os.path.exists(directory_path):
                return {"error": "Directorio no encontrado"}
            
            # Encontrar archivos
            files = self._find_files_in_directory(directory_path, file_patterns)
            
            if not files:
                return {"error": "No se encontraron archivos para procesar"}
            
            logger.info(f"Encontrados {len(files)} archivos para procesar")
            
            # Procesar en lotes
            all_results = {
                "successful": [],
                "failed": [],
                "total_processed": 0,
                "total_failed": 0,
                "processing_time": 0,
                "files_processed": []
            }
            
            start_time = datetime.now()
            
            # Dividir en lotes
            for i in range(0, len(files), self.batch_size):
                batch = files[i:i + self.batch_size]
                batch_results = await self.process_file_batch(batch, document_processor, vector_db)
                
                # Acumular resultados
                all_results["successful"].extend(batch_results.get("successful", []))
                all_results["failed"].extend(batch_results.get("failed", []))
                all_results["files_processed"].extend(batch)
            
            end_time = datetime.now()
            all_results["processing_time"] = (end_time - start_time).total_seconds()
            all_results["total_processed"] = len(all_results["successful"])
            all_results["total_failed"] = len(all_results["failed"])
            
            logger.info(f"Directorio procesado: {all_results['total_processed']} exitosos, {all_results['total_failed']} fallidos")
            return all_results
            
        except Exception as e:
            logger.error(f"Error procesando directorio {directory_path}: {e}")
            return {"error": str(e)}
    
    def _find_files_in_directory(self, directory_path: str, file_patterns: Optional[List[str]] = None) -> List[str]:
        """Encontrar archivos en directorio"""
        try:
            if file_patterns is None:
                file_patterns = ['.txt', '.md', '.html', '.json', '.csv']
            
            files = []
            directory = Path(directory_path)
            
            for pattern in file_patterns:
                if pattern.startswith('.'):
                    # Búsqueda por extensión
                    found_files = list(directory.rglob(f'*{pattern}'))
                else:
                    # Búsqueda por patrón
                    found_files = list(directory.rglob(pattern))
                
                files.extend([str(f) for f in found_files if f.is_file()])
            
            # Eliminar duplicados y ordenar
            files = sorted(list(set(files)))
            
            return files
            
        except Exception as e:
            logger.error(f"Error encontrando archivos en {directory_path}: {e}")
            return []
    
    async def process_zip_archive(self, zip_path: str, document_processor, vector_db) -> Dict[str, Any]:
        """Procesar archivo ZIP con documentos"""
        try:
            logger.info(f"Procesando archivo ZIP: {zip_path}")
            
            if not os.path.exists(zip_path):
                return {"error": "Archivo ZIP no encontrado"}
            
            results = {
                "successful": [],
                "failed": [],
                "total_processed": 0,
                "total_failed": 0,
                "processing_time": 0,
                "extracted_files": []
            }
            
            start_time = datetime.now()
            
            # Extraer archivos temporalmente
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                    
                    # Encontrar archivos extraídos
                    extracted_files = self._find_files_in_directory(temp_dir)
                    results["extracted_files"] = extracted_files
                    
                    logger.info(f"Extraídos {len(extracted_files)} archivos del ZIP")
                    
                    # Procesar archivos extraídos
                    if extracted_files:
                        batch_results = await self.process_file_batch(extracted_files, document_processor, vector_db)
                        results.update(batch_results)
            
            end_time = datetime.now()
            results["processing_time"] = (end_time - start_time).total_seconds()
            
            logger.info(f"ZIP procesado: {results['total_processed']} exitosos, {results['total_failed']} fallidos")
            return results
            
        except Exception as e:
            logger.error(f"Error procesando ZIP {zip_path}: {e}")
            return {"error": str(e)}
    
    async def process_csv_batch(self, csv_path: str, document_processor, vector_db,
                              title_column: str = "title", content_column: str = "content") -> Dict[str, Any]:
        """Procesar archivo CSV con documentos"""
        try:
            logger.info(f"Procesando archivo CSV: {csv_path}")
            
            if not os.path.exists(csv_path):
                return {"error": "Archivo CSV no encontrado"}
            
            results = {
                "successful": [],
                "failed": [],
                "total_processed": 0,
                "total_failed": 0,
                "processing_time": 0
            }
            
            start_time = datetime.now()
            
            # Leer CSV
            df = pd.read_csv(csv_path)
            
            if title_column not in df.columns or content_column not in df.columns:
                return {"error": f"Columnas requeridas no encontradas: {title_column}, {content_column}"}
            
            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    # Extraer datos de la fila
                    title = str(row[title_column]) if pd.notna(row[title_column]) else f"Documento {index + 1}"
                    content = str(row[content_column]) if pd.notna(row[content_column]) else ""
                    
                    if not content.strip():
                        results["failed"].append({
                            "row": index + 1,
                            "error": "Contenido vacío",
                            "success": False
                        })
                        continue
                    
                    # Crear metadatos de la fila
                    metadata = {
                        "title": title,
                        "source": "csv_batch",
                        "row_number": index + 1,
                        "csv_file": os.path.basename(csv_path)
                    }
                    
                    # Agregar otras columnas como metadatos
                    for col in df.columns:
                        if col not in [title_column, content_column] and pd.notna(row[col]):
                            metadata[col.lower()] = str(row[col])
                    
                    # Procesar documento
                    processed_doc = await document_processor.process_document(
                        title=title,
                        content=content,
                        metadata=metadata,
                        document_type="text"
                    )
                    
                    # Guardar en base de datos
                    document_id = await vector_db.add_document(processed_doc)
                    
                    results["successful"].append({
                        "row": index + 1,
                        "document_id": document_id,
                        "title": title,
                        "success": True
                    })
                    
                except Exception as e:
                    logger.error(f"Error procesando fila {index + 1}: {e}")
                    results["failed"].append({
                        "row": index + 1,
                        "error": str(e),
                        "success": False
                    })
            
            end_time = datetime.now()
            results["processing_time"] = (end_time - start_time).total_seconds()
            results["total_processed"] = len(results["successful"])
            results["total_failed"] = len(results["failed"])
            
            logger.info(f"CSV procesado: {results['total_processed']} exitosos, {results['total_failed']} fallidos")
            return results
            
        except Exception as e:
            logger.error(f"Error procesando CSV {csv_path}: {e}")
            return {"error": str(e)}
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de procesamiento"""
        return {
            "total_processed": self.processed_count,
            "total_failed": self.failed_count,
            "success_rate": (self.processed_count / (self.processed_count + self.failed_count) * 100) 
                           if (self.processed_count + self.failed_count) > 0 else 0,
            "max_workers": self.max_workers,
            "batch_size": self.batch_size
        }
    
    def reset_stats(self):
        """Reiniciar estadísticas"""
        self.processed_count = 0
        self.failed_count = 0



























