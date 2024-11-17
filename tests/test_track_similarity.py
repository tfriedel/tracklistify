"""
Tests for track similarity matching functionality.
"""

import pytest
from tracklistify.track import Track

# Test Data
TEST_TRACK_TIME = "00:00:00"
TEST_TRACK_CONFIDENCE = 90.0

@pytest.fixture
def base_track():
    """Create a base track for comparison."""
    return Track("Original Song", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)

def test_exact_match(base_track):
    """Test exact match between tracks."""
    exact_match = Track("Original Song", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)
    assert base_track.is_similar_to(exact_match)

def test_case_insensitive_match(base_track):
    """Test case-insensitive matching."""
    case_diff = Track("ORIGINAL SONG", "TEST ARTIST", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)
    assert base_track.is_similar_to(case_diff)

def test_remix_match(base_track):
    """Test matching with remix versions."""
    remixes = [
        Track("Original Song (Club Remix)", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE),
        Track("Original Song [Extended Mix]", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE),
        Track("Original Song - Radio Edit", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)
    ]
    for remix in remixes:
        assert base_track.is_similar_to(remix), f"Failed to match: {remix}"

def test_featuring_artist_match(base_track):
    """Test matching with featuring artists."""
    featuring_tracks = [
        Track("Original Song", "Test Artist feat. Other Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE),
        Track("Original Song", "Test Artist ft. Other Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE),
        Track("Original Song", "Test Artist & Other Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)
    ]
    for track in featuring_tracks:
        assert base_track.is_similar_to(track), f"Failed to match: {track}"

def test_similar_name_match(base_track):
    """Test matching with similar but not identical names."""
    similar_tracks = [
        Track("Original Songg", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE),  # Typo
        Track("Original Song ", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)   # Extra space
    ]
    for track in similar_tracks:
        assert base_track.is_similar_to(track), f"Failed to match: {track}"

def test_numbered_variations_no_match(base_track):
    """Test that numbered variations don't match."""
    numbered_tracks = [
        Track("Original Song 1", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE),
        Track("Original Song Part 1", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE),
        Track("Original Song Pt 2", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)
    ]
    for track in numbered_tracks:
        assert not base_track.is_similar_to(track), f"Should not match: {track}"

def test_different_name_no_match(base_track):
    """Test non-matching with different names."""
    different_tracks = [
        Track("Different Song", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE),
        Track("Original Different", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE),
        Track("Song Original", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)
    ]
    for track in different_tracks:
        assert not base_track.is_similar_to(track), f"Should not match: {track}"

def test_different_artist_no_match(base_track):
    """Test non-matching with different artists."""
    different_artists = [
        Track("Original Song", "Different Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE),
        Track("Original Song", "The Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE),
        Track("Original Song", "Test Artist Band", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)
    ]
    for track in different_artists:
        assert not base_track.is_similar_to(track), f"Should not match: {track}"

def test_edge_cases(base_track):
    """Test edge cases in similarity matching."""
    edge_cases = [
        # Very long names
        Track("Original Song " * 5, "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE),
        # Special characters
        Track("Original Song!@#$%", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE),
        # Unicode characters
        Track("Original Song 🎵", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE),
        # HTML-like content
        Track("Original Song <remix>", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)
    ]
    for track in edge_cases:
        # These should not crash, but we don't assert specific matching behavior
        base_track.is_similar_to(track)

def test_similarity_thresholds():
    """Test similarity matching thresholds."""
    base = Track("Original Song", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE)
    
    # Test name similarity thresholds
    assert base.is_similar_to(Track("Original Songg", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE))  # 90% similar
    assert not base.is_similar_to(Track("Original Songggg", "Test Artist", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE))  # <90% similar
    
    # Test artist similarity thresholds
    assert base.is_similar_to(Track("Original Song", "Test Artisst", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE))  # 90% similar
    assert not base.is_similar_to(Track("Original Song", "Test Artissst", TEST_TRACK_TIME, TEST_TRACK_CONFIDENCE))  # <90% similar
