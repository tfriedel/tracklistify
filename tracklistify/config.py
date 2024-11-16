"""
Configuration management for Tracklistify.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass

@dataclass
class ACRCloudConfig:
    """ACRCloud API configuration."""
    access_key: str
    access_secret: str
    host: str
    timeout: int = 10

@dataclass
class TrackConfig:
    """Track identification settings."""
    segment_length: int = 60
    min_confidence: int = 0
    time_threshold: int = 60
    max_duplicates: int = 2

@dataclass
class OutputConfig:
    """Output configuration."""
    format: str = 'json'
    directory: str = 'tracklists'

class Config:
    """Global configuration handler."""
    
    VALID_OUTPUT_FORMATS = ['json', 'text', 'csv']
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        load_dotenv()
        
        # Track configuration first
        self.track = self._load_track_config()
        
        # ACRCloud configuration
        self.acrcloud = self._load_acrcloud_config()
        
        # Output configuration
        self.output = self._load_output_config()
        
        # General settings
        self.verbose = self._get_bool('VERBOSE', False)

    def _load_acrcloud_config(self) -> ACRCloudConfig:
        """Load ACRCloud configuration from environment."""
        access_key = os.getenv('ACR_ACCESS_KEY')
        if not access_key:
            raise ConfigError("Missing required configuration: ACR_ACCESS_KEY")
            
        access_secret = os.getenv('ACR_ACCESS_SECRET')
        if not access_secret:
            raise ConfigError("Missing required configuration: ACR_ACCESS_SECRET")
            
        return ACRCloudConfig(
            access_key=access_key,
            access_secret=access_secret,
            host=os.getenv('ACR_HOST', 'identify-eu-west-1.acrcloud.com'),
            timeout=self._get_int('ACR_TIMEOUT', 10)
        )

    def _load_track_config(self) -> TrackConfig:
        """Load track configuration from environment."""
        try:
            segment_length = self._get_int('SEGMENT_LENGTH', 60)
            if segment_length <= 0:
                raise ValueError("Segment length must be positive")
        except ValueError as e:
            raise ConfigError(f"Invalid segment length: {str(e)}")
            
        return TrackConfig(
            segment_length=segment_length,
            min_confidence=self._get_int('MIN_CONFIDENCE', 0),
            time_threshold=self._get_int('TIME_THRESHOLD', 60),
            max_duplicates=self._get_int('MAX_DUPLICATES', 2)
        )

    def _load_output_config(self) -> OutputConfig:
        """Load output configuration from environment."""
        format = os.getenv('OUTPUT_FORMAT', 'json').lower()
        if format not in self.VALID_OUTPUT_FORMATS:
            raise ConfigError(f"Invalid output format. Must be one of: {', '.join(self.VALID_OUTPUT_FORMATS)}")
            
        return OutputConfig(
            format=format,
            directory=os.getenv('OUTPUT_DIR', 'tracklists')
        )

    def _get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean value from environment variable."""
        return os.getenv(key, str(default)).lower() == 'true'

    def _get_int(self, key: str, default: int) -> int:
        """Get integer value from environment variable."""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            raise ConfigError(f"Invalid value for {key}: must be an integer")

# Global configuration instance - lazy loaded
_config_instance = None

def get_config() -> Config:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
