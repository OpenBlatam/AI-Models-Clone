"""
Document Creation Monitor
Real-time monitoring system that integrates with TextQualityDetector
to provide feedback during document creation.
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

from .text_quality_detector import TextQualityDetector, QualityDetectionResult, TextQualityIssue

logger = logging.getLogger(__name__)

@dataclass
class DocumentSession:
    """Represents an active document creation session."""
    session_id: str
    user_id: str
    document_type: str
    start_time: datetime
    last_activity: datetime
    current_text: str = ""
    quality_history: List[QualityDetectionResult] = field(default_factory=list)
    warnings_count: int = 0
    suggestions_given: List[str] = field(default_factory=list)
    is_active: bool = True

@dataclass
class MonitoringConfig:
    """Configuration for document monitoring."""
    check_interval: float = 2.0  # seconds
    min_text_length: int = 10
    warning_threshold: float = 0.4
    critical_threshold: float = 0.2
    max_suggestions_per_session: int = 5
    enable_real_time_feedback: bool = True
    auto_save_quality_logs: bool = True

class DocumentMonitor:
    """
    Real-time document creation monitor that provides quality feedback.
    """
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        """
        Initialize the document monitor.
        
        Args:
            config: Monitoring configuration, uses default if None
        """
        self.config = config or MonitoringConfig()
        self.quality_detector = TextQualityDetector()
        self.active_sessions: Dict[str, DocumentSession] = {}
        self.callbacks: List[Callable] = []
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_monitoring = False
        
    def start_session(self, session_id: str, user_id: str, document_type: str = "general") -> DocumentSession:
        """
        Start a new document creation session.
        
        Args:
            session_id: Unique identifier for the session
            user_id: Identifier for the user
            document_type: Type of document being created
            
        Returns:
            DocumentSession object
        """
        session = DocumentSession(
            session_id=session_id,
            user_id=user_id,
            document_type=document_type,
            start_time=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        logger.info(f"Started document session {session_id} for user {user_id}")
        
        return session
    
    def update_text(self, session_id: str, new_text: str) -> Optional[Dict[str, Any]]:
        """
        Update the text content for a session and get quality feedback.
        
        Args:
            session_id: Session identifier
            new_text: Updated text content
            
        Returns:
            Quality feedback dictionary or None if session not found
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Session {session_id} not found")
            return None
        
        session = self.active_sessions[session_id]
        session.current_text = new_text
        session.last_activity = datetime.now()
        
        # Only analyze if text is long enough
        if len(new_text.strip()) < self.config.min_text_length:
            return None
        
        # Get quality analysis
        quality_result = self.quality_detector.analyze_text(new_text)
        session.quality_history.append(quality_result)
        
        # Check if we should provide feedback
        feedback = self._should_provide_feedback(session, quality_result)
        
        if feedback:
            self._trigger_callbacks(session, quality_result, feedback)
        
        return feedback
    
    def _should_provide_feedback(self, session: DocumentSession, 
                               quality_result: QualityDetectionResult) -> Optional[Dict[str, Any]]:
        """
        Determine if feedback should be provided based on quality analysis.
        
        Args:
            session: Current document session
            quality_result: Quality analysis result
            
        Returns:
            Feedback dictionary or None if no feedback needed
        """
        # Don't provide feedback if we've already given too many suggestions
        if len(session.suggestions_given) >= self.config.max_suggestions_per_session:
            return None
        
        # Check quality thresholds
        if quality_result.overall_quality_score < self.config.critical_threshold:
            session.warnings_count += 1
            return {
                "type": "critical_warning",
                "message": "Text quality is critically low. Please review and improve.",
                "quality_score": quality_result.overall_quality_score,
                "issues": [issue.value for issue in quality_result.issues],
                "suggestions": quality_result.suggestions[:2],  # Limit suggestions
                "severity": quality_result.severity
            }
        
        elif quality_result.overall_quality_score < self.config.warning_threshold:
            session.warnings_count += 1
            return {
                "type": "quality_warning",
                "message": "Text quality could be improved.",
                "quality_score": quality_result.overall_quality_score,
                "issues": [issue.value for issue in quality_result.issues],
                "suggestions": quality_result.suggestions[:1],  # Limit suggestions
                "severity": quality_result.severity
            }
        
        # Provide positive feedback for good quality
        elif quality_result.overall_quality_score > 0.8 and len(quality_result.issues) == 0:
            return {
                "type": "positive_feedback",
                "message": "Excellent text quality!",
                "quality_score": quality_result.overall_quality_score,
                "issues": [],
                "suggestions": [],
                "severity": "low"
            }
        
        return None
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of a document session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary dictionary or None if session not found
        """
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        # Calculate session statistics
        total_checks = len(session.quality_history)
        avg_quality = (
            sum(r.overall_quality_score for r in session.quality_history) / total_checks
            if total_checks > 0 else 0.0
        )
        
        # Count issues by type
        issue_counts = {}
        for result in session.quality_history:
            for issue in result.issues:
                issue_counts[issue.value] = issue_counts.get(issue.value, 0) + 1
        
        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "document_type": session.document_type,
            "start_time": session.start_time.isoformat(),
            "duration_minutes": (datetime.now() - session.start_time).total_seconds() / 60,
            "total_checks": total_checks,
            "average_quality_score": avg_quality,
            "warnings_count": session.warnings_count,
            "current_quality_score": session.quality_history[-1].overall_quality_score if session.quality_history else 0.0,
            "issue_counts": issue_counts,
            "suggestions_given": len(session.suggestions_given),
            "is_active": session.is_active
        }
    
    def end_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        End a document creation session and return final summary.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Final session summary or None if session not found
        """
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        session.is_active = False
        
        summary = self.get_session_summary(session_id)
        
        # Save quality logs if enabled
        if self.config.auto_save_quality_logs:
            self._save_quality_logs(session)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        logger.info(f"Ended document session {session_id}")
        return summary
    
    def _save_quality_logs(self, session: DocumentSession):
        """Save quality analysis logs for a session."""
        try:
            log_data = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "document_type": session.document_type,
                "start_time": session.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "quality_history": [
                    {
                        "text": result.text[:100] + "..." if len(result.text) > 100 else result.text,
                        "quality_score": result.overall_quality_score,
                        "issues": [issue.value for issue in result.issues],
                        "severity": result.severity,
                        "suggestions": result.suggestions
                    }
                    for result in session.quality_history
                ]
            }
            
            filename = f"quality_log_{session.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save quality logs for session {session.session_id}: {e}")
    
    def add_callback(self, callback: Callable):
        """
        Add a callback function to be called when quality feedback is provided.
        
        Args:
            callback: Function to call with (session, quality_result, feedback) arguments
        """
        self.callbacks.append(callback)
    
    def _trigger_callbacks(self, session: DocumentSession, quality_result: QualityDetectionResult, 
                          feedback: Dict[str, Any]):
        """Trigger all registered callbacks with quality feedback."""
        for callback in self.callbacks:
            try:
                callback(session, quality_result, feedback)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    async def start_monitoring(self):
        """Start the background monitoring task."""
        if self._is_monitoring:
            return
        
        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Document monitoring started")
    
    async def stop_monitoring(self):
        """Stop the background monitoring task."""
        if not self._is_monitoring:
            return
        
        self._is_monitoring = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Document monitoring stopped")
    
    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while self._is_monitoring:
            try:
                # Check for inactive sessions
                current_time = datetime.now()
                inactive_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    if session.is_active:
                        # Check if session has been inactive for too long
                        inactive_time = (current_time - session.last_activity).total_seconds()
                        if inactive_time > 300:  # 5 minutes
                            logger.info(f"Session {session_id} has been inactive for {inactive_time} seconds")
                            # Could implement auto-save or session timeout here
                
                await asyncio.sleep(self.config.check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.config.check_interval)

