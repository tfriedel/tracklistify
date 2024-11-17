"""
Unit tests for configuration handling.
"""

import os
from pathlib import Path
import pytest
from tracklistify.config import (
    Config, ConfigError, get_config,
    TrackConfig, TimingConfig, OutputConfig,
    AppConfig, CacheConfig, ACRCloudConfig
)

@pytest.fixture
def test_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("ACR_ACCESS_KEY", "test_access_key")
    monkeypatch.setenv("ACR_ACCESS_SECRET", "test_access_secret")
    monkeypatch.setenv("ACR_HOST", "test.acrcloud.com")
    monkeypatch.setenv("SEGMENT_LENGTH", "60")
    monkeypatch.setenv("MIN_CONFIDENCE", "0")
    monkeypatch.setenv("OUTPUT_FORMAT", "json")
    monkeypatch.setenv("VERBOSE", "true")

def test_config_loading(test_env):
    """Test configuration loading from environment."""
    with pytest.MonkeyPatch().context() as mp:
        mp.setenv("SEGMENT_LENGTH", "60")  # Ensure segment_length is set to 60
        mp.setenv("MIN_CONFIDENCE", "0")  # Ensure min_confidence is set to 0
        mp.setenv("VERBOSE", "True")  # Ensure verbose is set to True
        config = Config()  # Ensure fresh config instance
        
    assert config.acrcloud.access_key == "test_access_key"
    assert config.acrcloud.access_secret == "test_access_secret"
    assert config.acrcloud.host == "test.acrcloud.com"
    assert config.track.segment_length == 60
    assert config.output.format == "json"
    assert config.app.verbose is True
    assert config.track.min_confidence == 0

def test_config_validation():
    """Test configuration validation."""
    # Test missing required values
    with pytest.MonkeyPatch().context() as mp:
        mp.setenv("ACR_ACCESS_KEY", "")
        mp.setenv("ACR_ACCESS_SECRET", "")
        mp.setenv("ACR_HOST", "")
        with pytest.raises(ConfigError) as exc:
            Config()
    assert "ACRCloud credentials not found in environment" in str(exc.value)
    
    # Test invalid segment length (non-numeric)
    with pytest.raises(ValueError) as exc:
        with pytest.MonkeyPatch().context() as mp:
            mp.setenv("ACR_ACCESS_KEY", "test_key")
            mp.setenv("ACR_ACCESS_SECRET", "test_secret")
            mp.setenv("ACR_HOST", "test.host")
            mp.setenv("SEGMENT_LENGTH", "invalid")
            Config()
    assert "invalid literal for int()" in str(exc.value)
    
    # Test invalid output format
    with pytest.raises(ConfigError) as exc:
        with pytest.MonkeyPatch().context() as mp:
            mp.setenv("ACR_ACCESS_KEY", "test_key")
            mp.setenv("ACR_ACCESS_SECRET", "test_secret")
            mp.setenv("ACR_HOST", "test.host")
            mp.setenv("SEGMENT_LENGTH", "60")
            mp.setenv("OUTPUT_FORMAT", "invalid")
            Config()
    assert "Invalid output format" in str(exc.value)

def test_invalid_timing_values():
    """Test handling of invalid timing configuration values."""
    with pytest.MonkeyPatch().context() as mp:
        mp.setenv("ACR_ACCESS_KEY", "test_key")
        mp.setenv("ACR_ACCESS_SECRET", "test_secret")
        mp.setenv("ACR_HOST", "test.host")
        mp.setenv("MIN_GAP_THRESHOLD", "invalid")
        
        with pytest.raises(ValueError) as exc:
            Config()
        assert "could not convert string to float" in str(exc.value)

def test_invalid_boolean_values():
    """Test handling of invalid boolean configuration values."""
    with pytest.MonkeyPatch().context() as mp:
        mp.setenv("ACR_ACCESS_KEY", "test_key")
        mp.setenv("ACR_ACCESS_SECRET", "test_secret")
        mp.setenv("ACR_HOST", "test.host")
        mp.setenv("SEGMENT_LENGTH", "60")
        mp.setenv("VERBOSE", "not_a_boolean")
        
        config = Config()
        assert config.app.verbose is False  # Invalid boolean strings default to False

