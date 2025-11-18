#!/usr/bin/env python3
"""
Ejemplo Práctico: IA Generadora Continua de Documentos
=====================================================

Este script demuestra cómo usar el sistema de generación continua de documentos
para crear múltiples documentos relacionados a partir de una sola petición.

Autor: Sistema de Especificaciones Técnicas Blatam Academy
Versión: 1.0.0
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import yaml
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# MODELOS DE DATOS
# ============================================================================

class DocumentType(Enum):
    """Tipos de documentos que se pueden generar"""
    TECHNICAL_SPEC = "technical_specification"
    API_DOCUMENTATION = "api_documentation"
    IMPLEMENTATION_GUIDE = "implementation_guide"
    TEST_CASES = "test_cases"
    USER_MANUAL = "user_manual"
    ARCHITECTURE_DIAGRAM = "architecture_diagram"
    SECURITY_ANALYSIS = "security_analysis"
    DEPLOYMENT_GUIDE = "deployment_guide"
    TROUBLESHOOTING = "troubleshooting"

@dataclass
class ContinuousGenerationRequest:
    """Petición para generación continua de documentos"""
    query: str
    document_types: List[DocumentType]
    context: Optional[Dict[str, Any]] = None
    output_format: str = "markdown"
    language: str = "es"
    quality_level: str = "high"
    max_documents: int = 10
    include_examples: bool = True
    include_diagrams: bool = True
    custom_requirements: Optional[Dict[str, Any]] = None
    ai_provider: str = "mock"  # Para el ejemplo usamos mock
    api_key: Optional[str] = None

@dataclass
class GeneratedDocument:
    """Documento generado por la IA"""
    id: str
    title: str
    type: DocumentType
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    version: str
    dependencies: List[str]
    quality_score: float
    coherence_score: float

@dataclass
class GenerationProgress:
    """Progreso de la generación"""
    stage: str
    progress_percentage: int
    current_document: Optional[str]
    estimated_time_remaining: Optional[float]
    quality_indicators: Dict[str, Any]

# ============================================================================
# MOTOR DE GENERACIÓN CONTINUA
# ============================================================================

class ContinuousDocumentGenerator:
    """
    Motor principal para generación continua de documentos
    Versión simplificada para demostración
    """
    
    def __init__(self, ai_provider: str = "mock", api_key: Optional[str] = None):
        self.ai_provider = ai_provider
        self.api_key = api_key
        self.generated_documents: List[GeneratedDocument] = []
        self.generation_start_time: Optional[datetime] = None
        self.terminology_db = {}
        self.reference_map = {}
        
    async def __aenter__(self):
        """Context manager entry"""
        self.generation_start_time = datetime.now()
        logger.info("Iniciando motor de generación continua")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        logger.info("Finalizando motor de generación continua")
        
    async def generate_continuous_documents(
        self, 
        request: ContinuousGenerationRequest
    ) -> List[GeneratedDocument]:
        """
        Genera múltiples documentos de forma continua
        """
        logger.info(f"Iniciando generación continua para: {request.query[:50]}...")
        
        try:
            # 1. Análisis de la petición
            analysis = await self._analyze_request(request)
            logger.info(f"Análisis completado: {len(analysis)} elementos identificados")
            
            # 2. Planificación de documentos
            document_plan = await self._create_document_plan(analysis, request)
            logger.info(f"Plan creado: {len(document_plan)} documentos planificados")
            
            # 3. Generación paralela
            documents = await self._generate_documents_parallel(document_plan, request)
            logger.info(f"Generados {len(documents)} documentos")
            
            # 4. Validación de coherencia
            validated_documents = await self._validate_coherence(documents)
            logger.info("Validación de coherencia completada")
            
            # 5. Post-procesamiento
            final_documents = await self._post_process_documents(validated_documents)
            logger.info("Post-procesamiento completado")
            
            # 6. Almacenar documentos
            self.generated_documents.extend(final_documents)
            
            return final_documents
            
        except Exception as e:
            logger.error(f"Error en generación continua: {e}")
            raise
    
    async def _analyze_request(self, request: ContinuousGenerationRequest) -> Dict[str, Any]:
        """Analiza la petición para extraer información clave"""
        logger.info("Analizando petición...")
        
        # Simulación de análisis (en producción usaría IA real)
        analysis = {
            "domain": self._extract_domain(request.query),
            "complexity_level": self._assess_complexity(request.query),
            "target_audience": self._identify_audience(request.query),
            "technologies": self._extract_technologies(request.query),
            "requirements": self._extract_requirements(request.query)
        }
        
        return analysis
    
    def _extract_domain(self, query: str) -> str:
        """Extrae el dominio técnico de la consulta"""
        domains = {
            "api": ["api", "rest", "endpoint", "http"],
            "database": ["database", "sql", "postgresql", "mysql"],
            "frontend": ["frontend", "react", "vue", "angular"],
            "backend": ["backend", "server", "microservice"],
            "devops": ["deployment", "docker", "kubernetes", "ci/cd"],
            "security": ["security", "authentication", "authorization", "jwt"]
        }
        
        query_lower = query.lower()
        for domain, keywords in domains.items():
            if any(keyword in query_lower for keyword in keywords):
                return domain
        
        return "general"
    
    def _assess_complexity(self, query: str) -> str:
        """Evalúa el nivel de complejidad"""
        complex_keywords = ["microservices", "distributed", "scalable", "enterprise"]
        simple_keywords = ["basic", "simple", "tutorial", "getting started"]
        
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in complex_keywords):
            return "high"
        elif any(keyword in query_lower for keyword in simple_keywords):
            return "low"
        else:
            return "medium"
    
    def _identify_audience(self, query: str) -> str:
        """Identifica el público objetivo"""
        if "developer" in query.lower() or "programmer" in query.lower():
            return "developers"
        elif "user" in query.lower() or "end user" in query.lower():
            return "end_users"
        elif "admin" in query.lower() or "administrator" in query.lower():
            return "administrators"
        else:
            return "technical"
    
    def _extract_technologies(self, query: str) -> List[str]:
        """Extrae tecnologías mencionadas"""
        technologies = []
        tech_keywords = {
            "python": ["python", "fastapi", "django", "flask"],
            "javascript": ["javascript", "node.js", "express", "react"],
            "java": ["java", "spring", "maven"],
            "docker": ["docker", "container"],
            "kubernetes": ["kubernetes", "k8s"],
            "postgresql": ["postgresql", "postgres"],
            "redis": ["redis"],
            "aws": ["aws", "amazon web services"],
            "azure": ["azure", "microsoft azure"]
        }
        
        query_lower = query.lower()
        for tech, keywords in tech_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                technologies.append(tech)
        
        return technologies
    
    def _extract_requirements(self, query: str) -> List[str]:
        """Extrae requisitos específicos"""
        requirements = []
        if "authentication" in query.lower():
            requirements.append("authentication")
        if "security" in query.lower():
            requirements.append("security")
        if "scalable" in query.lower():
            requirements.append("scalability")
        if "monitoring" in query.lower():
            requirements.append("monitoring")
        if "testing" in query.lower():
            requirements.append("testing")
        
        return requirements
    
    async def _create_document_plan(
        self, 
        analysis: Dict[str, Any], 
        request: ContinuousGenerationRequest
    ) -> List[Dict[str, Any]]:
        """Crea un plan detallado para la generación de documentos"""
        logger.info("Creando plan de documentos...")
        
        plan = []
        for doc_type in request.document_types:
            plan_item = {
                "type": doc_type.value,
                "title": self._generate_document_title(doc_type, analysis),
                "sections": self._get_document_sections(doc_type),
                "dependencies": self._get_document_dependencies(doc_type, request.document_types),
                "detail_level": analysis["complexity_level"],
                "examples": self._get_required_examples(doc_type),
                "priority": self._get_document_priority(doc_type)
            }
            plan.append(plan_item)
        
        # Ordenar por prioridad
        plan.sort(key=lambda x: x["priority"])
        return plan
    
    def _generate_document_title(self, doc_type: DocumentType, analysis: Dict[str, Any]) -> str:
        """Genera un título apropiado para el documento"""
        domain = analysis["domain"]
        technologies = analysis["technologies"]
        
        titles = {
            DocumentType.TECHNICAL_SPEC: f"Especificación Técnica - Sistema de {domain.title()}",
            DocumentType.API_DOCUMENTATION: f"Documentación de API - {domain.title()}",
            DocumentType.IMPLEMENTATION_GUIDE: f"Guía de Implementación - {domain.title()}",
            DocumentType.TEST_CASES: f"Casos de Prueba - Sistema de {domain.title()}",
            DocumentType.USER_MANUAL: f"Manual de Usuario - {domain.title()}",
            DocumentType.ARCHITECTURE_DIAGRAM: f"Diagrama de Arquitectura - {domain.title()}",
            DocumentType.SECURITY_ANALYSIS: f"Análisis de Seguridad - {domain.title()}",
            DocumentType.DEPLOYMENT_GUIDE: f"Guía de Despliegue - {domain.title()}",
            DocumentType.TROUBLESHOOTING: f"Guía de Resolución de Problemas - {domain.title()}"
        }
        
        return titles.get(doc_type, f"Documento - {domain.title()}")
    
    def _get_document_sections(self, doc_type: DocumentType) -> List[str]:
        """Obtiene las secciones requeridas para un tipo de documento"""
        sections_map = {
            DocumentType.TECHNICAL_SPEC: [
                "Introducción", "Arquitectura", "Especificaciones Técnicas",
                "Casos de Uso", "Consideraciones de Seguridad", "Implementación"
            ],
            DocumentType.API_DOCUMENTATION: [
                "Información General", "Autenticación", "Endpoints",
                "Códigos de Error", "Rate Limiting", "Ejemplos"
            ],
            DocumentType.IMPLEMENTATION_GUIDE: [
                "Prerrequisitos", "Instalación", "Configuración",
                "Despliegue", "Monitoreo", "Troubleshooting"
            ],
            DocumentType.TEST_CASES: [
                "Casos de Prueba Unitarios", "Casos de Prueba de Integración",
                "Casos de Prueba de Rendimiento", "Casos de Prueba de Seguridad"
            ],
            DocumentType.USER_MANUAL: [
                "Introducción", "Instalación", "Configuración Inicial",
                "Uso Básico", "Funciones Avanzadas", "Solución de Problemas"
            ]
        }
        
        return sections_map.get(doc_type, ["Introducción", "Contenido Principal", "Conclusión"])
    
    def _get_document_dependencies(self, doc_type: DocumentType, all_types: List[DocumentType]) -> List[str]:
        """Obtiene las dependencias de un documento"""
        dependencies_map = {
            DocumentType.API_DOCUMENTATION: [DocumentType.TECHNICAL_SPEC],
            DocumentType.IMPLEMENTATION_GUIDE: [DocumentType.TECHNICAL_SPEC, DocumentType.API_DOCUMENTATION],
            DocumentType.TEST_CASES: [DocumentType.TECHNICAL_SPEC, DocumentType.API_DOCUMENTATION],
            DocumentType.USER_MANUAL: [DocumentType.IMPLEMENTATION_GUIDE],
            DocumentType.DEPLOYMENT_GUIDE: [DocumentType.IMPLEMENTATION_GUIDE],
            DocumentType.TROUBLESHOOTING: [DocumentType.USER_MANUAL, DocumentType.DEPLOYMENT_GUIDE]
        }
        
        deps = dependencies_map.get(doc_type, [])
        return [dep.value for dep in deps if dep in all_types]
    
    def _get_required_examples(self, doc_type: DocumentType) -> List[str]:
        """Obtiene los ejemplos requeridos para un tipo de documento"""
        examples_map = {
            DocumentType.API_DOCUMENTATION: ["Ejemplo de petición", "Ejemplo de respuesta", "Ejemplo de error"],
            DocumentType.IMPLEMENTATION_GUIDE: ["Ejemplo de configuración", "Ejemplo de código", "Ejemplo de despliegue"],
            DocumentType.TEST_CASES: ["Ejemplo de prueba unitaria", "Ejemplo de prueba de integración"],
            DocumentType.USER_MANUAL: ["Ejemplo de uso básico", "Ejemplo de configuración", "Ejemplo de flujo de trabajo"]
        }
        
        return examples_map.get(doc_type, ["Ejemplo básico"])
    
    def _get_document_priority(self, doc_type: DocumentType) -> int:
        """Obtiene la prioridad de generación de un documento"""
        priority_map = {
            DocumentType.TECHNICAL_SPEC: 1,
            DocumentType.API_DOCUMENTATION: 2,
            DocumentType.IMPLEMENTATION_GUIDE: 3,
            DocumentType.TEST_CASES: 4,
            DocumentType.USER_MANUAL: 5,
            DocumentType.ARCHITECTURE_DIAGRAM: 2,
            DocumentType.SECURITY_ANALYSIS: 3,
            DocumentType.DEPLOYMENT_GUIDE: 4,
            DocumentType.TROUBLESHOOTING: 5
        }
        
        return priority_map.get(doc_type, 5)
    
    async def _generate_documents_parallel(
        self, 
        document_plan: List[Dict[str, Any]], 
        request: ContinuousGenerationRequest
    ) -> List[GeneratedDocument]:
        """Genera documentos en paralelo"""
        logger.info(f"Generando {len(document_plan)} documentos en paralelo...")
        
        tasks = []
        for plan_item in document_plan:
            task = self._generate_single_document(plan_item, request)
            tasks.append(task)
        
        # Generar todos los documentos concurrentemente
        documents = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar excepciones
        valid_documents = []
        for i, doc in enumerate(documents):
            if isinstance(doc, Exception):
                logger.error(f"Error generando documento {i}: {doc}")
            else:
                valid_documents.append(doc)
        
        return valid_documents
    
    async def _generate_single_document(
        self, 
        plan_item: Dict[str, Any], 
        request: ContinuousGenerationRequest
    ) -> GeneratedDocument:
        """Genera un documento individual"""
        doc_type = DocumentType(plan_item['type'])
        logger.info(f"Generando documento: {plan_item['title']}")
        
        # Crear contenido del documento
        content = await self._create_document_content(plan_item, request)
        
        # Crear documento
        document = GeneratedDocument(
            id=f"{doc_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            title=plan_item['title'],
            type=doc_type,
            content=content,
            metadata={
                'plan_item': plan_item,
                'request_context': request.context,
                'generation_time': datetime.now().isoformat(),
                'ai_provider': self.ai_provider
            },
            created_at=datetime.now(),
            version="1.0.0",
            dependencies=plan_item.get('dependencies', []),
            quality_score=0.8,  # Simulado
            coherence_score=0.7  # Simulado
        )
        
        return document
    
    async def _create_document_content(
        self, 
        plan_item: Dict[str, Any], 
        request: ContinuousGenerationRequest
    ) -> str:
        """Crea el contenido de un documento"""
        doc_type = DocumentType(plan_item['type'])
        
        # Obtener plantilla base
        template = self._get_document_template(doc_type)
        
        # Generar contenido específico
        content = self._generate_content_from_template(template, plan_item, request)
        
        return content
    
    def _get_document_template(self, doc_type: DocumentType) -> str:
        """Obtiene la plantilla para un tipo de documento"""
        templates = {
            DocumentType.TECHNICAL_SPEC: """
