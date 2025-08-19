#!/usr/bin/env python3
"""
Enhanced HeyGen AI Demo Runner
==============================

Comprehensive demonstration of enhanced HeyGen AI capabilities:
- Real avatar generation with Stable Diffusion
- Advanced lip-sync with Wav2Lip
- High-quality TTS with multiple engines
- Professional video rendering pipeline
- Performance monitoring and optimization
- Error handling and recovery
"""

import asyncio
import os
import sys
import time
import argparse
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass

import torch
import numpy as np
from tqdm import tqdm
import structlog

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import enhanced HeyGen AI modules
try:
    from core.heygen_ai import HeyGenAI, VideoRequest, create_heygen_ai
    from core.avatar_manager import AvatarManager
    from core.voice_engine import VoiceEngine
    from core.video_renderer import VideoRenderer
    from core.script_generator import ScriptGenerator
except ImportError as e:
    print(f"Warning: Could not import enhanced modules: {e}")
    print("Some demos may not be available.")

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# =============================================================================
# Enhanced Demo Configuration
# =============================================================================

@dataclass
class EnhancedDemoConfig:
    """Configuration for enhanced HeyGen AI demos."""
    
    # Demo settings
    demo_type: str = "all"  # all, video_generation, avatar_creation, voice_synthesis, performance
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    num_runs: int = 3
    batch_size: int = 2
    
    # Model settings
    avatar_id: str = "professional_male_01"
    voice_id: str = "en_us_01"
    language: str = "en"
    
    # Quality settings
    quality_preset: str = "high"  # low, medium, high, ultra
    resolution: str = "1080p"  # 720p, 1080p, 4k
    
    # Performance settings
    enable_profiling: bool = True
    enable_caching: bool = True
    enable_monitoring: bool = True
    
    # Output settings
    output_dir: str = "./enhanced_demo_outputs"
    save_intermediates: bool = True
    cleanup_temp: bool = True

# =============================================================================
# Enhanced Demo Runner
# =============================================================================

