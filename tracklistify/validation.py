"""
Input validation utilities for Tracklistify.
"""

import re
from urllib.parse import urlparse, unquote
from typing import Optional

def validate_and_clean_url(url: str) -> Optional[str]:
    """
    Validate and clean a URL.
    
    Args:
        url: Input URL to validate and clean
        
    Returns:
        Cleaned URL if valid, None if invalid
        
    Features:
        - Strips backslashes and whitespace
        - Validates URL format
        - Supports YouTube and other video platforms
        - Unescapes URL-encoded characters
    """
    if not url:
        return None
        
    # Strip whitespace and backslashes
    url = url.strip().replace('\\', '')
    
    # Unescape URL-encoded characters
    url = unquote(url)
    
    try:
        # Parse URL
        parsed = urlparse(url)
        
        # Check basic URL validity
        if not all([parsed.scheme, parsed.netloc]):
            return None
            
        # Validate YouTube URLs
        if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            # Extract video ID
            if 'youtube.com' in parsed.netloc:
                video_id = re.search(r'[?&]v=([^&]+)', url)
            else:  # youtu.be
                video_id = re.search(r'youtu\.be/([^?&]+)', url)
                
            if not video_id:
                return None
                
            # Reconstruct clean YouTube URL
            return f'https://www.youtube.com/watch?v={video_id.group(1)}'
            
        # For other URLs, return cleaned version
        return f'{parsed.scheme}://{parsed.netloc}{parsed.path}'
        
    except Exception:
        return None

def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    return validate_and_clean_url(url) is not None

def is_youtube_url(url: str) -> bool:
    """
    Check if a URL is a valid YouTube URL.
    
    Args:
        url: URL to check
        
    Returns:
        bool: True if URL is a valid YouTube URL, False otherwise
    """
    if not url:
        return False
        
    cleaned_url = validate_and_clean_url(url)
    if not cleaned_url:
        return False
        
    return 'youtube.com/watch?v=' in cleaned_url
