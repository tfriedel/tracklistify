# Tracklistify API Documentation

## Core Components

### Track Identification Providers

#### Base Provider Interface
The `TrackIdentificationProvider` abstract base class defines the interface that all track identification providers must implement:

```python
class TrackIdentificationProvider(ABC):
    @abstractmethod
    async def identify_track(self, audio_data: bytes, start_time: float = 0) -> Dict:
        """Identify a track from audio data."""
        pass

    @abstractmethod
    async def enrich_metadata(self, track_info: Dict) -> Dict:
        """Enrich track metadata with additional information."""
        pass
```

#### Available Providers

##### ACRCloud Provider
- **Purpose**: Primary track identification using ACRCloud's audio recognition service
- **Features**:
  - High accuracy audio fingerprinting
  - Fast recognition speed
  - Rich metadata support
- **Configuration**:
  ```env
  ACR_ACCESS_KEY=your_access_key
  ACR_ACCESS_SECRET=your_access_secret
  ACR_HOST=your_host
  ```

##### Shazam Provider
- **Purpose**: Advanced audio fingerprinting with feature extraction
- **Features**:
  - Mel-frequency cepstral coefficients (MFCCs)
  - Spectral centroid analysis
  - Pre-emphasis filtering
  - Confidence scoring
- **Audio Processing**:
  - 10-second segment analysis
  - Feature normalization
  - Enhanced audio fingerprinting

##### Spotify Provider
- **Purpose**: Rich metadata enrichment and track search
- **Features**:
  - OAuth 2.0 authentication
  - Detailed track information
  - Audio features (tempo, key, etc.)
- **Configuration**:
  ```env
  SPOTIFY_CLIENT_ID=your_client_id
  SPOTIFY_CLIENT_SECRET=your_client_secret
  ```

### Track Processing

#### Track Class
The `Track` class represents a single identified track with its metadata:

```python
class Track:
    def __init__(self, title: str, artist: str, ...):
        self.title = title
        self.artist = artist
        self.album = album
        self.start_time = start_time
        self.duration = duration
        self.confidence = confidence
        self.audio_features = audio_features
```

Key methods:
- `merge_with()`: Merge duplicate track entries
- `to_dict()`: Convert track to dictionary format
- `from_dict()`: Create track from dictionary
- `validate()`: Validate track metadata

### Performance Optimization

#### Caching System
The `Cache` class provides file-based caching for API responses:

```python
class Cache:
    def get(self, key: str) -> Optional[Any]:
        """Retrieve cached value for key."""
        pass

    def set(self, key: str, value: Any, ttl: int = None):
        """Cache value with optional TTL."""
        pass
```

Features:
- Configurable cache duration
- Automatic expiration
- Thread-safe operations

#### Rate Limiting
The `RateLimiter` class implements token bucket algorithm:

```python
class RateLimiter:
    def acquire(self, timeout: float = None) -> bool:
        """Acquire a token with optional timeout."""
        pass
```

Features:
- Configurable rate limits
- Thread-safe implementation
- Optional timeout

### Error Handling

#### Exception Hierarchy
```
BaseException
└── Exception
    └── ProviderError
        ├── AuthenticationError
        ├── RateLimitError
        └── NetworkError
```

Error handling best practices:
1. Use specific exception types
2. Include error context
3. Implement retry mechanisms
4. Log error details

## Usage Examples

### Track Identification
```python
async def identify_track(audio_data: bytes, provider: str = "acrcloud"):
    provider = ProviderFactory.create(provider)
    try:
        result = await provider.identify_track(audio_data)
        return result
    except ProviderError as e:
        logger.error(f"Track identification failed: {e}")
        raise
```

### Metadata Enrichment
```python
async def enrich_track(track_info: Dict, provider: str = "spotify"):
    provider = ProviderFactory.create(provider)
    try:
        enriched = await provider.enrich_metadata(track_info)
        return enriched
    except ProviderError as e:
        logger.warning(f"Metadata enrichment failed: {e}")
        return track_info
```

### Cache Usage
```python
cache = Cache(ttl=86400)  # 24-hour cache
key = f"track_{track_id}"

# Try to get cached result
if result := cache.get(key):
    return result

# Identify track and cache result
result = await identify_track(audio_data)
cache.set(key, result)
return result
```

## Best Practices

### Provider Implementation
1. Implement both required methods
2. Handle all error cases
3. Use proper type hints
4. Add comprehensive logging
5. Include retry mechanisms

### Track Processing
1. Validate input data
2. Handle missing fields
3. Merge similar tracks
4. Calculate confidence scores
5. Clean metadata

### Performance
1. Use caching when possible
2. Implement rate limiting
3. Process in chunks
4. Optimize memory usage
5. Handle timeouts

### Error Handling
1. Use specific exceptions
2. Include error context
3. Log error details
4. Implement retries
5. Fail gracefully

## Contributing

### Adding New Providers
1. Create provider class:
   ```python
   class NewProvider(TrackIdentificationProvider):
       async def identify_track(self, audio_data: bytes) -> Dict:
           # Implementation
           pass

       async def enrich_metadata(self, track_info: Dict) -> Dict:
           # Implementation
           pass
   ```

2. Register in factory:
   ```python
   ProviderFactory.register("new_provider", NewProvider)
   ```

3. Add configuration:
   ```env
   NEW_PROVIDER_API_KEY=your_api_key
   NEW_PROVIDER_TIMEOUT=10
   ```

4. Update documentation

### Testing
1. Write unit tests:
   - Mock external APIs
   - Test error cases
   - Verify retry logic
   - Check edge cases

2. Run tests:
   ```bash
   pytest tests/
   ```

### Code Style
1. Follow PEP 8
2. Use type hints
3. Add docstrings
4. Write clear comments
5. Keep methods focused