class EnhancedHeyGenDemoRunner:
    """Enhanced demo runner for HeyGen AI system."""
    
    def __init__(self, config: EnhancedDemoConfig):
        """Initialize the demo runner."""
        self.config = config
        self.heygen_ai = None
        self.results = {}
        self.start_time = time.time()
        
        # Create output directory
        Path(self.config.output_dir).mkdir(exist_ok=True)
        
        logger.info("Enhanced HeyGen AI Demo Runner initialized")
        logger.info(f"Device: {self.config.device}")
        logger.info(f"Quality: {self.config.quality_preset}")
        logger.info(f"Resolution: {self.config.resolution}")
    
    async def initialize(self) -> bool:
        """Initialize the HeyGen AI system."""
        try:
            logger.info("Initializing HeyGen AI system...")
            
            # Create HeyGen AI instance
            self.heygen_ai = await create_heygen_ai()
            
            # Initialize components
            await self.heygen_ai.initialize()
            
            # Perform health check
            health_status = self.heygen_ai.health_check()
            logger.info(f"System health: {health_status}")
            
            if not all(health_status.values()):
                logger.warning("Some components are not healthy")
                return False
            
            logger.info("HeyGen AI system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize HeyGen AI: {e}")
            return False
    
    async def run_all_demos(self) -> Dict[str, Any]:
        """Run all available demos."""
        try:
            logger.info("Starting comprehensive demo suite...")
            
            # Health check demo
            await self.demo_health_check()
            
            # Avatar management demo
            await self.demo_avatar_management()
            
            # Voice engine demo
            await self.demo_voice_engine()
            
            # Full video generation demo
            await self.demo_video_generation()
            
            # Performance benchmarking
            await self.demo_performance_benchmark()
            
            # Quality assessment
            await self.demo_quality_assessment()
            
            # Error handling demo
            await self.demo_error_handling()
            
            # Resource monitoring
            await self.demo_resource_monitoring()
            
            # Generate final report
            await self.generate_demo_report()
            
            logger.info("All demos completed successfully")
            return self.results
            
        except Exception as e:
            logger.error(f"Demo suite failed: {e}")
            return self.results
    
    async def demo_health_check(self) -> None:
        """Demo system health check."""
        try:
            logger.info("Running health check demo...")
            
            # Check overall system health
            health_status = self.heygen_ai.health_check()
            
            # Check individual components
            avatar_health = self.heygen_ai.avatar_manager.health_check()
            voice_health = self.heygen_ai.voice_engine.health_check()
            
            # Store results
            self.results["health_check"] = {
                "overall_health": health_status,
                "avatar_manager_health": avatar_health,
                "voice_engine_health": voice_health,
                "timestamp": time.time()
            }
            
            logger.info("Health check demo completed")
            
        except Exception as e:
            logger.error(f"Health check demo failed: {e}")
            self.results["health_check"] = {"error": str(e)}
    
    async def demo_avatar_management(self) -> None:
        """Demo avatar management capabilities."""
        try:
            logger.info("Running avatar management demo...")
            
            # Get available avatars
            avatars = self.heygen_ai.avatar_manager.get_available_avatars()
            
            # Test avatar generation (placeholder)
            test_script = "Hello, this is a test of the avatar generation system."
            
            # Create a simple test audio file
            test_audio_path = Path(self.config.output_dir) / "test_audio.wav"
            self._create_test_audio(test_audio_path, test_script)
            
            # Generate avatar video
            avatar_video_path = await self.heygen_ai.avatar_manager.generate_avatar_video(
                request=type('obj', (object,), {
                    'avatar_id': self.config.avatar_id,
                    'audio_path': str(test_audio_path),
                    'quality': self.config.quality_preset,
                    'enable_lip_sync': True,
                    'enable_expressions': True
                })()
            )
            
            # Store results
            self.results["avatar_management"] = {
                "available_avatars": len(avatars),
                "avatar_ids": [a.id for a in avatars],
                "generated_video": avatar_video_path,
                "timestamp": time.time()
            }
            
            logger.info("Avatar management demo completed")
            
        except Exception as e:
            logger.error(f"Avatar management demo failed: {e}")
            self.results["avatar_management"] = {"error": str(e)}
    
    async def demo_voice_engine(self) -> None:
        """Demo voice engine capabilities."""
        try:
            logger.info("Running voice engine demo...")
            
            # Get available voices
            voices = self.heygen_ai.voice_engine.get_available_voices()
            
            # Test text-to-speech
            test_text = "Hello, this is a test of the enhanced voice engine."
            
            # Create voice generation request
            voice_request = type('obj', (object,), {
                'text': test_text,
                'voice_id': self.config.voice_id,
                'language': self.config.language,
                'quality': self.config.quality_preset,
                'emotion': 'neutral',
                'speed': 1.0,
                'pitch': 1.0,
                'volume': 1.0
            })()
            
            # Generate speech
            audio_path = await self.heygen_ai.voice_engine.synthesize_speech(voice_request)
            
            # Store results
            self.results["voice_engine"] = {
                "available_voices": len(voices),
                "voice_ids": [v.id for v in voices],
                "generated_audio": audio_path,
                "test_text": test_text,
                "timestamp": time.time()
            }
            
            logger.info("Voice engine demo completed")
            
        except Exception as e:
            logger.error(f"Voice engine demo failed: {e}")
            self.results["voice_engine"] = {"error": str(e)}
    
    async def demo_video_generation(self) -> None:
        """Demo full video generation pipeline."""
        try:
            logger.info("Running video generation demo...")
            
            # Create video request
            video_request = VideoRequest(
                script="Welcome to the enhanced HeyGen AI system. This is a demonstration of our advanced video generation capabilities.",
                avatar_id=self.config.avatar_id,
                voice_id=self.config.voice_id,
                language=self.config.language,
                resolution=self.config.resolution,
                quality_preset=self.config.quality_preset,
                enable_effects=True
            )
            
            # Generate video
            start_time = time.time()
            video_response = await self.heygen_ai.create_video(video_request)
            generation_time = time.time() - start_time
            
            # Store results
            self.results["video_generation"] = {
                "video_id": video_response.video_id,
                "status": video_response.status,
                "output_url": video_response.output_url,
                "generation_time": generation_time,
                "quality_metrics": video_response.quality_metrics,
                "timestamp": time.time()
            }
            
            logger.info("Video generation demo completed")
            
        except Exception as e:
            logger.error(f"Video generation demo failed: {e}")
            self.results["video_generation"] = {"error": str(e)}
    
    async def demo_performance_benchmark(self) -> None:
        """Demo performance benchmarking."""
        try:
            logger.info("Running performance benchmark demo...")
            
            # Get performance metrics
            avatar_metrics = self.heygen_ai.avatar_manager.get_performance_metrics()
            voice_metrics = self.heygen_ai.voice_engine.get_performance_metrics()
            overall_metrics = self.heygen_ai.get_performance_metrics()
            
            # Store results
            self.results["performance_benchmark"] = {
                "avatar_manager_metrics": avatar_metrics,
                "voice_engine_metrics": voice_metrics,
                "overall_metrics": overall_metrics,
                "timestamp": time.time()
            }
            
            logger.info("Performance benchmark demo completed")
            
        except Exception as e:
            logger.error(f"Performance benchmark demo failed: {e}")
            self.results["performance_benchmark"] = {"error": str(e)}
    
    async def demo_quality_assessment(self) -> None:
        """Demo quality assessment capabilities."""
        try:
            logger.info("Running quality assessment demo...")
            
            # Test different quality presets
            quality_presets = ["low", "medium", "high", "ultra"]
            quality_results = {}
            
            for quality in quality_presets:
                try:
                    # Create test request
                    test_request = VideoRequest(
                        script="Quality test for " + quality + " preset.",
                        avatar_id=self.config.avatar_id,
                        voice_id=self.config.voice_id,
                        language=self.config.language,
                        quality_preset=quality,
                        enable_effects=False
                    )
                    
                    # Generate video
                    start_time = time.time()
                    response = await self.heygen_ai.create_video(test_request)
                    generation_time = time.time() - start_time
                    
                    quality_results[quality] = {
                        "status": response.status,
                        "generation_time": generation_time,
                        "quality_score": response.quality_metrics.get("overall_score", 0) if response.quality_metrics else 0
                    }
                    
                except Exception as e:
                    quality_results[quality] = {"error": str(e)}
            
            # Store results
            self.results["quality_assessment"] = {
                "quality_results": quality_results,
                "timestamp": time.time()
            }
            
            logger.info("Quality assessment demo completed")
            
        except Exception as e:
            logger.error(f"Quality assessment demo failed: {e}")
            self.results["quality_assessment"] = {"error": str(e)}
    
    async def demo_error_handling(self) -> None:
        """Demo error handling capabilities."""
        try:
            logger.info("Running error handling demo...")
            
            error_tests = []
            
            # Test invalid avatar ID
            try:
                invalid_request = VideoRequest(
                    script="Test error handling",
                    avatar_id="invalid_avatar_id",
                    voice_id=self.config.voice_id,
                    language=self.config.language
                )
                await self.heygen_ai.create_video(invalid_request)
                error_tests.append({"test": "invalid_avatar", "result": "unexpected_success"})
            except Exception as e:
                error_tests.append({"test": "invalid_avatar", "result": "handled", "error": str(e)})
            
            # Test invalid voice ID
            try:
                invalid_request = VideoRequest(
                    script="Test error handling",
                    avatar_id=self.config.avatar_id,
                    voice_id="invalid_voice_id",
                    language=self.config.language
                )
                await self.heygen_ai.create_video(invalid_request)
                error_tests.append({"test": "invalid_voice", "result": "unexpected_success"})
            except Exception as e:
                error_tests.append({"test": "invalid_voice", "result": "handled", "error": str(e)})
            
            # Store results
            self.results["error_handling"] = {
                "error_tests": error_tests,
                "timestamp": time.time()
            }
            
            logger.info("Error handling demo completed")
            
        except Exception as e:
            logger.error(f"Error handling demo failed: {e}")
            self.results["error_handling"] = {"error": str(e)}
    
    async def demo_resource_monitoring(self) -> None:
        """Demo resource monitoring capabilities."""
        try:
            logger.info("Running resource monitoring demo...")
            
            # Get system resources
            import psutil
            
            system_info = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "gpu_available": torch.cuda.is_available(),
                "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
            }
            
            if torch.cuda.is_available():
                system_info["gpu_memory"] = {
                    f"gpu_{i}": torch.cuda.get_device_properties(i).total_memory / 1024**3
                    for i in range(torch.cuda.device_count())
                }
            
            # Store results
            self.results["resource_monitoring"] = {
                "system_info": system_info,
                "timestamp": time.time()
            }
            
            logger.info("Resource monitoring demo completed")
            
        except Exception as e:
            logger.error(f"Resource monitoring demo failed: {e}")
            self.results["resource_monitoring"] = {"error": str(e)}
    
    async def generate_demo_report(self) -> None:
        """Generate comprehensive demo report."""
        try:
            logger.info("Generating demo report...")
            
            # Calculate overall statistics
            total_demos = len(self.results)
            successful_demos = sum(1 for r in self.results.values() if "error" not in r)
            failed_demos = total_demos - successful_demos
            
            # Calculate total time
            total_time = time.time() - self.start_time
            
            # Create summary
            summary = {
                "total_demos": total_demos,
                "successful_demos": successful_demos,
                "failed_demos": failed_demos,
                "success_rate": successful_demos / total_demos if total_demos > 0 else 0,
                "total_time": total_time,
                "timestamp": time.time()
            }
            
            # Add summary to results
            self.results["summary"] = summary
            
            # Save report to file
            report_path = Path(self.config.output_dir) / "demo_report.json"
            import json
            with open(report_path, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            logger.info(f"Demo report saved to: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate demo report: {e}")
    
    def _create_test_audio(self, audio_path: Path, text: str) -> None:
        """Create a simple test audio file."""
        try:
            import numpy as np
            import soundfile as sf
            
            # Create simple sine wave audio
            sample_rate = 22050
            duration = len(text.split()) * 0.5  # Rough estimate
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio = np.sin(2 * np.pi * 440 * t) * 0.3  # 440 Hz tone
            
            # Save audio
            sf.write(str(audio_path), audio, sample_rate)
            logger.info(f"Created test audio: {audio_path}")
            
        except Exception as e:
            logger.warning(f"Failed to create test audio: {e}")
    
    async def cleanup(self) -> None:
        """Clean up demo resources."""
        try:
            logger.info("Cleaning up demo resources...")
            
            if self.heygen_ai:
                await self.heygen_ai.cleanup()
            
            if self.config.cleanup_temp:
                # Clean up temporary files
                temp_files = Path(self.config.output_dir).glob("*.wav")
                for temp_file in temp_files:
                    try:
                        temp_file.unlink()
                    except Exception:
                        pass
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")

# =============================================================================
# Main Execution
# =============================================================================

async def main():
    """Main demo execution function."""
    parser = argparse.ArgumentParser(description="Enhanced HeyGen AI Demo Runner")
    parser.add_argument("--demo-type", default="all", choices=["all", "health", "avatar", "voice", "video", "performance", "quality", "error", "resources"])
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high", "ultra"])
    parser.add_argument("--resolution", default="1080p", choices=["720p", "1080p", "4k"])
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--output-dir", default="./enhanced_demo_outputs")
    parser.add_argument("--no-cleanup", action="store_true", help="Skip cleanup of temporary files")
    
    args = parser.parse_args()
    
    # Configure demo
    device = args.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    config = EnhancedDemoConfig(
        demo_type=args.demo_type,
        device=device,
        quality_preset=args.quality,
        resolution=args.resolution,
        output_dir=args.output_dir,
        cleanup_temp=not args.no_cleanup
    )
    
    # Create and run demo
    runner = EnhancedHeyGenDemoRunner(config)
    
    try:
        # Initialize
        if not await runner.initialize():
            logger.error("Failed to initialize HeyGen AI system")
            return 1
        
        # Run demos
        if args.demo_type == "all":
            await runner.run_all_demos()
        else:
            # Run specific demo
            demo_method = getattr(runner, f"demo_{args.demo_type}")
            await demo_method()
        
        # Generate report
        await runner.generate_demo_report()
        
        logger.info("Demo execution completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Demo execution failed: {e}")
        return 1
        
    finally:
        # Cleanup
        await runner.cleanup()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