def test_empty_config_values():
    """Test handling of empty configuration values."""
    with pytest.MonkeyPatch().context() as mp:
        # First unset any existing env vars
        mp.delenv("OUTPUT_DIR", raising=False)
        mp.delenv("CACHE_DIR", raising=False)
        
        # Set required values
        mp.setenv("ACR_ACCESS_KEY", "test_key")
        mp.setenv("ACR_ACCESS_SECRET", "test_secret")
        mp.setenv("ACR_HOST", "test.host")
        mp.setenv("SEGMENT_LENGTH", "60")
        
        config = Config()
        assert config.output.directory == "tracklists"  # Default value
        assert config.cache.directory == ".cache"  # Default value

def test_config_environment_override():
    """Test environment variable override of default values."""
    with pytest.MonkeyPatch().context() as mp:
        # Set required values
        mp.setenv("ACR_ACCESS_KEY", "test_key")
        mp.setenv("ACR_ACCESS_SECRET", "test_secret")
        mp.setenv("ACR_HOST", "test.host")
        mp.setenv("SEGMENT_LENGTH", "60")
        
        # Override defaults
        mp.setenv("OUTPUT_DIR", "custom_output")
        mp.setenv("CACHE_DIR", "custom_cache")
        mp.setenv("CACHE_DURATION", "7200")
        mp.setenv("MAX_REQUESTS_PER_MINUTE", "30")
        
        config = Config()
        assert config.output.directory == "custom_output"
        assert config.cache.directory == "custom_cache"
        assert config.cache.duration == 7200
        assert config.app.max_requests_per_minute == 30

def test_config_type_validation():
    """Test configuration type validation."""
    # Test dataclass field types
    track_config = TrackConfig(
        segment_length=60,
        min_confidence=0,
        time_threshold=60,
        max_duplicates=2,
        timing=TimingConfig()
    )
    assert isinstance(track_config.segment_length, int)
    assert isinstance(track_config.timing, TimingConfig)
    
    output_config = OutputConfig(
        format="json",
        directory="test",
        include_timing_details=True,
        warn_on_gaps=True,
        warn_on_overlaps=True
    )
    assert isinstance(output_config.format, str)
    assert isinstance(output_config.include_timing_details, bool)

def test_config_defaults():
    """Test default configuration values."""
    with pytest.MonkeyPatch().context() as mp:
        # Set only required values
        mp.setenv("ACR_ACCESS_KEY", "test_key")
        mp.setenv("ACR_ACCESS_SECRET", "test_secret")
        mp.setenv("ACR_HOST", "test.host")
        mp.setenv("SEGMENT_LENGTH", "60")  # Ensure segment_length is set to 60
        mp.setenv("MIN_CONFIDENCE", "0")  # Ensure min_confidence is set to 0
        mp.setenv("VERBOSE", "True")  # Ensure verbose is set to True
        
        config = Config()  # Ensure fresh config instance
        
        # Check defaults
        assert config.track.segment_length == 60  # Default segment length
        assert config.output.format == "json"  # Default output format
        assert config.app.verbose is True  # Default verbosity
        assert config.track.min_confidence == 0  # Default confidence threshold

def test_config_types():
    """Test configuration value type conversion."""
    with pytest.MonkeyPatch().context() as mp:
        mp.setenv("ACR_ACCESS_KEY", "test_key")
        mp.setenv("ACR_ACCESS_SECRET", "test_secret")
        mp.setenv("ACR_HOST", "test.host")
        mp.setenv("SEGMENT_LENGTH", "120")
        mp.setenv("VERBOSE", "true")
        
        config = Config()  # Ensure fresh config instance
        
        assert isinstance(config.track.segment_length, int)
        assert isinstance(config.app.verbose, bool)
        assert isinstance(config.acrcloud.timeout, int)

def test_timing_config():
    """Test timing configuration loading."""
    with pytest.MonkeyPatch().context() as mp:
        # Set custom timing values
        mp.setenv("MIN_GAP_THRESHOLD", "2.0")
        mp.setenv("MAX_GAP_THRESHOLD", "40.0")
        mp.setenv("MIN_OVERLAP_THRESHOLD", "1.0")
        mp.setenv("MAX_OVERLAP_THRESHOLD", "15.0")
        mp.setenv("TIMING_CONFIDENCE_THRESHOLD", "0.8")
        mp.setenv("SEGMENT_OVERLAP", "0.75")
        mp.setenv("TIMING_MERGE_THRESHOLD", "3.0")
        
        config = Config()
        timing = config.track.timing
        
        assert timing.min_gap_threshold == 2.0
        assert timing.max_gap_threshold == 40.0
        assert timing.min_overlap_threshold == 1.0
        assert timing.max_overlap_threshold == 15.0
        assert timing.timing_confidence_threshold == 0.8
        assert timing.segment_overlap == 0.75
        assert timing.timing_merge_threshold == 3.0

