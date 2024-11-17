"""
Unit tests for cache functionality.
"""

import json
from pathlib import Path
import pytest
from tracklistify.cache import Cache, CacheEntry
from tracklistify.track import Track, TrackTiming
import os
from unittest.mock import MagicMock, patch

@pytest.fixture
def cache_dir(tmp_path):
    """Create a temporary cache directory."""
    cache_path = tmp_path / "test_cache"
    cache_path.mkdir()
    return cache_path

@pytest.fixture
def test_track():
    """Create a test track."""
    track = Track(
        song_name="Test Song",
        artist="Test Artist",
        time_in_mix="00:00:00",
        confidence=90.0
    )
    track.timing = TrackTiming(start_time=0, end_time=180, confidence=90.0)
    return track

def test_cache_initialization(cache_dir):
    """Test cache initialization."""
    cache = Cache(cache_dir)
    assert cache.cache_dir == cache_dir
    assert cache.cache_dir.exists()

def test_cache_key_generation(cache_dir, test_track):
    """Test cache key generation."""
    cache = Cache(cache_dir)
    url = "https://example.com/test"
    key = cache._generate_key(url)
    assert isinstance(key, str)
    assert len(key) > 0

def test_cache_save_and_load(cache_dir, test_track):
    """Test saving and loading from cache."""
    cache = Cache(cache_dir)
    url = "https://example.com/test"
    
    # Save to cache
    cache.save(url, test_track)
    assert (cache_dir / f"{cache._generate_key(url)}.json").exists()
    
    # Load from cache
    loaded_track = cache.load(url)
    assert loaded_track is not None
    assert loaded_track.song_name == test_track.song_name
    assert loaded_track.artist == test_track.artist

def test_cache_exists(cache_dir, test_track):
    """Test cache existence check."""
    cache = Cache(cache_dir)
    url = "https://example.com/test"
    
    # Save to cache
    cache.save(url, test_track)
    assert cache.load(url) is not None

def test_cache_clear(cache_dir, test_track):
    """Test cache clearing."""
    cache = Cache(cache_dir)
    url = "https://example.com/test"
    
    # Save some data
    cache.save(url, test_track)
    assert cache.load(url) is not None
    
    # Clear cache
    for file in cache_dir.glob("*.json"):
        file.unlink()
    assert cache.load(url) is None

def test_cache_invalid_data(cache_dir):
    """Test cache behavior with invalid data."""
    cache = Cache(cache_dir)
    url = "https://example.com/test"
    
    with pytest.raises(AttributeError):
        cache.save(url, None)

def test_cache_file_permissions(cache_dir, test_track):
    """Test cache file permissions."""
    cache = Cache(cache_dir)
    url = "https://example.com/test"
    cache.save(url, test_track)
    
    cache_file = cache_dir / f"{cache._generate_key(url)}.json"
    assert cache_file.exists()
    assert os.access(cache_file, os.R_OK)
    assert os.access(cache_file, os.W_OK)

def test_cache_concurrent_access(cache_dir, test_track):
    """Test concurrent cache access."""
    cache1 = Cache(cache_dir)
    cache2 = Cache(cache_dir)
    url = "https://example.com/test"
    
    # Both instances should work with the same cache directory
    cache1.save(url, test_track)
    loaded_track = cache2.load(url)
    assert loaded_track is not None
    assert loaded_track.song_name == test_track.song_name

def test_cache_expiration(cache_dir, test_track, mocker):
    """Test cache expiration."""
    cache = Cache(cache_dir)
    url = "https://example.com/test"
    
    # Mock time.time() to simulate cache entry creation
    current_time = 1000000
    mocker.patch('time.time', return_value=current_time)
    
    # Save to cache
    cache.save(url, test_track)
    
    # Mock time.time() to simulate future access (31 days later)
    future_time = current_time + (31 * 24 * 60 * 60)
    mocker.patch('time.time', return_value=future_time)
    
    # Load from cache - should return None as cache is expired
    loaded_track = cache.load(url)
    assert loaded_track is None
    
    # Cache file should be deleted
    assert not (cache_dir / f"{cache._generate_key(url)}.json").exists()

