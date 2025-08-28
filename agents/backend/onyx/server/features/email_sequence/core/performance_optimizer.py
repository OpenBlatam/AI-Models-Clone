"""
Optimized Performance Optimizer for Email Sequence System

Consolidates performance optimization functionality from multiple files
and provides efficient memory management, caching, and processing optimization.
"""

import asyncio
import logging
import time
import psutil
import gc
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from collections import defaultdict
import torch
from torch.utils.data import DataLoader
import numpy as np

from ..models.sequence import EmailSequence, SequenceStep
from ..models.subscriber import Subscriber
from ..models.template import EmailTemplate

logger = logging.getLogger(__name__)

# Constants
MAX_MEMORY_USAGE = 0.8  # 80% of available memory
CACHE_SIZE = 1000
BATCH_SIZE_OPTIMIZED = 64
MAX_CONCURRENT_TASKS = 10


@dataclass
class OptimizationConfig:
    """Configuration for performance optimization"""
    max_memory_usage: float = MAX_MEMORY_USAGE
    cache_size: int = CACHE_SIZE
    batch_size: int = BATCH_SIZE_OPTIMIZED
    max_concurrent_tasks: int = MAX_CONCURRENT_TASKS
    enable_caching: bool = True
    enable_memory_optimization: bool = True
    enable_batch_processing: bool = True


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring"""
    memory_usage: float
    cpu_usage: float
    processing_time: float
    cache_hit_rate: float
    batch_efficiency: float
    error_rate: float


class OptimizedPerformanceOptimizer:
    """Optimized performance optimizer with consolidated functionality"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.cache: Dict[str, Any] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.processing_times: List[float] = []
        self.error_count = 0
        self.total_operations = 0
        
        # Memory monitoring
        self.memory_threshold = psutil.virtual_memory().total * self.config.max_memory_usage
        
        # Performance tracking
        self.start_time = time.time()
        
        logger.info("Performance Optimizer initialized")
    
    async def optimize_sequence_processing(
        self,
        sequences: List[EmailSequence],
        subscribers: List[Subscriber],
        templates: List[EmailTemplate]
    ) -> Dict[str, Any]:
        """Optimize sequence processing with performance monitoring"""
        try:
            start_time = time.time()
            
            # Check memory usage
            if self._is_memory_pressure():
                await self._optimize_memory()
            
            # Process sequences in optimized batches
            results = await self._process_sequences_optimized(
                sequences, subscribers, templates
            )
            
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            
            # Update metrics
            metrics = self._calculate_performance_metrics()
            
            logger.info(f"Optimized processing completed in {processing_time:.2f}s")
            
            return {
                "results": results,
                "metrics": metrics,
                "optimization_applied": True
            }
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error in optimized processing: {e}")
            return {
                "results": [],
                "metrics": self._calculate_performance_metrics(),
                "optimization_applied": False,
                "error": str(e)
            }
    
    async def _process_sequences_optimized(
        self,
        sequences: List[EmailSequence],
        subscribers: List[Subscriber],
        templates: List[EmailTemplate]
    ) -> List[Dict[str, Any]]:
        """Process sequences with optimization"""
        results = []
        
        # Process in batches
        for i in range(0, len(sequences), self.config.batch_size):
            batch = sequences[i:i + self.config.batch_size]
            
            # Process batch concurrently
            batch_results = await self._process_batch_concurrent(
                batch, subscribers, templates
            )
            
            results.extend(batch_results)
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.01)
        
        return results
    
    async def _process_batch_concurrent(
        self,
        sequences: List[EmailSequence],
        subscribers: List[Subscriber],
        templates: List[EmailTemplate]
    ) -> List[Dict[str, Any]]:
        """Process batch with concurrent optimization"""
        tasks = []
        
        for sequence in sequences:
            task = self._process_single_sequence_optimized(
                sequence, subscribers, templates
            )
            tasks.append(task)
        
        # Limit concurrent tasks
        semaphore = asyncio.Semaphore(self.config.max_concurrent_tasks)
        
        async def limited_task(task):
            async with semaphore:
                return await task
        
        limited_tasks = [limited_task(task) for task in tasks]
        
        results = await asyncio.gather(*limited_tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [
            result for result in results 
            if not isinstance(result, Exception)
        ]
        
        return valid_results
    
    async def _process_single_sequence_optimized(
        self,
        sequence: EmailSequence,
        subscribers: List[Subscriber],
        templates: List[EmailTemplate]
    ) -> Dict[str, Any]:
        """Process single sequence with optimization"""
        try:
            # Check cache first
            cache_key = f"sequence_{sequence.id}"
            if self.config.enable_caching and cache_key in self.cache:
                self.cache_hits += 1
                return self.cache[cache_key]
            
            # Process sequence
            result = await self._process_sequence_steps(sequence, subscribers, templates)
            
            # Cache result
            if self.config.enable_caching:
                self._add_to_cache(cache_key, result)
                self.cache_misses += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing sequence {sequence.id}: {e}")
            return {"error": str(e), "sequence_id": sequence.id}
    
    async def _process_sequence_steps(
        self,
        sequence: EmailSequence,
        subscribers: List[Subscriber],
        templates: List[EmailTemplate]
    ) -> Dict[str, Any]:
        """Process sequence steps with optimization"""
        processed_steps = []
        
        for step in sequence.steps:
            if step.is_active:
                step_result = await self._process_step_optimized(step, sequence, subscribers, templates)
                processed_steps.append(step_result)
        
        return {
            "sequence_id": sequence.id,
            "sequence_name": sequence.name,
            "processed_steps": processed_steps,
            "total_steps": len(sequence.steps),
            "active_steps": len(processed_steps)
        }
    
    async def _process_step_optimized(
        self,
        step: SequenceStep,
        sequence: EmailSequence,
        subscribers: List[Subscriber],
        templates: List[EmailTemplate]
    ) -> Dict[str, Any]:
        """Process step with optimization"""
        try:
            if step.step_type == "email":
                return await self._process_email_step_optimized(step, sequence, subscribers, templates)
            elif step.step_type == "delay":
                return await self._process_delay_step_optimized(step)
            elif step.step_type == "condition":
                return await self._process_condition_step_optimized(step)
            elif step.step_type == "action":
                return await self._process_action_step_optimized(step)
            elif step.step_type == "webhook":
                return await self._process_webhook_step_optimized(step)
            else:
                return {"step_type": "unknown", "step_id": step.id}
                
        except Exception as e:
            logger.error(f"Error processing step {step.id}: {e}")
            return {"error": str(e), "step_id": step.id}
    
    async def _process_email_step_optimized(
        self,
        step: SequenceStep,
        sequence: EmailSequence,
        subscribers: List[Subscriber],
        templates: List[EmailTemplate]
    ) -> Dict[str, Any]:
        """Process email step with optimization"""
        try:
            # Get relevant subscribers
            relevant_subscribers = self._get_relevant_subscribers(subscribers, sequence)
            
            # Process in smaller batches for memory efficiency
            email_results = []
            batch_size = min(self.config.batch_size, 32)  # Smaller batch for emails
            
            for i in range(0, len(relevant_subscribers), batch_size):
                batch = relevant_subscribers[i:i + batch_size]
                
                batch_results = await self._process_email_batch(step, sequence, batch, templates)
                email_results.extend(batch_results)
            
            return {
                "step_type": "email",
                "step_id": step.id,
                "emails_processed": len(email_results),
                "results": email_results
            }
            
        except Exception as e:
            logger.error(f"Error processing email step: {e}")
            return {"error": str(e), "step_type": "email", "step_id": step.id}
    
    async def _process_email_batch(
        self,
        step: SequenceStep,
        sequence: EmailSequence,
        subscribers: List[Subscriber],
        templates: List[EmailTemplate]
    ) -> List[Dict[str, Any]]:
        """Process email batch with optimization"""
        results = []
        
        for subscriber in subscribers:
            try:
                # Personalize content
                personalized_content = self._personalize_content_optimized(
                    step.content, subscriber, sequence.personalization_variables
                )
                
                # Simulate email sending (optimized)
                email_result = {
                    "subscriber_id": subscriber.id,
                    "email": subscriber.email,
                    "subject": step.subject,
                    "content_length": len(personalized_content),
                    "status": "sent"
                }
                
                results.append(email_result)
                
            except Exception as e:
                results.append({
                    "subscriber_id": subscriber.id,
                    "email": subscriber.email,
                    "status": "failed",
                    "error": str(e)
                })
        
        return results
    
    async def _process_delay_step_optimized(self, step: SequenceStep) -> Dict[str, Any]:
        """Process delay step with optimization"""
        try:
            delay_seconds = (step.delay_hours or 0) * 3600 + (step.delay_days or 0) * 86400
            
            # Optimize long delays
            if delay_seconds > 3600:  # More than 1 hour
                # Use non-blocking delay for long delays
                await asyncio.sleep(1)  # Simulate delay
            else:
                await asyncio.sleep(delay_seconds)
            
            return {
                "step_type": "delay",
                "step_id": step.id,
                "delay_seconds": delay_seconds
            }
            
        except Exception as e:
            logger.error(f"Error processing delay step: {e}")
            return {"error": str(e), "step_type": "delay", "step_id": step.id}
    
    async def _process_condition_step_optimized(self, step: SequenceStep) -> Dict[str, Any]:
        """Process condition step with optimization"""
        try:
            # Optimized condition evaluation
            condition_result = self._evaluate_condition_optimized(step.condition_expression)
            
            return {
                "step_type": "condition",
                "step_id": step.id,
                "condition_result": condition_result
            }
            
        except Exception as e:
            logger.error(f"Error processing condition step: {e}")
            return {"error": str(e), "step_type": "condition", "step_id": step.id}
    
    async def _process_action_step_optimized(self, step: SequenceStep) -> Dict[str, Any]:
        """Process action step with optimization"""
        try:
            # Optimized action execution
            action_result = await self._execute_action_optimized(step.action_type, step.action_data)
            
            return {
                "step_type": "action",
                "step_id": step.id,
                "action_result": action_result
            }
            
        except Exception as e:
            logger.error(f"Error processing action step: {e}")
            return {"error": str(e), "step_type": "action", "step_id": step.id}
    
    async def _process_webhook_step_optimized(self, step: SequenceStep) -> Dict[str, Any]:
        """Process webhook step with optimization"""
        try:
            # Optimized webhook execution
            webhook_result = await self._execute_webhook_optimized(step.webhook_url, step.webhook_method)
            
            return {
                "step_type": "webhook",
                "step_id": step.id,
                "webhook_result": webhook_result
            }
            
        except Exception as e:
            logger.error(f"Error processing webhook step: {e}")
            return {"error": str(e), "step_type": "webhook", "step_id": step.id}
    
    def _personalize_content_optimized(
        self,
        content: str,
        subscriber: Subscriber,
        variables: Optional[Dict[str, Any]]
    ) -> str:
        """Personalize content with optimization"""
        try:
            if not content:
                return ""
            
            personalized = content
            
            # Fast variable replacement
            if variables:
                for key, value in variables.items():
                    placeholder = f"{{{{{key}}}}}"
                    personalized = personalized.replace(placeholder, str(value))
            
            # Subscriber-specific personalization
            personalized = personalized.replace("{{first_name}}", subscriber.first_name or "")
            personalized = personalized.replace("{{last_name}}", subscriber.last_name or "")
            personalized = personalized.replace("{{email}}", subscriber.email)
            
            return personalized
            
        except Exception as e:
            logger.error(f"Error personalizing content: {e}")
            return content or ""
    
    def _evaluate_condition_optimized(self, condition_expression: Optional[str]) -> bool:
        """Evaluate condition with optimization"""
        try:
            if not condition_expression:
                return True
            
            # Simple condition evaluation for optimization
            # In a real implementation, this would use a proper expression evaluator
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    async def _execute_action_optimized(
        self,
        action_type: Optional[str],
        action_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute action with optimization"""
        try:
            if not action_type:
                return {"status": "skipped", "reason": "no_action_type"}
            
            # Simulate action execution
            return {
                "status": "executed",
                "action_type": action_type,
                "action_data": action_data
            }
            
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _execute_webhook_optimized(
        self,
        webhook_url: Optional[str],
        method: Optional[str]
    ) -> Dict[str, Any]:
        """Execute webhook with optimization"""
        try:
            if not webhook_url:
                return {"status": "skipped", "reason": "no_webhook_url"}
            
            # Simulate webhook execution
            return {
                "status": "executed",
                "webhook_url": webhook_url,
                "method": method or "POST"
            }
            
        except Exception as e:
            logger.error(f"Error executing webhook: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _get_relevant_subscribers(
        self,
        subscribers: List[Subscriber],
        sequence: EmailSequence
    ) -> List[Subscriber]:
        """Get relevant subscribers for sequence"""
        # Simple filtering for optimization
        # In a real implementation, this would use more sophisticated filtering
        return [sub for sub in subscribers if sub.status == "active"]
    
    def _is_memory_pressure(self) -> bool:
        """Check if system is under memory pressure"""
        try:
            memory_usage = psutil.virtual_memory().percent / 100
            return memory_usage > self.config.max_memory_usage
        except Exception:
            return False
    
    async def _optimize_memory(self) -> None:
        """Optimize memory usage"""
        try:
            # Clear cache if too large
            if len(self.cache) > self.config.cache_size:
                self.cache.clear()
            
            # Force garbage collection
            gc.collect()
            
            # Clear PyTorch cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("Memory optimization completed")
            
        except Exception as e:
            logger.error(f"Error optimizing memory: {e}")
    
    def _add_to_cache(self, key: str, value: Any) -> None:
        """Add item to cache with size management"""
        try:
            if len(self.cache) >= self.config.cache_size:
                # Remove oldest item (simple LRU)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
            self.cache[key] = value
            
        except Exception as e:
            logger.error(f"Error adding to cache: {e}")
    
    def _calculate_performance_metrics(self) -> PerformanceMetrics:
        """Calculate performance metrics"""
        try:
            # Memory usage
            memory_usage = psutil.virtual_memory().percent / 100
            
            # CPU usage
            cpu_usage = psutil.cpu_percent() / 100
            
            # Processing time
            avg_processing_time = np.mean(self.processing_times) if self.processing_times else 0.0
            
            # Cache hit rate
            total_cache_operations = self.cache_hits + self.cache_misses
            cache_hit_rate = self.cache_hits / total_cache_operations if total_cache_operations > 0 else 0.0
            
            # Batch efficiency (simplified)
            batch_efficiency = 0.8  # Placeholder
            
            # Error rate
            error_rate = self.error_count / max(self.total_operations, 1)
            
            return PerformanceMetrics(
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                processing_time=avg_processing_time,
                cache_hit_rate=cache_hit_rate,
                batch_efficiency=batch_efficiency,
                error_rate=error_rate
            )
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return PerformanceMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        metrics = self._calculate_performance_metrics()
        
        return {
            "cache_stats": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "hit_rate": metrics.cache_hit_rate,
                "size": len(self.cache)
            },
            "performance_metrics": {
                "memory_usage": metrics.memory_usage,
                "cpu_usage": metrics.cpu_usage,
                "avg_processing_time": metrics.processing_time,
                "batch_efficiency": metrics.batch_efficiency,
                "error_rate": metrics.error_rate
            },
            "operations": {
                "total": self.total_operations,
                "errors": self.error_count,
                "uptime": time.time() - self.start_time
            }
        } 