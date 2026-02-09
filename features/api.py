"""
API endpoints for the Text Quality Detection and Document Monitoring system.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime

from .text_quality_detector import TextQualityDetector, QualityDetectionResult, TextQualityIssue
from .document_monitor import DocumentMonitor, DocumentSession, MonitoringConfig
from .config import FeaturesConfig, load_config_from_env

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Text Quality Detection API",
    description="API for detecting aggressive, low-quality, and subservient text patterns",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
config = load_config_from_env()
quality_detector = TextQualityDetector()
document_monitor = DocumentMonitor(config.document_monitor)

# Pydantic models for API
class TextAnalysisRequest(BaseModel):
    """Request model for text analysis."""
    text: str = Field(..., description="Text to analyze", min_length=1)
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking")
    user_id: Optional[str] = Field(None, description="Optional user ID")

class TextAnalysisResponse(BaseModel):
    """Response model for text analysis."""
    text: str
    quality_score: float = Field(..., ge=0.0, le=1.0)
    issues: List[str]
    severity: str
    suggestions: List[str]
    confidence_scores: Dict[str, float]
    is_acceptable: bool

class SessionStartRequest(BaseModel):
    """Request model for starting a document session."""
    user_id: str = Field(..., description="User identifier")
    document_type: str = Field("general", description="Type of document being created")

class SessionStartResponse(BaseModel):
    """Response model for session start."""
    session_id: str
    user_id: str
    document_type: str
    start_time: str
    status: str

class SessionUpdateRequest(BaseModel):
    """Request model for updating session text."""
    session_id: str = Field(..., description="Session identifier")
    text: str = Field(..., description="Updated text content")

class SessionUpdateResponse(BaseModel):
    """Response model for session update."""
    session_id: str
    feedback: Optional[Dict[str, Any]] = None
    quality_score: float
    status: str

class SessionSummaryResponse(BaseModel):
    """Response model for session summary."""
    session_id: str
    user_id: str
    document_type: str
    start_time: str
    duration_minutes: float
    total_checks: int
    average_quality_score: float
    warnings_count: int
    current_quality_score: float
    issue_counts: Dict[str, int]
    suggestions_given: int
    is_active: bool

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Text Quality Detection API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "analyze": "/analyze",
            "session": "/session",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(document_monitor.active_sessions),
        "config": {
            "debug_mode": config.debug_mode,
            "log_level": config.log_level
        }
    }

@app.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Analyze text for quality issues.
    
    Args:
        request: Text analysis request
        
    Returns:
        TextAnalysisResponse with quality analysis results
    """
    try:
        # Perform quality analysis
        result = quality_detector.analyze_text(request.text)
        
        # If session_id is provided, update the session
        if request.session_id:
            feedback = document_monitor.update_text(request.session_id, request.text)
        else:
            feedback = None
        
        return TextAnalysisResponse(
            text=request.text,
            quality_score=result.overall_quality_score,
            issues=[issue.value for issue in result.issues],
            severity=result.severity,
            suggestions=result.suggestions,
            confidence_scores={k.value: v for k, v in result.confidence_scores.items()},
            is_acceptable=result.overall_quality_score > 0.6 and result.severity in ["low", "medium"]
        )
    
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

@app.post("/session/start", response_model=SessionStartResponse)
async def start_session(request: SessionStartRequest):
    """
    Start a new document creation session.
    
    Args:
        request: Session start request
        
    Returns:
        SessionStartResponse with session details
    """
    try:
        session_id = f"session_{int(datetime.now().timestamp())}"
        session = document_monitor.start_session(
            session_id=session_id,
            user_id=request.user_id,
            document_type=request.document_type
        )
        
        return SessionStartResponse(
            session_id=session_id,
            user_id=session.user_id,
            document_type=session.document_type,
            start_time=session.start_time.isoformat(),
            status="active"
        )
    
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(status_code=500, detail=f"Session start failed: {str(e)}")

@app.post("/session/update", response_model=SessionUpdateResponse)
async def update_session(request: SessionUpdateRequest):
    """
    Update text content for a session.
    
    Args:
        request: Session update request
        
    Returns:
        SessionUpdateResponse with feedback and quality score
    """
    try:
        # Update session text
        feedback = document_monitor.update_text(request.session_id, request.text)
        
        # Get current quality score
        session = document_monitor.active_sessions.get(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        current_quality = 0.0
        if session.quality_history:
            current_quality = session.quality_history[-1].overall_quality_score
        
        return SessionUpdateResponse(
            session_id=request.session_id,
            feedback=feedback,
            quality_score=current_quality,
            status="updated"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        raise HTTPException(status_code=500, detail=f"Session update failed: {str(e)}")

@app.get("/session/{session_id}/summary", response_model=SessionSummaryResponse)
async def get_session_summary(session_id: str):
    """
    Get summary of a document session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        SessionSummaryResponse with session summary
    """
    try:
        summary = document_monitor.get_session_summary(session_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionSummaryResponse(**summary)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session summary: {str(e)}")

@app.delete("/session/{session_id}")
async def end_session(session_id: str):
    """
    End a document creation session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Final session summary
    """
    try:
        summary = document_monitor.end_session(session_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "message": "Session ended successfully",
            "summary": summary
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

@app.get("/sessions")
async def list_active_sessions():
    """
    List all active document sessions.
    
    Returns:
        List of active sessions
    """
    try:
        sessions = []
        for session_id, session in document_monitor.active_sessions.items():
            if session.is_active:
                sessions.append({
                    "session_id": session_id,
                    "user_id": session.user_id,
                    "document_type": session.document_type,
                    "start_time": session.start_time.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "warnings_count": session.warnings_count
                })
        
        return {
            "active_sessions": sessions,
            "total_count": len(sessions)
        }
    
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@app.get("/config")
async def get_configuration():
    """
    Get current configuration settings.
    
    Returns:
        Current configuration
    """
    return {
        "text_quality": {
            "excellent_threshold": config.text_quality.excellent_threshold,
            "good_threshold": config.text_quality.good_threshold,
            "warning_threshold": config.text_quality.warning_threshold,
            "critical_threshold": config.text_quality.critical_threshold,
            "language": config.text_quality.language
        },
        "document_monitor": {
            "check_interval": config.document_monitor.check_interval,
            "session_timeout": config.document_monitor.session_timeout,
            "min_text_length": config.document_monitor.min_text_length,
            "max_suggestions_per_session": config.document_monitor.max_suggestions_per_session,
            "enable_real_time_feedback": config.document_monitor.enable_real_time_feedback
        },
        "general": {
            "debug_mode": config.debug_mode,
            "log_level": config.log_level,
            "enable_api_endpoints": config.enable_api_endpoints
        }
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Text Quality Detection API")
    await document_monitor.start_monitoring()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Text Quality Detection API")
    await document_monitor.stop_monitoring()

# Run the API server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug_mode,
        log_level=config.log_level.lower()
    )


























