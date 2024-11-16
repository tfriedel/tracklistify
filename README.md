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

## Development

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Run tests:
```bash
pytest
```

## Logging

Logs are stored in the `logs` directory:
- Console output: Basic information and results
- File logs: Detailed debugging information

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.