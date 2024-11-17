"""
Unit tests for Track class.
"""

import json
from pathlib import Path
import pytest
from dataclasses import FrozenInstanceError
from tracklistify.track import Track
from tests.conftest import (
    TEST_TRACK_TITLE,
    TEST_TRACK_ARTIST,
    TEST_TRACK_ALBUM,
    TEST_TRACK_DURATION,
    TEST_TRACK_CONFIDENCE
)

def test_track_creation():
    """Test Track object creation."""
    track = Track(
        song_name=TEST_TRACK_TITLE,
        artist=TEST_TRACK_ARTIST,
        time_in_mix="00:00:00",
        confidence=TEST_TRACK_CONFIDENCE
    )
    assert track.song_name == TEST_TRACK_TITLE
    assert track.artist == TEST_TRACK_ARTIST
    assert track.time_in_mix == "00:00:00"
    assert track.confidence == TEST_TRACK_CONFIDENCE
    assert track.start_time is None
    assert track.end_time is None
    assert track.timing_confidence is None

def test_track_serialization():
    """Test Track serialization/deserialization."""
    track = Track(
        song_name=TEST_TRACK_TITLE,
        artist=TEST_TRACK_ARTIST,
        time_in_mix="00:00:00",
        confidence=TEST_TRACK_CONFIDENCE
    )
    
    # Test to_dict
    track_dict = track.to_dict()
    assert isinstance(track_dict, dict)
    assert track_dict["song_name"] == TEST_TRACK_TITLE
    assert track_dict["artist"] == TEST_TRACK_ARTIST
    assert track_dict["time_in_mix"] == "00:00:00"
    assert track_dict["confidence"] == TEST_TRACK_CONFIDENCE
    assert track_dict["start_time"] is None
    assert track_dict["end_time"] is None
    assert track_dict["timing_confidence"] is None

    # Test from_dict
    new_track = Track.from_dict(track_dict)
    assert new_track.song_name == track.song_name
    assert new_track.artist == track.artist
    assert new_track.time_in_mix == track.time_in_mix
    assert new_track.confidence == track.confidence

def test_track_timing():
    """Test track timing functionality."""
    track = Track("Test Song", "Test Artist", "00:00:00", 100)
    assert track.timing is None
    assert track.duration is None
    assert track.format_duration() == "--:--"

    # Set timing
    track.set_timing(0, 180, 90)  # 3 minutes
    assert track.timing is not None
    assert track.duration == 180
    assert track.format_duration() == "03:00"

    # Test invalid timing
    with pytest.raises(ValueError):
        track.set_timing(180, 0, 90)  # End before start

def test_track_overlap():
    """Test track overlap detection."""
    track1 = Track("Song 1", "Artist 1", "00:00:00", 100)
    track2 = Track("Song 2", "Artist 2", "00:03:00", 100)
    
    # No timing set
    assert not track1.overlaps_with(track2)
    
    # Set timing with gap
    track1.set_timing(0, 180, 90)  # 0-3 minutes
    track2.set_timing(240, 420, 90)  # 4-7 minutes
    assert not track1.overlaps_with(track2)
    assert track1.gap_to(track2) == 60  # 1 minute gap
    
    # Set timing with overlap
    track2.set_timing(120, 300, 90)  # 2-5 minutes
    assert track1.overlaps_with(track2)
    assert track1.gap_to(track2) == 0

def test_track_similarity():
    """Test track similarity matching."""
    base_track = Track("Original Song", "Test Artist", "00:00:00", 100)
    
    # Exact match
    exact_match = Track("Original Song", "Test Artist", "00:03:00", 100)
    assert base_track.is_similar_to(exact_match)
    
    # Similar name (90% similarity)
    similar_name = Track("Original Songg", "Test Artist", "00:03:00", 100)
    assert base_track.is_similar_to(similar_name)
    
    # Different name (below threshold)
    different_name = Track("Different Song", "Test Artist", "00:03:00", 100)
    assert not base_track.is_similar_to(different_name)
    
    # Remix version
    remix = Track("Original Song (Club Remix)", "Test Artist", "00:03:00", 100)
    assert base_track.is_similar_to(remix)
    
    # Different artist
    different_artist = Track("Original Song", "Other Artist", "00:03:00", 100)
    assert not base_track.is_similar_to(different_artist)
    
    # Similar artist (90% similarity)
    similar_artist = Track("Original Song", "Test Artisst", "00:03:00", 100)
    assert base_track.is_similar_to(similar_artist)

def test_track_validation():
    """Test Track validation."""
    # Test valid track
    track = Track(
        song_name=TEST_TRACK_TITLE,
        artist=TEST_TRACK_ARTIST,
        time_in_mix="00:00:00",
        confidence=TEST_TRACK_CONFIDENCE
    )
    
    # Test empty song name
    with pytest.raises(ValueError):
        Track(
            song_name="",
            artist=TEST_TRACK_ARTIST,
            time_in_mix="00:00:00",
            confidence=TEST_TRACK_CONFIDENCE
        )
    
    # Test invalid confidence
    with pytest.raises(ValueError):
        Track(
            song_name=TEST_TRACK_TITLE,
            artist=TEST_TRACK_ARTIST,
            time_in_mix="00:00:00",
            confidence=101  # Over 100
        )