# {title}

## Resumen Ejecutivo
{executive_summary}

## Introducción
{introduction}

## Arquitectura
{architecture}

## Especificaciones Técnicas
{technical_specifications}

## Casos de Uso
{use_cases}

## Consideraciones de Seguridad
{security_considerations}

## Implementación
{implementation}

## Referencias
{references}
""",
            DocumentType.API_DOCUMENTATION: """
# {title}

## Información General
{general_info}

## Autenticación
{authentication}

## Endpoints

### {endpoint_name}
- **Método**: {method}
- **URL**: {url}
- **Descripción**: {description}
- **Parámetros**: {parameters}
- **Respuesta**: {response}
- **Ejemplos**: {examples}

## Códigos de Error
{error_codes}

## Rate Limiting
{rate_limiting}
""",
            DocumentType.IMPLEMENTATION_GUIDE: """
# {title}

## Prerrequisitos
{prerequisites}

## Instalación
{installation}

## Configuración
{configuration}

## Despliegue
{deployment}

## Monitoreo
{monitoring}

## Troubleshooting
{troubleshooting}
"""
        }
        
        return templates.get(doc_type, """
# {title}

## Introducción
{introduction}

## Contenido Principal
{main_content}

## Conclusión
{conclusion}
""")
    
    def _generate_content_from_template(
        self, 
        template: str, 
        plan_item: Dict[str, Any], 
        request: ContinuousGenerationRequest
    ) -> str:
        """Genera contenido específico a partir de una plantilla"""
        # Simulación de generación de contenido
        # En producción, esto usaría IA real
        
        content_vars = {
            "title": plan_item["title"],
            "executive_summary": f"Este documento proporciona especificaciones técnicas para {plan_item['type']}.",
            "introduction": f"Introducción al sistema de {plan_item['type']} basado en los requisitos especificados.",
            "architecture": f"Arquitectura del sistema de {plan_item['type']} con componentes principales.",
            "technical_specifications": f"Especificaciones técnicas detalladas para {plan_item['type']}.",
            "use_cases": f"Casos de uso principales para {plan_item['type']}.",
            "security_considerations": f"Consideraciones de seguridad para {plan_item['type']}.",
            "implementation": f"Guía de implementación para {plan_item['type']}.",
            "references": "Referencias y enlaces útiles.",
            "general_info": f"Información general sobre la API de {plan_item['type']}.",
            "authentication": "Métodos de autenticación soportados.",
            "endpoint_name": "Ejemplo de Endpoint",
            "method": "GET",
            "url": "/api/example",
            "description": "Descripción del endpoint",
            "parameters": "Parámetros requeridos y opcionales",
            "response": "Formato de respuesta",
            "examples": "Ejemplos de uso",
            "error_codes": "Códigos de error comunes",
            "rate_limiting": "Límites de velocidad",
            "prerequisites": f"Prerrequisitos para implementar {plan_item['type']}.",
            "installation": f"Pasos de instalación para {plan_item['type']}.",
            "configuration": f"Configuración necesaria para {plan_item['type']}.",
            "deployment": f"Proceso de despliegue para {plan_item['type']}.",
            "monitoring": f"Configuración de monitoreo para {plan_item['type']}.",
            "troubleshooting": f"Resolución de problemas comunes para {plan_item['type']}.",
            "main_content": f"Contenido principal del documento de {plan_item['type']}.",
            "conclusion": f"Conclusión y próximos pasos para {plan_item['type']}."
        }
        
        # Reemplazar variables en la plantilla
        content = template
        for key, value in content_vars.items():
            content = content.replace(f"{{{key}}}", value)
        
        return content
    
    async def _validate_coherence(self, documents: List[GeneratedDocument]) -> List[GeneratedDocument]:
        """Valida y mejora la coherencia entre documentos"""
        logger.info("Validando coherencia entre documentos...")
        
        # Extraer terminología común
        terminology = self._extract_common_terminology(documents)
        
        # Unificar terminología
        unified_docs = self._unify_terminology(documents, terminology)
        
        # Gestionar referencias cruzadas
        referenced_docs = self._manage_cross_references(unified_docs)
        
        return referenced_docs
    
    def _extract_common_terminology(self, documents: List[GeneratedDocument]) -> Dict[str, str]:
        """Extrae terminología común de todos los documentos"""
        terminology = {}
        
        # Términos técnicos comunes
        common_terms = {
            "api": "API (Application Programming Interface)",
            "rest": "REST (Representational State Transfer)",
            "json": "JSON (JavaScript Object Notation)",
            "http": "HTTP (HyperText Transfer Protocol)",
            "database": "Base de datos",
            "authentication": "Autenticación",
            "authorization": "Autorización",
            "security": "Seguridad",
            "deployment": "Despliegue",
            "monitoring": "Monitoreo"
        }
        
        # Buscar términos en el contenido
        for doc in documents:
            content_lower = doc.content.lower()
            for term, definition in common_terms.items():
                if term in content_lower:
                    terminology[term] = definition
        
        return terminology
    
    def _unify_terminology(self, documents: List[GeneratedDocument], terminology: Dict[str, str]) -> List[GeneratedDocument]:
        """Unifica la terminología en todos los documentos"""
        unified_docs = []
        
        for document in documents:
            content = document.content
            
            # Aplicar unificación de terminología
            for term, definition in terminology.items():
                # Reemplazar términos con definiciones estándar
                content = content.replace(term, f"{term} ({definition})")
            
            document.content = content
            unified_docs.append(document)
        
        return unified_docs
    
    def _manage_cross_references(self, documents: List[GeneratedDocument]) -> List[GeneratedDocument]:
        """Gestiona referencias cruzadas entre documentos"""
        # Crear mapa de referencias
        reference_map = {}
        for doc in documents:
            reference_map[doc.title] = f"[{doc.title}](#{doc.id})"
            reference_map[doc.type.value] = f"[{doc.title}](#{doc.id})"
        
        # Actualizar referencias en cada documento
        updated_docs = []
        for document in documents:
            content = document.content
            
            # Agregar sección de referencias relacionadas
            related_docs = [ref for ref in reference_map.values() if ref != f"[{document.title}](#{document.id})"]
            if related_docs:
                references_section = "\n\n## Documentos Relacionados\n" + "\n".join(related_docs)
                content += references_section
            
            document.content = content
            updated_docs.append(document)
        
        return updated_docs
    
    async def _post_process_documents(self, documents: List[GeneratedDocument]) -> List[GeneratedDocument]:
        """Post-procesa los documentos para mejorar calidad"""
        logger.info("Post-procesando documentos...")
        
        processed_documents = []
        
        for document in documents:
            # Validar calidad básica
            quality_score = self._calculate_quality_score(document)
            document.quality_score = quality_score
            
            # Calcular coherencia
            coherence_score = self._calculate_coherence_score(document, documents)
            document.coherence_score = coherence_score
            
            # Aplicar mejoras si es necesario
            if quality_score < 0.7:
                document.content = self._improve_document_content(document)
                document.quality_score = min(quality_score + 0.1, 1.0)
            
            processed_documents.append(document)
        
        return processed_documents
    
    def _calculate_quality_score(self, document: GeneratedDocument) -> float:
        """Calcula un score de calidad básico"""
        content = document.content
        
        # Factores de calidad
        length_score = min(len(content) / 1000, 1.0)  # Longitud adecuada
        structure_score = 1.0 if "#" in content else 0.5  # Estructura con headers
        examples_score = 1.0 if "ejemplo" in content.lower() else 0.7  # Incluye ejemplos
        
        # Score promedio
        quality_score = (length_score + structure_score + examples_score) / 3
        return min(quality_score, 1.0)
    
    def _calculate_coherence_score(self, document: GeneratedDocument, all_documents: List[GeneratedDocument]) -> float:
        """Calcula un score de coherencia básico"""
        # Simulación de cálculo de coherencia
        # En producción, esto sería más sofisticado
        
        coherence_score = 0.8  # Base score
        
        # Ajustar basado en dependencias
        if document.dependencies:
            coherence_score += 0.1
        
        # Ajustar basado en referencias cruzadas
        if "## Documentos Relacionados" in document.content:
            coherence_score += 0.1
        
        return min(coherence_score, 1.0)
    
    def _improve_document_content(self, document: GeneratedDocument) -> str:
        """Mejora el contenido de un documento"""
        content = document.content
        
        # Agregar sección de mejoras si no existe
        if "## Mejoras y Optimizaciones" not in content:
            improvements_section = """
