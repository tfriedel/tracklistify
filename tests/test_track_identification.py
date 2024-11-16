"""
Integration tests for track identification functionality.
"""

import pytest
from pathlib import Path
from tracklistify.track import Track, TrackMatcher
from tracklistify.config import get_config
from tracklistify.exceptions import TrackIdentificationError
import re

def test_track_identification_with_test_file(test_env, mock_audio_file):
    """Test track identification with our test audio file."""
    # Initialize track matcher
    matcher = TrackMatcher()
    
    # Process the test file
    tracks = matcher.process_file(mock_audio_file)
    
    # Basic validation
    assert isinstance(tracks, list)
    assert all(isinstance(track, Track) for track in tracks)

def test_track_confidence_threshold(test_env, mock_audio_file):
    """Test that tracks below confidence threshold are filtered."""
    config = get_config()
    matcher = TrackMatcher()
    
    # Set a high confidence threshold
    matcher.min_confidence = 95
    tracks = matcher.process_file(mock_audio_file)
    
    # Verify all returned tracks meet the confidence threshold
    assert all(track.confidence >= 95 for track in tracks)

def test_track_deduplication(test_env, mock_audio_file):
    """Test that duplicate tracks are properly handled."""
    config = get_config()
    matcher = TrackMatcher()
    
    # Set parameters to test deduplication
    matcher.max_duplicates = 1
    matcher.time_threshold = 30
    
    tracks = matcher.process_file(mock_audio_file)
    
    # Check for duplicates within time threshold
    for i, track1 in enumerate(tracks):
        for track2 in tracks[i+1:]:
            if track1.song_name == track2.song_name:
                # If same track, ensure they're separated by at least time_threshold
                time_diff = abs(track1.time_to_seconds() - track2.time_to_seconds())
                assert time_diff >= matcher.time_threshold

def test_segment_length_processing(test_env, mock_audio_file):
    """Test that audio file is processed according to segment length."""
    config = get_config()
    matcher = TrackMatcher()
    
    # Set a specific segment length
    config.track.segment_length = 30
    
    tracks = matcher.process_file(mock_audio_file)
    
    # Our test file is 60 seconds, with 30 second segments we expect at least 2 segments
    assert len(tracks) >= 2

@pytest.mark.integration
def test_full_identification_pipeline(test_env, mock_audio_file, mock_track_data):
    """Test the complete track identification pipeline."""
    matcher = TrackMatcher()
    
    # Process the test file
    tracks = matcher.process_file(mock_audio_file)
    
    # Validate track objects
    for track in tracks:
        assert track.song_name is not None
        assert track.artist is not None
        assert isinstance(track.confidence, (int, float))
        assert 0 <= track.confidence <= 100
        assert isinstance(track.time_in_mix, str)
        assert ":" in track.time_in_mix  # Basic time format check

def test_empty_audio_file(test_env, tmp_path):
    """Test handling of empty audio file."""
    # Create an empty file
    empty_file = tmp_path / "empty.mp3"
    empty_file.write_bytes(b"")
    
    matcher = TrackMatcher()
    
    with pytest.raises(TrackIdentificationError) as exc_info:
        matcher.process_file(empty_file)
    assert "Failed to process audio file" in str(exc_info.value)

def test_missing_audio_file(test_env):
    """Test handling of non-existent audio file."""
    matcher = TrackMatcher()
    
    with pytest.raises(TrackIdentificationError) as exc_info:
        matcher.process_file(Path("/nonexistent/file.mp3"))
    assert "Failed to process audio file" in str(exc_info.value)

def test_invalid_audio_format(test_env, tmp_path):
    """Test handling of invalid audio format."""
    # Create a text file with .mp3 extension
    invalid_file = tmp_path / "invalid.mp3"
    invalid_file.write_text("This is not an MP3 file")
    
    matcher = TrackMatcher()
    
    with pytest.raises(TrackIdentificationError) as exc_info:
        matcher.process_file(invalid_file)
    assert "Failed to process audio file" in str(exc_info.value)

def test_zero_confidence_tracks(test_env, mock_audio_file):
    """Test handling of tracks with zero confidence."""
    matcher = TrackMatcher()
    
    # Set confidence threshold to filter out all tracks
    matcher.min_confidence = 100
    tracks = matcher.process_file(mock_audio_file)
    
    # Should return empty list when all tracks are filtered
    assert len(tracks) == 0

def test_identical_tracks(test_env, mock_audio_file):
    """Test handling of identical tracks at different timestamps."""
    matcher = TrackMatcher()
    
    # Allow duplicates for this test
    matcher.max_duplicates = 2
    matcher.time_threshold = 1  # Set small threshold to allow nearby duplicates
    
    # Process file and get tracks
    tracks = matcher.process_file(mock_audio_file)
    
    # Count occurrences of each track
    track_counts = {}
    for track in tracks:
        key = (track.song_name, track.artist)
        track_counts[key] = track_counts.get(key, 0) + 1
        
    # No track should appear more than max_duplicates times
    assert all(count <= matcher.max_duplicates for count in track_counts.values())

def test_track_timestamp_ordering(test_env, mock_audio_file):
    """Test that tracks are returned in chronological order."""
    matcher = TrackMatcher()
    
    tracks = matcher.process_file(mock_audio_file)
    
    # Convert timestamps to seconds and check ordering
    timestamps = [track.time_to_seconds() for track in tracks]
    assert timestamps == sorted(timestamps), "Tracks should be in chronological order"

def test_edge_case_confidence_values(test_env, mock_audio_file):
    """Test handling of edge case confidence values."""
    matcher = TrackMatcher()
    
    # Test various confidence thresholds
    test_cases = [-1, 0, 50, 99, 100, 101]
    for threshold in test_cases:
        matcher.min_confidence = threshold
        tracks = matcher.process_file(mock_audio_file)
        
        # Ensure all returned tracks meet the valid confidence threshold
        valid_threshold = max(0, min(threshold, 100))
        assert all(track.confidence >= valid_threshold for track in tracks)

@pytest.mark.integration
def test_track_metadata_validation(test_env, mock_audio_file):
    """Test validation of track metadata."""
    matcher = TrackMatcher()
    
    tracks = matcher.process_file(mock_audio_file)
    
    for track in tracks:
        # Basic metadata validation
        assert isinstance(track.song_name, str)
        assert len(track.song_name.strip()) > 0
        assert isinstance(track.artist, str)
        assert len(track.artist.strip()) > 0
        
        # Time format validation
        assert re.match(r'^\d{2}:\d{2}:\d{2}$', track.time_in_mix)
        time_parts = track.time_in_mix.split(':')
        assert 0 <= int(time_parts[0]) <= 23  # Hours
        assert 0 <= int(time_parts[1]) <= 59  # Minutes
        assert 0 <= int(time_parts[2]) <= 59  # Seconds
        
        # Confidence validation
        assert isinstance(track.confidence, (int, float))
        assert 0 <= track.confidence <= 100
