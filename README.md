# Tracklistify

A powerful tool for identifying tracks in DJ mixes, live streams, and audio files.

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

### Configuration

Configure Tracklistify through environment variables in `.env`:

#### ACRCloud Settings
- `ACRCLOUD_ACCESS_KEY`: Your ACRCloud access key
- `ACRCLOUD_ACCESS_SECRET`: Your ACRCloud access secret
- `ACRCLOUD_HOST`: ACRCloud API endpoint
- `ACRCLOUD_TIMEOUT`: API request timeout (seconds)

#### Track Identification
- `MIN_CONFIDENCE`: Minimum confidence score (0-100)
- `TIME_THRESHOLD`: Time window for merging duplicates (seconds)
- `MIN_TRACK_LENGTH`: Minimum track length (seconds)
- `MAX_DUPLICATES`: Maximum allowed duplicates
- `SEGMENT_LENGTH`: Analysis segment length (seconds)

#### Application Settings
- `VERBOSE`: Enable detailed logging
- `OUTPUT_FORMAT`: Output format (json)
- `CACHE_ENABLED`: Enable result caching
- `CACHE_DURATION`: Cache duration (seconds)

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