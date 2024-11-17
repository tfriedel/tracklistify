"""
Audio file downloader module.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yt_dlp

from .config import get_config
from .exceptions import DownloadError
from .logger import get_logger

logger = get_logger(__name__)

class AudioDownloader:
    """Base class for audio downloaders."""
    
    def __init__(self, download_dir: Optional[Path] = None, options: Optional[Dict[str, Any]] = None):
        """Initialize downloader with options."""
        self.config = get_config()
        self.download_dir = download_dir or Path(self.config.get('download_dir', 'downloads'))
        self.options = options or {}
        
        # Ensure download directory exists and is writable
        try:
            self.download_dir.mkdir(parents=True, exist_ok=True)
            test_file = self.download_dir / '.test'
            test_file.touch()
            test_file.unlink()
        except (PermissionError, OSError) as e:
            raise DownloadError(f"Cannot access download directory: {str(e)}")
        
    def download(self, url: str, filename: Optional[str] = None) -> Path:
        """Download audio from URL to output path."""
        if not filename:
            # For YouTube URLs, use video ID as filename
            if 'youtube.com' in url or 'youtu.be' in url:
                video_id = url.split('watch?v=')[-1].split('&')[0]
                filename = video_id
            else:
                filename = url.split('/')[-1]
        output_path = self.download_dir / filename
        return self._download_file(url, output_path)
    
    def _download_file(self, url: str, output_path: Path) -> Path:
        """Internal method to handle actual download."""
        raise NotImplementedError("Subclasses must implement _download_file")

class YouTubeDownloader(AudioDownloader):
    """YouTube audio downloader using yt-dlp."""
    
    def __init__(self, download_dir: Optional[Path] = None, options: Optional[Dict[str, Any]] = None):
        """Initialize YouTube downloader."""
        super().__init__(download_dir, options)
        self.default_options = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True
        }
        
    def _download_file(self, url: str, output_path: Path) -> Path:
        """Download audio from YouTube URL."""
        # Define paths for temporary files
        temp_files = [
            output_path.with_suffix('.part'),
            output_path.with_suffix('.ytdl'),
            output_path.with_name(f"{output_path.stem}.part"),
            output_path.with_name(f"{output_path.stem}.ytdl")
        ]
        
        # Clean up any existing temporary files
        for temp_file in temp_files:
            if temp_file.exists():
                temp_file.unlink()
            
        try:
            # Merge default options with user options
            options = {**self.default_options, **self.options}
            options['outtmpl'] = str(output_path.with_suffix(''))
            
            # Create YoutubeDL instance
            ydl = yt_dlp.YoutubeDL(options)
            
            # Extract info and download
            info = ydl.extract_info(url, download=True)
            if not info:
                raise DownloadError(f"Could not extract info from URL: {url}")
                
            ext = info.get('ext', self.default_options['postprocessors'][0]['preferredcodec'])
            final_path = output_path.with_suffix(f'.{ext}')
            
            # Clean up any temporary files that might have been created
            for temp_file in temp_files:
                if temp_file.exists():
                    temp_file.unlink()
                    
            return final_path
                
        except Exception as e:
            # Clean up any temporary files
            for temp_file in temp_files:
                if temp_file.exists():
                    temp_file.unlink()
            raise DownloadError(f"Failed to download from {url}: {str(e)}")

class DownloaderFactory:
    """Factory for creating appropriate downloaders."""
    
    DOWNLOADERS = {
        'youtube': YouTubeDownloader,
        'youtu.be': YouTubeDownloader
    }
    
    @classmethod
    def create_downloader(cls, url: str, download_dir: Optional[Path] = None, 
                         options: Optional[Dict[str, Any]] = None) -> AudioDownloader:
        """Create appropriate downloader for URL."""
        for domain, downloader_class in cls.DOWNLOADERS.items():
            if domain in url:
                return downloader_class(download_dir, options)
        raise DownloadError(f"No downloader available for URL: {url}")
    
    @classmethod
    def supports_url(cls, url: str) -> bool:
        """Check if URL is supported by any downloader."""
        return any(domain in url for domain in cls.DOWNLOADERS)
