"""
Integration tests for Tracklistify.
"""

import json
from pathlib import Path

import pytest
import responses
from tracklistify.__main__ import identify_tracks, get_mix_info
from tracklistify.track import Track

@pytest.fixture
def mock_acrcloud(mock_track_data):
    """Mock ACRCloud API responses."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://test.acrcloud.com/v1/identify",
            json=mock_track_data,
            status=200
        )
        yield rsps

@pytest.mark.integration
def test_track_identification(test_env, mock_audio_file, mock_acrcloud):
    """Test full track identification flow."""
    tracks = identify_tracks(str(mock_audio_file))
    assert tracks is not None
    assert len(tracks) > 0
    
    # Verify track data
    track = tracks[0]
    assert isinstance(track, Track)
    assert track.song_name == "Test Track 1"
    assert track.artist == "Test Artist 1"
    assert track.confidence == 90.0

@pytest.mark.integration
def test_mix_info_extraction(mock_audio_file):
    """Test mix information extraction."""
    mix_info = get_mix_info(str(mock_audio_file))
    assert mix_info is not None
    assert "title" in mix_info
    assert "artist" in mix_info
    assert "date" in mix_info

@pytest.mark.integration
def test_full_workflow(tmp_path, test_env, mock_audio_file, mock_acrcloud):
    """Test complete workflow from input to output."""
    from tracklistify.__main__ import main
    from tracklistify.output import TracklistOutput
    
    # Set up test environment
    output_dir = tmp_path / "tracklists"
    output_dir.mkdir()
    
    # Run identification
    tracks = identify_tracks(str(mock_audio_file))
    assert tracks is not None
    
    # Get mix info
    mix_info = get_mix_info(str(mock_audio_file))
    assert mix_info is not None
    
    # Generate outputs
    output = TracklistOutput(tracks, mix_info)
    output.output_dir = output_dir
    
    # Test all output formats
    json_file = output._save_json()
    assert json_file.exists()
    
    md_file = output._save_markdown()
    assert md_file.exists()
    
    m3u_file = output._save_m3u()
    assert m3u_file.exists()
    
    # Verify JSON content
    with open(json_file) as f:
        data = json.load(f)
        assert data["track_count"] == len(tracks)
        assert len(data["tracks"]) == len(tracks)
        
    # Verify Markdown content
    content = md_file.read_text()
    assert mix_info["title"] in content
    assert tracks[0].song_name in content
    
    # Verify M3U content
    content = m3u_file.read_text()
    assert "#EXTM3U" in content
    assert tracks[0].artist in content
