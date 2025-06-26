"""Analysis Manager for Modular NLP System."""

import logging
import time
from typing import Dict, List, Optional, Any, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from ..core import (
    IAnalyzerManager, IAnalyzer, AnalysisType, AnalysisResult, AnalysisConfig,
    AnalysisResults, get_config, get_analyzer_registry
)
from ..factories.analyzer_factory import get_analyzer_factory

logger = logging.getLogger(__name__)

@dataclass
class AnalysisTask:
    """Represents an analysis task."""
    analyzer: IAnalyzer
    text: str
    config: Optional[AnalysisConfig]
    task_id: str

@dataclass
class AnalysisSession:
    """Represents an analysis session with multiple tasks."""
    session_id: str
    text: str
    requested_analyses: Set[AnalysisType]
    results: AnalysisResults = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    status: str = "running"
    error_count: int = 0

class AnalysisManager(IAnalyzerManager):
    """Main manager for orchestrating NLP analysis."""
    
    def __init__(self):
        """Initialize the analysis manager."""
        self._config = get_config()
        self._registry = get_analyzer_registry()
        self._factory = get_analyzer_factory()
        
        # Performance settings
        self._performance_config = self._config.get_performance_config()
        self._max_workers = self._performance_config.max_parallel_analyzers
        self._default_timeout = self._performance_config.default_timeout_ms / 1000
        
        # Thread pool for parallel execution
        self._thread_pool = ThreadPoolExecutor(
            max_workers=self._max_workers,
            thread_name_prefix="nlp_analysis"
        )
        
        # Session tracking
        self._active_sessions: Dict[str, AnalysisSession] = {}
        self._session_counter = 0
        
        # Statistics
        self._total_analyses = 0
        self._total_processing_time = 0.0
        self._error_count = 0
        
        logger.info(f"AnalysisManager initialized with {self._max_workers} workers")
    
    def register_analyzer(self, analyzer: IAnalyzer) -> None:
        """Register an analyzer with the manager."""
        self._registry.register_analyzer(analyzer)
        logger.info(f"Registered analyzer: {analyzer.name}")
    
    def get_analyzer(self, name: str) -> Optional[IAnalyzer]:
        """Get an analyzer by name."""
        return self._registry.get_analyzer(name)
    
    def get_available_analyzers(self) -> List[IAnalyzer]:
        """Get all available analyzers."""
        return self._registry.get_available_analyzers()
    
    def analyze_all(
        self,
        text: str,
        config: Optional[Dict[str, AnalysisConfig]] = None
    ) -> AnalysisResults:
        """Run all available analyzers on the text."""
        session_id = self._create_session(text, set(AnalysisType))
        
        try:
            # Get all available analyzers
            analyzers = self.get_available_analyzers()
            
            if not analyzers:
                logger.warning("No available analyzers found")
                return {}
            
            # Execute analyses in parallel
            results = self._execute_parallel_analysis(
                analyzers, text, config or {}, session_id
            )
            
            # Update session
            session = self._active_sessions[session_id]
            session.results = results
            session.end_time = time.time()
            session.status = "completed"
            
            # Update statistics
            self._update_statistics(results)
            
            logger.info(
                f"Completed analysis session {session_id} with {len(results)} results "
                f"in {(session.end_time - session.start_time) * 1000:.1f}ms"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error in analyze_all: {e}")
            self._mark_session_error(session_id, str(e))
            return {}
        finally:
            # Clean up session
            self._cleanup_session(session_id)
    
    def analyze_single(
        self,
        text: str,
        analyzer_name: str,
        config: Optional[AnalysisConfig] = None
    ) -> Optional[AnalysisResult]:
        """Run a single analyzer on the text."""
        analyzer = self.get_analyzer(analyzer_name)
        if not analyzer:
            logger.error(f"Analyzer not found: {analyzer_name}")
            return None
        
        try:
            start_time = time.time()
            result = analyzer.analyze(text, config)
            processing_time = (time.time() - start_time) * 1000
            
            logger.debug(
                f"Single analysis completed: {analyzer_name} "
                f"in {processing_time:.1f}ms (score: {result.score:.1f})"
            )
            
            # Update statistics
            self._total_analyses += 1
            self._total_processing_time += processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"Error in single analysis {analyzer_name}: {e}")
            self._error_count += 1
            return None
    
    def get_manager_statistics(self) -> Dict[str, Any]:
        """Get manager performance statistics."""
        avg_processing_time = (
            self._total_processing_time / self._total_analyses
            if self._total_analyses > 0 else 0
        )
        
        return {
            'total_analyses': self._total_analyses,
            'total_processing_time_ms': self._total_processing_time,
            'average_processing_time_ms': avg_processing_time,
            'error_count': self._error_count,
            'success_rate': (
                (self._total_analyses - self._error_count) / self._total_analyses * 100
                if self._total_analyses > 0 else 0
            ),
            'active_sessions': len(self._active_sessions),
            'available_analyzers': len(self.get_available_analyzers()),
            'max_workers': self._max_workers
        }
    
    def shutdown(self):
        """Shutdown the analysis manager."""
        logger.info("Shutting down AnalysisManager")
        
        # Cancel all active sessions
        for session_id in list(self._active_sessions.keys()):
            self._cleanup_session(session_id)
        
        # Shutdown thread pool
        self._thread_pool.shutdown(wait=True)
        
        logger.info("AnalysisManager shutdown complete")
    
    def _execute_parallel_analysis(
        self,
        analyzers: List[IAnalyzer],
        text: str,
        config: Dict[str, AnalysisConfig],
        session_id: str
    ) -> AnalysisResults:
        """Execute multiple analyses in parallel."""
        results: AnalysisResults = {}
        
        # Create analysis tasks
        tasks = []
        for analyzer in analyzers:
            analyzer_config = config.get(analyzer.name)
            task = AnalysisTask(
                analyzer=analyzer,
                text=text,
                config=analyzer_config,
                task_id=f"{session_id}_{analyzer.name}"
            )
            tasks.append(task)
        
        # Submit all tasks to thread pool
        future_to_task = {}
        for task in tasks:
            future = self._thread_pool.submit(
                self._execute_single_analysis,
                task
            )
            future_to_task[future] = task
        
        # Collect results as they complete
        for future in as_completed(future_to_task, timeout=self._default_timeout * len(tasks)):
            task = future_to_task[future]
            
            try:
                result = future.result(timeout=self._default_timeout)
                if result:
                    results[task.analyzer.name] = result
                    logger.debug(f"Completed analysis: {task.analyzer.name}")
                else:
                    logger.warning(f"No result from analyzer: {task.analyzer.name}")
                    self._increment_session_error(session_id)
                    
            except Exception as e:
                logger.error(f"Error in parallel analysis {task.analyzer.name}: {e}")
                self._increment_session_error(session_id)
        
        return results
    
    def _execute_single_analysis(self, task: AnalysisTask) -> Optional[AnalysisResult]:
        """Execute a single analysis task."""
        try:
            return task.analyzer.analyze(task.text, task.config)
        except Exception as e:
            logger.error(f"Analysis task failed {task.task_id}: {e}")
            return None
    
    def _create_session(self, text: str, analysis_types: Set[AnalysisType]) -> str:
        """Create a new analysis session."""
        self._session_counter += 1
        session_id = f"session_{self._session_counter}_{int(time.time())}"
        
        session = AnalysisSession(
            session_id=session_id,
            text=text,
            requested_analyses=analysis_types
        )
        
        self._active_sessions[session_id] = session
        logger.debug(f"Created analysis session: {session_id}")
        
        return session_id
    
    def _cleanup_session(self, session_id: str):
        """Clean up a completed session."""
        self._active_sessions.pop(session_id, None)
    
    def _mark_session_error(self, session_id: str, error_message: str):
        """Mark a session as having an error."""
        if session_id in self._active_sessions:
            session = self._active_sessions[session_id]
            session.status = "error"
            session.end_time = time.time()
            session.error_count += 1
        
        self._error_count += 1
    
    def _increment_session_error(self, session_id: str):
        """Increment error count for a session."""
        if session_id in self._active_sessions:
            self._active_sessions[session_id].error_count += 1
    
    def _update_statistics(self, results: AnalysisResults):
        """Update manager statistics based on results."""
        self._total_analyses += len(results)
        
        for result in results.values():
            self._total_processing_time += result.processing_time_ms

# Global manager instance
_analysis_manager: Optional[AnalysisManager] = None

def get_analysis_manager() -> AnalysisManager:
    """Get the global analysis manager instance."""
    global _analysis_manager
    if _analysis_manager is None:
        _analysis_manager = AnalysisManager()
    return _analysis_manager
