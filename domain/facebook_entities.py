"""
🎯 Facebook Posts - Domain Entities
===================================

Entidades del dominio core para Facebook posts siguiendo Clean Architecture.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib
import uuid
from dataclasses import dataclass, field

from ..interfaces.facebook_interfaces import (
    PostIdentifier, PostSpecification, PostContent, AnalysisResult,
    ContentMetrics, EngagementMetrics, QualityScores, PostType,
    ContentTone, TargetAudience, AnalysisStatus, ContentQuality,
    FacebookPostError, ValidationError
)


class FacebookPostEntity:
    """Entidad principal del dominio - Facebook Post."""
    
    def __init__(
        self,
        identifier: PostIdentifier,
        specification: PostSpecification,
        content: PostContent,
        analysis: Optional[AnalysisResult] = None
    ):
        self._validate_inputs(identifier, specification, content)
        
        self._identifier = identifier
        self._specification = specification
        self._content = content
        self._analysis = analysis
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        self._version = 1
        self._status = "draft"
        self._metadata: Dict[str, Any] = {}
    
    def _validate_inputs(
        self, 
        identifier: PostIdentifier, 
        specification: PostSpecification, 
        content: PostContent
    ) -> None:
        """Validar inputs de creación."""
        if not identifier or not identifier.post_id:
            raise ValidationError("Post identifier is required")
        
        if not specification or not specification.topic:
            raise ValidationError("Post specification with topic is required")
        
        if not content or not content.text.strip():
            raise ValidationError("Post content with text is required")
        
        if len(content.text) > 2000:
            raise ValidationError("Content exceeds Facebook's 2000 character limit")
    
    # ===== PROPERTIES =====
    
    @property
    def identifier(self) -> PostIdentifier:
        """Identificador único del post."""
        return self._identifier
    
    @property
    def specification(self) -> PostSpecification:
        """Especificación del post."""
        return self._specification
    
    @property
    def content(self) -> PostContent:
        """Contenido del post."""
        return self._content
    
    @property
    def analysis(self) -> Optional[AnalysisResult]:
        """Resultado de análisis."""
        return self._analysis
    
    @property
    def created_at(self) -> datetime:
        """Fecha de creación."""
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        """Fecha de última actualización."""
        return self._updated_at
    
    @property
    def version(self) -> int:
        """Versión del post."""
        return self._version
    
    @property
    def status(self) -> str:
        """Estado del post."""
        return self._status
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Metadata adicional."""
        return self._metadata.copy()
    
    # ===== BUSINESS METHODS =====
    
    def update_content(self, new_content: PostContent) -> None:
        """Actualizar contenido del post."""
        if not new_content or not new_content.text.strip():
            raise ValidationError("New content cannot be empty")
        
        if len(new_content.text) > 2000:
            raise ValidationError("New content exceeds Facebook's character limit")
        
        self._content = new_content
        self._updated_at = datetime.now()
        self._version += 1
        
        # Invalidar análisis anterior
        self._analysis = None
    
    def set_analysis(self, analysis: AnalysisResult) -> None:
        """Establecer resultado de análisis."""
        if not analysis:
            raise ValidationError("Analysis result is required")
        
        self._analysis = analysis
        self._updated_at = datetime.now()
    
    def update_specification(self, new_spec: PostSpecification) -> None:
        """Actualizar especificación."""
        if not new_spec:
            raise ValidationError("New specification is required")
        
        self._specification = new_spec
        self._updated_at = datetime.now()
        self._version += 1
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Agregar metadata."""
        if not key:
            raise ValidationError("Metadata key cannot be empty")
        
        self._metadata[key] = value
        self._updated_at = datetime.now()
    
    def update_status(self, new_status: str) -> None:
        """Actualizar estado."""
        valid_statuses = ["draft", "reviewed", "approved", "published", "archived"]
        if new_status not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {valid_statuses}")
        
        self._status = new_status
        self._updated_at = datetime.now()
    
    # ===== COMPUTED PROPERTIES =====
    
    def get_display_text(self) -> str:
        """Obtener texto completo para mostrar."""
        text = self._content.text
        
        if self._content.hashtags:
            hashtag_text = " ".join(f"#{tag}" for tag in self._content.hashtags)
            text += f"\n\n{hashtag_text}"
        
        return text
    
    def get_character_count(self) -> int:
        """Obtener conteo total de caracteres."""
        return len(self.get_display_text())
    
    def is_within_facebook_limits(self) -> bool:
        """Verificar si cumple límites de Facebook."""
        return self.get_character_count() <= 2000
    
    def get_content_metrics(self) -> ContentMetrics:
        """Calcular métricas de contenido."""
        text = self._content.text
        
        return ContentMetrics(
            character_count=len(text),
            word_count=len(text.split()),
            hashtag_count=len(self._content.hashtags),
            mention_count=len(self._content.mentions),
            emoji_count=self._count_emojis(text),
            link_count=len(self._content.media_urls) + (1 if self._content.link_url else 0)
        )
    
    def get_engagement_prediction(self) -> float:
        """Obtener predicción de engagement."""
        if self._analysis:
            return self._analysis.quality_scores.engagement_prediction
        return 0.5  # Neutral default
    
    def get_quality_level(self) -> ContentQuality:
        """Obtener nivel de calidad."""
        if self._analysis:
            return self._analysis.quality_scores.overall_quality
        return ContentQuality.FAIR  # Default
    
    def has_call_to_action(self) -> bool:
        """Verificar si tiene call-to-action."""
        cta_patterns = [
            "click", "tap", "visit", "check out", "learn more", "read more",
            "buy now", "shop now", "order", "get yours", "sign up", "register",
            "subscribe", "follow", "join", "download", "try", "start",
            "comment", "share", "like", "tag", "call", "contact"
        ]
        
        text_lower = self._content.text.lower()
        return any(pattern in text_lower for pattern in cta_patterns)
    
    def has_multimedia(self) -> bool:
        """Verificar si tiene contenido multimedia."""
        return bool(self._content.media_urls or self._content.link_url)
    
    def get_audience_match_score(self) -> float:
        """Calcular score de match con audiencia objetivo."""
        # Lógica simplificada - en implementación real sería más compleja
        base_score = 0.5
        
        # Ajustar por tono vs audiencia
        tone_audience_match = {
            (ContentTone.PROFESSIONAL, TargetAudience.PROFESSIONALS): 0.9,
            (ContentTone.CASUAL, TargetAudience.YOUNG_ADULTS): 0.9,
            (ContentTone.EDUCATIONAL, TargetAudience.STUDENTS): 0.9,
            (ContentTone.INSPIRING, TargetAudience.ENTREPRENEURS): 0.9,
        }
        
        match_key = (self._specification.tone, self._specification.target_audience)
        if match_key in tone_audience_match:
            base_score = tone_audience_match[match_key]
        
        # Ajustar por presencia de hashtags relevantes
        if self._content.hashtags:
            base_score += 0.1
        
        # Ajustar por call-to-action
        if self.has_call_to_action():
            base_score += 0.1
        
        return min(1.0, base_score)
    
    # ===== HELPER METHODS =====
    
    def _count_emojis(self, text: str) -> int:
        """Contar emojis en el texto."""
        import re
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "]+", flags=re.UNICODE
        )
        return len(emoji_pattern.findall(text))
    
    # ===== VALIDATION METHODS =====
    
    def validate_for_publication(self) -> List[str]:
        """Validar post para publicación."""
        errors = []
        
        # Validar longitud
        if not self.is_within_facebook_limits():
            errors.append("Post exceeds Facebook's character limit")
        
        # Validar contenido mínimo
        if len(self._content.text.strip()) < 10:
            errors.append("Post content is too short")
        
        # Validar hashtags
        if len(self._content.hashtags) > 10:
            errors.append("Too many hashtags (max 10 recommended)")
        
        # Validar estado
        if self._status == "draft":
            errors.append("Post is still in draft status")
        
        return errors
    
    def is_ready_for_publication(self) -> bool:
        """Verificar si está listo para publicación."""
        return len(self.validate_for_publication()) == 0
    
    # ===== COMPARISON METHODS =====
    
    def __eq__(self, other) -> bool:
        """Comparar posts por identidad."""
        if not isinstance(other, FacebookPostEntity):
            return False
        return self._identifier.post_id == other._identifier.post_id
    
    def __hash__(self) -> int:
        """Hash basado en ID."""
        return hash(self._identifier.post_id)
    
    def __str__(self) -> str:
        """Representación string."""
        return f"FacebookPost(id={self._identifier.post_id}, topic={self._specification.topic})"
    
    def __repr__(self) -> str:
        """Representación detallada."""
        return (
            f"FacebookPostEntity("
            f"id={self._identifier.post_id}, "
            f"topic={self._specification.topic}, "
            f"type={self._specification.post_type}, "
            f"status={self._status})"
        )


# ===== FACTORY METHODS =====

class FacebookPostFactory:
    """Factory para crear posts de Facebook."""
    
    @staticmethod
    def create_new_post(
        topic: str,
        content_text: str,
        post_type: PostType = PostType.TEXT,
        tone: ContentTone = ContentTone.CASUAL,
        target_audience: TargetAudience = TargetAudience.GENERAL,
        keywords: Optional[List[str]] = None,
        hashtags: Optional[List[str]] = None,
        **kwargs
    ) -> FacebookPostEntity:
        """Crear nuevo post con configuración básica."""
        
        # Crear identificador
        post_id = str(uuid.uuid4())
        content_hash = hashlib.md5(content_text.encode()).hexdigest()
        identifier = PostIdentifier(
            post_id=post_id,
            content_hash=content_hash,
            created_at=datetime.now()
        )
        
        # Crear especificación
        from ..interfaces.facebook_interfaces import PostSpecification, GenerationConfig
        
        config = GenerationConfig(
            max_length=kwargs.get('max_length', 280),
            include_hashtags=kwargs.get('include_hashtags', True),
            include_emojis=kwargs.get('include_emojis', True),
            include_call_to_action=kwargs.get('include_call_to_action', True),
            target_engagement=kwargs.get('target_engagement', 'high'),
            brand_voice=kwargs.get('brand_voice'),
            campaign_context=kwargs.get('campaign_context')
        )
        
        specification = PostSpecification(
            topic=topic,
            post_type=post_type,
            tone=tone,
            target_audience=target_audience,
            keywords=keywords or [],
            config=config
        )
        
        # Crear contenido
        content = PostContent(
            text=content_text,
            hashtags=hashtags or [],
            mentions=kwargs.get('mentions', []),
            media_urls=kwargs.get('media_urls', []),
            link_url=kwargs.get('link_url')
        )
        
        return FacebookPostEntity(identifier, specification, content)
    
    @staticmethod
    def create_from_template(
        template_type: str,
        topic: str,
        **template_params
    ) -> FacebookPostEntity:
        """Crear post desde template predefinido."""
        
        templates = {
            "promotional": {
                "tone": ContentTone.PROMOTIONAL,
                "audience": TargetAudience.GENERAL,
                "include_call_to_action": True,
                "content_template": "🚀 Exciting news about {topic}! {details} Don't miss out! {cta}"
            },
            "educational": {
                "tone": ContentTone.EDUCATIONAL,
                "audience": TargetAudience.PROFESSIONALS,
                "include_hashtags": True,
                "content_template": "📚 Learn about {topic}: {insights} What's your experience? {hashtags}"
            },
            "inspirational": {
                "tone": ContentTone.INSPIRING,
                "audience": TargetAudience.ENTREPRENEURS,
                "include_emojis": True,
                "content_template": "✨ {topic} can transform your {area}! {motivation} Keep pushing forward! 💪"
            }
        }
        
        if template_type not in templates:
            raise ValueError(f"Unknown template type: {template_type}")
        
        template = templates[template_type]
        content_text = template["content_template"].format(
            topic=topic,
            **template_params
        )
        
        return FacebookPostFactory.create_new_post(
            topic=topic,
            content_text=content_text,
            tone=template["tone"],
            target_audience=template["audience"],
            **{k: v for k, v in template.items() if k not in ["tone", "audience", "content_template"]}
        ) 