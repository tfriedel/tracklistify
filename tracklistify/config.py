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

@dataclass
class AppConfig:
    """Application-wide settings."""
    verbose: bool = False
    max_requests_per_minute: int = 60

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
        
        # App configuration
        self.app = self._load_app_config()
    
    def _load_track_config(self) -> TrackConfig:
        """Load track identification configuration."""
        return TrackConfig(
            segment_length=int(os.getenv('SEGMENT_LENGTH', '60')),
            min_confidence=int(os.getenv('MIN_CONFIDENCE', '0')),
            time_threshold=int(os.getenv('TIME_THRESHOLD', '60')),
            max_duplicates=int(os.getenv('MAX_DUPLICATES', '2'))
        )
    
    def _load_acrcloud_config(self) -> ACRCloudConfig:
        """Load ACRCloud API configuration."""
        access_key = os.getenv('ACR_ACCESS_KEY')
        access_secret = os.getenv('ACR_ACCESS_SECRET')
        
        if not access_key or not access_secret:
            raise ConfigError("ACRCloud credentials not found in environment")
        
        return ACRCloudConfig(
            access_key=access_key,
            access_secret=access_secret,
            host=os.getenv('ACR_HOST', 'identify-eu-west-1.acrcloud.com'),
            timeout=int(os.getenv('ACR_TIMEOUT', '10'))
        )
    
    def _load_output_config(self) -> OutputConfig:
        """Load output configuration."""
        format = os.getenv('OUTPUT_FORMAT', 'json').lower()
        if format not in self.VALID_OUTPUT_FORMATS:
            raise ConfigError(f"Invalid output format: {format}")
        
        return OutputConfig(
            format=format,
            directory=os.getenv('OUTPUT_DIR', 'tracklists')
        )
        
    def _load_app_config(self) -> AppConfig:
        """Load application-wide settings."""
        return AppConfig(
            verbose=os.getenv('VERBOSE', 'false').lower() == 'true',
            max_requests_per_minute=int(os.getenv('MAX_REQUESTS_PER_MINUTE', '60'))
        )

# Global configuration instance - lazy loaded
_config_instance = None

def get_config() -> Config:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