# Example usage and integration
class DocumentCreationInterface:
    """
    Example interface showing how to integrate the document monitor
    with a document creation system.
    """
    
    def __init__(self):
        self.monitor = DocumentMonitor()
        self.monitor.add_callback(self._on_quality_feedback)
    
    def _on_quality_feedback(self, session: DocumentSession, quality_result: QualityDetectionResult, 
                           feedback: Dict[str, Any]):
        """Handle quality feedback from the monitor."""
        print(f"\n📝 Quality Feedback for Session {session.session_id}:")
        print(f"Type: {feedback['type']}")
        print(f"Message: {feedback['message']}")
        print(f"Quality Score: {feedback['quality_score']:.2f}")
        
        if feedback['issues']:
            print(f"Issues: {', '.join(feedback['issues'])}")
        
        if feedback['suggestions']:
            print("Suggestions:")
            for suggestion in feedback['suggestions']:
                print(f"  • {suggestion}")
        
        print("-" * 50)
    
    async def create_document(self, user_id: str, document_type: str = "general"):
        """Simulate document creation with real-time monitoring."""
        session_id = f"doc_{int(time.time())}"
        session = self.monitor.start_session(session_id, user_id, document_type)
        
        print(f"Started document creation session: {session_id}")
        print("Type your document content (type 'END' to finish):")
        
        # Start monitoring
        await self.monitor.start_monitoring()
        
        try:
            while True:
                text = input("\n> ")
                if text.strip().upper() == 'END':
                    break
                
                # Update text and get feedback
                feedback = self.monitor.update_text(session_id, text)
                
                if feedback and feedback['type'] != 'positive_feedback':
                    print(f"⚠️  {feedback['message']}")
        
        finally:
            # End session
            summary = self.monitor.end_session(session_id)
            await self.monitor.stop_monitoring()
            
            print(f"\n📊 Session Summary:")
            print(f"Average Quality: {summary['average_quality_score']:.2f}")
            print(f"Warnings: {summary['warnings_count']}")
            print(f"Duration: {summary['duration_minutes']:.1f} minutes")

if __name__ == "__main__":
    # Example usage
    async def main():
        interface = DocumentCreationInterface()
        await interface.create_document("user123", "report")
    
    # Run the example
    asyncio.run(main())


























