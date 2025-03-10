"""Spotify metadata provider implementation."""

import asyncio
import base64
import logging
from typing import Dict, List, Optional
import aiohttp
from .base import MetadataProvider, AuthenticationError, RateLimitError, ProviderError

logger = logging.getLogger(__name__)

class SpotifyProvider(MetadataProvider):
    """Spotify metadata provider for track information enrichment."""
    
    AUTH_URL = "https://accounts.spotify.com/api/token"
    API_BASE = "https://api.spotify.com/v1"
    
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize Spotify provider.
        
        Args:
            client_id: Spotify API client ID
            client_secret: Spotify API client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None
        self._token_expiry = 0
        self._session = None
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
    
    async def _get_access_token(self) -> str:
        """Get or refresh Spotify access token."""
        if self._access_token and self._token_expiry > asyncio.get_event_loop().time():
            return self._access_token
            
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_b64 = base64.b64encode(auth_string.encode()).decode()
        
        await self._ensure_session()
        async with self._session.post(
            self.AUTH_URL,
            headers={"Authorization": f"Basic {auth_b64}"},
            data={"grant_type": "client_credentials"}
        ) as response:
            if response.status == 401:
                raise AuthenticationError("Invalid Spotify credentials")
            elif response.status != 200:
                raise ProviderError(f"Failed to get Spotify token: {response.status}")
                
            data = await response.json()
            self._access_token = data["access_token"]
            self._token_expiry = asyncio.get_event_loop().time() + data["expires_in"]
            return self._access_token
    
    async def _api_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make authenticated request to Spotify API."""
        await self._ensure_session()
        token = await self._get_access_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            **kwargs.pop("headers", {})
        }
        
        url = f"{self.API_BASE}/{endpoint}"
        async with self._session.request(method, url, headers=headers, **kwargs) as response:
            if response.status == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise RateLimitError(f"Spotify rate limit exceeded. Retry after {retry_after}s")
            elif response.status == 401:
                self._access_token = None
                raise AuthenticationError("Spotify token expired")
            elif response.status != 200:
                raise ProviderError(f"Spotify API error: {response.status}")
                
            return await response.json()
    
    async def search_track(self, query: str) -> List[Dict]:
        """
        Search for tracks on Spotify.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching tracks with metadata
        """
        try:
            response = await self._api_request(
                "GET",
                "search",
                params={
                    "q": query,
                    "type": "track",
                    "limit": 5
                }
            )
            
            tracks = []
            for item in response["tracks"]["items"]:
                track = {
                    "id": item["id"],
                    "name": item["name"],
                    "artists": [artist["name"] for artist in item["artists"]],
                    "album": item["album"]["name"],
                    "release_date": item["album"]["release_date"],
                    "duration_ms": item["duration_ms"],
                    "popularity": item["popularity"],
                    "preview_url": item["preview_url"],
                    "external_urls": item["external_urls"]
                }
                tracks.append(track)
            return tracks
            
        except Exception as e:
            logger.error(f"Spotify search error: {e}")
            raise
    
    async def get_track_details(self, track_id: str) -> Dict:
        """
        Get detailed track information from Spotify.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Dict containing detailed track information
        """
        try:
            track = await self._api_request("GET", f"tracks/{track_id}")
            audio_features = await self._api_request("GET", f"audio-features/{track_id}")
            
            return {
                "id": track["id"],
                "name": track["name"],
                "artists": [artist["name"] for artist in track["artists"]],
                "album": track["album"]["name"],
                "release_date": track["album"]["release_date"],
                "duration_ms": track["duration_ms"],
                "popularity": track["popularity"],
                "preview_url": track["preview_url"],
                "external_urls": track["external_urls"],
                "audio_features": {
                    "tempo": audio_features["tempo"],
                    "key": audio_features["key"],
                    "mode": audio_features["mode"],
                    "time_signature": audio_features["time_signature"],
                    "danceability": audio_features["danceability"],
                    "energy": audio_features["energy"],
                    "loudness": audio_features["loudness"]
                }
            }
            
        except Exception as e:
            logger.error(f"Spotify track details error: {e}")
            raise
    
    async def close(self):
        """Close the aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None
