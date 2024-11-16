"""Tests for the Shazam provider."""

import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from tracklistify.providers.shazam import ShazamProvider
from tracklistify.providers.base import IdentificationError

@pytest.fixture
def shazam_provider():
    """Create a Shazam provider instance for testing."""
    return ShazamProvider()

@pytest.fixture
def mock_audio_data():
    """Create mock audio data for testing."""
    # Create 10 seconds of audio data at 44.1kHz
    duration = 10
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Generate a simple sine wave
    frequency = 440  # A4 note
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)
    return audio.tobytes()

@pytest.mark.asyncio
async def test_extract_audio_features(shazam_provider, mock_audio_data):
    """Test audio feature extraction."""
    enhanced_segment, sr = shazam_provider._extract_audio_features(mock_audio_data)
    
    assert isinstance(enhanced_segment, np.ndarray)
    assert isinstance(sr, int)
    assert sr > 0
    assert len(enhanced_segment) > 0

@pytest.mark.asyncio
async def test_identify_track_success(shazam_provider, mock_audio_data):
    """Test successful track identification."""
    mock_result = {
        'track': {
            'title': 'Test Track',
            'subtitle': 'Test Artist',
            'sections': [{'metadata': [{'text': 'Test Album'}, {'text': '2024'}]}],
            'genres': {'primary': 'Electronic'},
            'key': '123456'
        }
    }
    
    with patch('shazamio.Shazam.recognize_song', return_value=mock_result):
        result = await shazam_provider.identify_track(mock_audio_data)
        
        assert result['title'] == 'Test Track'
        assert result['artist'] == 'Test Artist'
        assert result['album'] == 'Test Album'
        assert result['year'] == '2024'
        assert result['genre'] == 'Electronic'
        assert result['provider'] == 'shazam'
        assert result['provider_id'] == '123456'
        assert 0 <= result['confidence'] <= 1.0
        assert 'audio_features' in result
        assert 'duration' in result['audio_features']
        assert 'sample_rate' in result['audio_features']

@pytest.mark.asyncio
async def test_identify_track_with_partial_metadata(shazam_provider, mock_audio_data):
    """Test track identification with partial metadata."""
    mock_result = {
        'track': {
            'title': 'Test Track',
            'subtitle': 'Test Artist',
            'key': '123456'
        }
    }
    
    with patch('shazamio.Shazam.recognize_song', return_value=mock_result):
        result = await shazam_provider.identify_track(mock_audio_data)
        assert result['confidence'] < 0.9  # Confidence should be lower due to missing metadata

@pytest.mark.asyncio
async def test_identify_track_no_match(shazam_provider, mock_audio_data):
    """Test track identification with no match."""
    with patch('shazamio.Shazam.recognize_song', return_value={}):
        with pytest.raises(IdentificationError):
            await shazam_provider.identify_track(mock_audio_data)

@pytest.mark.asyncio
async def test_enrich_metadata_success(shazam_provider):
    """Test successful metadata enrichment."""
    track_info = {
        'provider': 'shazam',
        'provider_id': '123456',
        'audio_features': {
            'duration': 180.0,
            'sample_rate': 44100
        }
    }
    
    mock_details = {
        'images': {'coverart': 'http://example.com/cover.jpg'},
        'hub': {
            'bpm': '128',
            'key': 'C major',
            'timeSignature': '4/4',
            'mode': 'major',
            'danceability': '0.8',
            'energy': '0.9',
            'isrc': 'ABC123',
            'label': 'Test Label'
        }
    }
    
    with patch('shazamio.Shazam.track_about', return_value=mock_details):
        result = await shazam_provider.enrich_metadata(track_info)
        
        assert result['album_art'] == 'http://example.com/cover.jpg'
        assert result['isrc'] == 'ABC123'
        assert result['label'] == 'Test Label'
        assert result['audio_features']['bpm'] == '128'
        assert result['audio_features']['key'] == 'C major'
        assert result['audio_features']['time_signature'] == '4/4'
        assert result['audio_features']['mode'] == 'major'
        assert result['audio_features']['danceability'] == '0.8'
        assert result['audio_features']['energy'] == '0.9'
        assert result['audio_features']['duration'] == 180.0
        assert result['audio_features']['sample_rate'] == 44100

@pytest.mark.asyncio
async def test_enrich_metadata_no_provider_id(shazam_provider):
    """Test metadata enrichment with no provider ID."""
    track_info = {'provider': 'shazam'}
    result = await shazam_provider.enrich_metadata(track_info)
    assert result == track_info

@pytest.mark.asyncio
async def test_enrich_metadata_error_handling(shazam_provider):
    """Test metadata enrichment error handling."""
    track_info = {
        'provider': 'shazam',
        'provider_id': '123456'
    }
    
    with patch('shazamio.Shazam.track_about', side_effect=Exception("API Error")):
        result = await shazam_provider.enrich_metadata(track_info)
        assert result == track_info  # Should return original track info on error
