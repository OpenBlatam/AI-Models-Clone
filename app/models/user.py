"""
User model for Enhanced Blog System v27.0.0 REFACTORED
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """User model with v27.0.0 advanced features and optimization"""
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic user information
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_superuser = Column(Boolean, default=False, index=True)
    
    # v27.0.0 Advanced features with optimization
    quantum_neural_intelligence_consciousness_temporal_networks_level = Column(
        Integer, default=1, index=True
    )
    evolution_swarm_consciousness_temporal_forecast_rate = Column(
        Float, default=0.20, index=True
    )
    bio_quantum_intelligence_consciousness_temporal_networks_id = Column(
        String(100), nullable=True, index=True
    )
    swarm_intelligence_consciousness_temporal_evolution_id = Column(
        String(100), nullable=True, index=True
    )
    consciousness_intelligence_quantum_neural_temporal_networks_id = Column(
        String(100), nullable=True, index=True
    )
    
    # Timestamps with optimization
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Optimized relationships
    blog_posts = relationship("BlogPost", back_populates="author", lazy="selectin")
    
    # Optimized indexes
    __table_args__ = (
        Index('idx_users_username_email', 'username', 'email'),
        Index('idx_users_active_superuser', 'is_active', 'is_superuser'),
        Index('idx_users_quantum_level', 'quantum_neural_intelligence_consciousness_temporal_networks_level'),
        Index('idx_users_evolution_rate', 'evolution_swarm_consciousness_temporal_forecast_rate'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def is_quantum_optimized(self) -> bool:
        """Check if user has quantum optimization enabled"""
        return self.quantum_neural_intelligence_consciousness_temporal_networks_level > 5
    
    @property
    def is_evolution_optimized(self) -> bool:
        """Check if user has evolution optimization enabled"""
        return self.evolution_swarm_consciousness_temporal_forecast_rate > 0.15
    
    def get_optimization_stats(self) -> dict:
        """Get user optimization statistics"""
        return {
            "quantum_level": self.quantum_neural_intelligence_consciousness_temporal_networks_level,
            "evolution_rate": self.evolution_swarm_consciousness_temporal_forecast_rate,
            "is_quantum_optimized": self.is_quantum_optimized,
            "is_evolution_optimized": self.is_evolution_optimized,
            "has_bio_quantum": bool(self.bio_quantum_intelligence_consciousness_temporal_networks_id),
            "has_swarm_intelligence": bool(self.swarm_intelligence_consciousness_temporal_evolution_id),
            "has_consciousness_intelligence": bool(self.consciousness_intelligence_quantum_neural_temporal_networks_id)
        } 