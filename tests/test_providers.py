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
                    "name": "Test Track",
                    "artists": [{"name": "Test Artist"}],
                    "album": {
                        "name": "Test Album",
                        "release_date": "2024-01-01"
                    },
                    "duration_ms": 180000,
                    "popularity": 80,
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
        "name": "Test Track",
        "artists": [{"name": "Test Artist"}],
        "album": {
            "name": "Test Album",
            "release_date": "2024-01-01"
        },
        "duration_ms": 180000,
        "popularity": 80,
        "preview_url": "https://example.com/preview",
        "external_urls": {"spotify": "https://example.com/track"}
    }

@pytest.fixture
def mock_audio_features():
    """Mock Spotify audio features fixture."""
    return {
        "tempo": 120.5,
        "key": 1,
        "mode": 1,
        "time_signature": 4,
        "danceability": 0.8,
        "energy": 0.9,
        "loudness": -5.5
    }

class TestSpotifyProvider:
    """Test cases for SpotifyProvider."""
    
    @pytest.mark.asyncio
    async def test_authentication(self, spotify_config):
        """Test Spotify authentication."""
        provider = SpotifyProvider(
            client_id=spotify_config["SPOTIFY_CLIENT_ID"],
            client_secret=spotify_config["SPOTIFY_CLIENT_SECRET"]
        )
        
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value.status = 200
            mock_post.return_value.__aenter__.return_value.json = \
                asyncio.coroutine(lambda: {"access_token": "test_token", "expires_in": 3600})
            
            token = await provider._get_access_token()
            assert token == "test_token"
    
    @pytest.mark.asyncio
    async def test_search_track(self, spotify_config, mock_spotify_response):
        """Test track search functionality."""
        provider = SpotifyProvider(
            client_id=spotify_config["SPOTIFY_CLIENT_ID"],
            client_secret=spotify_config["SPOTIFY_CLIENT_SECRET"]
        )
        
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.status = 200
            mock_request.return_value.__aenter__.return_value.json = \
                asyncio.coroutine(lambda: mock_spotify_response)
            
            tracks = await provider.search_track("test query")
            assert len(tracks) == 1
            assert tracks[0]["name"] == "Test Track"
            assert tracks[0]["artists"] == ["Test Artist"]
    
    @pytest.mark.asyncio
    async def test_get_track_details(self, spotify_config, mock_spotify_track, mock_audio_features):
        """Test track details retrieval."""
        provider = SpotifyProvider(
            client_id=spotify_config["SPOTIFY_CLIENT_ID"],
            client_secret=spotify_config["SPOTIFY_CLIENT_SECRET"]
        )
        
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.status = 200
            mock_request.return_value.__aenter__.return_value.json = \
                asyncio.coroutine(lambda: mock_spotify_track)
            
            details = await provider.get_track_details("test_id")
            assert details["name"] == "Test Track"
            assert details["artists"] == ["Test Artist"]
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, spotify_config):
        """Test rate limit error handling."""
        provider = SpotifyProvider(
            client_id=spotify_config["SPOTIFY_CLIENT_ID"],
            client_secret=spotify_config["SPOTIFY_CLIENT_SECRET"]
        )
        
        with patch("aiohttp.ClientSession.request") as mock_request:
            mock_request.return_value.__aenter__.return_value.status = 429
            mock_request.return_value.__aenter__.return_value.headers = {"Retry-After": "60"}
            
            with pytest.raises(RateLimitError):
                await provider.search_track("test query")

class TestProviderFactory:
    """Test cases for ProviderFactory."""
    
    def test_create_factory(self, spotify_config):
        """Test factory creation with configuration."""
        factory = create_provider_factory(spotify_config)
        assert factory.get_metadata_provider("spotify") is not None
    
    def test_register_providers(self):
        """Test provider registration."""
        factory = ProviderFactory()
        mock_provider = Mock(spec=MetadataProvider)
        
        factory.register_metadata_provider("test", mock_provider)
        assert factory.get_metadata_provider("test") == mock_provider
    
    @pytest.mark.asyncio
    async def test_close_all(self):
        """Test closing all provider connections."""
        factory = ProviderFactory()
        mock_provider = Mock(spec=MetadataProvider)
        mock_provider.close = asyncio.coroutine(lambda: None)
        
        factory.register_metadata_provider("test", mock_provider)
        await factory.close_all()
        
        mock_provider.close.assert_called_once()
