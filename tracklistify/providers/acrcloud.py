"""ACRCloud track identification provider."""

import base64
import hashlib
import hmac
import json
import logging
import time
from typing import Dict, Optional
from urllib.parse import urlencode

import aiohttp
from aiohttp import ClientTimeout

from tracklistify.providers.base import (
    TrackIdentificationProvider,
    ProviderError,
    AuthenticationError,
    RateLimitError,
    IdentificationError,
)

logger = logging.getLogger(__name__)

class ACRCloudProvider(TrackIdentificationProvider):
    """ACRCloud implementation of track identification provider."""

    def __init__(
        self,
        access_key: str,
        access_secret: str,
        host: str = "identify-eu-west-1.acrcloud.com",
        timeout: int = 10,
    ):
        """Initialize ACRCloud provider.

        Args:
            access_key: ACRCloud access key
            access_secret: ACRCloud access secret
            host: ACRCloud API host
            timeout: Request timeout in seconds
        """
        self.access_key = access_key
        self.access_secret = access_secret.encode()
        self.host = host
        self.endpoint = f"https://{host}/v1/identify"
        self.timeout = ClientTimeout(total=timeout)

    def _sign_string(self, string_to_sign: str) -> str:
        """Sign a string using HMAC-SHA1.

        Args:
            string_to_sign: String to be signed

        Returns:
            Base64 encoded signature
        """
        hmac_obj = hmac.new(self.access_secret, string_to_sign.encode(), hashlib.sha1)
        return base64.b64encode(hmac_obj.digest()).decode()

    def _prepare_request_data(self, audio_data: bytes) -> Dict:
        """Prepare request data for ACRCloud API.

        Args:
            audio_data: Raw audio data bytes

        Returns:
            Dict containing request parameters
        """
        timestamp = time.time()
        string_to_sign = f"POST\n/v1/identify\n{self.access_key}\n" \
                        f"audio\n1\n{int(timestamp)}"

        data = {
            "access_key": self.access_key,
            "sample_bytes": len(audio_data),
            "timestamp": str(int(timestamp)),
            "signature": self._sign_string(string_to_sign),
            "data_type": "audio",
            "signature_version": "1",
        }

        files = {"sample": ("sample.wav", audio_data)}
        return {"data": data, "files": files}

    async def identify_track(self, audio_data: bytes, start_time: float = 0) -> Dict:
        """Identify a track from audio data using ACRCloud.

        Args:
            audio_data: Raw audio data bytes
            start_time: Start time in seconds for the audio segment

        Returns:
            Dict containing track information

        Raises:
            AuthenticationError: If ACRCloud authentication fails
            RateLimitError: If ACRCloud rate limit is exceeded
            IdentificationError: If track identification fails
            ProviderError: For other provider-related errors
        """
        try:
            request_data = self._prepare_request_data(audio_data)
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    self.endpoint,
                    data=request_data["data"],
                    data=request_data["files"]
                ) as response:
                    if response.status == 401:
                        raise AuthenticationError("Invalid ACRCloud credentials")
                    elif response.status == 429:
                        raise RateLimitError("ACRCloud rate limit exceeded")
                    elif response.status != 200:
                        raise ProviderError(f"ACRCloud API error: {response.status}")

                    result = await response.json()

                    if result.get("status", {}).get("code") != 0:
                        error_msg = result.get("status", {}).get("msg", "Unknown error")
                        raise IdentificationError(f"ACRCloud identification failed: {error_msg}")

                    if not result.get("metadata", {}).get("music"):
                        return {}

                    track = result["metadata"]["music"][0]
                    return {
                        "title": track.get("title", ""),
                        "artist": track.get("artists", [{}])[0].get("name", ""),
                        "album": track.get("album", {}).get("name", ""),
                        "year": track.get("release_date", ""),
                        "duration": track.get("duration_ms", 0) / 1000,
                        "confidence": track.get("score", 0),
                        "start_time": start_time,
                        "provider": "acrcloud",
                        "external_ids": {
                            "acrcloud": track.get("acrid", ""),
                            "isrc": track.get("external_ids", {}).get("isrc", ""),
                        }
                    }

        except aiohttp.ClientError as e:
            raise ProviderError(f"ACRCloud request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise ProviderError(f"Invalid JSON response from ACRCloud: {str(e)}")
        except Exception as e:
            raise ProviderError(f"Unexpected error in ACRCloud provider: {str(e)}")

    async def enrich_metadata(self, track_info: Dict) -> Dict:
        """Enrich track metadata with additional information.

        Args:
            track_info: Basic track information

        Returns:
            Dict containing enriched track information
        """
        # ACRCloud doesn't support additional metadata enrichment
        return track_info
