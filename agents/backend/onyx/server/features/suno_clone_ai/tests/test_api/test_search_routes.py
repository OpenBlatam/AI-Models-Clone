"""
Tests modulares para endpoints de búsqueda
"""

import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock

from tests.helpers.test_helpers import create_song_dict, generate_test_song_id
from tests.helpers.mock_helpers import create_mock_song_service
from tests.helpers.assertion_helpers import assert_song_list_valid
from tests.helpers.advanced_helpers import ResponseValidator, DataFactory


class TestSearchSongs:
    """Tests para search_songs endpoint"""
    
    @pytest.fixture
    def endpoint_path(self):
        return "/suno/songs/search"
    
    @pytest.mark.asyncio
    @pytest.mark.happy_path
    async def test_search_songs_basic(
        self,
        test_client,
        endpoint_path,
        mock_song_service
    ):
        """Test básico de búsqueda"""
        songs = [
            create_song_dict(song_id="song-1", prompt="happy pop song"),
            create_song_dict(song_id="song-2", prompt="sad rock song"),
            create_song_dict(song_id="song-3", prompt="happy jazz song")
        ]
        mock_song_service.list_songs.return_value = songs
        
        with patch('api.routes.search.optimize_search_query') as mock_optimize, \
             patch('api.routes.search.get_song_async_or_sync') as mock_get, \
             patch('api.routes.search.filter_songs_efficiently') as mock_filter, \
             patch('api.routes.search.paginate_results') as mock_paginate:
            
            mock_optimize.return_value = "happy"
            mock_get.return_value = songs
            mock_filter.return_value = [songs[0], songs[2]]  # Solo las que tienen "happy"
            mock_paginate.return_value = {
                "items": [songs[0], songs[2]],
                "total": 2,
                "limit": 20,
                "offset": 0,
                "has_more": False,
                "page": 1,
                "total_pages": 1
            }
            
            response = test_client.get(
                endpoint_path,
                params={"query": "happy"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "songs" in data
            assert "total" in data
            assert data["total"] == 2
            assert len(data["songs"]) == 2
    
    @pytest.mark.asyncio
    @pytest.mark.happy_path
    async def test_search_songs_with_genre_filter(
        self,
        test_client,
        endpoint_path,
        mock_song_service
    ):
        """Test con filtro de género"""
        songs = [
            create_song_dict(song_id="song-1", prompt="pop song", genre="pop"),
            create_song_dict(song_id="song-2", prompt="rock song", genre="rock"),
            create_song_dict(song_id="song-3", prompt="pop song", genre="pop")
        ]
        
        with patch('api.routes.search.optimize_search_query') as mock_optimize, \
             patch('api.routes.search.get_song_async_or_sync') as mock_get, \
             patch('api.routes.search.filter_songs_efficiently') as mock_filter, \
             patch('api.routes.search.paginate_results') as mock_paginate:
            
            mock_optimize.return_value = "song"
            mock_get.return_value = songs
            mock_filter.return_value = [songs[0], songs[2]]  # Solo pop
            mock_paginate.return_value = {
                "items": [songs[0], songs[2]],
                "total": 2,
                "limit": 20,
                "offset": 0,
                "has_more": False,
                "page": 1,
                "total_pages": 1
            }
            
            response = test_client.get(
                endpoint_path,
                params={"query": "song", "genre": "pop"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total"] == 2
            assert "filters_applied" in data
            assert data["filters_applied"].get("genre") == "pop"
    
    @pytest.mark.asyncio
    @pytest.mark.happy_path
    async def test_search_songs_with_status_filter(
        self,
        test_client,
        endpoint_path,
        mock_song_service
    ):
        """Test con filtro de estado"""
        songs = [
            create_song_dict(song_id="song-1", status="completed"),
            create_song_dict(song_id="song-2", status="processing"),
            create_song_dict(song_id="song-3", status="completed")
        ]
        
        with patch('api.routes.search.optimize_search_query') as mock_optimize, \
             patch('api.routes.search.get_song_async_or_sync') as mock_get, \
             patch('api.routes.search.filter_songs_efficiently') as mock_filter, \
             patch('api.routes.search.paginate_results') as mock_paginate:
            
            mock_optimize.return_value = "song"
            mock_get.return_value = songs
            mock_filter.return_value = [songs[0], songs[2]]  # Solo completed
            mock_paginate.return_value = {
                "items": [songs[0], songs[2]],
                "total": 2,
                "limit": 20,
                "offset": 0,
                "has_more": False,
                "page": 1,
                "total_pages": 1
            }
            
            response = test_client.get(
                endpoint_path,
                params={"query": "song", "status_filter": "completed"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["filters_applied"].get("status") == "completed"
    
    @pytest.mark.asyncio
    @pytest.mark.happy_path
    async def test_search_songs_with_pagination(
        self,
        test_client,
        endpoint_path,
        mock_song_service
    ):
        """Test con paginación"""
        songs = [create_song_dict(song_id=f"song-{i}") for i in range(50)]
        
        with patch('api.routes.search.optimize_search_query') as mock_optimize, \
             patch('api.routes.search.get_song_async_or_sync') as mock_get, \
             patch('api.routes.search.filter_songs_efficiently') as mock_filter, \
             patch('api.routes.search.paginate_results') as mock_paginate:
            
            mock_optimize.return_value = "song"
            mock_get.return_value = songs
            mock_filter.return_value = songs
            mock_paginate.return_value = {
                "items": songs[:20],
                "total": 50,
                "limit": 20,
                "offset": 0,
                "has_more": True,
                "page": 1,
                "total_pages": 3
            }
            
            response = test_client.get(
                endpoint_path,
                params={"query": "song", "limit": 20, "offset": 0}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total"] == 50
            assert len(data["songs"]) == 20
            assert data["has_more"] is True
            assert data["page"] == 1
            assert data["total_pages"] == 3
    
    @pytest.mark.asyncio
    @pytest.mark.error_handling
    async def test_search_songs_empty_query(
        self,
        test_client,
        endpoint_path
    ):
        """Test con query vacío"""
        response = test_client.get(
            endpoint_path,
            params={"query": ""}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    @pytest.mark.error_handling
    async def test_search_songs_invalid_status_filter(
        self,
        test_client,
        endpoint_path
    ):
        """Test con filtro de estado inválido"""
        with patch('api.routes.search.optimize_search_query') as mock_optimize, \
             patch('api.routes.search.get_song_async_or_sync') as mock_get:
            
            mock_optimize.return_value = "song"
            mock_get.return_value = []
            
            response = test_client.get(
                endpoint_path,
                params={"query": "song", "status_filter": "invalid_status"}
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.asyncio
    @pytest.mark.boundary
    async def test_search_songs_max_limit(
        self,
        test_client,
        endpoint_path,
        mock_song_service
    ):
        """Test con límite máximo"""
        with patch('api.routes.search.optimize_search_query') as mock_optimize, \
             patch('api.routes.search.get_song_async_or_sync') as mock_get, \
             patch('api.routes.search.filter_songs_efficiently') as mock_filter, \
             patch('api.routes.search.paginate_results') as mock_paginate:
            
            mock_optimize.return_value = "song"
            mock_get.return_value = []
            mock_filter.return_value = []
            mock_paginate.return_value = {
                "items": [],
                "total": 0,
                "limit": 100,
                "offset": 0,
                "has_more": False,
                "page": 1,
                "total_pages": 1
            }
            
            response = test_client.get(
                endpoint_path,
                params={"query": "song", "limit": 100}
            )
            
            assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    @pytest.mark.edge_case
    async def test_search_songs_with_tags(
        self,
        test_client,
        endpoint_path,
        mock_song_service
    ):
        """Test con filtro de tags"""
        songs = [
            create_song_dict(song_id="song-1", metadata={"tags": ["happy", "pop"]}),
            create_song_dict(song_id="song-2", metadata={"tags": ["sad", "rock"]})
        ]
        
        with patch('api.routes.search.optimize_search_query') as mock_optimize, \
             patch('api.routes.search.get_song_async_or_sync') as mock_get, \
             patch('api.routes.search.filter_songs_efficiently') as mock_filter, \
             patch('api.routes.search.paginate_results') as mock_paginate:
            
            mock_optimize.return_value = "song"
            mock_get.return_value = songs
            mock_filter.return_value = [songs[0]]  # Solo con tag "happy"
            mock_paginate.return_value = {
                "items": [songs[0]],
                "total": 1,
                "limit": 20,
                "offset": 0,
                "has_more": False,
                "page": 1,
                "total_pages": 1
            }
            
            response = test_client.get(
                endpoint_path,
                params={"query": "song", "tags": "happy,pop"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total"] == 1
    
    @pytest.mark.asyncio
    @pytest.mark.edge_case
    async def test_search_songs_no_results(
        self,
        test_client,
        endpoint_path,
        mock_song_service
    ):
        """Test sin resultados"""
        with patch('api.routes.search.optimize_search_query') as mock_optimize, \
             patch('api.routes.search.get_song_async_or_sync') as mock_get, \
             patch('api.routes.search.filter_songs_efficiently') as mock_filter, \
             patch('api.routes.search.paginate_results') as mock_paginate:
            
            mock_optimize.return_value = "nonexistent"
            mock_get.return_value = []
            mock_filter.return_value = []
            mock_paginate.return_value = {
                "items": [],
                "total": 0,
                "limit": 20,
                "offset": 0,
                "has_more": False,
                "page": 1,
                "total_pages": 1
            }
            
            response = test_client.get(
                endpoint_path,
                params={"query": "nonexistent"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total"] == 0
            assert len(data["songs"]) == 0

