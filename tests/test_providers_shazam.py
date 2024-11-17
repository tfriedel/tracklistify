"""Unit tests for Shazam provider."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock, AsyncMock
import librosa
from tracklistify.providers.shazam import ShazamProvider
from tracklistify.providers.base import IdentificationError
import pytest
import aiohttp
from unittest.mock import AsyncMock, MagicMock, patch
from tracklistify.providers.shazam import ShazamProvider
from tracklistify.track import Track

@pytest.fixture
def shazam_provider():
    """Create Shazam provider instance."""
    return ShazamProvider()

@pytest.fixture
def mock_audio_data():
    """Create mock audio data."""
    # Create a simple sine wave as test audio data
    sample_rate = 44100
    duration = 0.1  # 100ms
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
    return audio.tobytes()

@pytest.fixture
def shazam_config():
    return {
        'api_key': 'test_key',
        'endpoint': 'https://test.shazam.com/api'
    }

@pytest.fixture
def shazam_provider(shazam_config):
    return ShazamProvider(shazam_config)

@pytest.fixture
def mock_shazam_response():
    return {
        'matches': [{
            'track': {
                'title': 'Test Track',
                'subtitle': 'Test Artist',
                'sections': [{
                    'type': 'SONG',
                    'metadata': [{
                        'title': 'Album',
                        'text': 'Test Album'
                    }]
                }],
                'hub': {
                    'providers': [{
                        'type': 'SPOTIFY',
                        'actions': [{
                            'uri': 'spotify:track:test_spotify_id'
                        }]
                    }]
                },
                'share': {
                    'subject': 'Test Track - Test Artist',
                    'href': 'https://www.shazam.com/track/12345'
                }
            }
        }]
    }

@pytest.mark.asyncio
async def test_extract_audio_features(shazam_provider):
    """Test audio feature extraction."""
    # Create valid test audio data
    sample_rate = 44100
    duration = 0.1
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440 * t)
    
    with patch('librosa.load') as mock_load, \
         patch('librosa.feature.mfcc') as mock_mfcc, \
         patch('librosa.feature.spectral_centroid') as mock_centroid:
        mock_load.return_value = (audio, sample_rate)
        mock_mfcc.return_value = np.random.rand(13, 100)
        mock_centroid.return_value = [np.random.rand(100)]
        
        # Test feature extraction
        audio_segment, sr = shazam_provider._extract_audio_features(audio.tobytes())
        assert isinstance(audio_segment, np.ndarray)
        assert sr == sample_rate
        assert len(audio_segment) > 0

@pytest.mark.asyncio
async def test_identify_track_success(shazam_provider):
    """Test successful track identification."""
    mock_recognition_result = {
        "track": {
            "title": "Test Song",
            "subtitle": "Test Artist",
            "sections": [{
                "metadata": [
                    {"title": "Album", "text": "Test Album"},
                    {"title": "Released", "text": "2023"}
                ]
            }],
            "genres": {"primary": "Pop"},
            "key": "test_id"
        }
    }
    
    # Create valid test audio data
    sample_rate = 44100
    duration = 0.1
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440 * t)
    
    with patch('librosa.load') as mock_load, \
         patch('librosa.feature.mfcc') as mock_mfcc, \
         patch('librosa.feature.spectral_centroid') as mock_centroid, \
         patch.object(shazam_provider.shazam, 'recognize_song', new_callable=AsyncMock) as mock_recognize:
        mock_load.return_value = (audio, sample_rate)
        mock_mfcc.return_value = np.random.rand(13, 100)
        mock_centroid.return_value = [np.random.rand(100)]
        mock_recognize.return_value = mock_recognition_result
        
        result = await shazam_provider.identify_track(audio.tobytes())
        
        assert result["title"] == "Test Song"
        assert result["artist"] == "Test Artist"
        assert result["album"] == "Test Album"
        assert result["year"] == "2023"
        assert result["genre"] == "Pop"
        assert result["provider"] == "shazam"
        assert result["provider_id"] == "test_id"
        assert isinstance(result["confidence"], float)
        assert 0 <= result["confidence"] <= 1

@pytest.mark.asyncio
async def test_identify_track_no_match(shazam_provider):
    """Test track identification with no matches."""
    # Create valid test audio data
    sample_rate = 44100
    duration = 0.1
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440 * t)
    
    with patch('librosa.load') as mock_load, \
         patch('librosa.feature.mfcc') as mock_mfcc, \
         patch('librosa.feature.spectral_centroid') as mock_centroid, \
         patch.object(shazam_provider.shazam, 'recognize_song', new_callable=AsyncMock) as mock_recognize:
        mock_load.return_value = (audio, sample_rate)
        mock_mfcc.return_value = np.random.rand(13, 100)
        mock_centroid.return_value = [np.random.rand(100)]
        mock_recognize.return_value = None
        
        with pytest.raises(IdentificationError) as exc:
            await shazam_provider.identify_track(audio.tobytes())
        assert "No track identified by Shazam" in str(exc.value)

@pytest.mark.asyncio
async def test_identify_track_invalid_audio(shazam_provider):
    """Test track identification with invalid audio data."""
    with patch('librosa.load', side_effect=Exception("Invalid audio data")):
        with pytest.raises(IdentificationError) as exc:
            await shazam_provider.identify_track(b"invalid_audio_data")
        assert "Failed to identify track with Shazam" in str(exc.value)

@pytest.mark.asyncio
async def test_identify_track_recognition_error(shazam_provider):
    """Test track identification with recognition error."""
    # Create valid test audio data
    sample_rate = 44100
    duration = 0.1
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440 * t)
    
    with patch('librosa.load') as mock_load, \
         patch('librosa.feature.mfcc') as mock_mfcc, \
         patch('librosa.feature.spectral_centroid') as mock_centroid, \
         patch.object(shazam_provider.shazam, 'recognize_song', side_effect=Exception("Recognition failed")) as mock_recognize:
        mock_load.return_value = (audio, sample_rate)
        mock_mfcc.return_value = np.random.rand(13, 100)
        mock_centroid.return_value = [np.random.rand(100)]
        
        with pytest.raises(IdentificationError) as exc:
            await shazam_provider.identify_track(audio.tobytes())
        assert "Failed to identify track with Shazam" in str(exc.value)

@pytest.mark.asyncio
async def test_identify_track_missing_metadata(shazam_provider):
    """Test track identification with missing metadata."""
    mock_recognition_result = {
        "track": {
            "title": "Test Song"
            # Missing other metadata
        }
    }
    
    # Create valid test audio data
    sample_rate = 44100
    duration = 0.1
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440 * t)
    
    with patch('librosa.load') as mock_load, \
         patch('librosa.feature.mfcc') as mock_mfcc, \
         patch('librosa.feature.spectral_centroid') as mock_centroid, \
         patch.object(shazam_provider.shazam, 'recognize_song', new_callable=AsyncMock) as mock_recognize:
        mock_load.return_value = (audio, sample_rate)
        mock_mfcc.return_value = np.random.rand(13, 100)
        mock_centroid.return_value = [np.random.rand(100)]
        mock_recognize.return_value = mock_recognition_result
        
        result = await shazam_provider.identify_track(audio.tobytes())
        
        assert result["title"] == "Test Song"
        assert result["artist"] == ""
        assert result["album"] == ""
        assert result["year"] == ""
        assert result["genre"] == ""

@pytest.mark.asyncio
async def test_enrich_metadata_success(shazam_provider):
    """Test successful metadata enrichment."""
    track_info = {
        'title': 'Test Song',
        'artist': 'Test Artist',
        'provider': 'shazam',
        'provider_id': 'test123',
        'audio_features': {
            'duration': 240,
            'sample_rate': 44100
        }
    }

    mock_track_details = {
        'hub': {
            'bpm': 120,
            'key': 'C',
            'timeSignature': '4/4',
            'mode': 'major',
            'danceability': 0.8,
            'energy': 0.9,
            'isrc': 'USRC12345678',
            'label': 'Test Label'
        },
        'images': {
            'coverart': 'http://example.com/cover.jpg'
        }
    }

    with patch.object(shazam_provider.shazam, 'track_about', new_callable=AsyncMock) as mock_about:
        mock_about.return_value = mock_track_details
        
        result = await shazam_provider.enrich_metadata(track_info)
        
        assert result['title'] == 'Test Song'
        assert result['artist'] == 'Test Artist'
        assert result['album_art'] == 'http://example.com/cover.jpg'
        assert result['isrc'] == 'USRC12345678'
        assert result['label'] == 'Test Label'
        assert result['audio_features']['bpm'] == 120
        assert result['audio_features']['key'] == 'C'
        assert result['audio_features']['time_signature'] == '4/4'
        assert result['audio_features']['mode'] == 'major'
        assert result['audio_features']['danceability'] == 0.8
        assert result['audio_features']['energy'] == 0.9
        assert result['audio_features']['duration'] == 240
        assert result['audio_features']['sample_rate'] == 44100

@pytest.mark.asyncio
async def test_enrich_metadata_no_provider_id(shazam_provider):
    """Test metadata enrichment with no provider ID."""
    track_info = {
        'title': 'Test Song',
        'artist': 'Test Artist',
        'provider': 'shazam'
        # No provider_id
    }

    result = await shazam_provider.enrich_metadata(track_info)
    assert result == track_info  # Should return original track info unchanged

@pytest.mark.asyncio
async def test_enrich_metadata_api_error(shazam_provider):
    """Test metadata enrichment with API error."""
    track_info = {
        'title': 'Test Song',
        'artist': 'Test Artist',
        'provider': 'shazam',
        'provider_id': 'test123'
    }

    with patch.object(shazam_provider.shazam, 'track_about', side_effect=Exception("API Error")):
        result = await shazam_provider.enrich_metadata(track_info)
        assert result == track_info  # Should return original track info unchanged

@pytest.mark.asyncio
async def test_enrich_metadata_missing_fields(shazam_provider):
    """Test metadata enrichment with missing fields in response."""
    track_info = {
        'title': 'Test Song',
        'artist': 'Test Artist',
        'provider': 'shazam',
        'provider_id': 'test123'
    }

    mock_track_details = {
        'hub': {
            # Only some fields present
            'bpm': 120,
            'key': 'C'
        },
        'images': {}  # No cover art
    }

    with patch.object(shazam_provider.shazam, 'track_about', new_callable=AsyncMock) as mock_about:
        mock_about.return_value = mock_track_details
        
        result = await shazam_provider.enrich_metadata(track_info)
        
        assert result['title'] == 'Test Song'
        assert result['artist'] == 'Test Artist'
        assert result['album_art'] == ''  # Should use default empty string
        assert result['isrc'] == ''  # Should use default empty string
        assert result['label'] == ''  # Should use default empty string
        assert result['audio_features']['bpm'] == 120
        assert result['audio_features']['key'] == 'C'
        assert result['audio_features']['time_signature'] == ''  # Should use default empty string
        assert result['audio_features']['mode'] == ''  # Should use default empty string
        assert result['audio_features']['danceability'] == ''  # Should use default empty string
        assert result['audio_features']['energy'] == ''  # Should use default empty string

@pytest.mark.asyncio
async def test_identify_track_success(shazam_provider, mock_shazam_response):
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_shazam_response
        )
        
        track = await shazam_provider.identify_track(b'audio_data')
        
        assert isinstance(track, Track)
        assert track.title == 'Test Track'
        assert track.artist == 'Test Artist'
        assert track.album == 'Test Album'
        assert track.spotify_id == 'test_spotify_id'
        assert track.source_url == 'https://www.shazam.com/track/12345'

@pytest.mark.asyncio
async def test_identify_track_no_match(shazam_provider):
    no_match_response = {'matches': []}
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=no_match_response
        )
        
        track = await shazam_provider.identify_track(b'audio_data')
        assert track is None

@pytest.mark.asyncio
async def test_identify_track_error(shazam_provider):
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            side_effect=aiohttp.ClientError
        )
        
        with pytest.raises(Exception):
            await shazam_provider.identify_track(b'audio_data')

@pytest.mark.asyncio
async def test_identify_track_invalid_response(shazam_provider):
    invalid_response = {'error': 'Invalid API key'}
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=invalid_response
        )
        
        with pytest.raises(Exception):
            await shazam_provider.identify_track(b'audio_data')

@pytest.mark.asyncio
async def test_identify_track_rate_limit(shazam_provider):
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 429
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={'error': 'Rate limit exceeded'}
        )
        
        with pytest.raises(Exception) as exc_info:
            await shazam_provider.identify_track(b'audio_data')
        assert 'Rate limit' in str(exc_info.value)

@pytest.mark.asyncio
async def test_identify_track_partial_metadata(shazam_provider):
    partial_response = {
        'matches': [{
            'track': {
                'title': 'Test Track',
                'subtitle': 'Test Artist',
                'sections': [],
                'hub': {},
                'share': {
                    'subject': 'Test Track - Test Artist',
                    'href': 'https://www.shazam.com/track/12345'
                }
            }
        }]
    }
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=partial_response
        )
        
        track = await shazam_provider.identify_track(b'audio_data')
        
        assert isinstance(track, Track)
        assert track.title == 'Test Track'
        assert track.artist == 'Test Artist'
        assert track.album is None
        assert track.spotify_id is None

@pytest.mark.asyncio
async def test_identify_track_multiple_matches(shazam_provider):
    multiple_matches_response = {
        'matches': [
            {
                'track': {
                    'title': 'Test Track 1',
                    'subtitle': 'Test Artist 1',
                    'sections': [],
                    'hub': {},
                    'share': {'href': 'https://www.shazam.com/track/12345'}
                }
            },
            {
                'track': {
                    'title': 'Test Track 2',
                    'subtitle': 'Test Artist 2',
                    'sections': [],
                    'hub': {},
                    'share': {'href': 'https://www.shazam.com/track/67890'}
                }
            }
        ]
    }
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=multiple_matches_response
        )
        
        track = await shazam_provider.identify_track(b'audio_data')
        
        assert isinstance(track, Track)
        assert track.title == 'Test Track 1'  # Should use first match
        assert track.artist == 'Test Artist 1'
