"""Provider factory for managing track identification and metadata providers."""

import logging
from typing import Dict, List, Optional, Type, Union
from .base import TrackIdentificationProvider, MetadataProvider
from .spotify import SpotifyProvider
from .shazam import ShazamProvider

logger = logging.getLogger(__name__)

class ProviderFactory:
    """Factory class for creating and managing providers."""
    
    def __init__(self):
        self._identification_providers: Dict[str, TrackIdentificationProvider] = {}
        self._metadata_providers: Dict[str, MetadataProvider] = {}
    
    def register_identification_provider(
        self, name: str, provider: TrackIdentificationProvider
    ) -> None:
        """Register a track identification provider."""
        self._identification_providers[name] = provider
    
    def register_metadata_provider(
        self, name: str, provider: MetadataProvider
    ) -> None:
        """Register a metadata provider."""
        self._metadata_providers[name] = provider
    
    def get_identification_provider(self, name: str) -> Optional[TrackIdentificationProvider]:
        """Get a track identification provider by name."""
        return self._identification_providers.get(name)
    
    def get_metadata_provider(self, name: str) -> Optional[MetadataProvider]:
        """Get a metadata provider by name."""
        return self._metadata_providers.get(name)
    
    def get_all_identification_providers(self) -> List[TrackIdentificationProvider]:
        """Get all registered track identification providers."""
        return list(self._identification_providers.values())
    
    def get_all_metadata_providers(self) -> List[MetadataProvider]:
        """Get all registered metadata providers."""
        return list(self._metadata_providers.values())
    
    async def close_all(self):
        """Close all provider connections."""
        for provider in self._identification_providers.values():
            if hasattr(provider, 'close'):
                await provider.close()
        
        for provider in self._metadata_providers.values():
            if hasattr(provider, 'close'):
                await provider.close()

def create_provider(provider_type: str) -> Union[TrackIdentificationProvider, MetadataProvider]:
    """
    Create a provider instance based on the provider type.
    
    Args:
        provider_type: Type of provider to create
        
    Returns:
        Provider instance
    """
    providers = {
        'spotify': SpotifyProvider,
        'shazam': ShazamProvider,
    }

def create_provider_factory(config: Dict) -> ProviderFactory:
    """
    Create and configure a provider factory based on configuration.
    
    Args:
        config: Configuration dictionary containing provider settings
        
    Returns:
        Configured ProviderFactory instance
    """
    factory = ProviderFactory()
    
    # Configure Spotify provider if credentials are available
    if config.get('SPOTIFY_CLIENT_ID') and config.get('SPOTIFY_CLIENT_SECRET'):
        spotify = SpotifyProvider(
            client_id=config['SPOTIFY_CLIENT_ID'],
            client_secret=config['SPOTIFY_CLIENT_SECRET']
        )
        factory.register_metadata_provider('spotify', spotify)
        logger.info("Registered Spotify metadata provider")
    
    # Configure Shazam provider if credentials are available
    if config.get('SHAZAM_API_KEY'):
        shazam = ShazamProvider(api_key=config['SHAZAM_API_KEY'])
        factory.register_identification_provider('shazam', shazam)
        logger.info("Registered Shazam track identification provider")
    
    # Add more providers here as they are implemented
    
    return factory