## Mejoras y Optimizaciones

### Optimizaciones de Rendimiento
- Implementar caché para consultas frecuentes
- Optimizar consultas a base de datos
- Usar compresión para respuestas grandes

### Mejoras de Seguridad
- Implementar validación de entrada
- Usar HTTPS en todas las comunicaciones
- Aplicar principios de seguridad por defecto

### Escalabilidad
- Diseñar para escalabilidad horizontal
- Implementar balanceadores de carga
- Usar bases de datos distribuidas cuando sea necesario
"""
            content += improvements_section
        
        return content
    
    def get_generation_time(self) -> float:
        """Obtiene el tiempo total de generación"""
        if self.generation_start_time:
            return (datetime.now() - self.generation_start_time).total_seconds()
        return 0.0
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de calidad de los documentos generados"""
        if not self.generated_documents:
            return {}
        
        quality_scores = [doc.quality_score for doc in self.generated_documents]
        coherence_scores = [doc.coherence_score for doc in self.generated_documents]
        
        return {
            'average_quality': sum(quality_scores) / len(quality_scores),
            'average_coherence': sum(coherence_scores) / len(coherence_scores),
            'min_quality': min(quality_scores),
            'max_quality': max(quality_scores),
            'total_documents': len(self.generated_documents)
        }
    
    async def save_documents(self, documents: List[GeneratedDocument], output_dir: str = "generated_docs") -> Dict[str, str]:
        """Guarda los documentos generados en archivos"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        saved_files = {}
        
        for document in documents:
            # Crear nombre de archivo
            filename = f"{document.id}_{document.type.value}.md"
            filepath = output_path / filename
            
            # Agregar metadatos al contenido
            content_with_metadata = f"""---
