"""Test suite for track identification and metadata providers."""

import pytest
import asyncio
from unittest.mock import Mock, patch
from tracklistify.providers.base import (
    TrackIdentificationProvider,
    MetadataProvider,
    ProviderError,
    AuthenticationError,
    RateLimitError
)
from tracklistify.providers.spotify import SpotifyProvider
from tracklistify.providers.factory import ProviderFactory, create_provider_factory
from tests.conftest import (
    TEST_TRACK_TITLE,
    TEST_TRACK_ARTIST,
    TEST_TRACK_ALBUM,
    TEST_TRACK_DURATION,
    TEST_TRACK_CONFIDENCE
)

@pytest.fixture
def spotify_config():
    """Spotify configuration fixture."""
    return {
        "SPOTIFY_CLIENT_ID": "test_client_id",
        "SPOTIFY_CLIENT_SECRET": "test_client_secret"
    }

@pytest.fixture
def mock_spotify_response():
    """Mock Spotify API response fixture."""
    return {
        "tracks": {
            "items": [
                {
                    "id": "test_id",
                    "name": TEST_TRACK_TITLE,
                    "artists": [{"name": TEST_TRACK_ARTIST}],
                    "album": {
                        "name": TEST_TRACK_ALBUM,
                        "release_date": "2024-01-01"
                    },
                    "duration_ms": int(TEST_TRACK_DURATION * 1000),
                    "popularity": int(TEST_TRACK_CONFIDENCE),
                    "preview_url": "https://example.com/preview",
                    "external_urls": {"spotify": "https://example.com/track"}
                }
            ]
        }
    }

@pytest.fixture
def mock_spotify_track():
    """Mock Spotify track details fixture."""
    return {
        "id": "test_id",
        "name": TEST_TRACK_TITLE,
        "artists": [{"name": TEST_TRACK_ARTIST}],
        "album": {
            "name": TEST_TRACK_ALBUM,
            "release_date": "2024-01-01"
        },
        "duration_ms": int(TEST_TRACK_DURATION * 1000),
        "popularity": int(TEST_TRACK_CONFIDENCE),
        "preview_url": "https://example.com/preview",
        "external_urls": {"spotify": "https://example.com/track"}
    }

@pytest.fixture
def mock_audio_features():
    """Mock Spotify audio features fixture."""
    return {
        "id": "test_id",
        "tempo": 120.0,
        "key": 1,
        "mode": 1,
        "time_signature": 4,
        "duration_ms": int(TEST_TRACK_DURATION * 1000),
        "loudness": -8.0,
        "energy": 0.8
    }

class TestSpotifyProvider:
    """Test cases for SpotifyProvider."""
    
    async def test_authentication(self, spotify_config):
        """Test Spotify authentication."""
        provider = SpotifyProvider(spotify_config)
        await provider.authenticate()
        assert provider.is_authenticated()
        
    async def test_search_track(self, spotify_config, mock_spotify_response):
        """Test track search functionality."""
        provider = SpotifyProvider(spotify_config)
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value.json.return_value = mock_spotify_response
            mock_get.return_value.__aenter__.return_value.status = 200
            
            track = await provider.search_track(TEST_TRACK_TITLE, TEST_TRACK_ARTIST)
            assert track is not None
            assert track.song_name == TEST_TRACK_TITLE
            assert track.artist == TEST_TRACK_ARTIST
            assert track.album == TEST_TRACK_ALBUM
            assert track.duration_ms == int(TEST_TRACK_DURATION * 1000)
    
    async def test_get_track_details(self, spotify_config, mock_spotify_track, mock_audio_features):
        """Test track details retrieval."""
        provider = SpotifyProvider(spotify_config)
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value.json.side_effect = [
                mock_spotify_track,
                mock_audio_features
            ]
            mock_get.return_value.__aenter__.return_value.status = 200
            
            details = await provider.get_track_details("test_id")
            assert details is not None
            assert details["name"] == TEST_TRACK_TITLE
            assert details["artists"][0]["name"] == TEST_TRACK_ARTIST
            assert details["album"]["name"] == TEST_TRACK_ALBUM
            assert details["duration_ms"] == int(TEST_TRACK_DURATION * 1000)
    
    async def test_rate_limit_handling(self, spotify_config):
        """Test rate limit error handling."""
        provider = SpotifyProvider(spotify_config)
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value.status = 429
            mock_get.return_value.__aenter__.return_value.headers = {"Retry-After": "1"}
            
            with pytest.raises(RateLimitError):
                await provider.search_track(TEST_TRACK_TITLE, TEST_TRACK_ARTIST)

class TestProviderFactory:
    """Test cases for ProviderFactory."""
    
    def test_create_factory(self, spotify_config):
        """Test factory creation with configuration."""
        factory = create_provider_factory(spotify_config)
        assert isinstance(factory, ProviderFactory)
        assert factory.config == spotify_config
    
    def test_register_providers(self):
        """Test provider registration."""
        factory = ProviderFactory({})
        provider = Mock(spec=TrackIdentificationProvider)
        factory.register_provider("test", provider)
        assert factory.get_provider("test") == provider
    
    async def test_close_all(self):
        """Test closing all provider connections."""
        factory = ProviderFactory({})
        provider1 = Mock(spec=TrackIdentificationProvider)
        provider2 = Mock(spec=MetadataProvider)
        
        factory.register_provider("provider1", provider1)
        factory.register_provider("provider2", provider2)
        
        await factory.close_all()
        provider1.close.assert_called_once()
        provider2.close.assert_called_once()
