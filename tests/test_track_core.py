import pytest
from tracklistify.track import Track, TrackTiming

# Test Data
TEST_TRACK_TITLE = "Test Song"
TEST_TRACK_ARTIST = "Test Artist"
TEST_TRACK_TIME = "00:00:00"
TEST_TRACK_CONFIDENCE = 90.0

def test_track_creation():
    """Test basic track creation."""
    track = Track(TEST_TRACK_TITLE, TEST_TRACK_ARTIST, TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)
    assert track.song_name == TEST_TRACK_TITLE
    assert track.artist == TEST_TRACK_ARTIST
    assert track.time_in_mix == TEST_TRACK_TIME
    assert track.confidence == TEST_TRACK_CONFIDENCE
    assert track.timing is None

def test_track_validation():
    """Test input validation."""
    # Test empty song name
    with pytest.raises(ValueError, match="Song name cannot be empty"):
        Track("", TEST_TRACK_ARTIST, TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)
    
    # Test empty artist
    with pytest.raises(ValueError, match="Artist cannot be empty"):
        Track(TEST_TRACK_TITLE, "", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)
    
    # Test empty time
    with pytest.raises(ValueError, match="Time in mix cannot be empty"):
        Track(TEST_TRACK_TITLE, TEST_TRACK_ARTIST, "", TEST_TRACK_CONFIDENCE)
    
    # Test invalid confidence
    with pytest.raises(ValueError, match="Confidence must be a number between 0 and 100"):
        Track(TEST_TRACK_TITLE, TEST_TRACK_ARTIST, TEST_TRACK_TIME, -1)
    with pytest.raises(ValueError, match="Confidence must be a number between 0 and 100"):
        Track(TEST_TRACK_TITLE, TEST_TRACK_ARTIST, TEST_TRACK_TIME, 101)

def test_track_serialization():
    """Test track serialization."""
    track = Track(TEST_TRACK_TITLE, TEST_TRACK_ARTIST, TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)
    
    # Test serialization without timing
    data = track.to_dict()
    assert data["song_name"] == TEST_TRACK_TITLE
    assert data["artist"] == TEST_TRACK_ARTIST
    assert data["time_in_mix"] == TEST_TRACK_TIME
    assert data["confidence"] == TEST_TRACK_CONFIDENCE
    
    # Test serialization with timing
    track.set_timing(0, 180, 95)
    data = track.to_dict()
    assert data["start_time"] == 0
    assert data["end_time"] == 180
    assert data["timing_confidence"] == 95
    
    # Test deserialization
    new_track = Track.from_dict(data)
    assert new_track.song_name == track.song_name
    assert new_track.artist == track.artist
    assert new_track.time_in_mix == track.time_in_mix
    assert new_track.confidence == track.confidence
    assert new_track.timing.start_time == 0
    assert new_track.timing.end_time == 180
    assert new_track.timing.confidence == 95

def test_track_string_representation():
    """Test string representation."""
    track = Track(TEST_TRACK_TITLE, TEST_TRACK_ARTIST, TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)
    
    # Test without timing
    expected = f"{TEST_TRACK_TIME} - {TEST_TRACK_ARTIST} - {TEST_TRACK_TITLE} (90%)"
    assert str(track) == expected
    
    # Test with timing
    track.set_timing(0, 180, 95)  # 3 minutes
    expected = f"{TEST_TRACK_TIME} - {TEST_TRACK_ARTIST} - {TEST_TRACK_TITLE} [03:00] (90%)"
    assert str(track) == expected