id: {document.id}
title: {document.title}
type: {document.type.value}
version: {document.version}
created_at: {document.created_at.isoformat()}
quality_score: {document.quality_score}
coherence_score: {document.coherence_score}
dependencies: {document.dependencies}
metadata: {json.dumps(document.metadata, indent=2, ensure_ascii=False)}
---

{document.content}
"""
            
            # Guardar archivo
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content_with_metadata)
            
            saved_files[document.id] = str(filepath)
            logger.info(f"Documento guardado: {filepath}")
        
        return saved_files

# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

async def example_api_documentation():
    """Ejemplo: Generación de documentación de API"""
    print("=" * 60)
    print("EJEMPLO 1: Documentación de API REST")
    print("=" * 60)
    
    request = ContinuousGenerationRequest(
        query="Genera documentación completa para una API REST de gestión de usuarios con autenticación JWT, operaciones CRUD, y sistema de roles",
        document_types=[
            DocumentType.TECHNICAL_SPEC,
            DocumentType.API_DOCUMENTATION,
            DocumentType.IMPLEMENTATION_GUIDE,
            DocumentType.TEST_CASES,
            DocumentType.SECURITY_ANALYSIS
        ],
        context={
            "framework": "FastAPI",
            "database": "PostgreSQL",
            "authentication": "JWT",
            "deployment": "Docker"
        },
        max_documents=5
    )
    
    generator = ContinuousDocumentGenerator()
    
    async with generator:
        documents = await generator.generate_continuous_documents(request)
    
    # Mostrar resultados
    print(f"\n✅ Generados {len(documents)} documentos:")
    for i, doc in enumerate(documents, 1):
        print(f"  {i}. {doc.title}")
        print(f"     Tipo: {doc.type.value}")
        print(f"     Calidad: {doc.quality_score:.2f}")
        print(f"     Coherencia: {doc.coherence_score:.2f}")
        print(f"     Dependencias: {len(doc.dependencies)}")
        print()
    
    # Guardar documentos
    saved_files = await generator.save_documents(documents, "output/api_docs")
    print(f"📁 Documentos guardados en: {list(saved_files.values())}")
    
    # Mostrar métricas
    metrics = generator.get_quality_metrics()
    print(f"\n📊 Métricas de calidad:")
    print(f"  - Calidad promedio: {metrics['average_quality']:.2f}")
    print(f"  - Coherencia promedio: {metrics['average_coherence']:.2f}")
    print(f"  - Tiempo de generación: {generator.get_generation_time():.2f}s")
    
    return documents

async def example_microservices_architecture():
    """Ejemplo: Documentación de arquitectura de microservicios"""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Arquitectura de Microservicios")
    print("=" * 60)
    
    request = ContinuousGenerationRequest(
        query="Crea documentación completa para una arquitectura de microservicios con API Gateway, service mesh, base de datos distribuida, y sistema de monitoreo",
        document_types=[
            DocumentType.ARCHITECTURE_DIAGRAM,
            DocumentType.TECHNICAL_SPEC,
            DocumentType.IMPLEMENTATION_GUIDE,
            DocumentType.DEPLOYMENT_GUIDE,
            DocumentType.PERFORMANCE_REPORT,
            DocumentType.TROUBLESHOOTING
        ],
        context={
            "pattern": "microservices",
            "gateway": "Kong",
            "service_mesh": "Istio",
            "database": "CockroachDB",
            "monitoring": "Prometheus + Grafana",
            "orchestration": "Kubernetes"
        },
        max_documents=6
    )
    
    generator = ContinuousDocumentGenerator()
    
    async with generator:
        documents = await generator.generate_continuous_documents(request)
    
    # Mostrar resultados
    print(f"\n✅ Generados {len(documents)} documentos:")
    for i, doc in enumerate(documents, 1):
        print(f"  {i}. {doc.title}")
        print(f"     Tipo: {doc.type.value}")
        print(f"     Calidad: {doc.quality_score:.2f}")
        print(f"     Coherencia: {doc.coherence_score:.2f}")
        print()
    
    # Guardar documentos
    saved_files = await generator.save_documents(documents, "output/microservices_docs")
    print(f"📁 Documentos guardados en: {list(saved_files.values())}")
    
    return documents

async def example_websocket_progress():
    """Ejemplo: Simulación de progreso en tiempo real"""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Progreso en Tiempo Real")
    print("=" * 60)
    
    request = ContinuousGenerationRequest(
        query="Genera documentación para un sistema de e-commerce con carrito de compras, procesamiento de pagos, y gestión de inventario",
        document_types=[
            DocumentType.TECHNICAL_SPEC,
            DocumentType.API_DOCUMENTATION,
            DocumentType.USER_MANUAL,
            DocumentType.TEST_CASES
        ],
        max_documents=4
    )
    
    generator = ContinuousDocumentGenerator()
    
    # Simular progreso en tiempo real
    async with generator:
        print("🚀 Iniciando generación...")
        
        # Análisis
        await asyncio.sleep(0.5)
        print("📊 Analizando petición...")
        
        # Planificación
        await asyncio.sleep(0.5)
        print("📋 Creando plan de documentos...")
        
        # Generación
        total_docs = len(request.document_types)
        for i, doc_type in enumerate(request.document_types):
            await asyncio.sleep(0.3)
            progress = int((i / total_docs) * 100)
            print(f"📝 Generando {doc_type.value}... ({progress}%)")
        
        # Validación
        await asyncio.sleep(0.5)
        print("✅ Validando coherencia...")
        
        # Post-procesamiento
        await asyncio.sleep(0.3)
        print("🔧 Post-procesando documentos...")
        
        # Generar documentos reales
        documents = await generator.generate_continuous_documents(request)
    
    print(f"\n🎉 Generación completada: {len(documents)} documentos")
    print(f"⏱️  Tiempo total: {generator.get_generation_time():.2f}s")
    
    return documents

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

async def main():
    """Función principal que ejecuta todos los ejemplos"""
    print("🤖 IA Generadora Continua de Documentos")
    print("Sistema de Especificaciones Técnicas Blatam Academy")
    print("Versión 1.0.0")
    print()
    
    try:
        # Ejecutar ejemplos
        await example_api_documentation()
        await example_microservices_architecture()
        await example_websocket_progress()
        
        print("\n" + "=" * 60)
        print("✅ TODOS LOS EJEMPLOS COMPLETADOS EXITOSAMENTE")
        print("=" * 60)
        
        print("\n📚 Documentos generados:")
        print("  - output/api_docs/ - Documentación de API REST")
        print("  - output/microservices_docs/ - Arquitectura de Microservicios")
        
        print("\n🔧 Características demostradas:")
        print("  ✅ Generación continua de múltiples documentos")
        print("  ✅ Coherencia inter-documental")
        print("  ✅ Validación de calidad")
        print("  ✅ Gestión de dependencias")
        print("  ✅ Progreso en tiempo real")
        print("  ✅ Almacenamiento estructurado")
        
    except Exception as e:
        logger.error(f"Error en ejecución principal: {e}")
        raise

if __name__ == "__main__":
    # Ejecutar el ejemplo
    asyncio.run(main())


















