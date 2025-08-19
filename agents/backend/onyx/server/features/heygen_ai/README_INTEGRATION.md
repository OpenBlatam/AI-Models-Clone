# Enhanced HeyGen AI - Complete Integration Guide

## 🚀 Overview

This is the **complete integration** of the Enhanced HeyGen AI system, featuring:

- **Real AI Models**: Stable Diffusion, Coqui TTS, Wav2Lip integration
- **Full Video Pipeline**: From script to final video with all processing steps
- **Production-Ready API**: FastAPI with comprehensive endpoints
- **Performance Monitoring**: Real-time metrics and health checks
- **Easy Deployment**: Automated setup and configuration

## 🏗️ Architecture

```
Enhanced HeyGen AI System
├── Core Components
│   ├── HeyGenAI (Main Orchestrator)
│   ├── VoiceEngine (TTS & Voice Cloning)
│   ├── AvatarManager (Avatar Generation & Lip-sync)
│   ├── VideoRenderer (Final Video Composition)
│   └── ScriptGenerator (AI Script Generation)
├── API Layer
│   ├── FastAPI Application
│   ├── Enhanced Routes
│   ├── Request/Response Models
│   └── Error Handling
├── Configuration
│   ├── Environment Settings
│   ├── Model Configuration
│   └── Quality Presets
└── Utilities
    ├── Demo Runner
    ├── Server Runner
    └── Health Monitoring
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- FFmpeg installed
- GPU recommended (CUDA compatible)
- OpenRouter API key

### 2. Automated Setup

```bash
# Navigate to the project directory
cd agents/backend/onyx/server/features/heygen_ai

# Run the automated setup and server
python run_enhanced_server.py
```

This script will:
- ✅ Check system requirements
- ✅ Create environment configuration
- ✅ Install dependencies
- ✅ Start the server

### 3. Manual Setup

```bash
# Install dependencies
pip install -r requirements-enhanced.txt

# Create environment file
cp .env.example .env
# Edit .env with your OpenRouter API key

# Start server
python main_enhanced.py
```

## 🌐 API Endpoints

### Core Video Generation

#### Create Video
```http
POST /api/v1/videos/create
Content-Type: application/json

{
  "script": "Welcome to our enhanced AI video system!",
  "avatar_id": "avatar_001",
  "voice_id": "voice_001",
  "language": "en",
  "resolution": "1080p",
  "quality_preset": "high",
  "enable_expressions": true,
  "enable_effects": false
}
```

#### Batch Video Creation
```http
POST /api/v1/videos/batch
Content-Type: application/json

[
  {
    "script": "First video script",
    "avatar_id": "avatar_001",
    "voice_id": "voice_001"
  },
  {
    "script": "Second video script",
    "avatar_id": "avatar_002",
    "voice_id": "voice_002"
  }
]
```

### Voice Generation

#### Generate Speech
```http
POST /api/v1/voice/generate
Content-Type: application/json

{
  "text": "This is a test of the voice synthesis system.",
  "voice_id": "voice_001",
  "language": "en",
  "quality": "high",
  "speed": 1.0,
  "pitch": 1.0
}
```

#### Get Available Voices
```http
GET /api/v1/voice/available
```

### Avatar Generation

#### Generate Avatar Video
```http
POST /api/v1/avatar/generate
Content-Type: application/json

{
  "avatar_id": "avatar_001",
  "audio_path": "/path/to/audio.wav",
  "resolution": "1080p",
  "quality_preset": "high",
  "enable_expressions": true
}
```

#### Get Available Avatars
```http
GET /api/v1/avatar/available
```

### System Status

#### Health Check
```http
GET /api/v1/health
```

#### System Status
```http
GET /api/v1/status
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Environment
HEYGEN_ENV=development
HEYGEN_DEBUG=true

# API Settings
HEYGEN_API_HOST=0.0.0.0
HEYGEN_API_PORT=8000
HEYGEN_API_WORKERS=1

# AI Models
OPENROUTER_API_KEY=your_key_here
HEYGEN_GPU_ENABLED=true
HEYGEN_MODEL_CACHE_DIR=./models

# Video Settings
HEYGEN_DEFAULT_RESOLUTION=1080p
HEYGEN_DEFAULT_FORMAT=mp4
HEYGEN_MAX_VIDEO_DURATION=600

# Audio Settings
HEYGEN_DEFAULT_SAMPLE_RATE=22050
HEYGEN_AUDIO_QUALITY=high

