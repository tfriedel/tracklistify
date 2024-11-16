"""
Rate limiting functionality for API calls.
"""

import time
from threading import Lock
from typing import Optional

from .config import get_config
from .logger import logger

class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self):
        """Initialize rate limiter."""
        self._config = get_config()
        self._tokens = self._config.app.max_requests_per_minute
        self._last_update = time.time()
        self._lock = Lock()
        
    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_update
        
        # Calculate tokens to add (1 token per (60/max_requests) seconds)
        new_tokens = int(elapsed / (60.0 / self._config.app.max_requests_per_minute))
        if new_tokens > 0:
            self._tokens = min(
                self._tokens + new_tokens,
                self._config.app.max_requests_per_minute
            )
            self._last_update = now
            
    def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire a token, blocking if necessary.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if token acquired, False if timed out
        """
        start_time = time.time()
        
        while True:
            with self._lock:
                self._refill()
                
                if self._tokens > 0:
                    self._tokens -= 1
                    logger.debug(f"Token acquired, {self._tokens} remaining")
                    return True
                    
            # Check timeout
            if timeout is not None:
                if time.time() - start_time >= timeout:
                    logger.warning("Rate limit timeout reached")
                    return False
                    
            # Wait before trying again
            time.sleep(0.1)
            
    def get_remaining(self) -> int:
        """Get remaining tokens."""
        with self._lock:
            self._refill()
            return self._tokens

# Global rate limiter instance
_rate_limiter_instance = None

def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = RateLimiter()
    return _rate_limiter_instance