def test_track_comparison():
    """Test Track comparison methods."""
    track1 = Track(
        song_name=TEST_TRACK_TITLE,
        artist=TEST_TRACK_ARTIST,
        time_in_mix="00:00:00",
        confidence=TEST_TRACK_CONFIDENCE
    )
    
    track2 = Track(
        song_name=TEST_TRACK_TITLE,
        artist=TEST_TRACK_ARTIST,
        time_in_mix="00:00:00",
        confidence=TEST_TRACK_CONFIDENCE
    )
    
    # Test equality
    assert track1.song_name == track2.song_name
    assert track1.artist == track2.artist
    assert track1.time_in_mix == track2.time_in_mix
    assert track1.confidence == track2.confidence

def test_track_string_representation():
    """Test Track string representation."""
    track = Track(
        song_name=TEST_TRACK_TITLE,
        artist=TEST_TRACK_ARTIST,
        time_in_mix="00:00:00",
        confidence=TEST_TRACK_CONFIDENCE
    )
    
    # Test str representation
    str_rep = str(track)
    assert TEST_TRACK_TITLE in str_rep
    assert TEST_TRACK_ARTIST in str_rep
    assert "00:00:00" in str_rep
    
    # Test repr
    repr_str = repr(track)
    assert "Track" in repr_str
    assert TEST_TRACK_TITLE in repr_str

def test_track_mutability():
    """Test Track mutability."""
    track = Track(
        song_name=TEST_TRACK_TITLE,
        artist=TEST_TRACK_ARTIST,
        time_in_mix="00:00:00",
        confidence=TEST_TRACK_CONFIDENCE
    )
    
    # Test that timing fields are mutable
    track.start_time = 0
    track.end_time = 120
    track.timing_confidence = 90.0
    
    assert track.start_time == 0
    assert track.end_time == 120
    assert track.timing_confidence == 90.0

def test_track_timing_properties():
    """Test track timing property getters and setters."""
    track = Track("Test Song", "Test Artist", "00:00:00", 100)
    
    # Test start_time property
    track.start_time = 60
    assert track.start_time == 60
    assert track.end_time == 60
    assert track.timing_confidence == 100.0
    
    # Test end_time property
    track.end_time = 180
    assert track.start_time == 60
    assert track.end_time == 180
    assert track.timing_confidence == 100.0
    
    # Test timing_confidence property
    track.timing_confidence = 90.0
    assert track.timing_confidence == 90.0
    
    # Test invalid start_time
    with pytest.raises(ValueError, match="Start time must be a number"):
        track.start_time = "invalid"
    with pytest.raises(ValueError, match="Start time cannot be greater than end time"):
        track.start_time = 200
    
    # Test invalid end_time
    with pytest.raises(ValueError, match="End time must be a number"):
        track.end_time = "invalid"
    with pytest.raises(ValueError, match="End time cannot be less than start time"):
        track.end_time = 30
    
    # Test clearing timing
    track.start_time = None
    assert track.timing is None
    assert track.start_time is None
    assert track.end_time is None
    assert track.timing_confidence is None

def test_track_format_methods():
    """Test track formatting methods."""
    track = Track("Test Song", "Test Artist", "00:00:00", 100)
    track.set_timing(0, 180, 90)
    
    # Test markdown_line property
    markdown = track.markdown_line
    assert "Test Song" in markdown
    assert "Test Artist" in markdown
    assert "00:00:00" in markdown
    assert "100%" in markdown
    
    # Test m3u_line property
    m3u = track.m3u_line
    assert "Test Song" in m3u
    assert "Test Artist" in m3u

def test_track_time_conversion():
    """Test time conversion methods."""
    track = Track("Test Song", "Test Artist", "01:30:00", 100)
    
    # Test time_to_seconds
    assert track.time_to_seconds() == 5400  # 1h30m = 5400s
    
    # Test invalid time format
    track.time_in_mix = "invalid"
    assert track.time_to_seconds() == 0

def test_track_string_normalization():
    """Test string normalization methods."""
    track = Track("Test Song", "Test Artist", "00:00:00", 100)
    
    # Test _normalize_string
    assert track._normalize_string("  Test  String  ") == "test string"
    assert track._normalize_string("Test-String") == "teststring"
    
    # Test _normalize_artist
    assert track._normalize_artist("DJ Test & Other Artist") == "dj test  other artist"
    assert track._normalize_artist("Test feat. Other") == "test"
    
    # Test _extract_base_name
    assert track._extract_base_name("Test Song (Club Mix)") == "test song"
    assert track._extract_base_name("Test Song [Radio Edit]") == "test song"
    assert track._extract_base_name("Test Song - Extended Version") == "test song"

def test_track_similarity_edge_cases():
    """Test track similarity matching edge cases."""
    track1 = Track("Test Song", "Test Artist", "00:00:00", 100)
    
    # Test with None values
    track2 = Track("None", "None", "00:00:00", 100)
    assert not track1.is_similar_to(track2)
    
    # Test with very short strings
    track3 = Track("Te", "Ar", "00:00:00", 100)
    assert not track1.is_similar_to(track3)
    
    # Test with special characters
    track4 = Track("Test Song!!!", "Test Artist???", "00:00:00", 100)
    assert track1.is_similar_to(track4)
    
    # Test remix detection
    track5 = Track("Test Song (Club Mix)", "Test Artist", "00:00:00", 100)
    assert track1.is_similar_to(track5)
    track6 = Track("Test Song [Radio Edit]", "Test Artist", "00:00:00", 100)
    assert track1.is_similar_to(track6)
    track7 = Track("Test Song - Extended Version", "Test Artist", "00:00:00", 100)
    assert track1.is_similar_to(track7)
