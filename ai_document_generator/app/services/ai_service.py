"""
AI service for integrating with various AI providers
"""
import asyncio
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import uuid

import httpx
from openai import AsyncOpenAI
import anthropic

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import AIProviderError
from app.schemas.ai import (
    AIGenerationRequest, AIGenerationResponse, AIProvider, AIModel,
    AIContentAnalysisRequest, AIContentAnalysisResponse,
    AITranslationRequest, AITranslationResponse,
    AISummarizationRequest, AISummarizationResponse,
    AIImprovementRequest, AIImprovementResponse,
    AIBatchRequest, AIBatchResponse,
    AIProviderConfig, AIProviderStatus
)

logger = get_logger(__name__)


class AIService:
    """Service for AI operations with multiple providers."""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.client_cache = {}
    
    def _initialize_providers(self) -> Dict[AIProvider, AIProviderConfig]:
        """Initialize AI provider configurations."""
        providers = {}
        
        if settings.OPENAI_API_KEY:
            providers[AIProvider.OPENAI] = AIProviderConfig(
                provider=AIProvider.OPENAI,
                api_key=settings.OPENAI_API_KEY,
                is_enabled=True,
                priority=1
            )
        
        if settings.ANTHROPIC_API_KEY:
            providers[AIProvider.ANTHROPIC] = AIProviderConfig(
                provider=AIProvider.ANTHROPIC,
                api_key=settings.ANTHROPIC_API_KEY,
                is_enabled=True,
                priority=2
            )
        
        if settings.DEEPSEEK_API_KEY:
            providers[AIProvider.DEEPSEEK] = AIProviderConfig(
                provider=AIProvider.DEEPSEEK,
                api_key=settings.DEEPSEEK_API_KEY,
                is_enabled=True,
                priority=3
            )
        
        if settings.GOOGLE_AI_API_KEY:
            providers[AIProvider.GOOGLE] = AIProviderConfig(
                provider=AIProvider.GOOGLE,
                api_key=settings.GOOGLE_AI_API_KEY,
                is_enabled=True,
                priority=4
            )
        
        return providers
    
    async def _get_client(self, provider: AIProvider) -> Any:
        """Get or create AI provider client."""
        if provider in self.client_cache:
            return self.client_cache[provider]
        
        config = self.providers.get(provider)
        if not config or not config.is_enabled:
            raise AIProviderError(f"Provider {provider} is not available")
        
        try:
            if provider == AIProvider.OPENAI:
                client = AsyncOpenAI(api_key=config.api_key)
            elif provider == AIProvider.ANTHROPIC:
                client = anthropic.AsyncAnthropic(api_key=config.api_key)
            elif provider == AIProvider.DEEPSEEK:
                client = AsyncOpenAI(
                    api_key=config.api_key,
                    base_url="https://api.deepseek.com"
                )
            elif provider == AIProvider.GOOGLE:
                # Google AI client implementation
                client = None  # Implement Google AI client
            else:
                raise AIProviderError(f"Unsupported provider: {provider}")
            
            self.client_cache[provider] = client
            return client
        
        except Exception as e:
            logger.error(f"Failed to initialize {provider} client: {e}")
            raise AIProviderError(f"Failed to initialize {provider} client")
    
    async def generate_content(self, request: AIGenerationRequest) -> AIGenerationResponse:
        """Generate content using specified AI provider."""
        start_time = time.time()
        
        try:
            client = await self._get_client(request.provider)
            
            if request.provider == AIProvider.OPENAI:
                response = await self._generate_openai(client, request)
            elif request.provider == AIProvider.ANTHROPIC:
                response = await self._generate_anthropic(client, request)
            elif request.provider == AIProvider.DEEPSEEK:
                response = await self._generate_deepseek(client, request)
            else:
                raise AIProviderError(f"Unsupported provider: {request.provider}")
            
            processing_time = time.time() - start_time
            
            return AIGenerationResponse(
                id=uuid.uuid4(),
                content=response["content"],
                provider=request.provider,
                model=request.model,
                usage=response["usage"],
                finish_reason=response["finish_reason"],
                created_at=datetime.utcnow()
            )
        
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            raise AIProviderError(f"AI generation failed: {str(e)}")
    
    async def _generate_openai(self, client: AsyncOpenAI, request: AIGenerationRequest) -> Dict[str, Any]:
        """Generate content using OpenAI."""
        messages = []
        
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        
        messages.append({"role": "user", "content": request.prompt})
        
        response = await client.chat.completions.create(
            model=request.model.value,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
            stop=request.stop_sequences
        )
        
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "tokens_used": response.usage.total_tokens,
                "tokens_prompt": response.usage.prompt_tokens,
                "tokens_completion": response.usage.completion_tokens
            },
            "finish_reason": response.choices[0].finish_reason
        }
    
    async def _generate_anthropic(self, client: anthropic.AsyncAnthropic, request: AIGenerationRequest) -> Dict[str, Any]:
        """Generate content using Anthropic."""
        system_prompt = request.system_prompt or "You are a helpful assistant."
        
        response = await client.messages.create(
            model=request.model.value,
            max_tokens=request.max_tokens or 1000,
            temperature=request.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": request.prompt}]
        )
        
        return {
            "content": response.content[0].text,
            "usage": {
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "tokens_prompt": response.usage.input_tokens,
                "tokens_completion": response.usage.output_tokens
            },
            "finish_reason": response.stop_reason
        }
    
    async def _generate_deepseek(self, client: AsyncOpenAI, request: AIGenerationRequest) -> Dict[str, Any]:
        """Generate content using DeepSeek."""
        messages = []
        
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        
        messages.append({"role": "user", "content": request.prompt})
        
        response = await client.chat.completions.create(
            model=request.model.value,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
            stop=request.stop_sequences
        )
        
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "tokens_used": response.usage.total_tokens,
                "tokens_prompt": response.usage.prompt_tokens,
                "tokens_completion": response.usage.completion_tokens
            },
            "finish_reason": response.choices[0].finish_reason
        }
    
    async def analyze_content(self, request: AIContentAnalysisRequest) -> AIContentAnalysisResponse:
        """Analyze content using AI."""
        start_time = time.time()
        
        try:
            # Create analysis prompt based on type
            prompt = self._create_analysis_prompt(request)
            
            generation_request = AIGenerationRequest(
                prompt=prompt,
                provider=request.provider,
                model=request.model,
                system_prompt=self._get_analysis_system_prompt(request.analysis_type)
            )
            
            response = await self.generate_content(generation_request)
            
            # Parse analysis results
            results = self._parse_analysis_results(response.content, request.analysis_type)
            
            return AIContentAnalysisResponse(
                id=uuid.uuid4(),
                analysis_type=request.analysis_type,
                results=results,
                confidence=results.get("confidence", 0.8),
                provider=request.provider,
                model=request.model,
                created_at=datetime.utcnow()
            )
        
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            raise AIProviderError(f"Content analysis failed: {str(e)}")
    
    def _create_analysis_prompt(self, request: AIContentAnalysisRequest) -> str:
        """Create analysis prompt based on type."""
        if request.analysis_type == "sentiment":
            return f"Analyze the sentiment of the following text and provide a score from -1 (very negative) to 1 (very positive):\n\n{request.content}"
        elif request.analysis_type == "quality":
            return f"Analyze the quality of the following text and provide scores for grammar, clarity, coherence, and style (0-10 scale):\n\n{request.content}"
        elif request.analysis_type == "plagiarism":
            return f"Check the following text for potential plagiarism and provide a similarity score (0-1):\n\n{request.content}"
        elif request.analysis_type == "readability":
            return f"Analyze the readability of the following text and provide a readability score and grade level:\n\n{request.content}"
        elif request.analysis_type == "summary":
            return f"Provide a concise summary of the following text:\n\n{request.content}"
        else:
            raise AIProviderError(f"Unsupported analysis type: {request.analysis_type}")
    
    def _get_analysis_system_prompt(self, analysis_type: str) -> str:
        """Get system prompt for analysis type."""
        prompts = {
            "sentiment": "You are an expert sentiment analysis tool. Provide accurate sentiment scores and explanations.",
            "quality": "You are an expert writing quality assessor. Provide detailed quality scores and suggestions.",
            "plagiarism": "You are a plagiarism detection tool. Provide similarity scores and identify potential issues.",
            "readability": "You are a readability analysis tool. Provide readability scores and grade levels.",
            "summary": "You are an expert summarization tool. Provide clear, concise summaries."
        }
        return prompts.get(analysis_type, "You are a helpful analysis tool.")
    
    def _parse_analysis_results(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """Parse analysis results from AI response."""
        # This is a simplified parser - in production, you'd want more robust parsing
        try:
            import json
            return json.loads(content)
        except:
            # Fallback to basic parsing
            return {
                "raw_response": content,
                "confidence": 0.8
            }
    
    async def translate_content(self, request: AITranslationRequest) -> AITranslationResponse:
        """Translate content using AI."""
        start_time = time.time()
        
        try:
            prompt = f"Translate the following text from {request.source_language} to {request.target_language}:\n\n{request.content}"
            
            generation_request = AIGenerationRequest(
                prompt=prompt,
                provider=request.provider,
                model=request.model,
                system_prompt="You are an expert translator. Provide accurate, natural translations while preserving the original meaning and tone."
            )
            
            response = await self.generate_content(generation_request)
            
            return AITranslationResponse(
                id=uuid.uuid4(),
                original_content=request.content,
                translated_content=response.content,
                source_language=request.source_language,
                target_language=request.target_language,
                confidence=0.9,  # Could be calculated based on response quality
                provider=request.provider,
                model=request.model,
                created_at=datetime.utcnow()
            )
        
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise AIProviderError(f"Translation failed: {str(e)}")
    
    async def summarize_content(self, request: AISummarizationRequest) -> AISummarizationResponse:
        """Summarize content using AI."""
        start_time = time.time()
        
        try:
            if request.summary_type == "extractive":
                prompt = f"Create an extractive summary of the following text (select the most important sentences):\n\n{request.content}"
            elif request.summary_type == "abstractive":
                prompt = f"Create an abstractive summary of the following text in approximately {request.max_length} words:\n\n{request.content}"
            elif request.summary_type == "bullet_points":
                prompt = f"Create a bullet-point summary of the following text:\n\n{request.content}"
            else:
                raise AIProviderError(f"Unsupported summary type: {request.summary_type}")
            
            generation_request = AIGenerationRequest(
                prompt=prompt,
                provider=request.provider,
                model=request.model,
                system_prompt="You are an expert summarization tool. Create clear, concise summaries that capture the key points."
            )
            
            response = await self.generate_content(generation_request)
            
            # Calculate compression ratio
            original_length = len(request.content.split())
            summary_length = len(response.content.split())
            compression_ratio = summary_length / original_length if original_length > 0 else 0
            
            return AISummarizationResponse(
                id=uuid.uuid4(),
                original_content=request.content,
                summary=response.content,
                summary_type=request.summary_type,
                compression_ratio=compression_ratio,
                provider=request.provider,
                model=request.model,
                created_at=datetime.utcnow()
            )
        
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise AIProviderError(f"Summarization failed: {str(e)}")
    
    async def improve_content(self, request: AIImprovementRequest) -> AIImprovementResponse:
        """Improve content using AI."""
        start_time = time.time()
        
        try:
            prompt = self._create_improvement_prompt(request)
            
            generation_request = AIGenerationRequest(
                prompt=prompt,
                provider=request.provider,
                model=request.model,
                system_prompt="You are an expert writing improvement tool. Provide improved versions with clear explanations of changes."
            )
            
            response = await self.generate_content(generation_request)
            
            # Parse improvements (simplified)
            changes = self._parse_improvements(response.content)
            
            return AIImprovementResponse(
                id=uuid.uuid4(),
                original_content=request.content,
                improved_content=response.content,
                improvement_type=request.improvement_type,
                changes=changes,
                confidence=0.8,
                provider=request.provider,
                model=request.model,
                created_at=datetime.utcnow()
            )
        
        except Exception as e:
            logger.error(f"Content improvement failed: {e}")
            raise AIProviderError(f"Content improvement failed: {str(e)}")
    
    def _create_improvement_prompt(self, request: AIImprovementRequest) -> str:
        """Create improvement prompt based on type."""
        base_prompt = f"Improve the following text for {request.improvement_type}:\n\n{request.content}\n\n"
        
        if request.target_audience:
            base_prompt += f"Target audience: {request.target_audience}\n"
        
        if request.writing_style:
            base_prompt += f"Writing style: {request.writing_style}\n"
        
        base_prompt += "Provide the improved version and explain the key changes made."
        
        return base_prompt
    
    def _parse_improvements(self, content: str) -> List[Dict[str, Any]]:
        """Parse improvement changes from AI response."""
        # Simplified parsing - in production, you'd want more sophisticated parsing
        return [
            {
                "type": "improvement",
                "description": "Content improved for better clarity and style",
                "confidence": 0.8
            }
        ]
    
    async def process_batch(self, request: AIBatchRequest) -> AIBatchResponse:
        """Process multiple AI requests in batch."""
        start_time = time.time()
        
        try:
            tasks = []
            for req in request.requests:
                if isinstance(req, AIGenerationRequest):
                    task = self.generate_content(req)
                elif isinstance(req, AIContentAnalysisRequest):
                    task = self.analyze_content(req)
                elif isinstance(req, AITranslationRequest):
                    task = self.translate_content(req)
                elif isinstance(req, AISummarizationRequest):
                    task = self.summarize_content(req)
                elif isinstance(req, AIImprovementRequest):
                    task = self.improve_content(req)
                else:
                    raise AIProviderError(f"Unsupported request type: {type(req)}")
                
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_results = []
            failed_count = 0
            
            for result in results:
                if isinstance(result, Exception):
                    failed_count += 1
                    successful_results.append({"error": str(result)})
                else:
                    successful_results.append(result.dict())
            
            processing_time = time.time() - start_time
            
            return AIBatchResponse(
                id=uuid.uuid4(),
                results=successful_results,
                total_requests=len(request.requests),
                successful_requests=len(request.requests) - failed_count,
                failed_requests=failed_count,
                processing_time=processing_time,
                created_at=datetime.utcnow()
            )
        
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise AIProviderError(f"Batch processing failed: {str(e)}")
    
    async def get_provider_status(self, provider: AIProvider) -> AIProviderStatus:
        """Get status of AI provider."""
        try:
            config = self.providers.get(provider)
            if not config or not config.is_enabled:
                return AIProviderStatus(
                    provider=provider,
                    is_available=False,
                    error_rate=1.0,
                    last_check=datetime.utcnow(),
                    error_message="Provider not configured or disabled"
                )
            
            # Test provider with simple request
            start_time = time.time()
            test_request = AIGenerationRequest(
                prompt="Hello",
                provider=provider,
                model=AIModel.GPT_3_5_TURBO if provider == AIProvider.OPENAI else AIModel.CLAUDE_3_HAIKU,
                max_tokens=10
            )
            
            await self.generate_content(test_request)
            response_time = time.time() - start_time
            
            return AIProviderStatus(
                provider=provider,
                is_available=True,
                response_time=response_time,
                error_rate=0.0,
                last_check=datetime.utcnow()
            )
        
        except Exception as e:
            return AIProviderStatus(
                provider=provider,
                is_available=False,
                error_rate=1.0,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )


# Global AI service instance
ai_service = AIService()




