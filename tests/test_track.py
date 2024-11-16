"""
Unit tests for Track class.
"""

import pytest
from tracklistify.track import Track, TrackMatcher

def test_track_creation():
    """Test Track instance creation."""
    track = Track(
        song_name="Test Track",
        artist="Test Artist",
        time_in_mix="00:00:00",
        confidence=90.0
    )
    
    assert track.song_name == "Test Track"
    assert track.artist == "Test Artist"
    assert track.time_in_mix == "00:00:00"
    assert track.confidence == 90.0

def test_track_string_representation():
    """Test Track string representation."""
    track = Track(
        song_name="Test Track",
        artist="Test Artist",
        time_in_mix="00:00:00",
        confidence=90.0
    )
    
    expected = "00:00:00 - Test Artist - Test Track (90%)"
    assert str(track) == expected

def test_track_similarity():
    """Test track similarity comparison."""
    track1 = Track(
        song_name="Test Track",
        artist="Test Artist",
        time_in_mix="00:00:00",
        confidence=90.0
    )
    
    track2 = Track(
        song_name="Test Track (Extended Mix)",
        artist="Test Artist feat. Someone",
        time_in_mix="00:00:30",
        confidence=85.0
    )
    
    assert track1.is_similar_to(track2)

def test_track_matcher():
    """Test TrackMatcher functionality."""
    matcher = TrackMatcher()
    
    # Add tracks with different confidence levels
    track1 = Track(
        song_name="Test Track",
        artist="Test Artist",
        time_in_mix="00:00:00",
        confidence=90.0
    )
    
    track2 = Track(
        song_name="Test Track",
        artist="Test Artist",
        time_in_mix="00:00:30",
        confidence=85.0
    )
    
    track3 = Track(
        song_name="Different Track",
        artist="Other Artist",
        time_in_mix="00:05:00",
        confidence=95.0
    )
    
    matcher.add_track(track1)
    matcher.add_track(track2)
    matcher.add_track(track3)
    
    merged_tracks = matcher.merge_nearby_tracks()
    assert len(merged_tracks) == 2  # track1 and track2 should be merged

def test_track_matcher_confidence_threshold():
    """Test TrackMatcher confidence threshold."""
    matcher = TrackMatcher()
    matcher.min_confidence = 90.0
    
    low_confidence_track = Track(
        song_name="Test Track",
        artist="Test Artist",
        time_in_mix="00:00:00",
        confidence=85.0
    )
    
    high_confidence_track = Track(
        song_name="Test Track",
        artist="Test Artist",
        time_in_mix="00:05:00",
        confidence=95.0
    )
    
    matcher.add_track(low_confidence_track)
    matcher.add_track(high_confidence_track)
    
    merged_tracks = matcher.merge_nearby_tracks()
    assert len(merged_tracks) == 1  # Only high confidence track should remain
