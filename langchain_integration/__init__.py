"""
ONYX BLOG POST - LangChain Integration Module
============================================

Integración con LangChain para manejo avanzado de prompts y chains.
Incluye templates, chains personalizadas y prompt engineering.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime

# LangChain imports
try:
    from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage
    from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
    from langchain.chains import LLMChain, SequentialChain
    from langchain.memory import ConversationBufferMemory
    from langchain.callbacks import AsyncCallbackHandler
    from langchain.schema.runnable import Runnable
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Fallback classes
    class BaseMessage:
        pass
    class PromptTemplate:
        pass
    class ChatPromptTemplate:
        pass
    class LLMChain:
        pass

from ..models import BlogPostRequest, BlogPostType, BlogPostTone, BlogPostLength, LangChainPrompt
from ..openrouter_client import OpenRouterClient, OpenRouterModelManager

logger = logging.getLogger(__name__)

class OnyxCallbackHandler:
    """Callback handler personalizado para Onyx"""
    
    def __init__(self):
        self.start_time = None
        self.tokens_used = 0
        self.cost = 0.0
        self.steps = []
    
    async def on_llm_start(self, serialized, prompts, **kwargs):
        """Cuando inicia el LLM"""
        self.start_time = datetime.now()
        logger.debug("LLM chain started")
    
    async def on_llm_end(self, response, **kwargs):
        """Cuando termina el LLM"""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            logger.debug(f"LLM chain completed in {duration:.2f}s")
    
    async def on_chain_start(self, serialized, inputs, **kwargs):
        """Cuando inicia una chain"""
        logger.debug(f"Chain started: {serialized.get('name', 'unknown')}")
    
    async def on_chain_end(self, outputs, **kwargs):
        """Cuando termina una chain"""
        logger.debug("Chain completed successfully")

class BlogPostPromptTemplates:
    """Templates de prompts para blog posts"""
    
    def __init__(self):
        self.system_prompts = {
            "base": """Eres un experto escritor de blog posts profesional especializado en crear contenido de alta calidad, SEO-optimizado y engaging para diferentes audiencias.

Tus responsabilidades:
- Crear contenido original, bien estructurado y valioso
- Optimizar para SEO con palabras clave naturalmente integradas
- Adaptar el tono y estilo según la audiencia objetivo
- Incluir calls-to-action efectivos
- Mantener coherencia y fluidez en todo el texto

Siempre produces contenido en formato JSON estructurado.""",

            "technical": """Eres un experto technical writer especializado en contenido técnico, tutoriales y documentación.

Características de tu escritura:
- Explicaciones claras de conceptos complejos
- Ejemplos prácticos y casos de uso
- Estructura lógica paso a paso
- Terminología técnica precisa pero accesible
- Code snippets cuando sea apropiado

Enfócate en educación y valor práctico para desarrolladores y profesionales técnicos.""",

            "marketing": """Eres un experto content marketer especializado en crear contenido que convierte y engage.

Tu enfoque incluye:
- Headlines irresistibles y hooks potentes
- Storytelling persuasivo
- Beneficios claros y value propositions
- Social proof y credibilidad
- CTAs que generan acción

Combinas creatividad con estrategia de marketing basada en datos."""
        }
        
        self.user_prompts = {
            "blog_post_generation": """Crea un blog post completo sobre: "{topic}"

Parámetros:
- Tipo: {blog_type}
- Tono: {tone}
- Audiencia: {target_audience}
- Longitud objetivo: {min_words}-{max_words} palabras
- Idioma: {language}
- Keywords: {keywords}
- Contexto adicional: {context}

{outline_instruction}

Estructura requerida en JSON:
{{
    "title": "Título principal del blog post",
    "introduction": "Introducción engaging que capte la atención",
    "main_sections": [
        {{
            "title": "Título de la sección",
            "content": "Contenido detallado de la sección"
        }}
    ],
    "conclusion": "Conclusión que refuerce el mensaje principal",
    "call_to_action": "CTA específico y accionable"
}}

