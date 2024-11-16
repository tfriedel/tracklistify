"""
Unit tests for TracklistOutput class.
"""

import json
from pathlib import Path

import pytest
from tracklistify.output import TracklistOutput
from tracklistify.track import Track

def test_output_initialization(mock_mix_info):
    """Test TracklistOutput initialization."""
    tracks = [
        Track("Test Track", "Test Artist", "00:00:00", 90.0)
    ]
    output = TracklistOutput(tracks, mock_mix_info)
    
    assert output.tracks == tracks
    assert output.mix_info == mock_mix_info
    assert isinstance(output.output_dir, Path)

def test_filename_formatting(mock_mix_info):
    """Test output filename formatting."""
    tracks = [
        Track("Test Track", "Test Artist", "00:00:00", 90.0)
    ]
    output = TracklistOutput(tracks, mock_mix_info)
    
    filename = output._format_filename("json")
    expected = f"[20240319] {mock_mix_info['artist']} - {mock_mix_info['title']}.json"
    assert filename == expected

def test_json_output(tmp_path, mock_mix_info):
    """Test JSON output generation."""
    tracks = [
        Track("Test Track 1", "Test Artist 1", "00:00:00", 90.0),
        Track("Test Track 2", "Test Artist 2", "00:05:00", 85.0)
    ]
    
    output = TracklistOutput(tracks, mock_mix_info)
    output.output_dir = tmp_path
    
    output_file = output._save_json()
    assert output_file.exists()
    
    with open(output_file) as f:
        data = json.load(f)
        
    assert data["mix_info"] == mock_mix_info
    assert len(data["tracks"]) == 2
    assert data["track_count"] == 2

def test_markdown_output(tmp_path, mock_mix_info):
    """Test Markdown output generation."""
    tracks = [
        Track("Test Track 1", "Test Artist 1", "00:00:00", 90.0),
        Track("Test Track 2", "Test Artist 2", "00:05:00", 75.0)  # Low confidence
    ]
    
    output = TracklistOutput(tracks, mock_mix_info)
    output.output_dir = tmp_path
    
    output_file = output._save_markdown()
    assert output_file.exists()
    
    content = output_file.read_text()
    assert mock_mix_info["title"] in content
    assert mock_mix_info["artist"] in content
    assert "Test Track 1" in content
    assert "Test Track 2" in content
    assert "_(Confidence: 75%)_" in content  # Low confidence note

def test_m3u_output(tmp_path, mock_mix_info):
    """Test M3U playlist generation."""
    tracks = [
        Track("Test Track 1", "Test Artist 1", "00:00:00", 90.0),
        Track("Test Track 2", "Test Artist 2", "00:05:00", 85.0)
    ]
    
    output = TracklistOutput(tracks, mock_mix_info)
    output.output_dir = tmp_path
    
    output_file = output._save_m3u()
    assert output_file.exists()
    
    content = output_file.read_text()
    assert "#EXTM3U" in content
    assert "Test Artist 1 - Test Track 1" in content
    assert "Test Artist 2 - Test Track 2" in content
    assert "Time in mix: 00:00:00" in content
