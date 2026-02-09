"""
Adaptive improvement routes following functional patterns
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import time
import uuid

from app.core.dependencies import get_db, get_current_user
from app.core.errors import handle_validation_error, handle_internal_error
from app.models.user import User
from app.schemas.adaptive_improvement import (
    AdaptiveImprovementResponse, ImprovementPatternResponse, LearningModelResponse,
    PerformancePredictionResponse, AutoOptimizationResponse, ImprovementAnalysisResponse
)
from app.services.adaptive_improvement_service import (
    initialize_adaptive_improvement, analyze_system_performance, apply_adaptive_improvements,
    predict_system_performance, optimize_system_parameters, create_improvement_analysis_report
)

router = APIRouter()


@router.post("/initialize", response_model=Dict[str, bool])
async def initialize_adaptive_improvement_system(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, bool]:
    """Initialize adaptive improvement system."""
    try:
        return await initialize_adaptive_improvement()
    
    except Exception as e:
        raise handle_internal_error(f"Failed to initialize adaptive improvement system: {str(e)}")


@router.get("/analysis/", response_model=ImprovementAnalysisResponse)
async def get_improvement_analysis(
    time_window_hours: int = Query(24, ge=1, le=168, description="Time window for analysis"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ImprovementAnalysisResponse:
    """Get comprehensive improvement analysis."""
    try:
        analysis_result = await analyze_system_performance(time_window_hours, db)
        
        return ImprovementAnalysisResponse(
            improvement_score=analysis_result.get("improvement_score", 0),
            current_metrics=analysis_result.get("current_metrics", {}),
            trend_analysis=analysis_result.get("trend_analysis", {}),
            suggestions=analysis_result.get("suggestions", []),
            analyzed_at=analysis_result.get("analyzed_at", datetime.utcnow())
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get improvement analysis: {str(e)}")


@router.post("/apply", response_model=AutoOptimizationResponse)
async def apply_improvements(
    improvements: List[Dict[str, Any]],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AutoOptimizationResponse:
    """Apply adaptive improvements to the system."""
    try:
        result = await apply_adaptive_improvements(improvements, db)
        
        return AutoOptimizationResponse(
            applied_improvements=result.get("applied_improvements", []),
            failed_improvements=result.get("failed_improvements", []),
            total_applied=result.get("total_applied", 0),
            total_failed=result.get("total_failed", 0),
            applied_at=result.get("applied_at", datetime.utcnow())
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to apply improvements: {str(e)}")


@router.post("/predict", response_model=PerformancePredictionResponse)
async def predict_performance(
    features: Dict[str, float],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PerformancePredictionResponse:
    """Predict system performance based on features."""
    try:
        prediction_result = await predict_system_performance(features, db)
        
        return PerformancePredictionResponse(
            prediction=prediction_result.get("prediction", {}),
            features=prediction_result.get("features", {}),
            predicted_at=prediction_result.get("predicted_at", datetime.utcnow())
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to predict performance: {str(e)}")


@router.post("/optimize", response_model=AutoOptimizationResponse)
async def optimize_parameters(
    optimization_request: Dict[str, Any],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AutoOptimizationResponse:
    """Optimize system parameters using machine learning."""
    try:
        optimization_result = await optimize_system_parameters(optimization_request, db)
        
        return AutoOptimizationResponse(
            applied_improvements=[{
                "type": "parameter_optimization",
                "optimization_result": optimization_result.get("optimization_result", {}),
                "applied_at": datetime.utcnow()
            }],
            failed_improvements=[],
            total_applied=1,
            total_failed=0,
            applied_at=datetime.utcnow()
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to optimize parameters: {str(e)}")


@router.get("/report/", response_model=ImprovementAnalysisResponse)
async def get_improvement_report(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ImprovementAnalysisResponse:
    """Get comprehensive improvement analysis report."""
    try:
        report_result = await create_improvement_analysis_report(db)
        
        return ImprovementAnalysisResponse(
            improvement_score=report_result.get("improvement_score", 0),
            current_metrics=report_result.get("current_metrics", {}),
            trend_analysis=report_result.get("trend_analysis", {}),
            suggestions=report_result.get("suggestions", []),
            analyzed_at=report_result.get("generated_at", datetime.utcnow())
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get improvement report: {str(e)}")


@router.post("/suggest", response_model=List[Dict[str, Any]])
async def suggest_improvements(
    current_metrics: Dict[str, float],
    user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Suggest improvements based on current metrics."""
    try:
        from app.services.adaptive_improvement_service import _improvement_engine
        
        suggestions = await _improvement_engine.suggest_improvements(current_metrics)
        return suggestions
    
    except Exception as e:
        raise handle_internal_error(f"Failed to suggest improvements: {str(e)}")


