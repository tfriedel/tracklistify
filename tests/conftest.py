"""
Test configuration and fixtures for Tracklistify.
"""

import os
from pathlib import Path
from typing import Generator

import pytest
from _pytest.fixtures import FixtureRequest

@pytest.fixture
def test_data_dir(request: FixtureRequest) -> Path:
    """Return the path to the test data directory."""
    return Path(request.module.__file__).parent / "data"

@pytest.fixture
def test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up test environment variables."""
    monkeypatch.setenv("ACR_ACCESS_KEY", "test_access_key")
    monkeypatch.setenv("ACR_ACCESS_SECRET", "test_access_secret")
    monkeypatch.setenv("ACR_HOST", "test.acrcloud.com")
    monkeypatch.setenv("SEGMENT_LENGTH", "60")
    monkeypatch.setenv("OUTPUT_FORMAT", "json")
    monkeypatch.setenv("VERBOSE", "true")

@pytest.fixture
def mock_audio_file(test_data_dir: Path) -> Path:
    """Return path to a mock audio file."""
    return test_data_dir / "test_mix.mp3"

@pytest.fixture
def mock_track_data() -> dict:
    """Return mock track identification data."""
    return {
        "status": {
            "code": 0,
            "msg": "Success"
        },
        "metadata": {
            "music": [
                {
                    "title": "Test Track 1",
                    "artists": [{"name": "Test Artist 1"}],
                    "score": 90
                },
                {
                    "title": "Test Track 2",
                    "artists": [{"name": "Test Artist 2"}],
                    "score": 85
                }
            ]
        }
    }

@pytest.fixture
def mock_mix_info() -> dict:
    """Return mock mix information."""
    return {
        "title": "Test Mix",
        "artist": "Test DJ",
        "date": "2024-03-19",
        "duration": 3600  # 1 hour in seconds
    }
