"""Unit tests for ACRCloud provider."""

import pytest
import aiohttp
import json
from unittest.mock import AsyncMock, MagicMock, patch
from tracklistify.providers.acrcloud import ACRCloudProvider
from tracklistify.track import Track

@pytest.fixture
def acrcloud_config():
    return {
        'host': 'test.acrcloud.com',
        'access_key': 'test_key',
        'access_secret': 'test_secret'
    }

@pytest.fixture
def acrcloud_provider(acrcloud_config):
    return ACRCloudProvider(acrcloud_config)

@pytest.fixture
def mock_acrcloud_response():
    return {
        'status': {
            'code': 0,
            'msg': 'Success'
        },
        'metadata': {
            'music': [{
                'title': 'Test Track',
                'artists': [{'name': 'Test Artist'}],
                'album': {'name': 'Test Album'},
                'duration_ms': 180000,
                'external_metadata': {
                    'spotify': {'track': {'id': 'test_spotify_id'}}
                }
            }]
        }
    }

@pytest.mark.asyncio
async def test_identify_track_success(acrcloud_provider, mock_acrcloud_response):
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_acrcloud_response
        )
        
        track = await acrcloud_provider.identify_track(b'audio_data')
        
        assert isinstance(track, Track)
        assert track.title == 'Test Track'
        assert track.artist == 'Test Artist'
        assert track.album == 'Test Album'
        assert track.duration == 180
        assert track.spotify_id == 'test_spotify_id'

@pytest.mark.asyncio
async def test_identify_track_no_match(acrcloud_provider):
    no_match_response = {'status': {'code': 1001, 'msg': 'No result'}}
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=no_match_response
        )
        
        track = await acrcloud_provider.identify_track(b'audio_data')
        assert track is None

@pytest.mark.asyncio
async def test_identify_track_error(acrcloud_provider):
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            side_effect=aiohttp.ClientError
        )
        
        with pytest.raises(Exception):
            await acrcloud_provider.identify_track(b'audio_data')

@pytest.mark.asyncio
async def test_identify_track_invalid_response(acrcloud_provider):
    invalid_response = {'status': {'code': 3000, 'msg': 'Invalid access key'}}
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=invalid_response
        )
        
        with pytest.raises(Exception):
            await acrcloud_provider.identify_track(b'audio_data')

@pytest.mark.asyncio
async def test_identify_track_rate_limit(acrcloud_provider):
    rate_limit_response = {'status': {'code': 2005, 'msg': 'Rate limit exceeded'}}
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=rate_limit_response
        )
        
        with pytest.raises(Exception) as exc_info:
            await acrcloud_provider.identify_track(b'audio_data')
        assert 'Rate limit' in str(exc_info.value)

@pytest.mark.asyncio
async def test_identify_track_partial_metadata(acrcloud_provider):
    partial_response = {
        'status': {'code': 0, 'msg': 'Success'},
        'metadata': {
            'music': [{
                'title': 'Test Track',
                'artists': [{'name': 'Test Artist'}],
                'duration_ms': 180000
            }]
        }
    }
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=partial_response
        )
        
        track = await acrcloud_provider.identify_track(b'audio_data')
        
        assert isinstance(track, Track)
        assert track.title == 'Test Track'
        assert track.artist == 'Test Artist'
        assert track.album is None
        assert track.spotify_id is None
