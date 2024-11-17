"""
Tests for track timing functionality.
"""

import pytest
from tracklistify.track import Track, TrackTiming

# Test Data
TEST_TRACK_TITLE = "Test Song"
TEST_TRACK_ARTIST = "Test Artist"
TEST_TRACK_TIME = "00:00:00"
TEST_TRACK_CONFIDENCE = 90.0

@pytest.fixture
def track():
    """Create a test track."""
    return Track(TEST_TRACK_TITLE, TEST_TRACK_ARTIST, TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)

def test_track_timing_creation(track):
    """Test track timing initialization."""
    # Initial state
    assert track.timing is None
    assert track.duration is None
    assert track.format_duration() == "--:--"
    
    # Set timing
    track.set_timing(10.0, 20.0, 90.0)
    assert track.timing is not None
    assert track.timing.start_time == 10.0
    assert track.timing.end_time == 20.0
    assert track.timing.confidence == 90.0

def test_track_timing_duration(track):
    """Test track duration calculation."""
    track.set_timing(0.0, 180.0, 90.0)  # 3 minutes
    assert track.duration == 180.0
    assert track.format_duration() == "03:00"

def test_track_timing_zero_duration(track):
    """Test handling of zero duration."""
    track.set_timing(10.0, 10.0, 90.0)
    assert track.duration == 0.0
    assert track.format_duration() == "00:00"

def test_track_timing_negative_duration(track):
    """Test handling of invalid negative duration."""
    with pytest.raises(ValueError, match="End time cannot be less than start time"):
        track.set_timing(20.0, 10.0, 90.0)

def test_track_overlap_detection():
    """Test overlap detection between tracks."""
    track1 = Track("Track 1", "Artist 1", "00:00:00", 90.0)
    track2 = Track("Track 2", "Artist 2", "00:03:00", 90.0)
    
    # No timing set
    assert not track1.overlaps_with(track2)
    
    # Setup overlapping tracks
    track1.set_timing(0.0, 190.0, 90.0)  # 0:00 - 3:10
    track2.set_timing(180.0, 360.0, 90.0)  # 3:00 - 6:00
    
    # Test overlap
    assert track1.overlaps_with(track2)
    assert track2.overlaps_with(track1)
    assert track1.gap_to(track2) == 0.0

def test_track_gap_detection():
    """Test gap detection between tracks."""
    track1 = Track("Track 1", "Artist 1", "00:00:00", 90.0)
    track2 = Track("Track 2", "Artist 2", "00:03:00", 90.0)
    
    # Setup tracks with gap
    track1.set_timing(0.0, 170.0, 90.0)  # 0:00 - 2:50
    track2.set_timing(180.0, 360.0, 90.0)  # 3:00 - 6:00
    
    # Test gap
    assert track1.gap_to(track2) == 10.0
    assert not track1.overlaps_with(track2)

def test_track_timing_validation():
    """Test timing validation."""
    track = Track("Test Track", "Test Artist", "00:00:00", 90.0)
    
    # Test valid timing
    track.set_timing(0.0, 180.0, 90.0)
    assert track.timing is not None
    
    # Test invalid confidence
    with pytest.raises(ValueError):
        track.set_timing(0.0, 180.0, -1.0)
    with pytest.raises(ValueError):
        track.set_timing(0.0, 180.0, 101.0)

def test_format_duration_edge_cases(track):
    """Test duration formatting edge cases."""
    # Test very short duration
    track.set_timing(0.0, 0.5, 90.0)
    assert track.format_duration() == "00:01"  # Round up to 1 second
    
    # Test hour+ duration
    track.set_timing(0.0, 3665.0, 90.0)  # 1:01:05
    assert track.format_duration() == "61:05"  # We use MM:SS format
    
    # Test exact minute
    track.set_timing(0.0, 60.0, 90.0)
    assert track.format_duration() == "01:00"

def test_track_timing_serialization(track):
    """Test timing serialization."""
    # Set timing
    track.set_timing(0.0, 180.0, 90.0)
    
    # Convert to dict
    data = track.to_dict()
    assert data["start_time"] == 0.0
    assert data["end_time"] == 180.0
    assert data["timing_confidence"] == 90.0
    
    # Create new track from dict
    new_track = Track.from_dict(data)
    assert new_track.timing is not None
    assert new_track.timing.start_time == 0.0
    assert new_track.timing.end_time == 180.0
    assert new_track.timing.confidence == 90.0
