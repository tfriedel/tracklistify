"""
Configuration management for Tracklistify.
"""

import os
from dataclasses import dataclass, field
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
class TimingConfig:
    """Track timing settings."""
    min_gap_threshold: float = 1.0  # Minimum gap duration to report (seconds)
    max_gap_threshold: float = 30.0  # Maximum acceptable gap duration (seconds)
    min_overlap_threshold: float = 0.5  # Minimum overlap duration to report (seconds)
    max_overlap_threshold: float = 10.0  # Maximum acceptable overlap duration (seconds)
    timing_confidence_threshold: float = 0.7  # Minimum confidence for timing information
    segment_overlap: float = 0.5  # Overlap between analysis segments (ratio)
    timing_merge_threshold: float = 2.0  # Maximum time difference to merge duplicate tracks (seconds)

@dataclass
class TrackConfig:
    """Track identification settings."""
    segment_length: int = 60
    min_confidence: int = 0
    time_threshold: int = 60
    max_duplicates: int = 2
    # Timing settings
    timing: TimingConfig = field(default_factory=TimingConfig)

@dataclass
class OutputConfig:
    """Output configuration."""
    format: str = 'json'
    directory: str = 'tracklists'
    include_timing_details: bool = True  # Whether to include detailed timing info in output
    warn_on_gaps: bool = True  # Whether to show warnings for gaps
    warn_on_overlaps: bool = True  # Whether to show warnings for overlaps

@dataclass
class AppConfig:
    """Application-wide settings."""
    verbose: bool = False
    max_requests_per_minute: int = 60
    rate_limit_enabled: bool = True

@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    directory: str = '.cache'
    duration: int = 86400  # 24 hours in seconds

class Config:
    """Global configuration handler."""
    
    VALID_OUTPUT_FORMATS = ['json', 'markdown', 'm3u']
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        dotenv_path = os.getenv("DOTENV_PATH", ".env")
        load_dotenv(dotenv_path=dotenv_path)
        
        # Track configuration first
        self.track = self._load_track_config()
        
        # Validate track configuration
        if not self.track.segment_length or self.track.segment_length <= 0:
            raise ConfigError("Invalid segment length configuration.")
        
        # ACRCloud configuration
        self.acrcloud = self._load_acrcloud_config()
        
        # Validate ACRCloud configuration
        if not self.acrcloud.access_key or not self.acrcloud.access_secret or not self.acrcloud.host:
            raise ConfigError("ACRCloud credentials not found in environment")
        
        # Output configuration
        self.output = self._load_output_config()
        
        # Validate output configuration
        if self.output.format not in self.VALID_OUTPUT_FORMATS:
            raise ConfigError("Invalid output format.")
        
        # App configuration
        self.app = self._load_app_config()
        
        # Cache configuration
        self.cache = self._load_cache_config()
    
    def _load_track_config(self) -> TrackConfig:
        """Load track identification configuration."""
        timing_config = TimingConfig(
            min_gap_threshold=float(os.getenv('MIN_GAP_THRESHOLD', '1.0')),
            max_gap_threshold=float(os.getenv('MAX_GAP_THRESHOLD', '30.0')),
            min_overlap_threshold=float(os.getenv('MIN_OVERLAP_THRESHOLD', '0.5')),
            max_overlap_threshold=float(os.getenv('MAX_OVERLAP_THRESHOLD', '10.0')),
            timing_confidence_threshold=float(os.getenv('TIMING_CONFIDENCE_THRESHOLD', '0.7')),
            segment_overlap=float(os.getenv('SEGMENT_OVERLAP', '0.5')),
            timing_merge_threshold=float(os.getenv('TIMING_MERGE_THRESHOLD', '2.0'))
        )
        
        return TrackConfig(
            segment_length=int(os.getenv('SEGMENT_LENGTH', '60')),
            min_confidence=int(os.getenv('MIN_CONFIDENCE', '0')),
            time_threshold=int(os.getenv('TIME_THRESHOLD', '60')),
            max_duplicates=int(os.getenv('MAX_DUPLICATES', '2')),
            timing=timing_config
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
            directory=os.getenv('OUTPUT_DIR', 'tracklists'),
            include_timing_details=os.getenv('INCLUDE_TIMING_DETAILS', 'true').lower() == 'true',
            warn_on_gaps=os.getenv('WARN_ON_GAPS', 'true').lower() == 'true',
            warn_on_overlaps=os.getenv('WARN_ON_OVERLAPS', 'true').lower() == 'true'
        )
    
    def _load_app_config(self) -> AppConfig:
        """Load application configuration."""
        return AppConfig(
            verbose=os.getenv('VERBOSE', 'false').lower() == 'true',
            max_requests_per_minute=int(os.getenv('MAX_REQUESTS_PER_MINUTE', '60')),
            rate_limit_enabled=os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
        )
    
    def _load_cache_config(self) -> CacheConfig:
        """Load cache configuration."""
        return CacheConfig(
            enabled=os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
            directory=os.getenv('CACHE_DIR', '.cache'),
            duration=int(os.getenv('CACHE_DURATION', '86400'))
        )

# Global configuration instance - lazy loaded
_config_instance = None

def get_config() -> Config:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