Asegúrate de:
1. Integrar las keywords naturalmente
2. Mantener el tono especificado consistentemente
3. Crear contenido valioso para la audiencia objetivo
4. Incluir transiciones fluidas entre secciones
5. Optimizar para legibilidad y engagement""",

            "seo_optimization": """Optimiza el SEO del siguiente blog post:

Título: {title}
Contenido: {content}
Keywords principales: {keywords}
Audiencia: {target_audience}

Genera metadata SEO en JSON:
{{
    "meta_title": "Título optimizado para SEO (máx 60 caracteres)",
    "meta_description": "Descripción compelling (máx 160 caracteres)",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "og_title": "Título para Open Graph",
    "og_description": "Descripción para redes sociales",
    "schema_markup": {{
        "@type": "Article",
        "headline": "...",
        "description": "...",
        "keywords": "..."
    }}
}}""",

            "content_improvement": """Mejora y refina el siguiente contenido de blog post:

Contenido actual:
{content}

Objetivos de mejora:
- Hacer más engaging y readable
- Mejorar estructura y flow
- Añadir ejemplos o casos de uso
- Optimizar calls-to-action
- Corregir errores y mejorar claridad

Devuelve el contenido mejorado manteniendo la estructura JSON original."""
        }
        
        if LANGCHAIN_AVAILABLE:
            self._create_langchain_templates()
    
    def _create_langchain_templates(self):
        """Crear templates de LangChain"""
        # Template principal para generación
        self.main_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_prompts["base"]),
            HumanMessagePromptTemplate.from_template(self.user_prompts["blog_post_generation"])
        ])
        
        # Template para SEO
        self.seo_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_prompts["marketing"]),
            HumanMessagePromptTemplate.from_template(self.user_prompts["seo_optimization"])
        ])
        
        # Template para mejoras
        self.improvement_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_prompts["base"]),
            HumanMessagePromptTemplate.from_template(self.user_prompts["content_improvement"])
        ])
    
    def get_system_prompt(self, prompt_type: str = "base") -> str:
        """Obtener system prompt"""
        return self.system_prompts.get(prompt_type, self.system_prompts["base"])
    
    def get_user_prompt(self, prompt_type: str) -> str:
        """Obtener user prompt"""
        return self.user_prompts.get(prompt_type, "")
    
    def format_blog_post_prompt(self, request: BlogPostRequest) -> LangChainPrompt:
        """Formatear prompt para generar blog post"""
        # Determinar system prompt basado en tipo
        system_prompt_type = "technical" if request.blog_type in [BlogPostType.TECHNICAL, BlogPostType.TUTORIAL] else "base"
        system_prompt = self.get_system_prompt(system_prompt_type)
        
        # Preparar outline instruction
        outline_instruction = ""
        if request.outline:
            outline_instruction = f"Outline sugerido:\n" + "\n".join(f"- {item}" for item in request.outline)
        else:
            outline_instruction = "Crea un outline lógico y bien estructurado."
        
        # Variables para el prompt
        variables = {
            "topic": request.topic,
            "blog_type": request.blog_type.value,
            "tone": request.tone.value,
            "target_audience": request.target_audience,
            "min_words": request.length.min_words,
            "max_words": request.length.max_words,
            "language": request.language,
            "keywords": ", ".join(request.keywords) if request.keywords else "N/A",
            "context": request.context or "N/A",
            "outline_instruction": outline_instruction
        }
        
        user_prompt = self.get_user_prompt("blog_post_generation")
        
        return LangChainPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            variables=variables,
            constraints=[
                f"Mínimo {request.length.min_words} palabras",
                f"Máximo {request.length.max_words} palabras",
                f"Tono: {request.tone.value}",
                "Formato JSON válido requerido",
                "Integración natural de keywords"
            ]
        )

class OnyxLLMWrapper:
    """Wrapper para usar OpenRouter con LangChain"""
    
    def __init__(self, openrouter_client: OpenRouterClient, model: str):
        self.client = openrouter_client
        self.model = model
        self.callback_handler = OnyxCallbackHandler()
    
    async def agenerate(self, messages: List[BaseMessage], **kwargs) -> str:
        """Generar respuesta async"""
        # Convertir mensajes de LangChain a formato OpenRouter
        or_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                or_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                or_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                or_messages.append({"role": "assistant", "content": msg.content})
        
        # Crear request para OpenRouter
        from ..models import OpenRouterRequest
        or_request = OpenRouterRequest(
            model=self.model,
            messages=or_messages,
            **kwargs
        )
        
        # Hacer llamada
        response = await self.client.complete(or_request)
        return response.get_content()

class BlogPostChain:
    """Chain personalizada para generar blog posts"""
    
    def __init__(
        self,
        openrouter_client: OpenRouterClient,
        model_manager: OpenRouterModelManager,
        prompt_templates: BlogPostPromptTemplates
    ):
        self.client = openrouter_client
        self.model_manager = model_manager
        self.templates = prompt_templates
        self.memory = ConversationBufferMemory() if LANGCHAIN_AVAILABLE else None
        
    async def generate_blog_post(
        self,
        request: BlogPostRequest,
        use_langchain: bool = True
    ) -> Dict[str, Any]:
        """Generar blog post usando chain"""
        
        if use_langchain and LANGCHAIN_AVAILABLE:
            return await self._generate_with_langchain(request)
        else:
            return await self._generate_direct(request)
    
    async def _generate_with_langchain(self, request: BlogPostRequest) -> Dict[str, Any]:
        """Generar usando LangChain chains"""
        # Crear prompt
        prompt_data = self.templates.format_blog_post_prompt(request)
        
        # Crear LLM wrapper
        best_model = self.model_manager.get_best_model_for_task(request.blog_type.value)
        llm_wrapper = OnyxLLMWrapper(self.client, best_model.value)
        
        # Crear mensajes
        messages = [
            SystemMessage(content=prompt_data.system_prompt),
            HumanMessage(content=prompt_data.format_prompt())
        ]
        
        # Generar
        result = await llm_wrapper.agenerate(messages)
        
        return {
            "content": result,
            "model_used": best_model.value,
            "tokens_used": llm_wrapper.callback_handler.tokens_used,
            "cost": llm_wrapper.callback_handler.cost
        }
    
    async def _generate_direct(self, request: BlogPostRequest) -> Dict[str, Any]:
        """Generar directamente con OpenRouter"""
        # Crear prompt
        prompt_data = self.templates.format_blog_post_prompt(request)
        
        # Seleccionar modelo
        best_model = self.model_manager.get_best_model_for_task(request.blog_type.value)
        
        # Crear request optimizado
        or_request = await self.model_manager.create_optimized_request(
            model=best_model,
            messages=[
                {"role": "system", "content": prompt_data.system_prompt},
                {"role": "user", "content": prompt_data.format_prompt()}
            ]
        )
        
        # Generar
        response = await self.client.complete(or_request)
        
        return {
            "content": response.get_content(),
            "model_used": best_model.value,
            "tokens_used": response.get_tokens_used(),
            "cost": 0.0  # Se calcula en el cliente
        }
    
    async def generate_seo_metadata(
        self,
        title: str,
        content: str,
        keywords: List[str],
        target_audience: str
    ) -> Dict[str, Any]:
        """Generar metadata SEO"""
        seo_prompt = self.templates.get_user_prompt("seo_optimization").format(
            title=title,
            content=content[:1000],  # Truncar para el prompt
            keywords=", ".join(keywords),
            target_audience=target_audience
        )
        
        messages = [
            {"role": "system", "content": self.templates.get_system_prompt("marketing")},
            {"role": "user", "content": seo_prompt}
        ]
        
        from ..models import OpenRouterRequest
        or_request = OpenRouterRequest(
            model="openai/gpt-4-turbo",
            messages=messages,
            temperature=0.3  # Más determinístico para SEO
        )
        
        response = await self.client.complete(or_request)
        return {
            "content": response.get_content(),
            "tokens_used": response.get_tokens_used()
        }
    
    async def improve_content(self, content: str) -> Dict[str, Any]:
        """Mejorar contenido existente"""
        improvement_prompt = self.templates.get_user_prompt("content_improvement").format(
            content=content
        )
        
        messages = [
            {"role": "system", "content": self.templates.get_system_prompt("base")},
            {"role": "user", "content": improvement_prompt}
        ]
        
        from ..models import OpenRouterRequest
        or_request = OpenRouterRequest(
            model="openai/gpt-4-turbo",
            messages=messages,
            temperature=0.5
        )
        
        response = await self.client.complete(or_request)
        return {
            "content": response.get_content(),
            "tokens_used": response.get_tokens_used()
        }

class LangChainOrchestrator:
    """Orquestador principal para LangChain integration"""
    
    def __init__(self, openrouter_client: OpenRouterClient):
        self.client = openrouter_client
        self.model_manager = OpenRouterModelManager(openrouter_client)
        self.prompt_templates = BlogPostPromptTemplates()
        self.blog_chain = BlogPostChain(
            openrouter_client,
            self.model_manager, 
            self.prompt_templates
        )
        
        logger.info(f"LangChain integration initialized (available: {LANGCHAIN_AVAILABLE})")
    
    async def generate_complete_blog_post(
        self,
        request: BlogPostRequest,
        include_seo: bool = True,
        improve_content: bool = False
    ) -> Dict[str, Any]:
        """Generar blog post completo con todas las features"""
        
        # 1. Generar contenido principal
        main_result = await self.blog_chain.generate_blog_post(request)
        
        result = {
            "main_content": main_result["content"],
            "model_used": main_result["model_used"],
            "total_tokens": main_result["tokens_used"],
            "total_cost": main_result.get("cost", 0.0)
        }
        
        # 2. Generar SEO metadata si se solicita
        if include_seo and request.include_seo:
            try:
                # Extraer título del contenido para SEO
                import json
                content_json = json.loads(main_result["content"])
                title = content_json.get("title", request.topic)
                
                seo_result = await self.blog_chain.generate_seo_metadata(
                    title=title,
                    content=main_result["content"],
                    keywords=request.keywords,
                    target_audience=request.target_audience
                )
                
                result["seo_metadata"] = seo_result["content"]
                result["total_tokens"] += seo_result["tokens_used"]
                
            except Exception as e:
                logger.warning(f"SEO generation failed: {e}")
                result["seo_metadata"] = None
        
        # 3. Mejorar contenido si se solicita
        if improve_content:
            try:
                improved_result = await self.blog_chain.improve_content(main_result["content"])
                result["improved_content"] = improved_result["content"]
                result["total_tokens"] += improved_result["tokens_used"]
            except Exception as e:
                logger.warning(f"Content improvement failed: {e}")
        
        return result
    
    def get_available_models(self) -> List[str]:
        """Obtener modelos disponibles"""
        return [model.value for model in self.model_manager.model_configs.keys()]
    
    def get_model_recommendations(self, blog_type: BlogPostType) -> Dict[str, Any]:
        """Obtener recomendaciones de modelo para tipo de blog"""
        best_model = self.model_manager.get_best_model_for_task(blog_type.value)
        config = self.model_manager.get_model_config(best_model)
        
        return {
            "recommended_model": best_model.value,
            "config": config,
            "alternatives": [
                model.value for model in self.model_manager.model_configs.keys()
                if model != best_model
            ][:3]
        }

# Factory function
def create_langchain_orchestrator(openrouter_client: OpenRouterClient) -> LangChainOrchestrator:
    """Factory para crear orchestrator de LangChain"""
    return LangChainOrchestrator(openrouter_client)

__all__ = [
    'OnyxCallbackHandler',
    'BlogPostPromptTemplates',
    'OnyxLLMWrapper',
    'BlogPostChain',
    'LangChainOrchestrator',
    'create_langchain_orchestrator',
    'LANGCHAIN_AVAILABLE',
] 