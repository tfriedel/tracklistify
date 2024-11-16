"""
Unit tests for URL validation and cleaning.
"""

import pytest
from tracklistify.validation import clean_url, validate_url, URLValidationError

def test_clean_url():
    """Test URL cleaning functionality."""
    # Test basic URL cleaning
    url = "https://www.youtube.com/watch?v=abc123\\&feature=share"
    cleaned = clean_url(url)
    assert cleaned == "https://www.youtube.com/watch?v=abc123"
    
    # Test URL encoding
    url = "https://www.youtube.com/watch?v=abc%20123"
    cleaned = clean_url(url)
    assert cleaned == "https://www.youtube.com/watch?v=abc 123"
    
    # Test query parameter cleaning
    url = "https://www.youtube.com/watch?v=abc123&t=30s&feature=youtu.be"
    cleaned = clean_url(url)
    assert cleaned == "https://www.youtube.com/watch?v=abc123"

def test_validate_url():
    """Test URL validation."""
    # Valid URLs
    valid_urls = [
        "https://www.youtube.com/watch?v=abc123",
        "https://youtu.be/abc123",
        "https://www.mixcloud.com/artist/mix-name/",
        "http://www.soundcloud.com/artist/track-name"
    ]
    
    for url in valid_urls:
        assert validate_url(url) is True
    
    # Invalid URLs
    invalid_urls = [
        "not_a_url",
        "ftp://invalid.com",
        "https://unsupported.com",
        "https://youtube.com/invalid/path"
    ]
    
    for url in invalid_urls:
        with pytest.raises(URLValidationError):
            validate_url(url)

def test_youtube_url_variants():
    """Test handling of different YouTube URL formats."""
    variants = [
        "https://www.youtube.com/watch?v=abc123",
        "https://youtu.be/abc123",
        "https://youtube.com/watch?v=abc123",
        "https://www.youtube.com/watch?v=abc123&t=30s",
        "https://www.youtube.com/watch?v=abc123&feature=share"
    ]
    
    expected = "https://www.youtube.com/watch?v=abc123"
    
    for url in variants:
        cleaned = clean_url(url)
        assert cleaned == expected
        assert validate_url(cleaned) is True

def test_mixcloud_url_variants():
    """Test handling of different Mixcloud URL formats."""
    variants = [
        "https://www.mixcloud.com/artist/mix-name/",
        "https://mixcloud.com/artist/mix-name",
        "http://www.mixcloud.com/artist/mix-name/?utm_source=widget"
    ]
    
    expected = "https://www.mixcloud.com/artist/mix-name"
    
    for url in variants:
        cleaned = clean_url(url)
        assert cleaned.startswith("https://") and cleaned.endswith("/mix-name")
        assert validate_url(cleaned) is True

def test_error_messages():
    """Test error message clarity."""
    with pytest.raises(URLValidationError) as exc:
        validate_url("not_a_url")
    assert "Invalid URL format" in str(exc.value)
    
    with pytest.raises(URLValidationError) as exc:
        validate_url("https://unsupported.com")
    assert "Unsupported platform" in str(exc.value)
