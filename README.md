# Tracklistify

Unleash the power of Tracklistify! Create playlists from Livesets, DJ Mixes and Podcasts by identifying tracks using advanced audio recognition. Whether you're analyzing local MP3 files or streaming from YouTube or Mixcloud, Tracklistify provides precise timestamps, detailed track info, and confidence scores. Perfect for DJs, music enthusiasts, and content creators.

Get started today and elevate your music experience!

## Features

- 🎵 Multi-provider track identification:
  - ACRCloud for accurate mix analysis
  - Spotify for rich metadata enrichment
  - Shazam audio fingerprinting with advanced features:
    * Mel-frequency cepstral coefficients (MFCCs)
    * Spectral centroid analysis
    * Pre-emphasis filtering
    * Confidence-based matching
  - Expandable provider system
- 🌐 Support for online streaming platforms:
  - YouTube
  - Mixcloud
  - Expandable to other platforms
- ⏱️ Precise timestamp tracking for each identified song
- 📊 Advanced track analysis:
  - Confidence scores for matches
  - Audio features (tempo, key, energy)
  - Popularity metrics
- 🎼 Rich track information:
  - Artists and collaborators
  - Album details
  - Release dates
  - Genre information
  - External links
- 📝 Flexible output formats:
  - JSON with detailed metadata
  - M3U playlists
  - Markdown reports
- 🔄 Smart track handling:
  - Duplicate detection and merging
  - Confidence-based filtering
  - Time-based track alignment
- 🎚️ Performance optimizations:
  - Intelligent caching system
  - Rate limiting protection
  - Memory-efficient processing
  - Configurable settings

## Documentation

📚 **[View Full Documentation](docs/README.md)**

- [Getting Started Guide](docs/GETTING_STARTED.md)
- [API Documentation](docs/API.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Audio Processing Guide](docs/AUDIO_PROCESSING.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Testing Guide](tests/TESTING.md)

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

Edit `.env` with your provider credentials and desired settings.

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
- `-o, --output-format`: Output format (json, m3u, markdown)
- `-d, --output-dir`: Custom output directory

## Configuration

The application uses environment variables for configuration. Create a `.env` file in the project root:

```env
# ACRCloud Configuration
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

# Provider Settings
PRIMARY_PROVIDER=acrcloud
METADATA_PROVIDERS=spotify

# Spotify Configuration
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
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

#### Provider Configuration
- `PRIMARY_PROVIDER`: Primary track identification provider (default: acrcloud)
- `METADATA_PROVIDERS`: Comma-separated list of metadata providers (default: spotify)
- Provider-specific credentials (ACRCloud, Spotify, etc.)

## Output Formats

### JSON Output
```json
{
    "mix_info": {
        "title": "Example Mix",
        "duration": 3600,
        "analysis_date": "2024-03-21T12:00:00Z"
    },
    "tracks": [
        {
            "title": "Example Track",
            "artists": ["Artist Name"],
            "album": "Album Name",
            "start_time": 120,
            "duration": 180,
            "confidence": 85,
            "audio_features": {
                "tempo": 128,
                "key": 1,
                "energy": 0.8
            },
            "external_urls": {
                "spotify": "https://open.spotify.com/track/..."
            }
        }
    ],
    "analysis_stats": {
        "total_tracks": 20,
        "avg_confidence": 82.5,
        "identified_duration": 3540
    }
}
```

### M3U Playlist
```m3u8
#EXTM3U
#EXTINF:180,Artist Name - Example Track
#EXTALB:Album Name
#EXTGENRE:Electronic
https://open.spotify.com/track/...
```

## Development

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific provider tests
pytest tests/test_providers/
```

For detailed testing information, see our [Testing Guide](tests/TESTING.md).

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.