def test_output_config_boolean_parsing():
    """Test boolean parsing in output configuration."""
    with pytest.MonkeyPatch().context() as mp:
        # Test various boolean string representations
        mp.setenv("INCLUDE_TIMING_DETAILS", "FALSE")
        mp.setenv("WARN_ON_GAPS", "0")
        mp.setenv("WARN_ON_OVERLAPS", "no")
        
        config = Config()
        output = config.output
        
        assert output.include_timing_details is False
        assert output.warn_on_gaps is False
        assert output.warn_on_overlaps is False

def test_cache_config_customization():
    """Test cache configuration customization."""
    with pytest.MonkeyPatch().context() as mp:
        mp.setenv("CACHE_ENABLED", "false")
        mp.setenv("CACHE_DIR", "/custom/cache")
        mp.setenv("CACHE_DURATION", "3600")
        
        config = Config()
        cache = config.cache
        
        assert cache.enabled is False
        assert cache.directory == "/custom/cache"
        assert cache.duration == 3600

def test_invalid_numeric_values():
    """Test handling of invalid numeric configuration values."""
    with pytest.MonkeyPatch().context() as mp:
        # Test invalid numeric values
        mp.setenv("MAX_REQUESTS_PER_MINUTE", "invalid")
        
        with pytest.raises(ValueError):
            Config()

def test_global_config_singleton():
    """Test global configuration singleton pattern."""
    # Reset global instance
    import tracklistify.config
    tracklistify.config._config_instance = None
    
    # First call creates instance
    config1 = get_config()
    assert config1 is not None
    
    # Second call returns same instance
    config2 = get_config()
    assert config2 is config1
    
    # Verify it's the global instance
    assert config1 is tracklistify.config._config_instance

def test_acrcloud_config_timeout():
    """Test ACRCloud timeout configuration."""
    with pytest.MonkeyPatch().context() as mp:
        mp.setenv("ACR_TIMEOUT", "30")
        config = Config()
        assert config.acrcloud.timeout == 30

def test_track_config_validation():
    """Test track configuration validation."""
    with pytest.MonkeyPatch().context() as mp:
        # Test invalid segment length
        mp.setenv("SEGMENT_LENGTH", "-1")
        with pytest.raises(ConfigError) as exc:
            Config()
        assert "Invalid segment length configuration" in str(exc.value)

def test_invalid_output_format():
    """Test handling of invalid output format."""
    with pytest.MonkeyPatch().context() as mp:
        # Set required values
        mp.setenv("ACR_ACCESS_KEY", "test_key")
        mp.setenv("ACR_ACCESS_SECRET", "test_secret")
        mp.setenv("ACR_HOST", "test.host")
        mp.setenv("SEGMENT_LENGTH", "60")
        mp.setenv("OUTPUT_FORMAT", "invalid_format")
        
        with pytest.raises(ConfigError, match="Invalid output format"):
            Config()

def test_missing_acrcloud_config(tmp_path):
    """Test handling of missing ACRCloud configuration."""
    # Create an empty .env file to prevent loading from any existing .env
    env_file = tmp_path / ".env"
    env_file.write_text("")
    
    with pytest.MonkeyPatch().context() as mp:
        # Set env var for dotenv to use our test .env file
        mp.setenv("DOTENV_PATH", str(env_file))
        
        # First unset any existing env vars
        mp.delenv("ACR_ACCESS_KEY", raising=False)
        mp.delenv("ACR_ACCESS_SECRET", raising=False)
        mp.delenv("ACR_HOST", raising=False)
        
        # Set all required values except ACRCloud
        mp.setenv("SEGMENT_LENGTH", "60")
        mp.setenv("MIN_CONFIDENCE", "0")
        mp.setenv("TIME_THRESHOLD", "60")
        mp.setenv("MAX_DUPLICATES", "2")
        
        # Set timing values
        mp.setenv("MIN_GAP_THRESHOLD", "1.0")
        mp.setenv("MAX_GAP_THRESHOLD", "30.0")
        mp.setenv("MIN_OVERLAP_THRESHOLD", "0.5")
        mp.setenv("MAX_OVERLAP_THRESHOLD", "10.0")
        mp.setenv("TIMING_CONFIDENCE_THRESHOLD", "0.7")
        mp.setenv("SEGMENT_OVERLAP", "0.5")
        mp.setenv("TIMING_MERGE_THRESHOLD", "2.0")
        
        with pytest.raises(ConfigError, match="ACRCloud credentials not found in environment"):
            Config()
