"""
Main entry point for Tracklistify.
"""

import argparse
import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Generator

from .config import get_config
from .logger import logger
from .track import Track, TrackMatcher
from .downloader import DownloaderFactory
from .output import TracklistOutput
from .validation import validate_and_clean_url, is_valid_url, is_youtube_url
from .cache import get_cache
from .rate_limiter import get_rate_limiter

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Identify tracks in audio files or streams'
    )
    parser.add_argument(
        'input',
        help='Audio file path or URL'
    )
    parser.add_argument(
        '-s', '--segment-length',
        type=int,
        help='Length of analysis segments in seconds'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '-f', '--formats',
        choices=['json', 'markdown', 'm3u', 'all'],
        default='all',
        help='Output format(s) to generate'
    )
    return parser.parse_args()

def read_audio_chunks(file_path: str, chunk_size: int = 1024*1024) -> Generator[bytes, None, None]:
    """
    Read audio file in chunks to optimize memory usage.
    
    Args:
        file_path: Path to audio file
        chunk_size: Size of each chunk in bytes
        
    Yields:
        bytes: Audio data chunks
    """
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

def get_segment_data(audio_data: bytes, start_bytes: int, end_bytes: int) -> bytes:
    """Get audio segment data from full audio."""
    return audio_data[start_bytes:end_bytes]

