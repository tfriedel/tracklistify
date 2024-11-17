"""Unit tests for Spotify provider."""

import pytest
import aiohttp
from unittest.mock import AsyncMock, MagicMock, patch
from tracklistify.providers.spotify import SpotifyProvider
from tracklistify.track import Track

@pytest.fixture
def spotify_config():
    return {
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret'
    }

@pytest.fixture
def spotify_provider(spotify_config):
    return SpotifyProvider(spotify_config)

@pytest.fixture
def mock_spotify_track():
    return {
        'id': 'test_spotify_id',
        'name': 'Test Track',
        'artists': [{'name': 'Test Artist'}],
        'album': {
            'name': 'Test Album',
            'release_date': '2024-01-01'
        },
        'duration_ms': 180000,
        'external_ids': {
            'isrc': 'TEST123'
        }
    }

@pytest.fixture
def mock_spotify_auth():
    return {
        'access_token': 'test_access_token',
        'token_type': 'Bearer',
        'expires_in': 3600
    }

@pytest.mark.asyncio
async def test_get_track_by_id_success(spotify_provider, mock_spotify_track, mock_spotify_auth):
    with patch('aiohttp.ClientSession.post') as mock_auth_post, \
         patch('aiohttp.ClientSession.get') as mock_get:
        
        mock_auth_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_spotify_auth
        )
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_spotify_track
        )
        
        track = await spotify_provider.get_track_by_id('test_spotify_id')
        
        assert isinstance(track, Track)
        assert track.title == 'Test Track'
        assert track.artist == 'Test Artist'
        assert track.album == 'Test Album'
        assert track.duration == 180
        assert track.spotify_id == 'test_spotify_id'
        assert track.isrc == 'TEST123'

@pytest.mark.asyncio
async def test_get_track_by_id_not_found(spotify_provider, mock_spotify_auth):
    with patch('aiohttp.ClientSession.post') as mock_auth_post, \
         patch('aiohttp.ClientSession.get') as mock_get:
        
        mock_auth_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_spotify_auth
        )
        mock_get.return_value.__aenter__.return_value.status = 404
        
        track = await spotify_provider.get_track_by_id('nonexistent_id')
        assert track is None

@pytest.mark.asyncio
async def test_get_track_by_id_auth_error(spotify_provider):
    with patch('aiohttp.ClientSession.post') as mock_auth_post:
        mock_auth_post.return_value.__aenter__.return_value.status = 401
        
        with pytest.raises(Exception) as exc_info:
            await spotify_provider.get_track_by_id('test_spotify_id')
        assert 'Authentication failed' in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_track_by_id_rate_limit(spotify_provider, mock_spotify_auth):
    with patch('aiohttp.ClientSession.post') as mock_auth_post, \
         patch('aiohttp.ClientSession.get') as mock_get:
        
        mock_auth_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_spotify_auth
        )
        mock_get.return_value.__aenter__.return_value.status = 429
        
        with pytest.raises(Exception) as exc_info:
            await spotify_provider.get_track_by_id('test_spotify_id')
        assert 'Rate limit' in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_track_by_id_network_error(spotify_provider, mock_spotify_auth):
    with patch('aiohttp.ClientSession.post') as mock_auth_post, \
         patch('aiohttp.ClientSession.get') as mock_get:
        
        mock_auth_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_spotify_auth
        )
        mock_get.side_effect = aiohttp.ClientError
        
        with pytest.raises(Exception):
            await spotify_provider.get_track_by_id('test_spotify_id')

@pytest.mark.asyncio
async def test_get_track_by_id_partial_metadata(spotify_provider, mock_spotify_auth):
    partial_track = {
        'id': 'test_spotify_id',
        'name': 'Test Track',
        'artists': [{'name': 'Test Artist'}],
        'duration_ms': 180000
    }
    
    with patch('aiohttp.ClientSession.post') as mock_auth_post, \
         patch('aiohttp.ClientSession.get') as mock_get:
        
        mock_auth_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_spotify_auth
        )
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=partial_track
        )
        
        track = await spotify_provider.get_track_by_id('test_spotify_id')
        
        assert isinstance(track, Track)
        assert track.title == 'Test Track'
        assert track.artist == 'Test Artist'
        assert track.album is None
        assert track.isrc is None

@pytest.mark.asyncio
async def test_search_track(spotify_provider, mock_spotify_auth, mock_spotify_track):
    search_response = {
        'tracks': {
            'items': [mock_spotify_track]
        }
    }
    
    with patch('aiohttp.ClientSession.post') as mock_auth_post, \
         patch('aiohttp.ClientSession.get') as mock_get:
        
        mock_auth_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_spotify_auth
        )
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=search_response
        )
        
        track = await spotify_provider.search_track('Test Track', 'Test Artist')
        
        assert isinstance(track, Track)
        assert track.title == 'Test Track'
        assert track.artist == 'Test Artist'
        assert track.spotify_id == 'test_spotify_id'
