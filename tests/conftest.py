"""
Test configuration and fixtures for Tracklistify.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from _pytest.fixtures import FixtureRequest
import numpy as np
from aioresponses import aioresponses

# Mock data constants for consistency across tests
TEST_TRACK_TITLE = "Test Track 1"
TEST_TRACK_ARTIST = "Test Artist 1"
TEST_TRACK_ALBUM = "Test Album"
TEST_TRACK_DURATION = 180.0  # seconds
TEST_TRACK_CONFIDENCE = 90.0
TEST_MIX_TITLE = "test_mix"

# Audio-specific test constants
TEST_AUDIO_FORMATS = ['mp3', 'wav']
TEST_AUDIO_BITRATE = 320000
TEST_SAMPLE_RATE = 44100
TEST_CHUNK_SIZE = 1024 * 1024  # 1MB chunks for processing

class MockMutagenInfo:
    """Mock implementation of mutagen.FileInfo."""
    def __init__(self, length=TEST_TRACK_DURATION, 
                 bitrate=TEST_AUDIO_BITRATE,
                 sample_rate=TEST_SAMPLE_RATE):
        self.length = length  # Duration in seconds
        self.bitrate = bitrate
        self.sample_rate = sample_rate

class MockMutagenFile:
    """Mock implementation of mutagen.File."""
    def __init__(self, path):
        self.path = path
        self.info = MockMutagenInfo()
        self.tags = {
            'title': [TEST_MIX_TITLE],
            'artist': [TEST_TRACK_ARTIST],
            'album': [TEST_TRACK_ALBUM]
        }

@pytest.fixture
def mock_mutagen():
    """Mock the mutagen module."""
    with patch('mutagen.File', new=MockMutagenFile) as mock_file:
        yield mock_file

@pytest.fixture
def test_data_dir(request: FixtureRequest) -> Path:
    """Return the path to the test data directory."""
    data_dir = Path(request.module.__file__).parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

@pytest.fixture
def mock_audio_file(test_data_dir: Path) -> Path:
    """Return path to a mock audio file."""
    audio_path = test_data_dir / f"{TEST_MIX_TITLE}.mp3"
    # Create an empty file to satisfy existence checks
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    audio_path.touch()
    return audio_path

@pytest.fixture
def mock_track_data() -> dict:
    """Return mock track identification data."""
    return {
        "status": {
            "code": 0,
            "msg": "Success"
        },
        "metadata": {
            "music": [{
                "title": TEST_TRACK_TITLE,
                "artists": [{"name": TEST_TRACK_ARTIST}],
                "album": {"name": TEST_TRACK_ALBUM},
                "acrid": "test_acrid",
                "score": TEST_TRACK_CONFIDENCE,
                "play_offset_ms": 0,
                "duration_ms": int(TEST_TRACK_DURATION * 1000)
            }]
        }
    }

@pytest.fixture
def mock_acrcloud(mock_track_data):
    """Mock ACRCloud API responses."""
    with aioresponses() as m:
        m.post(
            "https://test.acrcloud.com/v1/identify",
            payload=mock_track_data,
            status=200
        )
        yield m

@pytest.fixture
def test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up test environment variables."""
    monkeypatch.setenv("ACR_ACCESS_KEY", "test_access_key")
    monkeypatch.setenv("ACR_ACCESS_SECRET", "test_access_secret")
    monkeypatch.setenv("ACR_HOST", "test.acrcloud.com")
    monkeypatch.setenv("CACHE_DIR", ".test_cache")

@pytest.fixture
def mock_mix_info() -> dict:
    """Return mock mix information."""
    return {
        "title": TEST_MIX_TITLE,
        "source": f"{TEST_MIX_TITLE}.mp3",
        "duration": TEST_TRACK_DURATION,
        "tracks": [
            {
                "title": TEST_TRACK_TITLE,
                "artist": TEST_TRACK_ARTIST,
                "time": "00:00:00"
            }
        ]
    }
