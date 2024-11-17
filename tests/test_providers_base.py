"""
Unit tests for base provider classes.
"""

import pytest
from typing import Dict, List
from tracklistify.providers.base import (
    Provider,
    TrackIdentificationProvider,
    MetadataProvider,
    ProviderError,
    AuthenticationError,
    RateLimitError,
    IdentificationError
)

def test_base_provider():
    """Test base Provider class."""
    config = {"test": "config"}
    provider = Provider(config)
    assert provider.config == config
    
    # Test default identify_tracks implementation
    tracks = provider.identify_tracks("test.mp3")
    assert isinstance(tracks, list)
    assert len(tracks) == 0

class TestTrackIdentificationProvider:
    """Test TrackIdentificationProvider class."""
    
    class MockProvider(TrackIdentificationProvider):
        """Mock implementation of TrackIdentificationProvider."""
        
        async def identify_track(self, audio_data: bytes, start_time: float = 0) -> Dict:
            if not audio_data:
                raise IdentificationError("No audio data provided")
            return {"title": "Test Track", "artist": "Test Artist"}
        
        async def enrich_metadata(self, track_info: Dict) -> Dict:
            if not track_info:
                raise ProviderError("No track info provided")
            track_info["album"] = "Test Album"
            track_info["year"] = 2024
            return track_info
        
        async def get_provider_name(self) -> str:
            return "MockProvider"
        
        async def get_provider_version(self) -> str:
            return "1.0.0"
    
    @pytest.mark.asyncio
    async def test_identify_track(self):
        """Test track identification."""
        provider = self.MockProvider()
        
        # Test successful identification
        result = await provider.identify_track(b"test_audio_data")
        assert isinstance(result, dict)
        assert result["title"] == "Test Track"
        assert result["artist"] == "Test Artist"
        
        # Test error handling
        with pytest.raises(IdentificationError):
            await provider.identify_track(b"")
    
    @pytest.mark.asyncio
    async def test_enrich_metadata(self):
        """Test metadata enrichment."""
        provider = self.MockProvider()
        
        # Test successful enrichment
        track_info = {"title": "Test Track", "artist": "Test Artist"}
        enriched = await provider.enrich_metadata(track_info)
        assert enriched["album"] == "Test Album"
        assert enriched["year"] == 2024
        
        # Test error handling
        with pytest.raises(ProviderError):
            await provider.enrich_metadata({})
    
    @pytest.mark.asyncio
    async def test_provider_info(self):
        """Test provider information methods."""
        provider = self.MockProvider()
        
        name = await provider.get_provider_name()
        assert name == "MockProvider"
        
        version = await provider.get_provider_version()
        assert version == "1.0.0"

class TestMetadataProvider:
    """Test MetadataProvider class."""
    
    class MockMetadataProvider(MetadataProvider):
        """Mock implementation of MetadataProvider."""
        
        async def search_track(self, query: str) -> List[Dict]:
            if not query:
                raise ProviderError("Empty query")
            return [{"title": "Test Track", "artist": "Test Artist"}]
        
        async def get_track_details(self, track_id: str) -> Dict:
            if not track_id:
                raise ProviderError("Invalid track ID")
            return {
                "id": track_id,
                "title": "Test Track",
                "artist": "Test Artist",
                "album": "Test Album"
            }
    
    @pytest.mark.asyncio
    async def test_search_track(self):
        """Test track search."""
        provider = self.MockMetadataProvider()
        
        # Test successful search
        results = await provider.search_track("test query")
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["title"] == "Test Track"
        
        # Test error handling
        with pytest.raises(ProviderError):
            await provider.search_track("")
    
    @pytest.mark.asyncio
    async def test_get_track_details(self):
        """Test getting track details."""
        provider = self.MockMetadataProvider()
        
        # Test successful details retrieval
        details = await provider.get_track_details("track123")
        assert isinstance(details, dict)
        assert details["id"] == "track123"
        assert details["title"] == "Test Track"
        assert details["album"] == "Test Album"
        
        # Test error handling
        with pytest.raises(ProviderError):
            await provider.get_track_details("")

def test_provider_errors():
    """Test provider error classes."""
    # Test ProviderError
    error = ProviderError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)
    
    # Test AuthenticationError
    auth_error = AuthenticationError("Auth failed")
    assert str(auth_error) == "Auth failed"
    assert isinstance(auth_error, ProviderError)
    
    # Test RateLimitError
    rate_error = RateLimitError("Rate limit exceeded")
    assert str(rate_error) == "Rate limit exceeded"
    assert isinstance(rate_error, ProviderError)
    
    # Test IdentificationError
    id_error = IdentificationError("Identification failed")
    assert str(id_error) == "Identification failed"
    assert isinstance(id_error, ProviderError)
