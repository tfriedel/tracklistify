"""
Configuration management for Tracklistify.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

@dataclass
class ACRCloudConfig:
    """ACRCloud API configuration."""
    access_key: str
    access_secret: str
    host: str
    timeout: int = 10

@dataclass
class TrackIdentificationConfig:
    """Track identification settings."""
    min_confidence: int = 70
    time_threshold: int = 60
    min_track_length: int = 30
    max_duplicates: int = 2
    segment_length: int = 30

@dataclass
class AppConfig:
    """Application configuration."""
    verbose: bool = False
    output_format: str = 'json'
    cache_enabled: bool = True
    cache_duration: int = 86400  # 24 hours

class Config:
    """Global configuration handler."""
    
    def __init__(self):
        self.load_environment()
        self.acrcloud = self._load_acrcloud_config()
        self.track = self._load_track_config()
        self.app = self._load_app_config()

    def load_environment(self):
        """Load environment variables from .env file."""
        load_dotenv()

    def _load_acrcloud_config(self) -> ACRCloudConfig:
        """Load ACRCloud configuration from environment."""
        return ACRCloudConfig(
            access_key=os.getenv('ACRCLOUD_ACCESS_KEY', ''),
            access_secret=os.getenv('ACRCLOUD_ACCESS_SECRET', ''),
            host=os.getenv('ACRCLOUD_HOST', 'identify-eu-west-1.acrcloud.com'),
            timeout=int(os.getenv('ACRCLOUD_TIMEOUT', '10'))
        )

    def _load_track_config(self) -> TrackIdentificationConfig:
        """Load track identification configuration from environment."""
        return TrackIdentificationConfig(
            min_confidence=int(os.getenv('MIN_CONFIDENCE', '70')),
            time_threshold=int(os.getenv('TIME_THRESHOLD', '60')),
            min_track_length=int(os.getenv('MIN_TRACK_LENGTH', '30')),
            max_duplicates=int(os.getenv('MAX_DUPLICATES', '2')),
            segment_length=int(os.getenv('SEGMENT_LENGTH', '30'))
        )

    def _load_app_config(self) -> AppConfig:
        """Load application configuration from environment."""
        return AppConfig(
            verbose=os.getenv('VERBOSE', 'false').lower() == 'true',
            output_format=os.getenv('OUTPUT_FORMAT', 'json'),
            cache_enabled=os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
            cache_duration=int(os.getenv('CACHE_DURATION', '86400'))
        )

# Global configuration instance
config = Config()
