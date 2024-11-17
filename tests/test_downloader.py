"""
Tests for the audio downloader functionality.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock

from tracklistify.downloader import AudioDownloader, YouTubeDownloader, DownloaderFactory
from tracklistify.exceptions import DownloadError
from .conftest import (
    TEST_AUDIO_FORMATS,
    TEST_AUDIO_BITRATE,
    TEST_SAMPLE_RATE,
    TEST_MIX_TITLE
)

@pytest.fixture
def temp_download_dir(tmp_path):
    """Create a temporary download directory."""
    download_dir = tmp_path / "downloads"
    download_dir.mkdir(parents=True, exist_ok=True)
    return download_dir

@pytest.fixture
def downloader(temp_download_dir):
    """Create a downloader instance with temporary directory."""
    return YouTubeDownloader(download_dir=temp_download_dir)

def test_downloader_initialization(temp_download_dir):
    """Test downloader initialization creates directory."""
    downloader = YouTubeDownloader(download_dir=temp_download_dir)
    assert downloader.download_dir.exists()
    assert downloader.download_dir.is_dir()

@patch('yt_dlp.YoutubeDL')
def test_youtube_download_success(mock_ytdl, downloader):
    """Test successful YouTube video download."""
    url = "https://www.youtube.com/watch?v=test123"
    mock_info = {
        'id': 'test123',
        'title': TEST_MIX_TITLE,
        'ext': TEST_AUDIO_FORMATS[0]
    }
    
    # Mock the download behavior
    mock_ytdl_instance = Mock()
    mock_ytdl_instance.extract_info.return_value = mock_info
    mock_ytdl.return_value = mock_ytdl_instance
    
    # Perform download
    output_path = downloader.download(url)
    
    # Verify download was called with correct options
    mock_ytdl.assert_called_once()
    mock_ytdl_instance.extract_info.assert_called_once_with(url, download=True)
    
    # Verify output path
    assert output_path.suffix == f'.{TEST_AUDIO_FORMATS[0]}'

@patch('yt_dlp.YoutubeDL')
def test_youtube_download_failure(mock_ytdl, downloader):
    """Test YouTube download failure handling."""
    url = "https://www.youtube.com/watch?v=test123"
    
    # Mock download failure
    mock_ytdl_instance = Mock()
    mock_ytdl_instance.extract_info.side_effect = Exception("Download failed")
    mock_ytdl.return_value = mock_ytdl_instance
    
    # Verify download raises error
    with pytest.raises(DownloadError):
        downloader.download(url)

def test_invalid_url():
    """Test handling of invalid URLs."""
    url = "not_a_url"
    with pytest.raises(DownloadError):
        DownloaderFactory.create_downloader(url)

@patch('yt_dlp.YoutubeDL')
def test_download_options(mock_ytdl, temp_download_dir):
    """Test download options configuration."""
    url = "https://www.youtube.com/watch?v=test123"
    
    # Create downloader with custom options
    custom_options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': TEST_AUDIO_FORMATS[0],
        }]
    }
    downloader = YouTubeDownloader(
        download_dir=temp_download_dir,
        options=custom_options
    )
    
    # Mock successful download
    mock_ytdl_instance = Mock()
    mock_ytdl_instance.extract_info.return_value = {
        'id': 'test123',
        'title': TEST_MIX_TITLE,
        'ext': TEST_AUDIO_FORMATS[0]
    }
    mock_ytdl.return_value = mock_ytdl_instance
    
    # Perform download
    output_path = downloader.download(url)
    
    # Verify options were merged correctly
    mock_ytdl.assert_called_once()
    call_args = mock_ytdl.call_args[0][0]
    assert call_args['format'] == 'bestaudio/best'
    assert call_args['postprocessors'][0]['preferredcodec'] == TEST_AUDIO_FORMATS[0]

@patch('yt_dlp.YoutubeDL')
def test_download_with_custom_filename(mock_ytdl, downloader):
    """Test download with custom output filename."""
    url = "https://www.youtube.com/watch?v=test123"
    custom_filename = "custom_test_file"
    
    # Mock successful download
    mock_ytdl_instance = Mock()
    mock_ytdl_instance.extract_info.return_value = {
        'id': 'test123',
        'title': TEST_MIX_TITLE,
        'ext': TEST_AUDIO_FORMATS[0]
    }
    mock_ytdl.return_value = mock_ytdl_instance
    
    # Perform download with custom filename
    output_path = downloader.download(url, filename=custom_filename)
    
    # Verify output path
    assert output_path.name == f"{custom_filename}.{TEST_AUDIO_FORMATS[0]}"

@patch('yt_dlp.YoutubeDL')
def test_download_cleanup_on_failure(mock_ytdl, downloader):
    """Test cleanup of partial downloads on failure."""
    url = "https://www.youtube.com/watch?v=test123"
    video_id = "test123"  # Expected video ID from URL
    
    # Create a fake partial download file in the same location the downloader will use
    output_path = downloader.download_dir / video_id
    partial_file = output_path.with_suffix('.part')
    partial_file.parent.mkdir(parents=True, exist_ok=True)
    partial_file.touch()
    
    # Mock download failure
    mock_ytdl_instance = Mock()
    mock_ytdl_instance.extract_info.side_effect = Exception("Download failed")
    mock_ytdl.return_value = mock_ytdl_instance
    
    # Attempt download (should fail)
    with pytest.raises(DownloadError):
        downloader.download(url)
    
    # Verify partial file was cleaned up
    assert not partial_file.exists()

def test_download_dir_permissions(temp_download_dir):
    """Test handling of download directory permission issues."""
    # Remove read/write permissions from directory
    os.chmod(temp_download_dir, 0o000)
    
    # Attempt to create downloader
    with pytest.raises(DownloadError):
        YouTubeDownloader(download_dir=temp_download_dir)
    
    # Restore permissions for cleanup
    os.chmod(temp_download_dir, 0o755)

def test_youtube_download_info_extraction_failure(tmp_path, mocker):
    """Test YouTube download failure during info extraction."""
    download_dir = tmp_path / "test_download_dir"
    downloader = YouTubeDownloader(download_dir=download_dir)
    
    # Mock YoutubeDL to return None for info extraction
    mock_ydl = mocker.MagicMock()
    mock_ydl.extract_info.return_value = None
    mocker.patch('yt_dlp.YoutubeDL', return_value=mock_ydl)
    
    with pytest.raises(DownloadError, match="Could not extract info from URL"):
        downloader.download("https://www.youtube.com/watch?v=test")

def test_youtube_download_partial_cleanup(tmp_path, mocker):
    """Test cleanup of partial downloads on failure."""
    download_dir = tmp_path / "test_download_dir"
    downloader = YouTubeDownloader(download_dir=download_dir)
    
    # Create mock partial files with different suffixes
    test_url = "https://www.youtube.com/watch?v=test123"
    video_id = "test123"  # Expected video ID from URL
    output_path = download_dir / video_id
    
    # Create all possible temporary files
    temp_files = [
        output_path.with_suffix('.part'),
        output_path.with_suffix('.ytdl'),
        output_path.with_name(f"{output_path.stem}.part"),
        output_path.with_name(f"{output_path.stem}.ytdl")
    ]
    
    # Create the temporary files
    for temp_file in temp_files:
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file.touch()
    
    # Mock YoutubeDL to raise an exception
    mock_ydl = mocker.MagicMock()
    mock_ydl.extract_info.side_effect = Exception("Download failed")
    mocker.patch('yt_dlp.YoutubeDL', return_value=mock_ydl)
    
    with pytest.raises(DownloadError, match="Failed to download"):
        downloader.download(test_url)
    
    # Verify all temporary files were cleaned up
    for temp_file in temp_files:
        assert not temp_file.exists(), f"File {temp_file} was not cleaned up"

def test_base_downloader_not_implemented(mocker):
    """Test that base downloader raises NotImplementedError."""
    # Mock the config to avoid initialization issues
    mock_config = mocker.MagicMock()
    mock_config.get.return_value = 'downloads'
    mocker.patch('tracklistify.downloader.get_config', return_value=mock_config)
    
    downloader = AudioDownloader()
    with pytest.raises(NotImplementedError):
        downloader._download_file("test_url", Path("test_path"))
