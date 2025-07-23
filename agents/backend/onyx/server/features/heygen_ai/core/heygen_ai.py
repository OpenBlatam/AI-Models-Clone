"""
Main HeyGen AI class that orchestrates the entire video generation pipeline.
Now with LangChain and OpenRouter integration.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import uuid

from pydantic import BaseModel, Field
from .avatar_manager import AvatarManager
from .voice_engine import VoiceEngine
from .video_renderer import VideoRenderer
from .script_generator import ScriptGenerator
from .langchain_manager import LangChainManager
from .advanced_ai_workflows import AdvancedAIWorkflows

logger = logging.getLogger(__name__)


class VideoRequest(BaseModel):
    """Request model for video generation."""
    script: str = Field(..., description="Script text for the video")
    avatar_id: str = Field(..., description="ID of the avatar to use")
    voice_id: str = Field(..., description="ID of the voice to use")
    language: str = Field(default="en", description="Language code")
    output_format: str = Field(default="mp4", description="Output video format")
    resolution: str = Field(default="1080p", description="Video resolution")
    duration: Optional[int] = Field(None, description="Video duration in seconds")
    background: Optional[str] = Field(None, description="Background image/video URL")
    custom_settings: Optional[Dict] = Field(default_factory=dict)


class VideoResponse(BaseModel):
    """Response model for video generation."""
    video_id: str
    status: str
    output_url: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    metadata: Dict = Field(default_factory=dict)


class HeyGenAI:
    """
    Main class for HeyGen AI equivalent functionality with LangChain integration.
    
    This class orchestrates the entire video generation pipeline including:
    - Avatar management
    - Voice synthesis
    - Video rendering
    - Script generation with LangChain and OpenRouter
    - Advanced AI workflows
    - Automated content creation
    """
    
    def __init__(self, config_path: Optional[str] = None, openrouter_api_key: Optional[str] = None):
        """Initialize the HeyGen AI system with LangChain support."""
        self.config_path = config_path
        self.openrouter_api_key = openrouter_api_key
        
        # Initialize core components
        self.avatar_manager = AvatarManager()
        self.voice_engine = VoiceEngine()
        self.video_renderer = VideoRenderer()
        self.script_generator = ScriptGenerator(openrouter_api_key)
        
        # Initialize LangChain manager if API key is provided
        self.langchain_manager = None
        self.advanced_workflows = None
        if openrouter_api_key:
            self.langchain_manager = LangChainManager(openrouter_api_key)
            self.advanced_workflows = AdvancedAIWorkflows(self.langchain_manager)
        
        # Initialize components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all system components."""
        try:
            self.avatar_manager.initialize()
            self.voice_engine.initialize()
            self.video_renderer.initialize()
            self.script_generator.initialize()
            
            # Initialize LangChain manager if available
            if self.langchain_manager:
                self.langchain_manager.initialize()
                logger.info("LangChain Manager initialized successfully")
                
                # Initialize advanced workflows
                if self.advanced_workflows:
                    self.advanced_workflows.initialize()
                    logger.info("Advanced AI Workflows initialized successfully")
            
            logger.info("All HeyGen AI components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def create_video(self, request: VideoRequest) -> VideoResponse:
        """
        Create a video with the specified parameters.
        
        Args:
            request: VideoRequest object containing all video parameters
            
        Returns:
            VideoResponse object with video details
        """
        video_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting video generation for ID: {video_id}")
            
            # Step 1: Process script (with LangChain if available)
            processed_script = await self.script_generator.process_script(
                request.script, request.language
            )
            
            # Step 2: Generate voice audio
            audio_path = await self.voice_engine.synthesize_speech(
                processed_script, request.voice_id, request.language
            )
            
            # Step 3: Generate avatar video
            avatar_video_path = await self.avatar_manager.generate_avatar_video(
                request.avatar_id, audio_path, request.duration
            )
            
            # Step 4: Render final video
            final_video_path = await self.video_renderer.render_video(
                avatar_video_path, audio_path, request.background,
                request.resolution, request.output_format
            )
            
            # Step 5: Upload to storage and get URL
            output_url = await self._upload_video(final_video_path, video_id)
            
            # Get video metadata
            duration = await self.video_renderer.get_video_duration(final_video_path)
            file_size = Path(final_video_path).stat().st_size
            
            return VideoResponse(
                video_id=video_id,
                status="completed",
                output_url=output_url,
                duration=duration,
                file_size=file_size,
                metadata={
                    "avatar_id": request.avatar_id,
                    "voice_id": request.voice_id,
                    "language": request.language,
                    "resolution": request.resolution,
                    "langchain_used": self.langchain_manager is not None
                }
            )
            
        except Exception as e:
            logger.error(f"Video generation failed for ID {video_id}: {e}")
            return VideoResponse(
                video_id=video_id,
                status="failed",
                metadata={"error": str(e)}
            )
    
    async def create_video_sync(self, request: VideoRequest) -> VideoResponse:
        """Synchronous wrapper for create_video."""
        return await self.create_video(request)
    
    async def batch_create_videos(self, requests: List[VideoRequest]) -> List[VideoResponse]:
        """
        Create multiple videos in batch.
        
        Args:
            requests: List of VideoRequest objects
            
        Returns:
            List of VideoResponse objects
        """
        tasks = [self.create_video(request) for request in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    # Advanced Workflow Methods
    async def create_educational_series(self, topic: str, series_length: int = 5) -> Dict[str, Any]:
        """
        Create a complete educational video series using advanced AI workflows.
        
        Args:
            topic: Main topic for the series
            series_length: Number of videos in the series
            
        Returns:
            Series creation results with all episodes
        """
        if not self.advanced_workflows:
            raise ValueError("Advanced workflows not available. Please provide OpenRouter API key.")
        
        return await self.advanced_workflows.execute_educational_series_workflow(topic, series_length)
    
    async def create_marketing_campaign(self, product_info: Dict, target_audience: str) -> Dict[str, Any]:
        """
        Create a marketing campaign with multiple video variants.
        
        Args:
            product_info: Product information dictionary
            target_audience: Target audience description
            
        Returns:
            Marketing campaign results
        """
        if not self.advanced_workflows:
            raise ValueError("Advanced workflows not available. Please provide OpenRouter API key.")
        
        return await self.advanced_workflows.execute_marketing_campaign_workflow(product_info, target_audience)
    
    async def create_product_demo(self, product_info: Dict) -> Dict[str, Any]:
        """
        Create a product demonstration video with feature analysis.
        
        Args:
            product_info: Product information dictionary
            
        Returns:
            Product demo results
        """
        if not self.advanced_workflows:
            raise ValueError("Advanced workflows not available. Please provide OpenRouter API key.")
        
        return await self.advanced_workflows.execute_product_demo_workflow(product_info)
    
    async def create_news_summary(self, news_topic: str, target_languages: List[str] = ["en"]) -> Dict[str, Any]:
        """
        Create a news summary video with fact-checking and multi-language support.
        
        Args:
            news_topic: News topic to summarize
            target_languages: List of target languages for translation
            
        Returns:
            News summary results
        """
        if not self.advanced_workflows:
            raise ValueError("Advanced workflows not available. Please provide OpenRouter API key.")
        
        return await self.advanced_workflows.execute_news_summary_workflow(news_topic, target_languages)
    
    # Legacy Methods (for backward compatibility)
    async def get_available_avatars(self) -> List[Dict]:
        """Get list of available avatars."""
        return await self.avatar_manager.get_available_avatars()
    
    async def get_available_voices(self) -> List[Dict]:
        """Get list of available voices."""
        return await self.voice_engine.get_available_voices()
    
    async def generate_script(self, topic: str, language: str = "en", 
                            style: str = "professional", duration: str = "2 minutes",
                            context: str = "") -> str:
        """
        Generate a script using LangChain and OpenRouter.
        
        Args:
            topic: Topic for the script
            language: Language code
            style: Script style (professional, casual, etc.)
            duration: Target duration
            context: Additional context for generation
            
        Returns:
            Generated script text
        """
        return await self.script_generator.generate_script(
            topic, language, style, duration, context
        )
    
    async def optimize_script(self, script: str, duration: str = "2 minutes",
                            style: str = "professional", language: str = "en") -> str:
        """
        Optimize a script using LangChain.
        
        Args:
            script: Original script
            duration: Target duration
            style: Script style
            language: Target language
            
        Returns:
            Optimized script text
        """
        return await self.script_generator.process_script(script, language)
    
    async def translate_script(self, script: str, target_language: str,
                             source_language: str = "en", preserve_style: bool = True) -> str:
        """
        Translate script to target language using LangChain.
        
        Args:
            script: Source script text
            target_language: Target language code
            source_language: Source language code
            preserve_style: Whether to preserve original style
            
        Returns:
            Translated script text
        """
        return await self.script_generator.translate_script(
            script, target_language, source_language, preserve_style
        )
    
    async def analyze_script(self, script: str) -> Dict:
        """
        Analyze script for various metrics using LangChain.
        
        Args:
            script: Script text to analyze
            
        Returns:
            Analysis results dictionary
        """
        return await self.script_generator.analyze_script(script)
    
    async def chat_with_agent(self, message: str) -> str:
        """
        Chat with LangChain agent for complex workflows.
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        return await self.script_generator.chat_with_agent(message)
    
    async def create_knowledge_base(self, documents: List[str], name: str = "scripts"):
        """
        Create a knowledge base for script generation using LangChain.
        
        Args:
            documents: List of document texts
            name: Name for the knowledge base
        """
        await self.script_generator.create_knowledge_base(documents, name)
    
    async def search_knowledge_base(self, query: str, name: str = "scripts", k: int = 5) -> List[str]:
        """
        Search knowledge base for relevant content.
        
        Args:
            query: Search query
            name: Knowledge base name
            k: Number of results
            
        Returns:
            List of relevant document chunks
        """
        return await self.script_generator.search_knowledge_base(query, name, k)
    
    async def _upload_video(self, video_path: str, video_id: str) -> str:
        """Upload video to cloud storage and return URL."""
        # Implementation would depend on cloud storage provider
        # For now, return a placeholder URL
        return f"https://storage.example.com/videos/{video_id}.mp4"
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all components."""
        health_status = {
            "avatar_manager": self.avatar_manager.is_healthy(),
            "voice_engine": self.voice_engine.is_healthy(),
            "video_renderer": self.video_renderer.is_healthy(),
            "script_generator": self.script_generator.is_healthy()
        }
        
        # Add LangChain health status if available
        if self.langchain_manager:
            health_status["langchain_manager"] = self.langchain_manager.is_healthy()
            
        # Add advanced workflows health status if available
        if self.advanced_workflows:
            health_status["advanced_workflows"] = self.advanced_workflows.is_healthy()
        
        return health_status
    
    def get_langchain_status(self) -> Dict[str, bool]:
        """Get LangChain integration status."""
        if self.langchain_manager:
            return {
                "enabled": True,
                "healthy": self.langchain_manager.is_healthy(),
                "models_available": len(self.langchain_manager.models) > 0,
                "chains_available": len(self.langchain_manager.chains) > 0,
                "agents_available": len(self.langchain_manager.agents) > 0,
                "advanced_workflows": self.advanced_workflows.is_healthy() if self.advanced_workflows else False
            }
        else:
            return {
                "enabled": False,
                "healthy": False,
                "models_available": False,
                "chains_available": False,
                "agents_available": False,
                "advanced_workflows": False,
                "reason": "OpenRouter API key not provided"
            }
    
    def get_available_workflows(self) -> List[str]:
        """Get list of available advanced workflows."""
        if self.advanced_workflows:
            return list(self.advanced_workflows.templates.keys())
        return [] 