# Storage
HEYGEN_STORAGE_TYPE=local
HEYGEN_TEMP_DIR=./temp
```

### Quality Presets

The system supports multiple quality presets:

- **Low**: 720p, 1000k bitrate, 24fps
- **Medium**: 1080p, 2000k bitrate, 30fps
- **High**: 1080p, 4000k bitrate, 30fps
- **Ultra**: 4K, 8000k bitrate, 30fps

## 🧪 Testing & Demo

### Run Demo Suite

```bash
python run_enhanced_demo.py
```

This will test:
- ✅ Health checks
- ✅ Voice generation
- ✅ Avatar generation
- ✅ Full video pipeline
- ✅ Performance metrics
- ✅ Error handling

### Test Individual Components

```bash
# Test voice engine
python -c "
from core.voice_engine import VoiceEngine
engine = VoiceEngine()
print(engine.health_check())
"

# Test avatar manager
python -c "
from core.avatar_manager import AvatarManager
manager = AvatarManager()
print(manager.health_check())
"
```

## 📊 Monitoring & Health

### Health Check Response

```json
{
  "status": "healthy",
  "components": {
    "core": true,
    "voice_engine": true,
    "avatar_manager": true,
    "video_renderer": true,
    "script_generator": true
  },
  "version": "2.0.0",
  "metadata": {
    "enhanced_core": true,
    "voice_engines": ["coqui_tts", "your_tts"],
    "avatar_models": ["stable_diffusion_v1_5", "stable_diffusion_xl"]
  }
}
```

### Performance Metrics

```json
{
  "status": "operational",
  "components": {
    "voice_engine": {
      "request_count": 150,
      "success_rate": 0.98,
      "avg_processing_time": 2.3
    },
    "avatar_manager": {
      "request_count": 75,
      "success_rate": 0.95,
      "avg_processing_time": 15.7
    }
  }
}
```

## 🚀 Deployment

### Development

```bash
python run_enhanced_server.py
```

### Production

```bash
# Set environment
export HEYGEN_ENV=production
export HEYGEN_DEBUG=false

# Start with multiple workers
uvicorn main_enhanced:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Coming Soon)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements-enhanced.txt .
RUN pip install -r requirements-enhanced.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main_enhanced:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔍 Troubleshooting

### Common Issues

#### 1. GPU Not Available
```bash
# Check CUDA installation
nvidia-smi

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 2. FFmpeg Not Found
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

#### 3. Model Download Issues
```bash
# Clear model cache
rm -rf ./models/*

# Set Hugging Face token
export HUGGINGFACE_TOKEN=your_token_here
```

#### 4. Memory Issues
```bash
# Reduce batch size
export HEYGEN_MAX_BATCH_SIZE=1

# Use CPU only
export HEYGEN_GPU_ENABLED=false
```

### Logs

Check logs for detailed error information:

```bash
# View real-time logs
tail -f logs/heygen_ai.log

# Check specific component logs
grep "voice_engine" logs/heygen_ai.log
grep "avatar_manager" logs/heygen_ai.log
```

## 📈 Performance Optimization

### GPU Optimization

- Use CUDA-enabled PyTorch
- Enable attention slicing for large models
- Use mixed precision training
- Monitor GPU memory usage

### Memory Management

- Adjust batch sizes based on available RAM
- Use model caching
- Implement streaming for large videos
- Monitor memory usage with `psutil`

### Caching Strategy

- Audio cache for TTS results
- Avatar cache for generated images
- Model cache for AI models
- Response cache for API calls

## 🔐 Security

### API Key Management

- Store API keys in environment variables
- Use secure key rotation
- Implement rate limiting
- Monitor API usage

### Input Validation

- Validate all user inputs
- Sanitize file uploads
- Implement request size limits
- Use HTTPS in production

## 🌟 What's New in v2.0

### Enhanced Core
- ✅ Real Stable Diffusion integration
- ✅ Coqui TTS with voice cloning
- ✅ Wav2Lip lip-sync
- ✅ Performance monitoring
- ✅ Comprehensive error handling

### API Improvements
- ✅ RESTful endpoints
- ✅ Request/response validation
- ✅ Health checks
- ✅ Performance metrics
- ✅ Debug endpoints

### Developer Experience
- ✅ Automated setup
- ✅ Comprehensive documentation
- ✅ Demo suite
- ✅ Easy configuration
- ✅ Production deployment

## 🚀 Next Steps

1. **Test the System**: Run the demo suite
2. **Configure API Keys**: Set up OpenRouter access
3. **Customize Settings**: Adjust quality and performance
4. **Deploy**: Move to production environment
5. **Monitor**: Set up logging and metrics
6. **Scale**: Add load balancing and caching

## 📞 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Review troubleshooting section
- **Demo**: Run `python run_enhanced_demo.py`
- **Health**: Check `/api/v1/health` endpoint

---

**🎉 Congratulations!** You now have a fully functional, production-ready HeyGen AI equivalent system that integrates real AI models, provides a comprehensive API, and includes all the tools needed for deployment and monitoring.

**Ready to create amazing AI-generated videos! 🎬✨**
