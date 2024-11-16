"""
Audio download and processing functionality.
"""

import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import yt_dlp
from .logger import logger
from .config import get_config

class Downloader(ABC):
    """Base class for audio downloaders."""
    
    @abstractmethod
    def download(self, url: str) -> Optional[str]:
        """Download audio from URL."""
        pass
        
    @staticmethod
    def get_ffmpeg_path() -> str:
        """Find FFmpeg executable path."""
        # Check common locations
        common_paths = [
            '/opt/homebrew/bin/ffmpeg',  # Homebrew on Apple Silicon
            '/usr/local/bin/ffmpeg',     # Homebrew on Intel Mac
            '/usr/bin/ffmpeg',           # Linux
        ]
        
        for path in common_paths:
            if os.path.isfile(path):
                return path
                
        # Try finding in PATH
        import shutil
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path
            
        raise FileNotFoundError("FFmpeg not found. Please install FFmpeg first.")

class YouTubeDownloader(Downloader):
    """YouTube video downloader."""
    
    def __init__(self):
        self.ffmpeg_path = self.get_ffmpeg_path()
        logger.info(f"Using FFmpeg from: {self.ffmpeg_path}")
        
    def download(self, url: str) -> Optional[str]:
        """
        Download audio from YouTube URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            str: Path to downloaded audio file, or None if download failed
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': self.ffmpeg_path,
            'outtmpl': os.path.join(tempfile.gettempdir(), '%(id)s.%(ext)s'),
            'verbose': get_config().app.verbose,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                mp3_path = str(Path(filename).with_suffix('.mp3'))
                logger.info(f"Downloaded: {info.get('title', 'Unknown title')}")
                return mp3_path
                
        except Exception as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            return None

class DownloaderFactory:
    """Factory for creating appropriate downloader instances."""
    
    def __init__(self):
        self._config = get_config()
    
    @staticmethod
    def create_downloader(url: str) -> Optional[Downloader]:
        """
        Create appropriate downloader based on URL.
        
        Args:
            url: Media URL
            
        Returns:
            Downloader: Appropriate downloader instance, or None if unsupported
        """
        if 'youtube.com' in url or 'youtu.be' in url:
            return YouTubeDownloader()
        # Add more platform support here
        
        logger.error(f"Unsupported platform: {url}")
        return None