def identify_tracks(audio_path: str) -> Optional[List[Track]]:
    """
    Identify tracks in an audio file.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        List[Track]: List of identified tracks, or None if identification failed
    """
    config = get_config()
    cache = get_cache()
    rate_limiter = get_rate_limiter()
    
    try:
        from acrcloud.recognizer import ACRCloudRecognizer
        from mutagen import File
        
        # Get audio file metadata
        audio = File(audio_path)
        if audio is None:
            logger.error("Failed to read audio file metadata")
            return None
            
        total_length = audio.info.length  # Duration in seconds
        segment_length = config.track.segment_length  # Already in seconds
        total_segments = int(total_length // segment_length)
        
        recognizer = ACRCloudRecognizer({
            'access_key': config.acrcloud.access_key,
            'access_secret': config.acrcloud.access_secret,
            'host': config.acrcloud.host,
            'timeout': config.acrcloud.timeout
        })
        
        matcher = TrackMatcher()
        
        logger.info(f"Starting track identification...")
        total_time_str = f"{int(total_length//3600):02d}:{int((total_length%3600)//60):02d}:{int(total_length%60):02d}"
        logger.info(f"Total length: {total_time_str}")
        logger.info(f"Total segments to analyze: {total_segments}")
        logger.info(f"Segment length: {segment_length} seconds")
        
        identified_count = 0
        
        # Process file in chunks
        audio_size = os.path.getsize(audio_path)
        bytes_per_second = audio_size / total_length
        
        for i in range(total_segments):
            start_time = i * segment_length
            start_bytes = int((start_time / total_length) * audio_size)
            end_bytes = int(((start_time + segment_length) / total_length) * audio_size)
            
            # Format time with leading zeros (HH:MM:SS)
            time_str = f"{int(start_time//3600):02d}:{int((start_time%3600)//60):02d}:{int(start_time%60):02d}"
            logger.info(f"Analyzing segment {i+1}/{total_segments} at {time_str}...")
            
            # Calculate cache key
            segment_hash = hashlib.md5(f"{audio_path}:{start_time}".encode()).hexdigest()
            
            # Try to get from cache first
            if config.cache.enabled:
                cached_result = cache.get(segment_hash)
                if cached_result:
                    data = cached_result
                else:
                    # Read just the segment we need
                    with open(audio_path, 'rb') as f:
                        f.seek(start_bytes)
                        segment = f.read(end_bytes - start_bytes)
                    
                    # Apply rate limiting if enabled
                    if config.app.rate_limit_enabled:
                        if not rate_limiter.acquire(timeout=30):
                            logger.warning("Rate limit exceeded, skipping segment")
                            continue
                    
                    result = recognizer.recognize_by_filebuffer(segment, 0)
                    try:
                        data = json.loads(result)
                        if config.cache.enabled:
                            cache.set(segment_hash, data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse ACRCloud response: {str(e)}")
                        continue
            else:
                # No caching, just read and process
                with open(audio_path, 'rb') as f:
                    f.seek(start_bytes)
                    segment = f.read(end_bytes - start_bytes)
                
                # Apply rate limiting if enabled
                if config.app.rate_limit_enabled:
                    if not rate_limiter.acquire(timeout=30):
                        logger.warning("Rate limit exceeded, skipping segment")
                        continue
                
                result = recognizer.recognize_by_filebuffer(segment, 0)
                try:
                    data = json.loads(result)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse ACRCloud response: {str(e)}")
                    continue
            
            if data['status']['code'] == 0 and data['metadata'].get('music'):
                for music in data['metadata']['music']:
                    track = Track(
                        song_name=music['title'],
                        artist=music['artists'][0]['name'],
                        time_in_mix=time_str,
                        confidence=float(music['score'])
                    )
                    matcher.add_track(track)
                    identified_count += 1
                    logger.info(f"Found track: {track.song_name} by {track.artist} (Confidence: {track.confidence:.1f}%)")
            else:
                logger.debug(f"No music detected in segment {i+1}")
                
        logger.info(f"\nTrack identification completed:")
        logger.info(f"- Segments analyzed: {total_segments}")
        logger.info(f"- Raw tracks identified: {identified_count}")
        
        merged_tracks = matcher.merge_nearby_tracks()
        logger.info(f"- Final unique tracks after merging: {len(merged_tracks)}")
        
        return merged_tracks
        
    except Exception as e:
        logger.error(f"Track identification failed: {str(e)}")
        return None

def get_mix_info(input_path: str) -> Optional[dict]:
    """
    Extract mix information from input.
    
    Args:
        input_path: Path to audio file or URL
        
    Returns:
        dict: Mix information, or None if extraction failed
    """
    try:
        if is_youtube_url(input_path):
            import yt_dlp
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(input_path, download=False)
                return {
                    'title': info.get('title', 'Unknown Mix'),
                    'uploader': info.get('uploader', 'Unknown Artist'),
                    'duration': str(timedelta(seconds=info.get('duration', 0))),
                    'source': input_path
                }
        else:
            from mutagen import File
            audio = File(input_path)
            if audio is None:
                return None
                
            return {
                'title': os.path.splitext(os.path.basename(input_path))[0],
                'duration': str(timedelta(seconds=int(audio.info.length))),
                'source': input_path
            }
            
    except Exception as e:
        logger.error(f"Failed to get mix information: {str(e)}")
        return None

def main():
    """Main entry point."""
    args = parse_args()
    
    # Set verbose logging if requested
    if args.verbose:
        logger.setLevel('DEBUG')
        logger.debug("Verbose logging enabled")
    
    # Validate and clean input URL/path
    input_path = args.input
    if '://' in input_path:  # Looks like a URL
        cleaned_url = validate_and_clean_url(input_path)
        if not cleaned_url:
            logger.error(f"Invalid URL: {input_path}")
            return 1
        input_path = cleaned_url
        logger.debug(f"Cleaned URL: {input_path}")
    
    # Download if URL
    if is_youtube_url(input_path):
        logger.info("Downloading YouTube video...")
        try:
            import yt_dlp  # Import here to catch import error
            downloader = DownloaderFactory.create_downloader(input_path)
            if not downloader:
                logger.error("Failed to create downloader")
                return 1
            
            audio_path = downloader.download(input_path)
            if not audio_path:
                logger.error("Failed to download audio")
                return 1
        except ImportError:
            logger.error("yt-dlp not installed. Please install it with: pip install yt-dlp")
            return 1
    else:
        audio_path = input_path
    
    # Get mix information
    mix_info = get_mix_info(input_path)
    if not mix_info:
        logger.error("Failed to get mix information")
        return 1
    
    # Identify tracks
    tracks = identify_tracks(audio_path)
    if not tracks:
        logger.error("No tracks identified")
        return 1
    
    # Generate output
    output = TracklistOutput(tracks, mix_info)
    if args.formats == 'all':
        formats = ['json', 'markdown', 'm3u']
    else:
        formats = [args.formats]
    
    for fmt in formats:
        output.save(fmt)
    
    logger.info(f"Found {len(tracks)} tracks")
    return 0

if __name__ == '__main__':
    main()
