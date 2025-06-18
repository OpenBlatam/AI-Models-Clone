"""
Brand Kit Voice Component - Onyx Integration
Component for managing brand voice.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Literal
from dataclasses import dataclass, field
from datetime import datetime
from ..base_types import (
    CACHE_TTL, VALIDATION_TIMEOUT,
    ModelId, ModelKey, ModelValue,
    ValidationType, CacheType, EventType,
    StatusType, CategoryType, PermissionType
)
from ..model_field import ModelField, FieldConfig
from ..base import ValidationMixin, CacheMixin, EventMixin, IndexMixin, PermissionMixin, StatusMixin

T = TypeVar('T')

@dataclass
class BrandKitVoice:
    """Brand Kit Voice Component"""
    name: str
    tone: Literal['formal', 'casual', 'professional', 'friendly', 'authoritative', 'playful'] = 'professional'
    style: Literal['conversational', 'technical', 'creative', 'academic', 'journalistic'] = 'conversational'
    personality_traits: List[str] = field(default_factory=lambda: ['professional', 'trustworthy'])
    industry_terms: List[str] = field(default_factory=list)
    vocabulary_level: Literal['basic', 'intermediate', 'advanced', 'expert'] = 'intermediate'
    sentence_structure: Literal['simple', 'compound', 'complex', 'mixed'] = 'mixed'
    formality_level: Literal['very_formal', 'formal', 'neutral', 'casual', 'very_casual'] = 'neutral'
    emotional_tone: List[str] = field(default_factory=lambda: ['confident', 'positive'])
    cultural_references: List[str] = field(default_factory=list)
    description: Optional[str] = None
    usage_guidelines: Optional[str] = None
    examples: List[Dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: str = '1.0.0'
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize voice field with validation and caching"""
        self.voice_field = ModelField(
            name=self.name,
            value=self.tone,
            required=True,
            validation={
                'type': 'string',
                'min_length': 1,
                'timeout': 0.5,
                'rules': {
                    'tone': '^[a-zA-Z\\s\\-]+$',
                    'style': '^[a-zA-Z\\s\\-]+$',
                    'personality_traits': '^[a-zA-Z\\s\\-\\,]+$'
                }
            },
            cache={
                'enabled': True,
                'ttl': 3600,
                'prefix': 'brand_kit:voice'
            },
            events={
                'enabled': True,
                'types': ['voice_created', 'voice_updated', 'voice_deleted'],
                'notify': True
            },
            index={
                'enabled': True,
                'fields': ['name', 'tone', 'style'],
                'type': 'hash'
            },
            permissions={
                'roles': ['admin', 'writer', 'editor'],
                'actions': ['create', 'read', 'update', 'delete']
            },
            status={
                'active': True,
                'archived': False
            }
        )

    def get_data(self) -> Dict[str, Any]:
        """Get voice data with caching"""
        cache_key = f"brand_kit:voice:{self.name}"
        cached_data = self.voice_field.get_cache(cache_key)
        
        if cached_data:
            return cached_data
        
        data = {
            'name': self.name,
            'tone': self.tone,
            'style': self.style,
            'personality_traits': self.personality_traits,
            'industry_terms': self.industry_terms,
            'vocabulary_level': self.vocabulary_level,
            'sentence_structure': self.sentence_structure,
            'formality_level': self.formality_level,
            'emotional_tone': self.emotional_tone,
            'cultural_references': self.cultural_references,
            'description': self.description,
            'usage_guidelines': self.usage_guidelines,
            'examples': self.examples,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'version': self.version,
            'metadata': self.metadata
        }
        
        self.voice_field.set_cache(cache_key, data)
        return data

    def update(self, **kwargs) -> None:
        """Update voice properties"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        self.voice_field.clear_cache(f"brand_kit:voice:{self.name}")

    def add_example(self, context: str, text: str, explanation: Optional[str] = None) -> None:
        """Add a usage example"""
        self.examples.append({
            'context': context,
            'text': text,
            'explanation': explanation,
            'created_at': datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow()
        self.voice_field.clear_cache(f"brand_kit:voice:{self.name}")

    def get_voice_guidelines(self) -> Dict[str, Any]:
        """Get comprehensive voice guidelines"""
        return {
            'tone': {
                'primary': self.tone,
                'style': self.style,
                'formality': self.formality_level,
                'emotional': self.emotional_tone
            },
            'language': {
                'vocabulary': self.vocabulary_level,
                'sentence_structure': self.sentence_structure,
                'industry_terms': self.industry_terms,
                'cultural_references': self.cultural_references
            },
            'personality': {
                'traits': self.personality_traits,
                'examples': self.examples
            },
            'guidelines': {
                'description': self.description,
                'usage': self.usage_guidelines
            }
        }

    def get_voice_score(self, text: str) -> Dict[str, float]:
        """Calculate voice consistency score for given text"""
        # This is a simplified scoring system
        scores = {
            'tone_match': 0.0,
            'style_match': 0.0,
            'vocabulary_match': 0.0,
            'formality_match': 0.0
        }
        
        # Implement actual scoring logic here
        # This would typically involve NLP analysis
        
        return scores

    def get_voice_suggestions(self, text: str) -> List[Dict[str, Any]]:
        """Get suggestions to improve voice consistency"""
        suggestions = []
        
        # Implement suggestion logic here
        # This would typically involve comparing text against voice guidelines
        
        return suggestions

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> 'BrandKitVoice':
        """Create voice from data"""
        return cls(**data) 