def test_cache_file_operation_errors(cache_dir, test_track, mocker):
    """Test error handling for file operations."""
    cache = Cache(cache_dir)
    url = "https://example.com/test"
    
    # Test save error
    mocker.patch('builtins.open', side_effect=OSError("Mock write error"))
    cache.save(url, test_track)  # Should log warning but not raise
    
    # Test load error
    cache_file = cache_dir / f"{cache._generate_key(url)}.json"
    cache_file.touch()
    mocker.patch('builtins.open', side_effect=OSError("Mock read error"))
    loaded_track = cache.load(url)  # Should return None
    assert loaded_track is None

def test_cache_clear_errors(cache_dir, test_track, mocker):
    """Test error handling during cache clearing."""
    cache = Cache(cache_dir)
    url = "https://example.com/test"
    
    # Save a file to cache
    cache.save(url, test_track)
    
    # Mock Path.unlink to simulate error
    mocker.patch('pathlib.Path.unlink', side_effect=OSError("Mock delete error"))
    
    # Should log warning but not raise
    cache.clear()

def test_global_cache_instance(mocker):
    """Test global cache instance."""
    from tracklistify.cache import get_cache
    
    # Reset global instance
    import tracklistify.cache
    tracklistify.cache._cache_instance = None
    
    # First call should create instance
    cache1 = get_cache()
    assert cache1 is not None
    
    # Second call should return same instance
    cache2 = get_cache()
    assert cache2 is cache1
    
    # Should be the global instance
    assert cache1 is tracklistify.cache._cache_instance

def test_cache_json_decode_error(cache_dir):
    """Test handling of invalid JSON in cache file."""
    cache = Cache(cache_dir)
    url = "https://example.com/test"
    
    # Create invalid cache file
    cache_file = cache_dir / f"{cache._generate_key(url)}.json"
    cache_file.write_text("invalid json content")
    
    # Should return None for invalid JSON
    loaded_track = cache.load(url)
    assert loaded_track is None

def test_cache_initialization_error(tmp_path):
    """Test cache initialization with invalid directory."""
    # Create a file that will conflict with cache directory creation
    conflict_path = tmp_path / "conflict_cache"
    conflict_path.write_text("")  # Create as file instead of directory
    
    with pytest.raises(FileExistsError):
        Cache(str(conflict_path))  # Should raise when trying to mkdir

def test_cache_entry_serialization(test_track):
    """Test CacheEntry serialization and deserialization."""
    # Create cache entry
    entry = CacheEntry(test_track, timestamp=1000.0)
    
    # Test to_dict
    entry_dict = entry.to_dict()
    assert isinstance(entry_dict, dict)
    assert 'track' in entry_dict
    assert 'timestamp' in entry_dict
    assert entry_dict['timestamp'] == 1000.0
    
    # Test to_json and from_json
    json_str = entry.to_json()
    assert isinstance(json_str, str)
    
    # Deserialize
    loaded_entry = CacheEntry.from_json(json_str)
    assert isinstance(loaded_entry, CacheEntry)
    assert loaded_entry.timestamp == entry.timestamp
    assert loaded_entry.track.song_name == entry.track.song_name
    assert loaded_entry.track.artist == entry.track.artist

def test_cache_directory_permissions(tmp_path):
    """Test cache directory creation with different permissions."""
    cache_dir = tmp_path / "perm_test_cache"
    
    # Test with read-only parent directory
    cache_dir.parent.chmod(0o555)  # Read + execute only
    try:
        with pytest.raises(PermissionError):
            Cache(str(cache_dir / "readonly"))
    finally:
        # Restore permissions to allow cleanup
        cache_dir.parent.chmod(0o755)
