"""
Cache management for API responses and audio processing.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .track import Track
from .logger import logger

class CacheEntry:
    """Represents a cached track entry."""
    
    def __init__(self, track: Track, timestamp: float):
        """Initialize cache entry."""
        self.track = track
        self.timestamp = timestamp
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary."""
        return {
            'track': self.track.to_dict(),
            'timestamp': self.timestamp
        }
        
    def to_json(self) -> str:
        """Convert entry to JSON string."""
        return json.dumps(self.to_dict())
        
    @classmethod
    def from_json(cls, json_str: str) -> 'CacheEntry':
        """Create entry from JSON string."""
        data = json.loads(json_str)
        return cls(
            track=Track.from_dict(data['track']),
            timestamp=data['timestamp']
        )

class Cache:
    """Simple file-based cache for track identification results."""
    
    def __init__(self, cache_dir: str = ".cache"):
        """Initialize cache with directory."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _generate_key(self, url: str) -> str:
        """Generate cache key from URL."""
        import hashlib
        return hashlib.sha256(url.encode()).hexdigest()
        
    def save(self, url: str, track: Track) -> None:
        """
        Save track to cache.
        
        Args:
            url: Source URL
            track: Track to cache
        """
        key = self._generate_key(url)
        entry = CacheEntry(track=track, timestamp=time.time())
        
        try:
            cache_file = self.cache_dir / f"{key}.json"
            with open(cache_file, 'w') as f:
                json.dump(entry.to_dict(), f)
            logger.debug(f"Cached track for URL: {url}")
            
        except OSError as e:
            logger.warning(f"Failed to write cache for URL {url}: {str(e)}")
            
    def load(self, url: str) -> Optional[Track]:
        """
        Load track from cache if valid.
        
        Args:
            url: Source URL
            
        Returns:
            Track if valid cache exists, None otherwise
        """
        key = self._generate_key(url)
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, 'r') as f:
                entry = CacheEntry.from_json(f.read())
                
            # Check if cache is expired (30 days)
            if time.time() - entry.timestamp > 30 * 24 * 60 * 60:
                logger.debug(f"Cache expired for URL: {url}")
                os.remove(cache_file)
                return None
                
            logger.debug(f"Cache hit for URL: {url}")
            return entry.track
            
        except (json.JSONDecodeError, KeyError, OSError) as e:
            logger.warning(f"Failed to read cache for URL {url}: {str(e)}")
            return None
            
    def clear(self) -> None:
        """Clear all cache entries."""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except OSError as e:
                logger.warning(f"Failed to delete cache file {cache_file}: {str(e)}")

# Global cache instance
_cache_instance = None

def get_cache() -> Cache:
    """Get the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = Cache()
    return _cache_instance
