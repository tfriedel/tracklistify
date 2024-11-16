# Tracklistify

🎵 A powerful DJ mix track identification tool that helps you discover and catalog tracks from mixes, live streams, and audio files.

## Description

Tracklistify is an intelligent audio analysis tool that automatically identifies tracks in DJ mixes and generates formatted track lists. It uses advanced audio fingerprinting to detect songs, handles overlapping transitions, and exports results in multiple formats (JSON, Markdown, M3U).

## Topics

`audio-analysis` `dj-tools` `music-recognition` `python` `track-identification` `playlist-generation` `audio-fingerprinting` `music-metadata` `tracklist-generator` `mix-analysis` `acrcloud` `audio-processing` `music-tools` `dj-software` `streaming-tools`

## Features

- Track identification using ACRCloud API
- Support for YouTube downloads
- Confidence-based track filtering
- Automatic track merging for duplicates
- Detailed JSON output with timestamps
- Comprehensive logging system
- Configurable via environment variables

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

# Application Settings
SEGMENT_LENGTH=60  # Length of each analysis segment in seconds
OUTPUT_FORMAT=json
VERBOSE=false

# API Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
```

### Configuration Parameters

- `SEGMENT_LENGTH`: Length of each analysis segment in seconds (default: 60)
  - Shorter segments (30-60s) provide more accurate track timing
  - Longer segments (120s+) reduce API calls but may miss short tracks

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