"""
Configuración compartida de pytest y fixtures base
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock, patch
import numpy as np

# Importar módulos del proyecto
import sys
from pathlib import Path as PathLib

# Agregar el directorio raíz al path
project_root = PathLib(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from api.schemas import (
        ChatMessage,
        SongGenerationRequest,
        AudioEditRequest,
        AudioMixRequest
    )
    from services.song_service import SongService
    from core.music_generator import get_music_generator
    from core.chat_processor import get_chat_processor
    from core.cache_manager import get_cache_manager
    from core.audio_processor import get_audio_processor
    from services.metrics_service import get_metrics_service
    from services.notification_service import get_notification_service
except ImportError:
    # Intentar imports relativos
    pass


# ============================================================================
# Fixtures de Directorios Temporales
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Crea un directorio temporal para tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_audio_dir(temp_dir: Path) -> Path:
    """Crea un directorio temporal para archivos de audio"""
    audio_dir = temp_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    return audio_dir


# ============================================================================
# Fixtures de Mocks de Servicios
# ============================================================================

@pytest.fixture
def mock_song_service() -> Mock:
    """Mock del servicio de canciones"""
    service = Mock(spec=SongService)
    service.list_songs = Mock(return_value=[])
    service.get_song = Mock(return_value=None)
    service.save_song = Mock(return_value=True)
    service.delete_song = Mock(return_value=True)
    service.update_song_status = Mock(return_value=True)
    service.get_chat_history = Mock(return_value=[])
    return service


@pytest.fixture
def mock_music_generator() -> Mock:
    """Mock del generador de música"""
    generator = Mock()
    generator.generate_from_text = Mock(return_value=np.array([0.1, 0.2, 0.3]))
    generator.save_audio = Mock(return_value=True)
    return generator


@pytest.fixture
def mock_chat_processor() -> Mock:
    """Mock del procesador de chat"""
    processor = Mock()
    processor.extract_song_info = Mock(return_value={
        "prompt": "test song",
        "genre": "pop",
        "mood": "happy",
        "duration": 30
    })
    return processor


@pytest.fixture
def mock_cache_manager() -> Mock:
    """Mock del gestor de caché"""
    manager = Mock()
    manager.get = Mock(return_value=None)
    manager.set = Mock(return_value=True)
    manager.clear = Mock(return_value=True)
    manager.stats = Mock(return_value={"hits": 0, "misses": 0, "size": 0})
    return manager


@pytest.fixture
def mock_audio_processor() -> Mock:
    """Mock del procesador de audio"""
    processor = Mock()
    processor.normalize = Mock(side_effect=lambda x: x)
    processor.apply_fade = Mock(side_effect=lambda x, **kwargs: x)
    processor.trim_silence = Mock(side_effect=lambda x: x)
    processor.apply_reverb = Mock(side_effect=lambda x, **kwargs: x)
    processor.apply_eq = Mock(side_effect=lambda x, **kwargs: x)
    processor.change_tempo = Mock(side_effect=lambda x, **kwargs: x)
    processor.change_pitch = Mock(side_effect=lambda x, **kwargs: x)
    processor.mix_audio = Mock(return_value=np.array([0.1, 0.2, 0.3]))
    processor.analyze_audio = Mock(return_value={
        "duration": 30.0,
        "sample_rate": 44100,
        "channels": 2
    })
    return processor


@pytest.fixture
def mock_metrics_service() -> Mock:
    """Mock del servicio de métricas"""
    service = Mock()
    service.record_generation = Mock(return_value=True)
    service.get_stats = Mock(return_value={
        "total_songs": 0,
        "total_users": 0,
        "avg_generation_time": 0.0
    })
    service.get_user_stats = Mock(return_value={
        "user_id": "test_user",
        "songs_generated": 0,
        "avg_generation_time": 0.0
    })
    return service


@pytest.fixture
def mock_notification_service() -> AsyncMock:
    """Mock del servicio de notificaciones"""
    service = AsyncMock()
    service.notify_generation_started = AsyncMock(return_value=True)
    service.notify_song_completed = AsyncMock(return_value=True)
    service.notify_song_failed = AsyncMock(return_value=True)
    return service


# ============================================================================
# Fixtures de Datos de Prueba
# ============================================================================

@pytest.fixture
def sample_audio_data() -> np.ndarray:
    """Genera datos de audio de prueba"""
    sample_rate = 44100
    duration = 1.0  # 1 segundo
    frequency = 440.0  # A4
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * frequency * t)
    return audio.astype(np.float32)


@pytest.fixture
def sample_song_data() -> Dict[str, Any]:
    """Datos de ejemplo de una canción"""
    return {
        "song_id": "test-song-123",
        "user_id": "test-user-456",
        "prompt": "A happy pop song",
        "genre": "pop",
        "mood": "happy",
        "duration": 30,
        "status": "completed",
        "file_path": "/tmp/test-song.wav",
        "metadata": {
            "model_used": "facebook/musicgen-medium",
            "generation_time": 5.2
        }
    }


@pytest.fixture
def sample_chat_message() -> Dict[str, Any]:
    """Mensaje de chat de ejemplo"""
    return {
        "message": "Create a happy pop song",
        "user_id": "test-user-456",
        "chat_history": []
    }


@pytest.fixture
def sample_song_generation_request() -> Dict[str, Any]:
    """Request de generación de ejemplo"""
    return {
        "prompt": "A happy pop song",
        "duration": 30,
        "genre": "pop",
        "mood": "happy",
        "user_id": "test-user-456"
    }


# ============================================================================
# Fixtures de Configuración
# ============================================================================

@pytest.fixture
def mock_settings(monkeypatch):
    """Mock de configuración"""
    mock_config = {
        "audio_storage_path": "/tmp/test_audio",
        "sample_rate": 44100,
        "default_duration": 30,
        "max_audio_length": 300,
        "music_model": "facebook/musicgen-medium"
    }
    
    for key, value in mock_config.items():
        monkeypatch.setattr(f"config.settings.{key}", value, raising=False)
    
    return mock_config


# ============================================================================
# Fixtures de FastAPI
# ============================================================================

@pytest.fixture
def test_client():
    """Cliente de prueba para FastAPI"""
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


# ============================================================================
# Helpers de Utilidad
# ============================================================================

def create_test_audio_file(file_path: Path, duration: float = 1.0, sample_rate: int = 44100) -> Path:
    """Crea un archivo de audio de prueba"""
    import soundfile as sf
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440.0 * t).astype(np.float32)
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(file_path), audio, sample_rate)
    
    return file_path


def assert_audio_file_valid(file_path: Path) -> None:
    """Verifica que un archivo de audio sea válido"""
    import soundfile as sf
    
    assert file_path.exists(), f"Audio file not found: {file_path}"
    data, sr = sf.read(str(file_path))
    assert len(data) > 0, "Audio file is empty"
    assert sr > 0, "Invalid sample rate"