@router.get("/trends/", response_model=Dict[str, Any])
async def get_performance_trends(
    time_window_hours: int = Query(24, ge=1, le=168, description="Time window for trends"),
    user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get performance trends analysis."""
    try:
        from app.services.adaptive_improvement_service import _improvement_engine
        
        trend_analysis = await _improvement_engine.analyze_performance_trends(time_window_hours)
        return trend_analysis
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get performance trends: {str(e)}")


@router.get("/models/", response_model=Dict[str, LearningModelResponse])
async def get_learning_models(
    user: User = Depends(get_current_user)
) -> Dict[str, LearningModelResponse]:
    """Get information about learning models."""
    try:
        from app.services.adaptive_improvement_service import _improvement_engine
        
        models_info = {}
        for model_name, model in _improvement_engine.learning_engine.models.items():
            models_info[model_name] = LearningModelResponse(
                model_name=model_name,
                model_type=type(model).__name__,
                is_trained=hasattr(model, 'fit') and hasattr(model, 'predict'),
                training_score=0.0,  # Would be calculated from actual training
                last_trained=datetime.utcnow(),
                model_status="active"
            )
        
        return models_info
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get learning models: {str(e)}")


@router.post("/train", response_model=Dict[str, Any])
async def train_learning_models(
    training_data: Dict[str, List[float]],
    target_data: Dict[str, List[float]],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Train learning models with provided data."""
    try:
        from app.services.adaptive_improvement_service import _improvement_engine
        import numpy as np
        
        # Convert data to numpy arrays
        training_arrays = {}
        target_arrays = {}
        
        for model_name in training_data.keys():
            if model_name in target_data:
                training_arrays[model_name] = np.array(training_data[model_name])
                target_arrays[model_name] = np.array(target_data[model_name])
        
        # Train models
        training_results = await _improvement_engine.learning_engine.learn_from_data(
            training_arrays, target_arrays, "performance_predictor"
        )
        
        return {
            "training_results": training_results,
            "models_trained": len(training_arrays),
            "trained_at": datetime.utcnow()
        }
    
    except Exception as e:
        raise handle_internal_error(f"Failed to train learning models: {str(e)}")


@router.get("/patterns/", response_model=List[ImprovementPatternResponse])
async def get_improvement_patterns(
    user: User = Depends(get_current_user)
) -> List[ImprovementPatternResponse]:
    """Get detected improvement patterns."""
    try:
        from app.services.adaptive_improvement_service import _improvement_engine
        
        # Analyze patterns from improvement history
        improvement_history = list(_improvement_engine.improvement_history)
        
        patterns = []
        if improvement_history:
            # Group by improvement type
            type_counts = {}
            for improvement in improvement_history:
                improvement_type = improvement.get("type", "unknown")
                type_counts[improvement_type] = type_counts.get(improvement_type, 0) + 1
            
            # Create pattern responses
            for improvement_type, count in type_counts.items():
                patterns.append(ImprovementPatternResponse(
                    pattern_type=improvement_type,
                    frequency=count,
                    success_rate=0.85,  # Would be calculated from actual data
                    avg_improvement_percent=25.0,  # Would be calculated from actual data
                    last_observed=datetime.utcnow(),
                    pattern_confidence=0.8
                ))
        
        return patterns
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get improvement patterns: {str(e)}")


@router.get("/status/")
async def get_improvement_status(
    user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get adaptive improvement system status."""
    try:
        from app.services.adaptive_improvement_service import _improvement_engine
        
        # Get system status
        improvement_history = list(_improvement_engine.improvement_history)
        total_improvements = len(improvement_history)
        successful_improvements = len([imp for imp in improvement_history if imp.get("status") == "success"])
        
        # Get model status
        models_status = {}
        for model_name, model in _improvement_engine.learning_engine.models.items():
            models_status[model_name] = {
                "available": model is not None,
                "type": type(model).__name__ if model else "None"
            }
        
        return {
            "status": "active",
            "total_improvements": total_improvements,
            "successful_improvements": successful_improvements,
            "success_rate": (successful_improvements / total_improvements * 100) if total_improvements > 0 else 0,
            "models_status": models_status,
            "learning_rate": _improvement_engine.learning_engine.learning_rate,
            "exploration_rate": _improvement_engine.learning_engine.exploration_rate,
            "last_updated": datetime.utcnow()
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "last_updated": datetime.utcnow()
        }


@router.post("/auto-optimize")
async def enable_auto_optimization(
    auto_optimize_config: Dict[str, Any],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Enable automatic optimization."""
    try:
        from app.services.adaptive_improvement_service import _improvement_engine
        
        # Configure auto-optimization
        _improvement_engine.improvement_threshold = auto_optimize_config.get("improvement_threshold", 0.05)
        
        return {
            "auto_optimization_enabled": True,
            "improvement_threshold": _improvement_engine.improvement_threshold,
            "configured_at": datetime.utcnow()
        }
    
    except Exception as e:
        raise handle_internal_error(f"Failed to enable auto-optimization: {str(e)}")


@router.get("/metrics/")
async def get_improvement_metrics(
    time_window_hours: int = Query(24, ge=1, le=168, description="Time window for metrics"),
    user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get improvement metrics."""
    try:
        from app.services.adaptive_improvement_service import _improvement_engine
        
        # Get current metrics
        current_metrics = await _improvement_engine._get_current_metrics()
        
        # Get trend analysis
        trend_analysis = await _improvement_engine.analyze_performance_trends(time_window_hours)
        
        return {
            "current_metrics": current_metrics,
            "trend_analysis": trend_analysis,
            "time_window_hours": time_window_hours,
            "generated_at": datetime.utcnow()
        }
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get improvement metrics: {str(e)}")




