"""
Input validation utilities for Tracklistify.
"""

import re
from urllib.parse import urlparse, unquote
from typing import Optional

class URLValidationError(Exception):
    """Raised when URL validation fails."""
    pass

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
            
        # Check for supported platforms
        domain = parsed.netloc.lower()
        if not any(platform in domain for platform in ['youtube.com', 'youtu.be', 'mixcloud.com', 'soundcloud.com']):
            return None
            
        # Validate YouTube URLs
        if 'youtube.com' in domain or 'youtu.be' in domain:
            # Extract video ID
            if 'youtube.com' in domain:
                video_id = re.search(r'[?&]v=([^&]+)', url)
            else:  # youtu.be
                video_id = re.search(r'youtu\.be/([^?&]+)', url)
                
            if not video_id:
                return None
                
            # Reconstruct clean YouTube URL
            return f'https://www.youtube.com/watch?v={video_id.group(1)}'
            
        # For other URLs, return cleaned version
        return f'{parsed.scheme}://{parsed.netloc}{parsed.path}'.rstrip('/')
        
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
    try:
        cleaned = clean_url(url)
        parsed = urlparse(cleaned)
        
        # Check for supported platforms
        domain = parsed.netloc.lower()
        if not any(platform in domain for platform in ['youtube.com', 'youtu.be', 'mixcloud.com', 'soundcloud.com']):
            return False
            
        return True
    except URLValidationError:
        return False
    except Exception:
        return False

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

def clean_url(url: str) -> str:
    """
    Clean a URL by removing unnecessary parameters and normalizing format.
    
    Args:
        url: Input URL to clean
        
    Returns:
        Cleaned URL
        
    Raises:
        URLValidationError: If URL is invalid
    """
    if not url:
        raise URLValidationError("URL cannot be empty")
        
    # Strip whitespace and backslashes
    url = url.strip().replace('\\', '')
    
    # Unescape URL-encoded characters
    url = unquote(url)
    
    try:
        # Parse URL
        parsed = urlparse(url)
        
        # Check basic URL validity
        if not all([parsed.scheme, parsed.netloc]):
            raise URLValidationError("Invalid URL format")
            
        # Clean YouTube URLs
        if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            # Extract video ID
            if 'youtube.com' in parsed.netloc:
                video_id = re.search(r'[?&]v=([^&]+)', url)
            else:  # youtu.be
                video_id = re.search(r'youtu\.be/([^?&]+)', url)
                
            if not video_id:
                raise URLValidationError("Invalid YouTube URL format")
                
            # Return clean YouTube URL
            return f'https://www.youtube.com/watch?v={video_id.group(1)}'
            
        # Clean Mixcloud URLs
        if 'mixcloud.com' in parsed.netloc:
            # Remove trailing slash and query parameters
            path = parsed.path.rstrip('/')
            return f'https://www.mixcloud.com{path}'
            
        # For other URLs, return cleaned version
        return f'{parsed.scheme}://{parsed.netloc}{parsed.path}'
        
    except URLValidationError:
        raise
    except Exception as e:
        raise URLValidationError(f"Invalid URL: {str(e)}")

def validate_url(url: str) -> bool:
    """
    Validate a URL.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if URL is valid
        
    Raises:
        URLValidationError: If URL is invalid
    """
    try:
        cleaned = clean_url(url)
        parsed = urlparse(cleaned)
        
        # Check for supported platforms
        domain = parsed.netloc.lower()
        if not any(platform in domain for platform in ['youtube.com', 'youtu.be', 'mixcloud.com', 'soundcloud.com']):
            raise URLValidationError("Unsupported platform")
            
        return True
    except URLValidationError:
        raise
    except Exception as e:
        raise URLValidationError(f"Invalid URL: {str(e)}")
