#!/usr/bin/env python3
"""
LinkedIn Post Entity - Domain Layer
===================================

Core business entity representing a LinkedIn post with domain logic
and business rules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
import hashlib
import json

from ..value_objects.post_tone import PostTone
from ..value_objects.post_length import PostLength
from ..value_objects.optimization_strategy import OptimizationStrategy


@dataclass
class LinkedInPost:
    """
    Core LinkedIn Post entity with domain logic and business rules.
    
    This entity encapsulates all business logic related to LinkedIn posts
    and ensures data integrity through domain validation.
    """
    
    # Identity
    id: UUID = field(default_factory=uuid4)
    
    # Core content
    topic: str
    content: str
    tone: PostTone
    length: PostLength
    
    # Optional features
    hashtags: List[str] = field(default_factory=list)
    call_to_action: Optional[str] = None
    
    # Optimization metadata
    optimization_strategy: OptimizationStrategy = field(default_factory=OptimizationStrategy.default)
    optimization_score: float = 0.0
    optimization_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Performance metrics
    generation_time_ms: float = 0.0
    optimization_time_ms: float = 0.0
    cache_hit: bool = False
    
    def __post_init__(self):
        """Validate entity after initialization"""
        self._validate_entity()
        self._update_timestamps()
    
    def _validate_entity(self):
        """Validate entity business rules"""
        if not self.topic or not self.topic.strip():
            raise ValueError("Topic cannot be empty")
        
        if not self.content or not self.content.strip():
            raise ValueError("Content cannot be empty")
        
        if len(self.content) > 3000:  # LinkedIn character limit
            raise ValueError("Content exceeds LinkedIn character limit")
        
        if len(self.hashtags) > 30:  # LinkedIn hashtag limit
            raise ValueError("Too many hashtags")
    
    def _update_timestamps(self):
        """Update timestamps"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def add_hashtag(self, hashtag: str) -> None:
        """Add a hashtag to the post"""
        if not hashtag.startswith('#'):
            hashtag = f"#{hashtag}"
        
        if hashtag not in self.hashtags and len(self.hashtags) < 30:
            self.hashtags.append(hashtag)
            self._update_timestamps()
    
    def remove_hashtag(self, hashtag: str) -> None:
        """Remove a hashtag from the post"""
        if hashtag in self.hashtags:
            self.hashtags.remove(hashtag)
            self._update_timestamps()
    
    def set_call_to_action(self, cta: str) -> None:
        """Set call to action for the post"""
        self.call_to_action = cta
        self._update_timestamps()
    
    def update_content(self, new_content: str) -> None:
        """Update post content with validation"""
        if not new_content or not new_content.strip():
            raise ValueError("Content cannot be empty")
        
        if len(new_content) > 3000:
            raise ValueError("Content exceeds LinkedIn character limit")
        
        self.content = new_content
        self._update_timestamps()
    
    def apply_optimization(self, strategy: OptimizationStrategy, score: float, metadata: Dict[str, Any]) -> None:
        """Apply optimization results to the post"""
        self.optimization_strategy = strategy
        self.optimization_score = max(0.0, min(1.0, score))  # Clamp between 0 and 1
        self.optimization_metadata.update(metadata)
        self._update_timestamps()
    
    def set_performance_metrics(self, generation_time: float, optimization_time: float, cache_hit: bool = False) -> None:
        """Set performance metrics for the post"""
        self.generation_time_ms = max(0.0, generation_time)
        self.optimization_time_ms = max(0.0, optimization_time)
        self.cache_hit = cache_hit
        self._update_timestamps()
    
    def get_total_length(self) -> int:
        """Get total character length including hashtags and CTA"""
        total = len(self.content)
        
        if self.hashtags:
            total += len(' '.join(self.hashtags))
        
        if self.call_to_action:
            total += len(self.call_to_action)
        
        return total
    
    def get_engagement_score(self) -> float:
        """Calculate engagement score based on content quality"""
        score = 0.0
        
        # Content length factor
        content_length = len(self.content)
        if 100 <= content_length <= 500:
            score += 0.3
        elif 500 < content_length <= 1000:
            score += 0.4
        elif 1000 < content_length <= 2000:
            score += 0.3
        
        # Hashtag factor
        if 3 <= len(self.hashtags) <= 10:
            score += 0.2
        
        # Call to action factor
        if self.call_to_action:
            score += 0.1
        
        # Optimization factor
        score += self.optimization_score * 0.4
        
        return min(1.0, score)
    
    def is_ready_for_posting(self) -> bool:
        """Check if post is ready for posting"""
        return (
            bool(self.content.strip()) and
            len(self.content) <= 3000 and
            self.optimization_score >= 0.7
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            'id': str(self.id),
            'topic': self.topic,
            'content': self.content,
            'tone': self.tone.value,
            'length': self.length.value,
            'hashtags': self.hashtags,
            'call_to_action': self.call_to_action,
            'optimization_strategy': self.optimization_strategy.value,
            'optimization_score': self.optimization_score,
            'optimization_metadata': self.optimization_metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'generation_time_ms': self.generation_time_ms,
            'optimization_time_ms': self.optimization_time_ms,
            'cache_hit': self.cache_hit,
            'total_length': self.get_total_length(),
            'engagement_score': self.get_engagement_score(),
            'ready_for_posting': self.is_ready_for_posting()
        }
    
    def to_json(self) -> str:
        """Convert entity to JSON string"""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LinkedInPost':
        """Create entity from dictionary"""
        return cls(
            id=UUID(data['id']) if isinstance(data['id'], str) else data['id'],
            topic=data['topic'],
            content=data['content'],
            tone=PostTone(data['tone']),
            length=PostLength(data['length']),
            hashtags=data.get('hashtags', []),
            call_to_action=data.get('call_to_action'),
            optimization_strategy=OptimizationStrategy(data.get('optimization_strategy', 'default')),
            optimization_score=data.get('optimization_score', 0.0),
            optimization_metadata=data.get('optimization_metadata', {}),
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data['created_at'], str) else data['created_at'],
            updated_at=datetime.fromisoformat(data['updated_at']) if isinstance(data['updated_at'], str) else data['updated_at'],
            generation_time_ms=data.get('generation_time_ms', 0.0),
            optimization_time_ms=data.get('optimization_time_ms', 0.0),
            cache_hit=data.get('cache_hit', False)
        )
    
    def __eq__(self, other: object) -> bool:
        """Compare entities by ID"""
        if not isinstance(other, LinkedInPost):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self.id)
    
    def __str__(self) -> str:
        """String representation"""
        return f"LinkedInPost(id={self.id}, topic='{self.topic}', score={self.optimization_score:.2f})"
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return f"LinkedInPost(id={self.id}, topic='{self.topic}', content='{self.content[:50]}...', score={self.optimization_score:.2f})" 