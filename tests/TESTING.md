# Tracklistify Testing Guide

## Overview
This guide provides comprehensive documentation for testing Tracklistify, including test organization, fixtures, mocks, and best practices.

## Table of Contents
1. [Test Organization](#test-organization)
2. [Provider Tests](#provider-tests)
3. [Test Fixtures](#test-fixtures)
4. [Mock Objects](#mock-objects)
5. [Test Coverage](#test-coverage)
6. [Best Practices](#best-practices)

## Test Organization

### Directory Structure
```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_providers/          # Provider-specific tests
│   ├── test_acrcloud.py     # ACRCloud provider tests
│   ├── test_shazam.py       # Shazam provider tests
│   └── test_spotify.py      # Spotify provider tests
├── test_core/              # Core functionality tests
│   ├── test_track.py       # Track object tests
│   └── test_config.py      # Configuration tests
└── test_integration/       # Integration tests
    └── test_providers.py   # Provider integration tests
```

## Provider Tests

### ACRCloud Provider Tests
- Authentication and authorization
- Track identification
- Error handling (rate limits, network errors)
- Response parsing
- Partial metadata handling

### Shazam Provider Tests
- Track matching
- Multiple match handling
- Response parsing
- Error scenarios
- Network resilience

### Spotify Provider Tests
- Track search
- Track details retrieval
- Authentication flow
- Rate limiting
- Error handling

## Test Fixtures

### Common Fixtures (conftest.py)
```python
@pytest.fixture
def mock_track():
    return {
        'title': 'Test Track',
        'artist': 'Test Artist',
        'album': 'Test Album',
        'duration': 180
    }

@pytest.fixture
def audio_data():
    return generate_test_audio()
```

### Provider-Specific Fixtures
```python
@pytest.fixture
def spotify_config():
    return {
        'client_id': 'test_id',
        'client_secret': 'test_secret'
    }

@pytest.fixture
def mock_spotify_response():
    # Provider-specific response format
    return {...}
```

## Mock Objects

### Network Mocks
```python
@pytest.mark.asyncio
async def test_api_call():
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        # Test implementation
```

### File System Mocks
```python
@pytest.fixture
def mock_audio_file(tmp_path):
    file_path = tmp_path / "test.mp3"
    # Create mock audio file
    return file_path
```

## Test Coverage

### Coverage Requirements
- Unit tests: 90% coverage
- Integration tests: 80% coverage
- Provider tests: 95% coverage

### Running Coverage
```bash
pytest --cov=tracklistify tests/
pytest --cov=tracklistify --cov-report=html tests/
```

## Best Practices

### Test Organization
1. Group related tests in classes
2. Use descriptive test names
3. Follow AAA pattern (Arrange, Act, Assert)

### Async Testing
```python
@pytest.mark.asyncio
async def test_async_function():
    # Test async code
    result = await async_function()
    assert result is not None
```

### Error Testing
```python
@pytest.mark.asyncio
async def test_error_handling():
    with pytest.raises(SpecificError) as exc_info:
        await function_that_raises()
    assert str(exc_info.value) == "Expected error message"
```

### Mock Usage
1. Mock external services
2. Use context managers
3. Verify mock calls
4. Reset mocks between tests

### Fixtures
1. Keep fixtures focused
2. Use appropriate scope
3. Document dependencies
4. Clean up resources

### Documentation
1. Document test purpose
2. Explain complex test scenarios
3. Include example usage
4. Document fixture dependencies

## Running Tests

### Basic Usage
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_providers/test_spotify.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov
```

### Test Selection
```bash
# Run tests matching pattern
pytest -k "spotify"

# Run marked tests
pytest -m "integration"
```

### Debugging
```bash
# Show print statements
pytest -s

# Enter debugger on failures
pytest --pdb

# Testing Guide

This guide covers testing practices and patterns for the Tracklistify project.

## Table of Contents
- [Overview](#overview)
- [Test Organization](#test-organization)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Mocking](#mocking)
- [Provider Testing](#provider-testing)
- [Best Practices](#best-practices)

## Overview

Tracklistify uses pytest for testing. Our test suite covers:
- Unit tests for core functionality
- Integration tests for providers
- End-to-end tests for key workflows
- Performance tests for critical paths

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── test_core/              # Core functionality tests
├── test_providers/         # Provider-specific tests
│   ├── test_acrcloud.py
│   ├── test_shazam.py
│   └── test_spotify.py
├── test_utils/             # Utility function tests
└── test_integration/       # Integration tests
```

## Running Tests

Basic test commands:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_providers/test_spotify.py

# Run tests matching pattern
pytest -k "spotify"

# Run with detailed output
pytest -v

# Run with logging
pytest --log-cli-level=DEBUG
```

## Writing Tests

### Test Structure
```python
import pytest
from tracklistify import SpotifyProvider

@pytest.fixture
def spotify_provider():
    return SpotifyProvider(
        client_id="test_id",
        client_secret="test_secret"
    )

def test_track_search(spotify_provider):
    result = spotify_provider.search_track("Test Track")
    assert result is not None
    assert "id" in result
```

### Async Tests
```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

## Test Coverage

We aim for:
- 90%+ coverage for core functionality
- 95%+ coverage for provider implementations
- 80%+ coverage for integration tests

Check coverage:
```bash
pytest --cov=tracklistify --cov-report=term-missing
```

## Mocking

### Network Requests
```python
import pytest
from unittest.mock import patch

def test_api_call(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"track": "data"}
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response
        result = await provider.get_track()
        assert result["track"] == "data"
```

### File Operations
```python
def test_file_processing(tmp_path):
    test_file = tmp_path / "test.mp3"
    test_file.write_bytes(b"test data")
    result = process_audio_file(test_file)
    assert result.success
```

## Provider Testing

### ACRCloud Provider
- Authentication tests
- Track identification tests
- Rate limiting tests
- Error handling tests
- Response parsing tests

### Shazam Provider
- Track matching tests
- Multiple match handling
- Network resilience tests
- Error scenario tests
- Response format tests

### Spotify Provider
- Track search tests
- Authentication flow tests
- Rate limit handling
- Error recovery tests
- Response parsing tests

## Best Practices

1. **Test Isolation**
   - Each test should run independently
   - Clean up resources after tests
   - Use fixtures for setup/teardown

2. **Meaningful Assertions**
   - Test specific behaviors
   - Include descriptive messages
   - Check edge cases

3. **Mock External Dependencies**
   - API calls
   - File system operations
   - Time-dependent operations

4. **Error Scenarios**
   - Test error handling
   - Validate error messages
   - Check recovery behavior

5. **Performance Testing**
   - Use benchmarks for critical paths
   - Test with realistic data sizes
   - Monitor memory usage

6. **Documentation**
   - Document test purpose
   - Explain complex fixtures
   - Include example usage

## Example Test Cases

### Unit Test
```python
def test_track_normalization():
    track = {
        "title": " Test Track ",
        "artist": "Test Artist  "
    }
    normalized = normalize_track(track)
    assert normalized["title"] == "Test Track"
    assert normalized["artist"] == "Test Artist"
```

### Integration Test
```python
@pytest.mark.asyncio
async def test_track_identification_flow():
    # Setup
    provider = create_test_provider()
    audio_file = create_test_audio()
    
    # Identify track
    result = await provider.identify_track(audio_file)
    
    # Verify result
    assert result.success
    assert result.track.title
    assert result.track.artist
```

### Error Test
```python
@pytest.mark.asyncio
async def test_rate_limit_handling():
    provider = create_test_provider()
    
    # Simulate rate limit
    with patch.object(provider, "_make_request") as mock_request:
        mock_request.side_effect = RateLimitError()
        
        # Should retry with backoff
        result = await provider.identify_track(audio_file)
        assert result.retried
        assert not result.error
```

## Continuous Integration

Our CI pipeline:
1. Runs all tests
2. Checks coverage
3. Validates formatting
4. Runs security checks
5. Generates reports

## Contributing

When adding new tests:
1. Follow existing patterns
2. Update documentation
3. Check coverage
4. Add necessary fixtures
5. Include edge cases
