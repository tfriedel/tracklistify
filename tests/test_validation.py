"""
Unit tests for URL validation and cleaning.
"""

import pytest
from tracklistify.validation import (
    clean_url, validate_url, URLValidationError,
    validate_and_clean_url, is_valid_url, is_youtube_url
)

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
    
    # Test empty URL
    with pytest.raises(URLValidationError) as exc:
        clean_url("")
    assert "URL cannot be empty" in str(exc.value)
    
    # Test malformed URL
    with pytest.raises(URLValidationError) as exc:
        clean_url("not_a_url")
    assert "Invalid URL format" in str(exc.value)

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
        "https://unsupported.com",
        "https://youtube.com/invalid/path",
        "",  # Empty URL
        None,  # None value
        "https://",  # Incomplete URL
        "http://no-path",  # Missing path
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
        "https://www.youtube.com/watch?v=abc123&feature=share",
        "https://youtu.be/abc123?t=30",
        "https://youtube.com/watch?v=abc123&list=PLxxx"
    ]
    
    expected = "https://www.youtube.com/watch?v=abc123"
    
    for url in variants:
        cleaned = clean_url(url)
        assert cleaned == expected
        assert validate_url(cleaned) is True
        assert is_youtube_url(url) is True

def test_mixcloud_url_variants():
    """Test handling of different Mixcloud URL formats."""
    variants = [
        "https://www.mixcloud.com/artist/mix-name/",
        "https://mixcloud.com/artist/mix-name",
        "http://www.mixcloud.com/artist/mix-name/?utm_source=widget",
        "https://www.mixcloud.com/artist/mix-name/?utm_campaign=share",
        "https://www.mixcloud.com/artist/mix-name/#comments"
    ]
    
    expected = "https://www.mixcloud.com/artist/mix-name"
    
    for url in variants:
        cleaned = clean_url(url)
        assert cleaned == expected
        assert validate_url(cleaned) is True
        assert not is_youtube_url(url)

def test_error_messages():
    """Test error message clarity."""
    with pytest.raises(URLValidationError) as exc:
        validate_url("not_a_url")
    assert "Invalid URL format" in str(exc.value)
    
    with pytest.raises(URLValidationError) as exc:
        validate_url("https://unsupported.com")
    assert "Unsupported platform" in str(exc.value)
    
    with pytest.raises(URLValidationError) as exc:
        validate_url("")
    assert "URL cannot be empty" in str(exc.value)

def test_validate_and_clean_url():
    """Test validate_and_clean_url function."""
    # Valid URLs
    assert validate_and_clean_url("https://www.youtube.com/watch?v=abc123") == "https://www.youtube.com/watch?v=abc123"
    assert validate_and_clean_url("https://youtu.be/abc123") == "https://www.youtube.com/watch?v=abc123"
    assert validate_and_clean_url("https://www.mixcloud.com/artist/mix-name") == "https://www.mixcloud.com/artist/mix-name"
    
    # Invalid URLs
    assert validate_and_clean_url("") is None
    assert validate_and_clean_url("not_a_url") is None
    assert validate_and_clean_url("https://") is None
    assert validate_and_clean_url("ftp://invalid.com") is None

def test_is_valid_url():
    """Test is_valid_url function."""
    # Valid URLs
    assert is_valid_url("https://www.youtube.com/watch?v=abc123") is True
    assert is_valid_url("https://youtu.be/abc123") is True
    assert is_valid_url("https://www.mixcloud.com/artist/mix-name") is True
    
    # Invalid URLs
    assert is_valid_url("") is False
    assert is_valid_url("not_a_url") is False
    assert is_valid_url("https://") is False
    assert is_valid_url("https://unsupported.com") is False

def test_is_youtube_url():
    """Test is_youtube_url function."""
    # Valid YouTube URLs
    assert is_youtube_url("https://www.youtube.com/watch?v=abc123") is True
    assert is_youtube_url("https://youtu.be/abc123") is True
    assert is_youtube_url("https://youtube.com/watch?v=abc123") is True
    
    # Invalid YouTube URLs
    assert is_youtube_url("") is False
    assert is_youtube_url("not_a_url") is False
    assert is_youtube_url("https://www.mixcloud.com/artist/mix-name/") is False
    assert is_youtube_url("https://youtube.com/playlist") is False

def test_validation_edge_cases():
    """Test edge cases in URL validation."""
    # Test exception handling in validate_and_clean_url
    assert validate_and_clean_url(None) is None
    assert validate_and_clean_url("") is None
    assert validate_and_clean_url("invalid://url") is None
    
    # Test exception handling in is_valid_url
    assert not is_valid_url(None)
    assert not is_valid_url("")
    assert not is_valid_url("invalid://url")
    
    # Test exception handling in clean_url
    with pytest.raises(URLValidationError):
        clean_url(None)
    with pytest.raises(URLValidationError):
        clean_url("")
    
    # Test exception handling in validate_url
    with pytest.raises(URLValidationError):
        validate_url(None)
    with pytest.raises(URLValidationError):
        validate_url("")

def test_validation_generic_exceptions():
    """Test handling of generic exceptions in validation functions."""
    # Test invalid URL that raises a generic exception
    with pytest.raises(URLValidationError, match="Invalid URL:"):
        clean_url("http://[invalid]")
    
    # Test validate_url with invalid URL
    with pytest.raises(URLValidationError, match="Invalid URL:"):
        validate_url("http://[invalid]")
    
    # Test is_valid_url with invalid URL
    assert not is_valid_url("http://[invalid]")
    
    # Test validate_and_clean_url with invalid URL
    assert validate_and_clean_url("http://[invalid]") is None

def test_validation_reraise():
    """Test re-raising of URLValidationError."""
    # Test clean_url re-raising URLValidationError for empty URL
    with pytest.raises(URLValidationError, match="URL cannot be empty"):
        clean_url("")
    
    # Test validate_url re-raising URLValidationError for empty URL
    with pytest.raises(URLValidationError, match="URL cannot be empty"):
        validate_url("")
