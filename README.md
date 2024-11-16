# Tracklistify

Unleash the power of Tracklistify! Create playlists from Livesets, DJ Mixes and Podcasts by identifying tracks using advanced audio recognition. Whether you're analyzing local MP3 files or streaming from YouTube or Mixcloud, Tracklistify provides precise timestamps, detailed track info, and confidence scores. Perfect for DJs, music enthusiasts, and content creators.

Get started today and elevate your music experience!

## Features

- 🎵 Accurate track identification in DJ mixes
- 🌐 Support for online streaming platforms:
  - YouTube
  - Mixcloud
  - Expandable to other platforms
- ⏱️ Precise timestamp tracking for each identified song
- 📊 Confidence scores for each match
- 🎼 Detailed track information (artists, albums, labels, genres)
- 📝 JSON export of results
- 🔄 Smart duplicate detection and merging
- 🎚️ Configurable analysis parameters
- 💨 High-performance processing:
  - Intelligent caching system
  - Rate limiting protection
  - Memory-efficient chunk processing
  - Configurable optimization settings

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tracklistify.git
cd tracklistify
```

2. Install FFmpeg (if not already installed):
```bash
# macOS with Homebrew
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg
```

3. Install the package:
```bash
pip install -e .
```

4. Copy the example environment file and configure your settings:
```bash
cp .env.example .env
```

Edit `.env` with your ACRCloud credentials and desired settings.

## Usage

### Basic Usage

Process a local audio file:
```bash
tracklistify path/to/audio.mp3
```

Analyze a YouTube video:
```bash
tracklistify https://youtube.com/watch?v=example
```

### Options

- `-s, --segment-length`: Length of analysis segments in seconds (default: 30)
- `-v, --verbose`: Enable verbose output

## Configuration

The application uses environment variables for configuration. Create a `.env` file in the project root:

```env
# ACRCloud API Credentials
ACR_ACCESS_KEY=your_access_key
ACR_ACCESS_SECRET=your_access_secret
ACR_HOST=your_host
ACR_TIMEOUT=10

# Track Identification Settings
SEGMENT_LENGTH=30
MIN_CONFIDENCE=70
TIME_THRESHOLD=60
MAX_DUPLICATES=2

# Output Settings
OUTPUT_FORMAT=json
OUTPUT_DIR=tracklists

# Application Settings
VERBOSE=false
MAX_REQUESTS_PER_MINUTE=60
RATE_LIMIT_ENABLED=true

# Cache Settings
CACHE_ENABLED=true
CACHE_DIR=.cache
CACHE_DURATION=86400  # 24 hours in seconds
```

### Configuration Parameters

#### Track Identification
- `SEGMENT_LENGTH`: Length of each analysis segment in seconds (default: 30)
  - Shorter segments (30-60s) provide more accurate track timing
  - Longer segments (120s+) reduce API calls but may miss short tracks
- `MIN_CONFIDENCE`: Minimum confidence score for track matches (default: 70)
- `TIME_THRESHOLD`: Time threshold for merging similar tracks (default: 60)
- `MAX_DUPLICATES`: Maximum allowed duplicate tracks (default: 2)

#### Performance Optimization
- `CACHE_ENABLED`: Enable/disable response caching (default: true)
- `CACHE_DIR`: Directory for cached responses (default: .cache)
- `CACHE_DURATION`: Cache expiration in seconds (default: 86400)
- `RATE_LIMIT_ENABLED`: Enable/disable rate limiting (default: true)
- `MAX_REQUESTS_PER_MINUTE`: Maximum API requests per minute (default: 60)

## Performance Features

### Caching System
- File-based caching of API responses
- Configurable cache duration
- Automatic cache expiration
- Segment-level caching for track identification

### Rate Limiting
- Token bucket algorithm for API request management
- Configurable requests per minute
- Thread-safe implementation
- Optional timeout for token acquisition

### Memory Optimization
- Chunk-based audio file reading
- Segment-level processing
- Efficient memory management
- Reduced memory footprint

## Output

Results are saved in the `tracklists` directory as JSON files:

```json
{
    "mix_info": {
        "title": "Example Mix",
        "analysis_date": "2024-02-21T15:30:45"
    },
    "track_count": 12,
    "tracks": [
        {
            "song_name": "Example Track",
            "artist": "Example Artist",
            "time_in_mix": "00:05:30",
            "confidence": 95
        }
    ]
}
```

## Output Formats

Tracklistify supports multiple output formats for the identified tracks:

### JSON Output
The JSON output includes comprehensive track information and analysis statistics:
```json
{
    "mix_info": {
        "title": "Example Mix",
        "artist": "DJ Example",
        "date": "2024-01-15"
    },
    "analysis_info": {
        "track_count": 25,
        "average_confidence": 85.5,
        "min_confidence": 15.2,
        "max_confidence": 98.7
    },
    "tracks": [
        {
            "song_name": "Example Track",
            "artist": "Example Artist",
            "time_in_mix": "00:05:30",
            "confidence": 92.5
        }
    ]
}
```

### Markdown Output
The markdown output provides a human-readable format with analysis information:
```markdown
# Example Mix

