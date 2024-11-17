# Getting Started with Tracklistify

## Overview

Tracklistify is a powerful audio track identification and playlist generation system. This guide will help you get started with setting up and using the system.

## Prerequisites

- Python 3.11.9 or higher
- FFmpeg installed and available in PATH
- API credentials for supported providers (ACRCloud, Shazam, Spotify)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tracklistify.git
cd tracklistify
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API credentials
```

## Configuration

### Environment Variables

Required variables:
```env
# ACRCloud Configuration
ACR_ACCESS_KEY=your_access_key
ACR_ACCESS_SECRET=your_access_secret
ACR_HOST=your_host

# Spotify Configuration
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret

# Optional Configuration
CACHE_DIR=./cache
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT=30
```

### Provider Configuration

Each provider can be configured in `config.yaml`:
```yaml
providers:
  acrcloud:
    enabled: true
    timeout: 10
    max_retries: 3
    
  shazam:
    enabled: true
    segment_length: 10
    confidence_threshold: 0.8
    
  spotify:
    enabled: true
    market: US
    include_audio_features: true
```

## Basic Usage

### Command Line Interface

1. Identify tracks in an audio file:
```bash
python -m tracklistify identify path/to/audio.mp3
```

2. Generate a playlist:
```bash
python -m tracklistify playlist path/to/audio.mp3 --format spotify
```

3. View identified tracks:
```bash
python -m tracklistify list path/to/audio.mp3
```

### Python API

1. Basic track identification:
```python
from tracklistify import TrackIdentifier

async def identify_tracks():
    identifier = TrackIdentifier()
    tracks = await identifier.identify_file("path/to/audio.mp3")
    for track in tracks:
        print(f"Found: {track.title} by {track.artist}")
```

2. Using specific providers:
```python
from tracklistify.providers import ACRCloudProvider, ShazamProvider

async def identify_with_providers():
    providers = [ACRCloudProvider(), ShazamProvider()]
    identifier = TrackIdentifier(providers=providers)
    tracks = await identifier.identify_file("path/to/audio.mp3")
```

3. Generating playlists:
```python
from tracklistify import PlaylistGenerator

async def create_playlist():
    generator = PlaylistGenerator()
    playlist = await generator.create_from_file(
        "path/to/audio.mp3",
        format="spotify",
        name="My Awesome Mix"
    )
    print(f"Playlist URL: {playlist.url}")
```

## Advanced Usage

### Custom Providers

Create a custom provider by implementing the `TrackIdentificationProvider` interface:

```python
from tracklistify.providers import TrackIdentificationProvider

class CustomProvider(TrackIdentificationProvider):
    async def identify_track(self, audio_data: bytes) -> Dict:
        # Implement track identification logic
        pass
        
    async def enrich_metadata(self, track_info: Dict) -> Dict:
        # Implement metadata enrichment logic
        pass
```

Register your provider:
```python
from tracklistify import ProviderFactory

ProviderFactory.register("custom", CustomProvider)
```

### Caching

Enable caching to improve performance:

```python
from tracklistify.cache import FileCache

cache = FileCache(directory="./cache", ttl=86400)
identifier = TrackIdentifier(cache=cache)
```

### Error Handling

Handle common errors:

```python
from tracklistify.exceptions import (
    ProviderError,
    AuthenticationError,
    RateLimitError
)

try:
    tracks = await identifier.identify_file("path/to/audio.mp3")
except AuthenticationError:
    print("Invalid API credentials")
except RateLimitError:
    print("Rate limit exceeded")
except ProviderError as e:
    print(f"Provider error: {e}")
```

## Testing

1. Run tests:
```bash
pytest tests/
```

2. Run specific test suite:
```bash
pytest tests/test_providers/
```

3. Run with coverage:
```bash
pytest --cov=tracklistify tests/
```

## Troubleshooting

### Common Issues

1. **API Authentication Errors**
   - Verify API credentials in `.env`
   - Check API key permissions
   - Ensure proper environment setup

2. **Audio Processing Errors**
   - Verify FFmpeg installation
   - Check audio file format
   - Ensure file permissions

3. **Rate Limiting**
   - Implement backoff strategy
   - Use caching
   - Check API quotas

### Logging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Configure file logging:

```python
logging.basicConfig(
    filename='tracklistify.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Best Practices

1. **Error Handling**
   - Always use try-except blocks
   - Implement proper cleanup
   - Log errors appropriately

2. **Resource Management**
   - Close file handles
   - Release API connections
   - Clear cache when needed

3. **Performance**
   - Use caching
   - Implement rate limiting
   - Process in chunks

4. **Testing**
   - Write unit tests
   - Mock external APIs
   - Test error cases

## Support

- GitHub Issues: Report bugs and feature requests
- Documentation: Read the full documentation
- Community: Join our Discord server

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
