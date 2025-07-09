"""
Key Messages service for Onyx.
"""
import logging
import time
import asyncio
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib
import json

from onyx.utils.logger import setup_logger
from onyx.core.exceptions import ServiceException, ValidationException
from onyx.core.functions import format_response, handle_error
from onyx.server.features.key_messages.models import (
    KeyMessageRequest,
    GeneratedResponse,
    KeyMessageResponse,
    MessageType,
    MessageTone,
    MessageAnalysis,
    BatchKeyMessageRequest,
    BatchKeyMessageResponse
)

logger = setup_logger(__name__)

# Pre-generated responses for common patterns
COMMON_RESPONSES = {
    "test_message": {
        "informational": {
            "professional": "Test message received. System operational.",
            "casual": "Hey! Got your test message, everything's working fine!",
            "friendly": "Hi there! Your test message came through perfectly.",
            "authoritative": "Test message confirmed. System status: Operational.",
            "conversational": "Got your test message! Everything's working as expected."
        }
    },
    "welcome": {
        "marketing": {
            "professional": "Welcome to our platform. Start your journey today.",
            "casual": "Hey! Welcome aboard! Let's get started!",
            "friendly": "Welcome! We're excited to have you here!",
            "authoritative": "Welcome. Your success journey begins now.",
            "conversational": "Welcome! Ready to explore what we offer?"
        }
    }
}

