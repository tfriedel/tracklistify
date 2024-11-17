"""Base classes for track identification and metadata providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class Provider:
    """Base class for track identification providers."""

    def __init__(self, config):
        """Initialize provider with config."""
        self.config = config

    def identify_tracks(self, file_path: str, start_time: int = 0, duration: int = None) -> List:
        """Identify tracks in an audio file.
        
        Args:
            file_path: Path to audio file
            start_time: Start time in seconds
            duration: Duration in seconds
            
        Returns:
            List of identified tracks
        """
        # This is a default implementation that returns an empty list
        # Subclasses should override this method
        return []

class Track:
    pass

class TrackIdentificationProvider(ABC):
    """Base class for track identification providers."""
    
    @abstractmethod
    async def identify_track(self, audio_data: bytes, start_time: float = 0) -> Dict:
        """
        Identify a track from audio data.
        
        Args:
            audio_data: Raw audio data bytes
            start_time: Start time in seconds for the audio segment
            
        Returns:
            Dict containing track information
        """
        pass
    
    @abstractmethod
    async def enrich_metadata(self, track_info: Dict) -> Dict:
        """
        Enrich track metadata with additional information.
        
        Args:
            track_info: Basic track information
            
        Returns:
            Dict containing enriched track information
        """
        pass

class MetadataProvider(ABC):
    """Base class for metadata-only providers."""
    
    @abstractmethod
    async def search_track(self, query: str) -> List[Dict]:
        """
        Search for track metadata.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching tracks with metadata
        """
        pass
    
    @abstractmethod
    async def get_track_details(self, track_id: str) -> Dict:
        """
        Get detailed track information.
        
        Args:
            track_id: Provider-specific track ID
            
        Returns:
            Dict containing detailed track information
        """
        pass

class ProviderError(Exception):
    """Base exception for provider errors."""
    pass

class AuthenticationError(ProviderError):
    """Raised when provider authentication fails."""
    pass

class RateLimitError(ProviderError):
    """Raised when provider rate limit is exceeded."""
    pass

class IdentificationError(ProviderError):
    """Raised when track identification fails."""
    pass
