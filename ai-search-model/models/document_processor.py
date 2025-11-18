"""
Document Processor - Procesador de documentos
Maneja la indexación y procesamiento de diferentes tipos de documentos
"""

import asyncio
import logging
import hashlib
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import json

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Procesador de documentos que maneja diferentes formatos
    y extrae información relevante para la búsqueda
    """
    
    def __init__(self):
        self.supported_types = ["text", "markdown", "html", "json", "pdf"]
        self.max_content_length = 100000  # 100KB máximo por documento
        
    async def process_document(
        self, 
        title: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        document_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Procesar un documento y prepararlo para indexación
        """
        try:
            logger.info(f"Procesando documento: '{title}'")
            
            # Validar tipo de documento
            if document_type not in self.supported_types:
                raise ValueError(f"Tipo de documento no soportado: {document_type}")
            
            # Generar ID único
            document_id = self._generate_document_id(title, content)
            
            # Limpiar y procesar contenido según el tipo
            processed_content = await self._process_content_by_type(content, document_type)
            
            # Extraer metadatos adicionales
            extracted_metadata = self._extract_metadata(processed_content, metadata)
            
            # Crear documento procesado
            processed_document = {
                "document_id": document_id,
                "title": self._clean_title(title),
                "content": processed_content,
                "original_content": content,
                "document_type": document_type,
                "metadata": extracted_metadata,
                "created_at": datetime.now().isoformat(),
                "content_length": len(processed_content),
                "word_count": len(processed_content.split())
            }
            
            logger.info(f"Documento procesado exitosamente: {document_id}")
            return processed_document
            
        except Exception as e:
            logger.error(f"Error al procesar documento: {e}")
            raise
    
    def _generate_document_id(self, title: str, content: str) -> str:
        """Generar ID único para el documento"""
        try:
            # Crear hash basado en título y contenido
            content_hash = hashlib.md5(f"{title}{content}".encode()).hexdigest()
            return f"doc_{content_hash[:12]}"
            
        except Exception as e:
            logger.error(f"Error al generar ID: {e}")
            return f"doc_{uuid.uuid4().hex[:12]}"
    
    def _clean_title(self, title: str) -> str:
        """Limpiar y normalizar título"""
        if not title:
            return "Documento sin título"
        
        # Remover caracteres especiales excesivos
        cleaned = re.sub(r'[^\w\s\.\,\!\?\;\:\-]', ' ', title)
        
        # Normalizar espacios
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Truncar si es muy largo
        if len(cleaned) > 200:
            cleaned = cleaned[:200] + "..."
        
        return cleaned
    
    async def _process_content_by_type(self, content: str, document_type: str) -> str:
        """Procesar contenido según el tipo de documento"""
        try:
            if document_type == "text":
                return self._process_text_content(content)
            elif document_type == "markdown":
                return self._process_markdown_content(content)
            elif document_type == "html":
                return self._process_html_content(content)
            elif document_type == "json":
                return self._process_json_content(content)
            else:
                return self._process_text_content(content)
                
        except Exception as e:
            logger.error(f"Error al procesar contenido {document_type}: {e}")
            return content
    
    def _process_text_content(self, content: str) -> str:
        """Procesar contenido de texto plano"""
        if not content:
            return ""
        
        # Limpiar texto
        cleaned = re.sub(r'\s+', ' ', content)
        cleaned = cleaned.strip()
        
        # Truncar si es muy largo
        if len(cleaned) > self.max_content_length:
            cleaned = cleaned[:self.max_content_length] + "..."
        
        return cleaned
    
    def _process_markdown_content(self, content: str) -> str:
        """Procesar contenido Markdown"""
        if not content:
            return ""
        
        # Remover sintaxis Markdown básica
        cleaned = content
        
        # Remover headers
        cleaned = re.sub(r'^#+\s*', '', cleaned, flags=re.MULTILINE)
        
        # Remover enlaces pero mantener texto
        cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)
        
        # Remover código inline
        cleaned = re.sub(r'`([^`]+)`', r'\1', cleaned)
        
        # Remover código de bloque
        cleaned = re.sub(r'```[\s\S]*?```', '', cleaned)
        
        # Limpiar espacios
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Truncar si es muy largo
        if len(cleaned) > self.max_content_length:
            cleaned = cleaned[:self.max_content_length] + "..."
        
        return cleaned
    
    def _process_html_content(self, content: str) -> str:
        """Procesar contenido HTML"""
        if not content:
            return ""
        
        # Remover tags HTML básicos
        cleaned = re.sub(r'<[^>]+>', ' ', content)
        
        # Decodificar entidades HTML básicas
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' '
        }
        
        for entity, char in html_entities.items():
            cleaned = cleaned.replace(entity, char)
        
        # Limpiar espacios
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Truncar si es muy largo
        if len(cleaned) > self.max_content_length:
            cleaned = cleaned[:self.max_content_length] + "..."
        
        return cleaned
    
    def _process_json_content(self, content: str) -> str:
        """Procesar contenido JSON"""
        if not content:
            return ""
        
        try:
            # Intentar parsear JSON
            data = json.loads(content)
            
            # Extraer texto de valores
            text_parts = []
            self._extract_text_from_json(data, text_parts)
            
            # Unir texto extraído
            extracted_text = ' '.join(text_parts)
            
            # Limpiar y truncar
            cleaned = re.sub(r'\s+', ' ', extracted_text).strip()
            
            if len(cleaned) > self.max_content_length:
                cleaned = cleaned[:self.max_content_length] + "..."
            
            return cleaned
            
        except json.JSONDecodeError:
            # Si no es JSON válido, tratar como texto
            return self._process_text_content(content)
    
    def _extract_text_from_json(self, data: Any, text_parts: List[str]):
        """Extraer texto de estructura JSON recursivamente"""
        if isinstance(data, dict):
            for value in data.values():
                self._extract_text_from_json(value, text_parts)
        elif isinstance(data, list):
            for item in data:
                self._extract_text_from_json(item, text_parts)
        elif isinstance(data, str):
            text_parts.append(data)
    
    def _extract_metadata(self, content: str, provided_metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extraer metadatos del contenido"""
        try:
            metadata = provided_metadata or {}
            
            # Metadatos automáticos
            metadata.update({
                "content_length": len(content),
                "word_count": len(content.split()),
                "sentence_count": len(re.findall(r'[.!?]+', content)),
                "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
                "has_numbers": bool(re.search(r'\d', content)),
                "has_urls": bool(re.search(r'http[s]?://', content)),
                "has_emails": bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content))
            })
            
            # Extraer palabras clave más frecuentes
            words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Top 10 palabras más frecuentes
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            metadata["top_keywords"] = [word for word, freq in top_words]
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error al extraer metadatos: {e}")
            return provided_metadata or {}
    
    async def batch_process_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Procesar múltiples documentos en lote"""
        try:
            logger.info(f"Procesando lote de {len(documents)} documentos...")
            
            processed_documents = []
            
            for doc in documents:
                try:
                    processed_doc = await self.process_document(
                        title=doc.get("title", ""),
                        content=doc.get("content", ""),
                        metadata=doc.get("metadata"),
                        document_type=doc.get("document_type", "text")
                    )
                    processed_documents.append(processed_doc)
                    
                except Exception as e:
                    logger.error(f"Error al procesar documento en lote: {e}")
                    continue
            
            logger.info(f"Lote procesado: {len(processed_documents)}/{len(documents)} documentos exitosos")
            return processed_documents
            
        except Exception as e:
            logger.error(f"Error al procesar lote de documentos: {e}")
            raise
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del procesador"""
        return {
            "supported_types": self.supported_types,
            "max_content_length": self.max_content_length,
            "processor_version": "1.0.0"
        }



























