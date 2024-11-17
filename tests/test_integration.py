"""
Integration tests for Tracklistify.
"""

import json
from pathlib import Path

import pytest
from tracklistify.__main__ import identify_tracks, get_mix_info
from tracklistify.track import Track
from tracklistify.output import TracklistOutput
from tests.conftest import (
    TEST_TRACK_TITLE,
    TEST_TRACK_ARTIST,
    TEST_TRACK_CONFIDENCE,
    TEST_MIX_TITLE
)

@pytest.fixture
def mock_acrcloud(mock_track_data):
    """Mock ACRCloud API responses."""
    with aioresponses.aioresponses() as m:
        m.post(
            "https://test.acrcloud.com/v1/identify",
            payload=mock_track_data,
            status=200
        )
        yield m

@pytest.mark.asyncio
async def test_track_identification(test_env, mock_audio_file, mock_acrcloud, mock_mutagen):
    """Test full track identification flow."""
    tracks = await identify_tracks(str(mock_audio_file))
    assert tracks is not None
    assert len(tracks) > 0
    
    # Verify track data
    track = tracks[0]
    assert isinstance(track, Track)
    assert track.song_name == TEST_TRACK_TITLE
    assert track.artist == TEST_TRACK_ARTIST
    assert track.confidence == TEST_TRACK_CONFIDENCE

@pytest.mark.asyncio
async def test_mix_info_extraction(mock_audio_file, mock_mutagen):
    """Test mix information extraction."""
    mix_info = await get_mix_info(str(mock_audio_file))
    assert mix_info is not None
    assert mix_info['title'] == TEST_MIX_TITLE
    assert mix_info['source'] == str(mock_audio_file).split('/')[-1]
    assert 'duration' in mix_info

@pytest.mark.asyncio
async def test_full_workflow(tmp_path, test_env, mock_audio_file, mock_acrcloud, mock_mutagen):
    """Test complete workflow from input to output."""
    # Identify tracks
    tracks = await identify_tracks(str(mock_audio_file))
    assert tracks is not None
    assert len(tracks) > 0
    
    # Get mix info
    mix_info = await get_mix_info(str(mock_audio_file))
    assert mix_info is not None
    
    # Create output
    output = TracklistOutput(tracks, mix_info)
    
    # Test different output formats
    formats = ['text', 'json', 'markdown']
    for fmt in formats:
        output_file = tmp_path / f"tracklist.{fmt}"
        output.save(output_file, fmt)
        assert output_file.exists()
        
        # Verify content
        content = output_file.read_text()
        assert content
        if fmt == 'json':
            data = json.loads(content)
            assert 'tracks' in data
            assert 'mix_info' in data
            assert data['tracks'][0]['title'] == TEST_TRACK_TITLE
            assert data['tracks'][0]['artist'] == TEST_TRACK_ARTIST
            assert data['mix_info']['title'] == TEST_MIX_TITLE