class KeyMessageService:
    """Service for generating and analyzing key messages."""
    
    def __init__(self):
        """Initialize the service."""
        self.cache = {}
        self.cache_ttl = timedelta(hours=24)
        logger.info("KeyMessageService initialized")
    
    def _generate_cache_key(self, data: Dict) -> str:
        """Generate a cache key for the given data."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if available and not expired using if-return pattern."""
        if cache_key not in self.cache:
            return None
        
        cached_data = self.cache[cache_key]
        if datetime.now() - cached_data['timestamp'] >= self.cache_ttl:
            del self.cache[cache_key]
            return None
        
        return cached_data['response']
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache a response with timestamp."""
        self.cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now()
        }
    
    async def generate_response(self, request: KeyMessageRequest) -> KeyMessageResponse:
        """Generate a response for a key message."""
        start_time = time.perf_counter()
        
        try:
            # Validate request
            if not request.message.strip():
                raise ValidationException("Message cannot be empty")
            
            # Generate cache key
            cache_key = self._generate_cache_key(request.model_dump())
            
            # Check cache
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                logger.info(f"Cache hit for key: {cache_key}")
                return await self._create_response(
                    request, cached_response, start_time, from_cache=True
                )
            
            # Check for common responses
            if request.message.lower() in COMMON_RESPONSES:
                common_responses = COMMON_RESPONSES[request.message.lower()]
                if request.message_type.value in common_responses:
                    tone_responses = common_responses[request.message_type.value]
                    if request.tone.value in tone_responses:
                        response = tone_responses[request.tone.value]
                        self._cache_response(cache_key, response)
                        return await self._create_response(request, response, start_time)
            
            # Generate new response using LLM
            response = await self._generate_with_llm(request)
            
            # Cache the response
            self._cache_response(cache_key, response)
            
            return await self._create_response(request, response, start_time)
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return KeyMessageResponse(
                success=False,
                error=str(e),
                processing_time=time.perf_counter() - start_time
            )
    
    async def analyze_message(self, request: KeyMessageRequest) -> KeyMessageResponse:
        """Analyze a message and return insights."""
        start_time = time.perf_counter()
        
        try:
            # Validate request
            if not request.message.strip():
                raise ValidationException("Message cannot be empty")
            
            # Generate cache key for analysis
            cache_key = f"analysis_{self._generate_cache_key(request.model_dump())}"
            
            # Check cache
            cached_analysis = self._get_cached_response(cache_key)
            if cached_analysis:
                logger.info(f"Analysis cache hit for key: {cache_key}")
                return await self._create_analysis_response(
                    request, cached_analysis, start_time, from_cache=True
                )
            
            # Perform analysis
            analysis = await self._analyze_with_llm(request)
            
            # Cache the analysis
            self._cache_response(cache_key, analysis)
            
            return await self._create_analysis_response(request, analysis, start_time)
            
        except Exception as e:
            logger.error(f"Error analyzing message: {str(e)}")
            return KeyMessageResponse(
                success=False,
                error=str(e),
                processing_time=time.perf_counter() - start_time
            )
    
    async def generate_batch(self, request: BatchKeyMessageRequest) -> BatchKeyMessageResponse:
        """Generate responses for multiple messages in batch."""
        start_time = time.perf_counter()
        results = []
        failed_count = 0
        
        try:
            # Limit batch size
            batch_size = min(request.batch_size, 50)
            messages = request.messages[:batch_size]
            
            # Process messages concurrently
            tasks = [self.generate_response(msg) for msg in messages]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.error(f"Error processing message {i}: {str(response)}")
                    results.append(KeyMessageResponse(
                        success=False,
                        error=str(response),
                        processing_time=0.0
                    ))
                    failed_count += 1
                    continue
                
                results.append(response)
                if not response.success:
                    failed_count += 1
            
            return BatchKeyMessageResponse(
                success=failed_count == 0,
                results=results,
                total_processed=len(messages),
                failed_count=failed_count,
                processing_time=time.perf_counter() - start_time
            )
            
        except Exception as e:
            logger.error(f"Error in batch generation: {str(e)}")
            return BatchKeyMessageResponse(
                success=False,
                results=[],
                total_processed=0,
                failed_count=len(request.messages),
                processing_time=time.perf_counter() - start_time
            )
    
    async def _generate_with_llm(self, request: KeyMessageRequest) -> str:
        """Generate response using LLM."""
        try:
            # Prepare the prompt for the LLM
            prompt = f"""Generate a {request.message_type.value} message with a {request.tone.value} tone.
            
            Original message: {request.message}
            
            Additional context:
            - Target audience: {request.target_audience or 'General audience'}
            - Context: {request.context or 'No specific context provided'}
            - Keywords to include: {', '.join(request.keywords) if request.keywords else 'None specified'}
            - Industry: {request.industry or 'General'}
            - Call to action: {request.call_to_action or 'None specified'}
            
            Requirements:
            - Maintain the specified tone throughout
            - Include relevant keywords naturally
            - Keep it engaging and clear
            - Length: {request.max_length or 'Appropriate for the message type'}
            
            Generate the response:"""
            
            # Call LLM (placeholder - replace with actual LLM call)
            # For now, return a generated response
            response = await self._call_llm_api(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in LLM generation: {str(e)}")
            raise ServiceException(f"Failed to generate response: {str(e)}")
    
    async def _analyze_with_llm(self, request: KeyMessageRequest) -> str:
        """Analyze message using LLM."""
        try:
            prompt = f"""Analyze the following message and provide insights:
            
            Message: {request.message}
            Type: {request.message_type.value}
            Tone: {request.tone.value}
            
            Provide analysis on:
            1. Sentiment
            2. Tone consistency
            3. Clarity and readability
            4. Engagement potential
            5. Keyword optimization
            6. Suggestions for improvement
            
            Analysis:"""
            
            # Call LLM (placeholder - replace with actual LLM call)
            analysis = await self._call_llm_api(prompt)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in LLM analysis: {str(e)}")
            raise ServiceException(f"Failed to analyze message: {str(e)}")
    
    async def _call_llm_api(self, prompt: str) -> str:
        """Call the LLM API (placeholder implementation)."""
        # Simulate API call delay
        await asyncio.sleep(0.1)
        
        # Return a mock response for now
        # In production, this would call the actual LLM service
        return f"Generated response for: {prompt[:50]}..."
    
    async def _create_response(
        self, 
        request: KeyMessageRequest, 
        response: str, 
        start_time: float,
        from_cache: bool = False
    ) -> KeyMessageResponse:
        """Create a KeyMessageResponse from the generated content."""
        processing_time = time.perf_counter() - start_time
        
        generated_response = GeneratedResponse(
            id=str(uuid.uuid4()),
            original_message=request.message,
            response=response,
            message_type=request.message_type,
            tone=request.tone,
            created_at=datetime.now(),
            word_count=len(response.split()),
            character_count=len(response),
            keywords_used=request.keywords,
            sentiment_score=0.5,  # Placeholder
            readability_score=0.8,  # Placeholder
            processing_time=processing_time,
            suggestions=[]
        )
        
        return KeyMessageResponse(
            success=True,
            data=generated_response,
            processing_time=processing_time,
            metadata={"from_cache": from_cache}
        )
    
    async def _create_analysis_response(
        self, 
        request: KeyMessageRequest, 
        analysis: str, 
        start_time: float,
        from_cache: bool = False
    ) -> KeyMessageResponse:
        """Create a KeyMessageResponse for analysis results."""
        processing_time = time.perf_counter() - start_time
        
        generated_response = GeneratedResponse(
            id=str(uuid.uuid4()),
            original_message=request.message,
            response=analysis,
            message_type=request.message_type,
            tone=request.tone,
            created_at=datetime.now(),
            word_count=len(request.message.split()),
            character_count=len(request.message),
            keywords_used=request.keywords,
            sentiment_score=0.6,  # Placeholder
            readability_score=0.7,  # Placeholder
            processing_time=processing_time,
            suggestions=[]
        )
        
        return KeyMessageResponse(
            success=True,
            data=generated_response,
            processing_time=processing_time,
            metadata={"from_cache": from_cache, "analysis": True}
        )
    
    async def clear_cache(self):
        """Clear all cached responses."""
        self.cache.clear()
        logger.info("Key message cache cleared")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self.cache),
            "cache_ttl_hours": self.cache_ttl.total_seconds() / 3600,
            "cache_keys": list(self.cache.keys())
        } 