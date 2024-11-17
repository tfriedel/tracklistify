"""Provider factory for managing track identification and metadata providers."""

import logging
from typing import Dict, List, Optional, Type, Union
from .base import TrackIdentificationProvider, MetadataProvider
from .spotify import SpotifyProvider
from .shazam import ShazamProvider
from .acrcloud import ACRCloudProvider

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

def create_provider(provider_type: str, **kwargs) -> Union[TrackIdentificationProvider, MetadataProvider]:
    """Create a provider instance based on the provider type.

    Args:
        provider_type: Type of provider to create
        **kwargs: Provider-specific configuration options

    Returns:
        Provider instance
    """
    providers = {
        "spotify": SpotifyProvider,
        "shazam": ShazamProvider,
        "acrcloud": ACRCloudProvider,
    }

    provider_class = providers.get(provider_type)
    if not provider_class:
        raise ValueError(f"Unknown provider type: {provider_type}")

    return provider_class(**kwargs)

def create_provider_factory(config: Dict) -> ProviderFactory:
    """Create and configure a provider factory based on configuration.

    Args:
        config: Configuration dictionary containing provider settings

    Returns:
        Configured ProviderFactory instance
    """
    factory = ProviderFactory()

    # Configure ACRCloud provider
    if "ACR_ACCESS_KEY" in config and "ACR_ACCESS_SECRET" in config:
        acr_provider = ACRCloudProvider(
            access_key=config["ACR_ACCESS_KEY"],
            access_secret=config["ACR_ACCESS_SECRET"],
            host=config.get("ACR_HOST", "identify-eu-west-1.acrcloud.com"),
            timeout=int(config.get("ACR_TIMEOUT", 10)),
        )
        factory.register_identification_provider("acrcloud", acr_provider)

    # Configure Shazam provider
    if "SHAZAM_API_KEY" in config:
        shazam_provider = ShazamProvider(
            api_key=config["SHAZAM_API_KEY"],
            timeout=int(config.get("SHAZAM_TIMEOUT", 10)),
        )
        factory.register_identification_provider("shazam", shazam_provider)

    # Configure Spotify provider
    if "SPOTIFY_CLIENT_ID" in config and "SPOTIFY_CLIENT_SECRET" in config:
        spotify_provider = SpotifyProvider(
            client_id=config["SPOTIFY_CLIENT_ID"],
            client_secret=config["SPOTIFY_CLIENT_SECRET"],
            timeout=int(config.get("SPOTIFY_TIMEOUT", 10)),
        )
        factory.register_metadata_provider("spotify", spotify_provider)

    return factory
