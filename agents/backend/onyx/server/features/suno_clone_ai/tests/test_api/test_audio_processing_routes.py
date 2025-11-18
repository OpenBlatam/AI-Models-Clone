"""
Tests modulares para endpoints de procesamiento de audio
"""

import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path

from tests.helpers.test_helpers import create_song_dict, generate_test_song_id, create_mock_audio, save_test_audio
from tests.helpers.mock_helpers import create_mock_song_service, create_mock_audio_processor
from tests.helpers.assertion_helpers import assert_song_response_valid
from tests.helpers.advanced_helpers import ResponseValidator, MockVerifier


class TestEditSong:
    """Tests para edit_song endpoint"""
    
    @pytest.fixture
    def endpoint_path(self):
        return "/suno/songs/{song_id}/edit"
    
    @pytest.mark.asyncio
    @pytest.mark.happy_path
    async def test_edit_song_success(
        self,
        test_client,
        endpoint_path,
        mock_song_service,
        mock_audio_processor,
        temp_audio_dir
    ):
        """Test exitoso de edición de canción"""
        song_id = generate_test_song_id()
        audio_file = temp_audio_dir / f"{song_id}.wav"
        audio = create_mock_audio()
        save_test_audio(audio, audio_file)
        
        song = create_song_dict(song_id=song_id, file_path=str(audio_file))
        mock_song_service.get_song.return_value = song
        
        edit_request = {
            "operations": [
                {"type": "reverb", "room_size": 0.5, "damping": 0.5},
                {"type": "eq", "low_gain": 1.0, "mid_gain": 0.5, "high_gain": 0.0}
            ],
            "normalize": True,
            "trim_silence": False,
            "fade_in": 0.5,
            "fade_out": 0.5
        }
        
        with patch('api.routes.audio_processing.validate_song_id'), \
             patch('api.routes.audio_processing.get_song_async_or_sync') as mock_get, \
             patch('api.routes.audio_processing.ensure_song_exists') as mock_ensure, \
             patch('api.routes.audio_processing.load_audio_file') as mock_load, \
             patch('api.routes.audio_processing.apply_audio_operations') as mock_apply, \
             patch('api.routes.audio_processing.save_audio_file') as mock_save, \
             patch('api.routes.audio_processing.get_audio_file_path') as mock_path:
            
            mock_get.return_value = song
            mock_ensure.return_value = song
            mock_load.return_value = (audio, 44100)
            mock_apply.return_value = audio
            mock_path.return_value = temp_audio_dir / "new.wav"
            
            response = test_client.post(
                endpoint_path.format(song_id=song_id),
                json=edit_request
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert_song_response_valid(data)
            assert data["status"] == "completed"
    
    @pytest.mark.asyncio
    @pytest.mark.error_handling
    async def test_edit_song_not_found(
        self,
        test_client,
        endpoint_path,
        mock_song_service
    ):
        """Test cuando la canción no existe"""
        song_id = generate_test_song_id()
        mock_song_service.get_song.return_value = None
        
        with patch('api.routes.audio_processing.validate_song_id'), \
             patch('api.routes.audio_processing.get_song_async_or_sync') as mock_get, \
             patch('api.routes.audio_processing.ensure_song_exists') as mock_ensure:
            mock_get.return_value = None
            from api.routes.audio_processing import SongNotFoundError
            mock_ensure.side_effect = SongNotFoundError(song_id)
            
            edit_request = {"operations": []}
            response = test_client.post(
                endpoint_path.format(song_id=song_id),
                json=edit_request
            )
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    @pytest.mark.error_handling
    async def test_edit_song_no_file_path(
        self,
        test_client,
        endpoint_path,
        mock_song_service
    ):
        """Test cuando la canción no tiene file_path"""
        song_id = generate_test_song_id()
        song = create_song_dict(song_id=song_id, file_path="")
        mock_song_service.get_song.return_value = song
        
        with patch('api.routes.audio_processing.validate_song_id'), \
             patch('api.routes.audio_processing.get_song_async_or_sync') as mock_get, \
             patch('api.routes.audio_processing.ensure_song_exists') as mock_ensure:
            mock_get.return_value = song
            mock_ensure.return_value = song
            
            edit_request = {"operations": []}
            response = test_client.post(
                endpoint_path.format(song_id=song_id),
                json=edit_request
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.asyncio
    @pytest.mark.edge_case
    async def test_edit_song_multiple_operations(
        self,
        test_client,
        endpoint_path,
        mock_song_service,
        temp_audio_dir
    ):
        """Test con múltiples operaciones"""
        song_id = generate_test_song_id()
        audio_file = temp_audio_dir / f"{song_id}.wav"
        audio = create_mock_audio()
        save_test_audio(audio, audio_file)
        
        song = create_song_dict(song_id=song_id, file_path=str(audio_file))
        
        edit_request = {
            "operations": [
                {"type": "reverb", "room_size": 0.5},
                {"type": "eq", "low_gain": 1.0},
                {"type": "tempo", "factor": 1.2},
                {"type": "pitch", "semitones": 2.0}
            ],
            "normalize": True,
            "trim_silence": True
        }
        
        with patch('api.routes.audio_processing.validate_song_id'), \
             patch('api.routes.audio_processing.get_song_async_or_sync') as mock_get, \
             patch('api.routes.audio_processing.ensure_song_exists') as mock_ensure, \
             patch('api.routes.audio_processing.load_audio_file') as mock_load, \
             patch('api.routes.audio_processing.apply_audio_operations') as mock_apply, \
             patch('api.routes.audio_processing.save_audio_file') as mock_save, \
             patch('api.routes.audio_processing.get_audio_file_path') as mock_path:
            
            mock_get.return_value = song
            mock_ensure.return_value = song
            mock_load.return_value = (audio, 44100)
            mock_apply.return_value = audio
            mock_path.return_value = temp_audio_dir / "new.wav"
            
            response = test_client.post(
                endpoint_path.format(song_id=song_id),
                json=edit_request
            )
            
            assert response.status_code == status.HTTP_200_OK
            # Verificar que se aplicaron las operaciones
            mock_apply.assert_called_once()


class TestMixSongs:
    """Tests para mix_songs endpoint"""
    
    @pytest.fixture
    def endpoint_path(self):
        return "/suno/songs/mix"
    
    @pytest.mark.asyncio
    @pytest.mark.happy_path
    async def test_mix_songs_success(
        self,
        test_client,
        endpoint_path,
        mock_song_service,
        mock_audio_processor,
        temp_audio_dir
    ):
        """Test exitoso de mezcla de canciones"""
        song_ids = [generate_test_song_id() for _ in range(3)]
        songs = []
        
        for i, song_id in enumerate(song_ids):
            audio_file = temp_audio_dir / f"{song_id}.wav"
            audio = create_mock_audio(frequency=440.0 * (i + 1))
            save_test_audio(audio, audio_file)
            songs.append(create_song_dict(song_id=song_id, file_path=str(audio_file)))
        
        mock_song_service.get_song.side_effect = lambda sid: next(
            (s for s in songs if s["song_id"] == sid), None
        )
        
        mix_request = {
            "song_ids": song_ids,
            "volumes": [1.0, 0.8, 0.6]
        }
        
        with patch('api.routes.audio_processing.load_audio_file') as mock_load, \
             patch('api.routes.audio_processing.save_audio_file') as mock_save, \
             patch('api.routes.audio_processing.get_audio_file_path') as mock_path, \
             patch('api.routes.audio_processing.get_song_async_or_sync') as mock_get:
            
            audio = create_mock_audio()
            mock_load.return_value = (audio, 44100)
            mock_path.return_value = temp_audio_dir / "mixed.wav"
            mock_get.return_value = songs
            
            response = test_client.post(endpoint_path, json=mix_request)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert_song_response_valid(data)
            assert data["status"] == "completed"
    
    @pytest.mark.asyncio
    @pytest.mark.error_handling
    async def test_mix_songs_no_valid_songs(
        self,
        test_client,
        endpoint_path,
        mock_song_service
    ):
        """Test cuando no hay canciones válidas"""
        song_ids = [generate_test_song_id() for _ in range(3)]
        mock_song_service.get_song.return_value = None
        
        mix_request = {
            "song_ids": song_ids
        }
        
        with patch('api.routes.audio_processing.get_song_async_or_sync') as mock_get:
            mock_get.return_value = []
            
            response = test_client.post(endpoint_path, json=mix_request)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.asyncio
    @pytest.mark.edge_case
    async def test_mix_songs_without_volumes(
        self,
        test_client,
        endpoint_path,
        mock_song_service,
        temp_audio_dir
    ):
        """Test mezclando sin especificar volúmenes"""
        song_ids = [generate_test_song_id() for _ in range(2)]
        songs = []
        
        for song_id in song_ids:
            audio_file = temp_audio_dir / f"{song_id}.wav"
            audio = create_mock_audio()
            save_test_audio(audio, audio_file)
            songs.append(create_song_dict(song_id=song_id, file_path=str(audio_file)))
        
        mock_song_service.get_song.side_effect = lambda sid: next(
            (s for s in songs if s["song_id"] == sid), None
        )
        
        mix_request = {
            "song_ids": song_ids
            # Sin volumes
        }
        
        with patch('api.routes.audio_processing.load_audio_file') as mock_load, \
             patch('api.routes.audio_processing.save_audio_file') as mock_save, \
             patch('api.routes.audio_processing.get_audio_file_path') as mock_path, \
             patch('api.routes.audio_processing.get_song_async_or_sync') as mock_get:
            
            audio = create_mock_audio()
            mock_load.return_value = (audio, 44100)
            mock_path.return_value = temp_audio_dir / "mixed.wav"
            mock_get.return_value = songs
            
            response = test_client.post(endpoint_path, json=mix_request)
            
            assert response.status_code == status.HTTP_200_OK


class TestAnalyzeSong:
    """Tests para analyze_song endpoint"""
    
    @pytest.fixture
    def endpoint_path(self):
        return "/suno/songs/{song_id}/analyze"
    
    @pytest.mark.asyncio
    @pytest.mark.happy_path
    async def test_analyze_song_success(
        self,
        test_client,
        endpoint_path,
        mock_song_service,
        mock_audio_processor,
        temp_audio_dir
    ):
        """Test exitoso de análisis de canción"""
        song_id = generate_test_song_id()
        audio_file = temp_audio_dir / f"{song_id}.wav"
        audio = create_mock_audio()
        save_test_audio(audio, audio_file)
        
        song = create_song_dict(song_id=song_id, file_path=str(audio_file))
        mock_song_service.get_song.return_value = song
        
        analysis_result = {
            "duration": 30.0,
            "sample_rate": 44100,
            "channels": 2,
            "rms": 0.5,
            "peak": 1.0,
            "frequency_analysis": {}
        }
        mock_audio_processor.analyze_audio.return_value = analysis_result
        
        with patch('api.routes.audio_processing.validate_song_id'), \
             patch('api.routes.audio_processing.get_song_async_or_sync') as mock_get, \
             patch('api.routes.audio_processing.ensure_song_exists') as mock_ensure, \
             patch('api.routes.audio_processing.load_audio_file') as mock_load:
            
            mock_get.return_value = song
            mock_ensure.return_value = song
            mock_load.return_value = (audio, 44100)
            
            response = test_client.get(endpoint_path.format(song_id=song_id))
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "song_id" in data
            assert "analysis" in data
            assert data["analysis"]["duration"] == 30.0
    
    @pytest.mark.asyncio
    @pytest.mark.error_handling
    async def test_analyze_song_not_found(
        self,
        test_client,
        endpoint_path,
        mock_song_service
    ):
        """Test cuando la canción no existe"""
        song_id = generate_test_song_id()
        mock_song_service.get_song.return_value = None
        
        with patch('api.routes.audio_processing.validate_song_id'), \
             patch('api.routes.audio_processing.get_song_async_or_sync') as mock_get, \
             patch('api.routes.audio_processing.ensure_song_exists') as mock_ensure:
            mock_get.return_value = None
            from api.routes.audio_processing import SongNotFoundError
            mock_ensure.side_effect = SongNotFoundError(song_id)
            
            response = test_client.get(endpoint_path.format(song_id=song_id))
            
            assert response.status_code == status.HTTP_404_NOT_FOUND

