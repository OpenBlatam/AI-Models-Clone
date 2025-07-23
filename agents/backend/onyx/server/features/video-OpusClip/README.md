# Video-OpusClip

AI-driven video processing system for short-form video platforms, integrating advanced AI features like LangChain, FastAPI, PyTorch, and Diffusers.

## 🚀 Features

- **AI-Powered Video Processing**: Advanced video analysis and processing using PyTorch, Transformers, and Diffusers
- **Async Architecture**: High-performance async flows with event-driven design
- **FastAPI Integration**: Modern REST API with comprehensive documentation
- **Database Support**: Async database operations with PostgreSQL, MySQL, SQLite, and Redis
- **External API Integration**: YouTube, OpenAI, Stability AI, and ElevenLabs APIs
- **Performance Optimization**: Multi-GPU training, gradient accumulation, mixed precision
- **Monitoring & Logging**: Comprehensive metrics collection and structured logging
- **Error Handling**: Robust error handling with recovery mechanisms
- **User Interfaces**: Gradio-based user-friendly interfaces

## 📋 Requirements

- Python 3.8+
- PostgreSQL (recommended) or MySQL/SQLite
- GPU support (optional, for AI processing)
- External API keys (YouTube, OpenAI, Stability AI, ElevenLabs)

## 🛠 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd video-OpusClip
```

2. **Install dependencies**
```bash
pip install -r requirements_main.txt
```

3. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Setup database**
```bash
# For PostgreSQL
createdb video_opusclip
```

## 🚀 Quick Start

### Run the main application
```bash
python run_app.py
```

### Or run directly
```bash
python main.py
```

The application will be available at:
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

### Health Check
```http
GET /health
```

### Video Processing
```http
POST /videos
GET /videos/{video_id}
PATCH /videos/{video_id}
POST /videos/batch
```

### Metrics
```http
GET /metrics
```

## 🔧 Configuration

### Environment Variables

```env
# Application
APP_NAME=Video-OpusClip
APP_VERSION=1.0.0
DEBUG=False
HOST=0.0.0.0
PORT=8000
RELOAD=True

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/video_opusclip
DATABASE_TYPE=postgresql

# External APIs
YOUTUBE_API_KEY=your_youtube_api_key
OPENAI_API_KEY=your_openai_api_key
STABILITY_API_KEY=your_stability_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Async Flow
MAX_CONCURRENT_TASKS=100
MAX_CONCURRENT_CONNECTIONS=50
TIMEOUT=30.0
RETRY_ATTEMPTS=3
```

## 🏗 Architecture

### Core Components

1. **FastAPI Application** (`main.py`)
   - Main application entry point
   - Middleware configuration
   - Error handling
   - Dependency injection

2. **Async Flows** (`async_flows.py`)
   - Event-driven architecture
   - Priority task queues
   - Circuit breaker pattern
   - Workflow engine

3. **Database Operations** (`async_database.py`)
   - Connection pooling
   - Async CRUD operations
   - Transaction management
   - Caching

4. **External APIs** (`async_external_apis.py`)
   - Rate limiting
   - Retry logic
   - Response caching
   - Error handling

5. **Structured Routes** (`structured_routes.py`)
   - Route organization
   - Dependency injection
   - Route factories
   - Route registry

6. **FastAPI Best Practices** (`fastapi_best_practices.py`)
   - Pydantic v2 models
   - Path operations
   - Middleware
   - Error handling

### File Structure

```
video-OpusClip/
├── main.py                          # Main application
├── run_app.py                       # Application launcher
├── requirements_main.txt            # Dependencies
├── README.md                        # This file
├── .env                             # Environment variables
├── fastapi_best_practices.py        # FastAPI best practices
├── structured_routes.py             # Structured routing
├── async_flows.py                   # Async flow management
├── async_database.py                # Database operations
├── async_external_apis.py           # External API operations
├── *_examples.py                    # Example implementations
├── *_guide.md                       # Detailed guides
├── *_summary.md                     # Quick references
└── quick_start_*.py                 # Quick start scripts
```

## 🔍 Usage Examples

### Create a video processing job
```python
import requests

# Create video
response = requests.post("http://localhost:8000/videos", json={
    "title": "Amazing Sunset",
    "description": "Beautiful sunset timelapse",
    "url": "https://example.com/video.mp4",
    "duration": 120.5,
    "resolution": "1920x1080",
    "priority": "normal",
    "tags": ["nature", "sunset"]
})

video_id = response.json()["data"]["id"]
print(f"Created video: {video_id}")
```

### Get video status
```python
# Get video
response = requests.get(f"http://localhost:8000/videos/{video_id}")
video = response.json()["data"]
print(f"Video status: {video['status']}")
```

### Batch processing
```python
# Create multiple videos
response = requests.post("http://localhost:8000/videos/batch", json={
    "videos": [
        {
            "title": "Video 1",
            "description": "First video",
            "url": "https://example.com/video1.mp4",
            "duration": 60.0,
            "resolution": "1920x1080",
            "priority": "normal"
        },
        {
            "title": "Video 2", 
            "description": "Second video",
            "url": "https://example.com/video2.mp4",
            "duration": 90.0,
            "resolution": "1920x1080",
            "priority": "high"
        }
    ]
})

video_ids = response.json()["data"]["video_ids"]
print(f"Created {len(video_ids)} videos")
```

## 🧪 Testing

### Run tests
```bash
pytest tests/
```

### Run with coverage
```bash
pytest --cov=. tests/
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Metrics
```bash
curl http://localhost:8000/metrics
```

### Logs
```bash
tail -f video_opusclip.log
```

## 🔧 Development

### Code formatting
```bash
black .
isort .
```

### Linting
```bash
flake8 .
mypy .
```

### Type checking
```bash
mypy .
```

## 🚀 Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements_main.txt .
RUN pip install -r requirements_main.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Production
```bash
# Use production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📖 Documentation

- [FastAPI Best Practices Guide](FASTAPI_BEST_PRACTICES_GUIDE.md)
- [Async Flows Guide](ASYNC_FLOWS_GUIDE.md)
- [Database Operations Guide](ASYNC_DATABASE_AND_APIS_GUIDE.md)
- [Structured Routes Guide](STRUCTURED_ROUTES_GUIDE.md)
- [Performance Optimization Guide](PERFORMANCE_OPTIMIZATION_GUIDE.md)
- [PyTorch Integration Guide](PYTORCH_GUIDE.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the examples

## 🔄 Changelog

### v1.0.0
- Initial release
- FastAPI integration
- Async architecture
- Database operations
- External API integration
- Performance optimization
- Comprehensive documentation 