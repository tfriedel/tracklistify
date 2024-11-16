"""
Unit tests for configuration handling.
"""

import os
from pathlib import Path

import pytest
from tracklistify.config import Config, ConfigError

def test_config_loading(test_env):
    """Test configuration loading from environment."""
    config = Config()
    
    assert config.acrcloud.access_key == "test_access_key"
    assert config.acrcloud.access_secret == "test_access_secret"
    assert config.acrcloud.host == "test.acrcloud.com"
    assert config.track.segment_length == 60
    assert config.output.format == "json"
    assert config.verbose is True

def test_config_validation():
    """Test configuration validation."""
    # Test missing required values
    with pytest.raises(ConfigError) as exc:
        with pytest.MonkeyPatch().context() as mp:
            mp.delenv("ACR_ACCESS_KEY", raising=False)
            Config()
    assert "Missing required configuration" in str(exc.value)
    
    # Test invalid segment length
    with pytest.raises(ConfigError) as exc:
        with pytest.MonkeyPatch().context() as mp:
            mp.setenv("SEGMENT_LENGTH", "invalid")
            Config()
    assert "Invalid segment length" in str(exc.value)
    
    # Test invalid format
    with pytest.raises(ConfigError) as exc:
        with pytest.MonkeyPatch().context() as mp:
            mp.setenv("OUTPUT_FORMAT", "invalid")
            Config()
    assert "Invalid output format" in str(exc.value)

def test_config_defaults():
    """Test default configuration values."""
    with pytest.MonkeyPatch().context() as mp:
        # Set only required values
        mp.setenv("ACR_ACCESS_KEY", "test_key")
        mp.setenv("ACR_ACCESS_SECRET", "test_secret")
        mp.setenv("ACR_HOST", "test.host")
        
        config = Config()
        
        # Check defaults
        assert config.track.segment_length == 60  # Default segment length
        assert config.output.format == "json"  # Default output format
        assert config.verbose is False  # Default verbosity
        assert config.track.min_confidence == 0  # Default confidence threshold

def test_config_types():
    """Test configuration value type conversion."""
    with pytest.MonkeyPatch().context() as mp:
        mp.setenv("ACR_ACCESS_KEY", "test_key")
        mp.setenv("ACR_ACCESS_SECRET", "test_secret")
        mp.setenv("ACR_HOST", "test.host")
        mp.setenv("SEGMENT_LENGTH", "120")
        mp.setenv("VERBOSE", "true")
        
        config = Config()
        
        assert isinstance(config.track.segment_length, int)
        assert isinstance(config.verbose, bool)
        assert isinstance(config.acrcloud.timeout, int)
