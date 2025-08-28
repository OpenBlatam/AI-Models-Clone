"""
API endpoints for Enhanced Blog System v27.0.0 REFACTORED
"""

from fastapi import APIRouter

from .endpoints import (
    quantum_neural_intelligence_consciousness_temporal_networks_router,
    evolution_swarm_intelligence_consciousness_temporal_forecasting_router,
    bio_quantum_intelligence_consciousness_temporal_networks_router,
    swarm_intelligence_consciousness_temporal_evolution_router,
    consciousness_intelligence_quantum_neural_temporal_networks_router,
    optimization_router
)

# Create main API router
router = APIRouter()

# Include all endpoint routers
router.include_router(
    quantum_neural_intelligence_consciousness_temporal_networks_router,
    prefix="/quantum-neural-intelligence-consciousness-temporal-networks",
    tags=["Quantum Neural Intelligence Consciousness Temporal Networks"]
)

router.include_router(
    evolution_swarm_intelligence_consciousness_temporal_forecasting_router,
    prefix="/evolution-swarm-intelligence-consciousness-temporal-forecasting",
    tags=["Evolution Swarm Intelligence Consciousness Temporal Forecasting"]
)

router.include_router(
    bio_quantum_intelligence_consciousness_temporal_networks_router,
    prefix="/bio-quantum-intelligence-consciousness-temporal-networks",
    tags=["Bio-Quantum Intelligence Consciousness Temporal Networks"]
)

router.include_router(
    swarm_intelligence_consciousness_temporal_evolution_router,
    prefix="/swarm-intelligence-consciousness-temporal-evolution",
    tags=["Swarm Intelligence Consciousness Temporal Evolution"]
)

router.include_router(
    consciousness_intelligence_quantum_neural_temporal_networks_router,
    prefix="/consciousness-intelligence-quantum-neural-temporal-networks",
    tags=["Consciousness Intelligence Quantum Neural Temporal Networks"]
)

router.include_router(
    optimization_router,
    prefix="/optimization",
    tags=["Optimization"]
)

__all__ = ["router"] 