**Artist:** DJ Example
**Date:** 2024-01-15

## Analysis Info
- **Total Tracks:** 25
- **Average Confidence:** 85.5%
- **Confidence Range:** 15.2% - 98.7%

## Tracks
- [00:05:30] **Example Artist** - Example Track (92.5%)
```

### M3U Playlist
The M3U output includes extended playlist metadata:
```m3u
#EXTM3U
#PLAYLIST:Example Mix
#EXTALB:DJ Example
#EXTGENRE:DJ Mix - 2024-01-15
#EXTINF:-1,Example Artist - Example Track
```

## File Naming

Output files follow the format: `[YYYYMMDD] Artist - Description.extension`

Examples:
- `[20240115] DJ Example - Summer Mix 2024.json`
- `[20240115] DJ Example - Summer Mix 2024.md`
- `[20240115] DJ Example - Summer Mix 2024.m3u`

## Project Structure

```
tracklistify/
├── tracklistify/
│   ├── __init__.py      # Package initialization
│   ├── __main__.py      # CLI entry point
│   ├── config.py        # Configuration management
│   ├── logger.py        # Logging setup
│   ├── track.py         # Track identification
│   └── downloader.py    # Audio download handling
├── setup.py             # Package setup
├── requirements.txt     # Dependencies
├── .env.example         # Example configuration
└── README.md           # Documentation
```

## Logging

Tracklistify uses a comprehensive logging system with both console and file output:

### Console Output
- Colored log levels for better visibility:
  - DEBUG: Cyan
  - INFO: Green
  - WARNING: Yellow
  - ERROR: Red
  - CRITICAL: Magenta
- Configurable verbosity level
- Clean format focused on essential information

### File Logging
- Detailed logs with timestamps
- Automatic log file creation with date-time stamps
- Debug-level logging for development and troubleshooting
- Log files stored in `logs` directory

### Usage Example
```python
from tracklistify.logger import logger, set_verbose, add_file_logging
from pathlib import Path

# Enable verbose logging
set_verbose(True)

# Add file logging
add_file_logging(Path('logs'))

# Log messages
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
```

### Log File Format
```
2024-01-15 14:30:45 [INFO] Starting track identification...
2024-01-15 14:30:45 [DEBUG] Analyzing segment 1/120 at 00:00:00
2024-01-15 14:30:46 [INFO] Found track: Example Track by Artist (92.5%)
2024-01-15 14:30:46 [WARNING] Low confidence track detected (45.2%)
2024-01-15 14:30:47 [ERROR] Failed to parse ACRCloud response: Invalid JSON
```

## Error Handling

Tracklistify implements a robust error handling system with retry mechanisms and timeouts:

### Custom Exceptions
```python
from tracklistify.exceptions import APIError, DownloadError, TimeoutError

# Handle specific error types
try:
    result = identify_track(audio_file)
except APIError as e:
    logger.error(f"API Error: {e.status_code} - {e.response}")
except DownloadError as e:
    logger.error(f"Download failed for {e.url}: {str(e.cause)}")
except TimeoutError as e:
    logger.error(f"{e.operation} timed out after {e.timeout}s")
```

### Retry Mechanism
```python
from tracklistify.retry import retry, with_timeout

# Retry API calls with exponential backoff
@retry(max_attempts=3, base_delay=1.0, exceptions=[APIError])
@with_timeout(timeout=30.0)
def make_api_request():
    # API call implementation
    pass

# Custom retry behavior
@retry(
    max_attempts=5,
    base_delay=2.0,
    max_delay=30.0,
    exceptions=[ConnectionError, TimeoutError],
    timeout=60.0,
    on_retry=lambda attempt, delay, error: print(f"Retrying... {attempt}")
)
def download_file(url: str):
    # Download implementation
    pass
```

### Error Types
- `TracklistifyError`: Base exception class
- `APIError`: API request failures
- `DownloadError`: Download operation failures
- `ConfigError`: Configuration issues
- `AudioProcessingError`: Audio processing failures
- `TrackIdentificationError`: Track identification issues
- `ValidationError`: Input validation failures
- `RetryExceededError`: Maximum retry attempts exceeded
- `TimeoutError`: Operation timeout

## Testing

Tracklistify includes a comprehensive test suite covering core functionality, edge cases, and error conditions:

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=tracklistify

# Run specific test file
pytest tests/test_track_identification.py
```

### Test Coverage

The test suite includes:
- Unit tests for configuration and track handling
- Integration tests for the full identification pipeline
- Error condition tests (empty files, invalid formats)
- Edge case tests (confidence thresholds, duplicates)
- Validation tests for track metadata

### Writing Tests

When adding new features, please ensure:
1. Test coverage for new functionality
2. Error handling tests for potential failure modes
3. Edge case tests for boundary conditions
4. Integration tests for feature interactions

## Development

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Run tests:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.