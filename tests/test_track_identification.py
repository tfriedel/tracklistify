"""
Integration tests for track identification functionality.
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from tracklistify.track import Track, TrackMatcher, TrackTiming
from tracklistify.config import get_config
from tracklistify.exceptions import TrackIdentificationError
import re
from unittest.mock import patch, MagicMock

@pytest.fixture
def sample_track():
    """Create a sample track for testing."""
    track = Track(
        song_name="Test Song",
        artist="Test Artist",
        time_in_mix="00:01:30",
        confidence=95.0
    )
    track.set_timing(90.0, 210.0, 90.0)
    return track

@pytest.fixture
def sample_track_timing():
    """Create a sample track timing for testing."""
    return TrackTiming(
        start_time=90.0,
        end_time=210.0,
        confidence=90.0
    )

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

    # Mock the provider to return different tracks for different segments
    def mock_identify_tracks(file_path, start_time=0, duration=None):
        if start_time == 0:
            return [Track("Test Track 1", "Test Artist 1", "00:00:00", 90.0)]
        else:
            return [Track("Test Track 2", "Test Artist 2", "00:00:30", 85.0)]

    # Create a mock provider instance
    mock_provider = MagicMock()
    mock_provider.identify_tracks.side_effect = mock_identify_tracks

    # Patch the provider factory to return our mock provider
    with patch('tracklistify.providers.factory.create_provider', return_value=mock_provider):
        tracks = matcher.process_file(mock_audio_file)
        
        # Our test file is 60 seconds, with 30 second segments we expect 2 segments
        assert len(tracks) >= 2, "Should identify at least 2 tracks from different segments"

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

def test_track_timing_calculations(sample_track_timing):
    """Test track timing calculations."""
    # Test duration calculation
    assert sample_track_timing.duration == 120.0  # 210 - 90 = 120 seconds
    
    # Test overlap detection
    overlapping = TrackTiming(start_time=180.0, end_time=240.0, confidence=85.0)
    non_overlapping = TrackTiming(start_time=300.0, end_time=360.0, confidence=85.0)
    
    assert sample_track_timing.overlaps_with(overlapping)
    assert not sample_track_timing.overlaps_with(non_overlapping)
    
    # Test gap calculation
    assert sample_track_timing.gap_to(non_overlapping) == 90.0  # 300 - 210 = 90
    assert sample_track_timing.gap_to(overlapping) == 0.0  # Overlapping tracks have no gap

def test_track_serialization(sample_track):
    """Test track serialization and deserialization."""
    # Test to_dict
    track_dict = sample_track.to_dict()
    assert isinstance(track_dict, dict)
    assert track_dict["song_name"] == "Test Song"
    assert track_dict["artist"] == "Test Artist"
    assert track_dict["time_in_mix"] == "00:01:30"
    assert track_dict["confidence"] == 95.0
    assert track_dict["start_time"] == 90
    assert track_dict["end_time"] == 210
    assert track_dict["timing_confidence"] == 90.0
    
    # Test from_dict
    new_track = Track.from_dict(track_dict)
    assert new_track.song_name == sample_track.song_name
    assert new_track.artist == sample_track.artist
    assert new_track.time_in_mix == sample_track.time_in_mix
    assert new_track.confidence == sample_track.confidence
    assert new_track.start_time == sample_track.start_time
    assert new_track.end_time == sample_track.end_time
    assert new_track.timing_confidence == sample_track.timing_confidence

def test_track_list_operations():
    """Test track list operations in TrackMatcher."""
    matcher = TrackMatcher()
    
    # Create test tracks
    track1 = Track("Song 1", "Artist 1", "00:00:00", 95.0)
    track2 = Track("Song 2", "Artist 2", "00:01:00", 90.0)
    track3 = Track("Song 3", "Artist 3", "00:02:00", 85.0)
    
    # Test track addition
    matcher.add_track(track1)
    assert len(matcher.tracks) == 1
    
    # Test confidence filtering
    matcher.min_confidence = 92.0
    matcher.add_track(track2)  # Should not be added (90 < 92)
    assert len(matcher.tracks) == 1
    
    # Test track ordering
    matcher.min_confidence = 80.0  # Lower threshold to allow all tracks
    matcher.add_track(track2)
    matcher.add_track(track3)
    
    # Verify chronological ordering
    times = [track.time_in_mix for track in matcher.tracks]
    assert times == ["00:00:00", "00:01:00", "00:02:00"]

def test_track_comparison():
    """Test track comparison and matching logic."""
    # Create similar tracks
    track1 = Track("Song Name", "Artist", "00:00:00", 95.0)
    track2 = Track("Song Name", "Artist", "00:00:05", 90.0)  # Same song, slightly different time
    track3 = Track("Different Song", "Artist", "00:00:00", 85.0)
    
    matcher = TrackMatcher()
    matcher.time_threshold = 10  # Set small threshold for testing
    
    # Add tracks and test merging
    matcher.add_track(track1)
    matcher.add_track(track2)
    matcher.add_track(track3)
    
    merged_tracks = matcher.merge_nearby_tracks()
    
    # After merging, we should have 2 tracks (track1 and track2 merged, track3 separate)
    assert len(merged_tracks) == 2
    
    # Verify the higher confidence track was kept
    remaining_tracks = [t for t in merged_tracks if t.song_name == "Song Name"]
    assert len(remaining_tracks) == 1
    assert remaining_tracks[0].confidence == 95.0

def test_track_timing_edge_cases():
    """Test edge cases in track timing."""
    # Test zero duration
    zero_duration = TrackTiming(start_time=100.0, end_time=100.0, confidence=80.0)
    assert zero_duration.duration == 0.0
    
    # Test negative duration (should not occur in practice)
    negative_duration = TrackTiming(start_time=100.0, end_time=90.0, confidence=80.0)
    assert negative_duration.duration == -10.0
    
    # Test touching but not overlapping tracks
    timing1 = TrackTiming(start_time=0.0, end_time=100.0, confidence=90.0)
    timing2 = TrackTiming(start_time=100.0, end_time=200.0, confidence=90.0)
    assert not timing1.overlaps_with(timing2)
    assert timing1.gap_to(timing2) == 0.0

def test_track_time_format_errors():
    """Test handling of invalid time formats."""
    # Invalid time format
    track = Track("Test Song", "Test Artist", "25:00:00", 95.0)  # Invalid hour
    assert track.time_to_seconds() == 0.0
    
    # Missing components
    track = Track("Test Song", "Test Artist", "5:00", 95.0)  # Missing hour
    assert track.time_to_seconds() == 0.0
    
    # Invalid characters
    track = Track("Test Song", "Test Artist", "aa:bb:cc", 95.0)
    assert track.time_to_seconds() == 0.0

def test_track_timing_validation():
    """Test track timing validation and edge cases."""
    track = Track("Test Song", "Test Artist", "00:00:00", 95.0)

    # Test unset timing
    assert track.format_duration() == "--:--"
    assert not track.overlaps_with(Track("Other Song", "Other Artist", "00:01:00", 90.0))
    assert track.gap_to(Track("Other Song", "Other Artist", "00:01:00", 90.0)) is None

    # Set timing
    track.set_timing(0, 60, 90.0)
    assert track.format_duration() == "01:00"

    # Test partial timing
    partial_track = Track("Partial Song", "Test Artist", "00:01:00", 90.0)
    partial_track.set_timing(90, 120, 85.0)  # Set non-overlapping timing
    assert partial_track.start_time == 90
    assert partial_track.end_time == 120
    assert partial_track.timing.confidence == 85.0
    assert not track.overlaps_with(partial_track)
    assert track.gap_to(partial_track) == 30  # Gap should be 30 seconds

def test_track_similarity_edge_cases():
    """Test track similarity comparison edge cases."""
    # Test exact matches with different formatting
    track1 = Track("Test Song", "Main Artist feat. Other Artist", "00:00:00", 95.0)
    track2 = Track("Test Song", "Main Artist featuring Other Artist", "00:01:00", 90.0)
    assert track1.is_similar_to(track2)

    # Test remixes
    track3 = Track("Test Song (Club Mix)", "Main Artist", "00:02:00", 85.0)
    track4 = Track("Test Song", "Main Artist", "00:03:00", 80.0)
    assert track3.is_similar_to(track4)

    # Test non-similar tracks
    track5 = Track("Different Song", "Different Artist", "00:04:00", 75.0)
    assert not track1.is_similar_to(track5)

def test_track_similarity_complex():
    """Test more complex track similarity scenarios."""
    base_track = Track("Original Song", "Main Artist", "00:00:00", 95.0)

    # Test various remix formats
    remix_tracks = [
        Track("Original Song (Club Mix)", "Main Artist", "00:01:00", 90.0),
        Track("Original Song - Extended Mix", "Main Artist", "00:02:00", 85.0),
        Track("Original Song [Radio Edit]", "Main Artist", "00:03:00", 80.0),
        Track("Original Song (Original Mix)", "Main Artist", "00:04:00", 75.0),
    ]

    for remix in remix_tracks:
        assert base_track.is_similar_to(remix), f"Failed to match: {remix}"

    # Test artist variations
    artist_variations = [
        Track("Original Song", "Main Artist featuring Artist One", "00:05:00", 70.0),
        Track("Original Song", "Main Artist ft. Artist One", "00:06:00", 65.0),
        Track("Original Song", "Main Artist feat Artist One", "00:07:00", 60.0),
    ]

    for variation in artist_variations:
        assert base_track.is_similar_to(variation), f"Failed to match: {variation}"

    # Test non-matching tracks
    non_matching = [
        Track("Different Song", "Main Artist", "00:08:00", 55.0),
        Track("Original Different", "Other Artist", "00:09:00", 50.0),
        Track("Original Song 2", "Main Artist", "00:10:00", 45.0),
    ]

    for non_match in non_matching:
        assert not base_track.is_similar_to(non_match), f"Should not match: {non_match}"

def test_track_matcher_edge_cases():
    """Test TrackMatcher edge cases."""
    matcher = TrackMatcher()
    
    # Test empty track list
    assert matcher.merge_nearby_tracks() == []
    
    # Test single track
    track = Track("Test Song", "Test Artist", "00:00:00", 95.0)
    matcher.add_track(track)
    merged = matcher.merge_nearby_tracks()
    assert len(merged) == 1
    assert merged[0] == track
    
    # Test confidence threshold
    matcher.min_confidence = 95  # Set high threshold
    track_below = Track("Below Threshold", "Test Artist", "00:01:00", 94.9)
    matcher.add_track(track_below)  # Should not be added
    assert len([t for t in matcher.tracks if t.song_name == "Below Threshold"]) == 0
    
    # Test track ordering
    track_later = Track("Later Song", "Test Artist", "00:02:00", 96.0)
    matcher.add_track(track_later)
    merged = matcher.merge_nearby_tracks()
    assert len(merged) == 2
    assert merged[0].time_in_mix < merged[1].time_in_mix

def test_track_format_methods():
    """Test track formatting methods."""
    track = Track("Test Song", "Test Artist", "01:30:00", 95.0)
    
    # Test string representation without timing
    assert str(track) == "01:30:00 - Test Artist - Test Song (95%)"
    
    # Test string representation with timing
    track.set_timing(90, 210, 90.0)
    assert str(track) == "01:30:00 - Test Artist - Test Song [02:00] (95%)"
    
    # Test markdown formatting
    assert track.markdown_line == "- [01:30:00] **Test Artist** - Test Song (95%)"
    
    # Test M3U formatting
    assert track.m3u_line == "#EXTINF:-1,Test Artist - Test Song"

def test_track_timing_edge_cases_extended():
    """Test track timing edge cases more thoroughly."""
    track = Track("Test Song", "Test Artist", "01:30:00", 95.0)
    
    # Test invalid time format
    track.time_in_mix = "invalid"
    assert track.time_to_seconds() == 0.0
    
    # Test format_duration with no timing
    assert track.format_duration() == "--:--"
    
    # Test format_duration with timing
    track.set_timing(3665, 3725, 90.0)  # 1h 1m 5s to 1h 2m 5s (60s duration)
    assert track.format_duration() == "01:00"
    
    # Test gap calculation with missing timing
    other_track = Track("Other Song", "Other Artist", "02:00:00", 90.0)
    assert track.gap_to(other_track) is None
    
    # Test gap calculation with valid timing
    other_track.set_timing(3800, 4000, 90.0)
    assert track.gap_to(other_track) == 75.0  # 75 second gap
    
    # Test overlapping tracks
    track.set_timing(100, 200, 90.0)
    other_track.set_timing(150, 250, 90.0)
    assert track.overlaps_with(other_track)
    assert other_track.overlaps_with(track)

def test_track_similarity_complex():
    """Test more complex track similarity scenarios."""
    base_track = Track("Original Song", "Main Artist", "00:00:00", 95.0)

    # Test various remix formats
    remix_tracks = [
        Track("Original Song (Club Mix)", "Main Artist", "00:01:00", 90.0),
        Track("Original Song - Extended Mix", "Main Artist", "00:02:00", 85.0),
        Track("Original Song [Radio Edit]", "Main Artist", "00:03:00", 80.0),
        Track("Original Song (Original Mix)", "Main Artist", "00:04:00", 75.0),
    ]

    for remix in remix_tracks:
        assert base_track.is_similar_to(remix), f"Failed to match: {remix}"

    # Test artist variations
    artist_variations = [
        Track("Original Song", "Main Artist featuring Artist One", "00:05:00", 70.0),
        Track("Original Song", "Main Artist ft Artist One", "00:06:00", 65.0),
        Track("Original Song", "Main Artist feat Artist One", "00:07:00", 60.0),
    ]

    for variation in artist_variations:
        assert base_track.is_similar_to(variation), f"Failed to match: {variation}"
    
    # Test non-matching tracks
    non_matching = [
        Track("Different Song", "Main Artist", "00:08:00", 55.0),
        Track("Original Different", "Other Artist", "00:09:00", 50.0),
        Track("Original Song 2", "Main Artist", "00:10:00", 45.0),
    ]

    for non_match in non_matching:
        assert not base_track.is_similar_to(non_match), f"Should not match: {non_match}"

def test_track_matcher_performance():
    """Test track matcher performance with a large number of tracks."""
    import time
    
    # Create a large number of similar tracks
    num_tracks = 100
    tracks = []
    for i in range(num_tracks):
        # Add some variation to create potential matches
        remix_type = ["Original Mix", "Radio Edit", "Club Mix", "Extended Mix"][i % 4]
        track = Track(f"Test Song ({remix_type})", f"Artist {i % 10}", f"00:{i:02d}:00", 90.0)
        tracks.append(track)
    
    # Measure time to process tracks
    matcher = TrackMatcher()
    start_time = time.time()
    
    for track in tracks:
        matcher.add_track(track)
    
    processing_time = time.time() - start_time
    
    # Assert reasonable performance (should process 100 tracks in under 1 second)
    assert processing_time < 1.0, f"Track matching took too long: {processing_time:.2f} seconds"
    
    # Verify results
    assert len(matcher.tracks) <= num_tracks, "Track matcher should deduplicate similar tracks"
    
    # Test confidence threshold
    high_confidence_tracks = [t for t in matcher.tracks if t.confidence >= 90.0]
    assert len(high_confidence_tracks) > 0, "Should retain high confidence tracks"
