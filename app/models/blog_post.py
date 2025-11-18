"""
BlogPost model for Enhanced Blog System v27.0.0 REFACTORED
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class BlogPost(Base):
    """BlogPost model with v27.0.0 advanced features and optimization"""
    __tablename__ = "blog_posts"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, index=True)
    
    # Basic post information
    title = Column(String(500), nullable=False, index=True)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), default="draft", index=True)
    category = Column(String(50), default="other", index=True)
    tags = Column(JSONB, default=list)
    metadata = Column(JSONB, default=dict)
    
    # SEO and analytics with optimization
    seo_title = Column(String(500), nullable=True, index=True)
    seo_description = Column(Text, nullable=True)
    seo_keywords = Column(JSONB, default=list)
    view_count = Column(Integer, default=0, index=True)
    like_count = Column(Integer, default=0, index=True)
    share_count = Column(Integer, default=0, index=True)
    
    # Timestamps with optimization
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # AI/ML features with optimization
    embedding = Column(JSONB, nullable=True)
    sentiment_score = Column(Integer, nullable=True, index=True)
    readability_score = Column(Integer, nullable=True, index=True)
    topic_tags = Column(JSONB, default=list)
    
    # v27.0.0 Advanced features with optimization
    # Quantum Neural Intelligence Consciousness Temporal Networks
    quantum_neural_intelligence_consciousness_temporal_networks_processed = Column(
        Boolean, default=False, index=True
    )
    intelligence_consciousness_temporal_networks_level = Column(
        Integer, default=9, index=True
    )
    quantum_neural_intelligence_consciousness_temporal_networks_state = Column(
        JSONB, nullable=True
    )
    intelligence_consciousness_temporal_networks_measures = Column(
        JSONB, nullable=True
    )
    intelligence_consciousness_temporal_networks_fidelity = Column(
        Float, nullable=True, index=True
    )
    
    # Evolution Swarm Intelligence Consciousness Temporal Forecasting
    evolution_swarm_intelligence_consciousness_temporal_forecasting_processed = Column(
        Boolean, default=False, index=True
    )
    evolution_swarm_consciousness_temporal_forecast_rate = Column(
        Float, default=0.20, index=True
    )
    evolution_swarm_intelligence_consciousness_temporal_forecasting_state = Column(
        JSONB, nullable=True
    )
    evolution_swarm_consciousness_temporal_forecasting_adaptation = Column(
        JSONB, nullable=True
    )
    evolution_swarm_consciousness_temporal_forecasting_learning_rate = Column(
        Float, nullable=True
    )
    
    # Bio-Quantum Intelligence Consciousness Temporal Networks
    bio_quantum_intelligence_consciousness_temporal_networks_processed = Column(
        Boolean, default=False, index=True
    )
    intelligence_consciousness_temporal_networks_algorithm_result = Column(
        JSONB, nullable=True
    )
    bio_quantum_intelligence_consciousness_temporal_networks_sequence = Column(
        Text, nullable=True
    )
    intelligence_consciousness_temporal_networks_fitness = Column(
        Float, nullable=True, index=True
    )
    intelligence_consciousness_temporal_networks_convergence = Column(
        JSONB, nullable=True
    )
    
    # Swarm Intelligence Consciousness Temporal Evolution
    swarm_intelligence_consciousness_temporal_evolution_processed = Column(
        Boolean, default=False, index=True
    )
    intelligence_consciousness_temporal_evolution_particles = Column(
        JSONB, nullable=True
    )
    swarm_intelligence_consciousness_temporal_evolution_state = Column(
        JSONB, nullable=True
    )
    intelligence_consciousness_temporal_evolution_convergence = Column(
        JSONB, nullable=True
    )
    intelligence_consciousness_temporal_evolution_fitness = Column(
        Float, nullable=True, index=True
    )
    
    # Consciousness Intelligence Quantum Neural Temporal Networks
    consciousness_intelligence_quantum_neural_temporal_networks_processed = Column(
        Boolean, default=False, index=True
    )
    consciousness_intelligence_quantum_neural_temporal_horizon = Column(
        Integer, default=100, index=True
    )
    consciousness_intelligence_quantum_neural_temporal_networks_patterns = Column(
        JSONB, nullable=True
    )
    consciousness_intelligence_quantum_neural_temporal_networks_forecast = Column(
        JSONB, nullable=True
    )
    consciousness_intelligence_quantum_neural_temporal_networks_confidence = Column(
        Float, nullable=True, index=True
    )
    
    # Optimized relationships
    author = relationship("User", back_populates="blog_posts", lazy="selectin")
    
    # Optimized indexes
    __table_args__ = (
        Index('idx_blog_posts_status_category', 'status', 'category'),
        Index('idx_blog_posts_author_status', 'author_id', 'status'),
        Index('idx_blog_posts_published_at', 'published_at'),
        Index('idx_blog_posts_view_count', 'view_count'),
        Index('idx_blog_posts_quantum_processed', 'quantum_neural_intelligence_consciousness_temporal_networks_processed'),
        Index('idx_blog_posts_evolution_processed', 'evolution_swarm_intelligence_consciousness_temporal_forecasting_processed'),
        Index('idx_blog_posts_bio_quantum_processed', 'bio_quantum_intelligence_consciousness_temporal_networks_processed'),
        Index('idx_blog_posts_swarm_processed', 'swarm_intelligence_consciousness_temporal_evolution_processed'),
        Index('idx_blog_posts_consciousness_processed', 'consciousness_intelligence_quantum_neural_temporal_networks_processed'),
        Index('idx_blog_posts_quantum_level', 'intelligence_consciousness_temporal_networks_level'),
        Index('idx_blog_posts_evolution_rate', 'evolution_swarm_consciousness_temporal_forecast_rate'),
        Index('idx_blog_posts_consciousness_horizon', 'consciousness_intelligence_quantum_neural_temporal_horizon'),
    )
    
    def __repr__(self):
        return f"<BlogPost(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    @property
    def is_quantum_optimized(self) -> bool:
        """Check if post has quantum optimization enabled"""
        return (
            self.quantum_neural_intelligence_consciousness_temporal_networks_processed and
            self.intelligence_consciousness_temporal_networks_level > 5
        )
    
    @property
    def is_evolution_optimized(self) -> bool:
        """Check if post has evolution optimization enabled"""
        return (
            self.evolution_swarm_intelligence_consciousness_temporal_forecasting_processed and
            self.evolution_swarm_consciousness_temporal_forecast_rate > 0.15
        )
    
    @property
    def is_bio_quantum_optimized(self) -> bool:
        """Check if post has bio-quantum optimization enabled"""
        return (
            self.bio_quantum_intelligence_consciousness_temporal_networks_processed and
            self.intelligence_consciousness_temporal_networks_fitness and
            self.intelligence_consciousness_temporal_networks_fitness > 0.8
        )
    
    @property
    def is_swarm_optimized(self) -> bool:
        """Check if post has swarm optimization enabled"""
        return (
            self.swarm_intelligence_consciousness_temporal_evolution_processed and
            self.intelligence_consciousness_temporal_evolution_fitness and
            self.intelligence_consciousness_temporal_evolution_fitness > 0.8
        )
    
    @property
    def is_consciousness_optimized(self) -> bool:
        """Check if post has consciousness optimization enabled"""
        return (
            self.consciousness_intelligence_quantum_neural_temporal_networks_processed and
            self.consciousness_intelligence_quantum_neural_temporal_networks_confidence and
            self.consciousness_intelligence_quantum_neural_temporal_networks_confidence > 0.9
        )
    
    def get_optimization_stats(self) -> dict:
        """Get post optimization statistics"""
        return {
            "quantum_optimized": self.is_quantum_optimized,
            "evolution_optimized": self.is_evolution_optimized,
            "bio_quantum_optimized": self.is_bio_quantum_optimized,
            "swarm_optimized": self.is_swarm_optimized,
            "consciousness_optimized": self.is_consciousness_optimized,
            "quantum_level": self.intelligence_consciousness_temporal_networks_level,
            "evolution_rate": self.evolution_swarm_consciousness_temporal_forecast_rate,
            "consciousness_horizon": self.consciousness_intelligence_quantum_neural_temporal_horizon,
            "quantum_fidelity": self.intelligence_consciousness_temporal_networks_fidelity,
            "bio_quantum_fitness": self.intelligence_consciousness_temporal_networks_fitness,
            "swarm_fitness": self.intelligence_consciousness_temporal_evolution_fitness,
            "consciousness_confidence": self.consciousness_intelligence_quantum_neural_temporal_networks_confidence,
            "total_optimizations": sum([
                self.is_quantum_optimized,
                self.is_evolution_optimized,
                self.is_bio_quantum_optimized,
                self.is_swarm_optimized,
                self.is_consciousness_optimized
            ])
        }
    
    def get_performance_metrics(self) -> dict:
        """Get post performance metrics"""
        return {
            "view_count": self.view_count,
            "like_count": self.like_count,
            "share_count": self.share_count,
            "sentiment_score": self.sentiment_score,
            "readability_score": self.readability_score,
            "engagement_rate": (self.like_count + self.share_count) / max(self.view_count, 1),
            "optimization_score": self.get_optimization_stats()["total_optimizations"] / 5.0
        } 