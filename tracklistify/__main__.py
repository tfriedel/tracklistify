"""
Main entry point for Tracklistify.
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .config import config
from .logger import logger
from .track import Track, TrackMatcher
from .downloader import DownloaderFactory
from .output import TracklistOutput
from .validation import validate_and_clean_url, is_valid_url, is_youtube_url

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

def identify_tracks(audio_path: str) -> Optional[List[Track]]:
    """
    Identify tracks in an audio file.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        List[Track]: List of identified tracks, or None if identification failed
    """
    try:
        from acrcloud.recognizer import ACRCloudRecognizer
        
        recognizer = ACRCloudRecognizer({
            'access_key': config.acrcloud.access_key,
            'access_secret': config.acrcloud.access_secret,
            'host': config.acrcloud.host,
            'timeout': config.acrcloud.timeout
        })
        
        matcher = TrackMatcher()
        
        # Process file in segments
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
            
        total_length = len(audio_data)
        segment_length = config.track.segment_length * 1000  # Convert to bytes
        total_segments = total_length // segment_length
        
        logger.info(f"Starting track identification...")
        logger.info(f"Total segments to analyze: {total_segments}")
        logger.info(f"Segment length: {config.track.segment_length} seconds")
        
        identified_count = 0
        for i, start in enumerate(range(0, total_length, segment_length)):
            segment = audio_data[start:start + segment_length]
            logger.info(f"Analyzing segment {i+1}/{total_segments} at {str(datetime.fromtimestamp(start // 1000).strftime('%H:%M:%S'))}...")
            
            result = recognizer.recognize_by_filebuffer(segment, 0)
            
            try:
                data = json.loads(result)
                if data['status']['code'] == 0 and data['metadata'].get('music'):
                    for music in data['metadata']['music']:
                        track = Track(
                            song_name=music['title'],
                            artist=music['artists'][0]['name'],
                            time_in_mix=str(datetime.fromtimestamp(start // 1000).strftime('%H:%M:%S')),
                            confidence=float(music['score'])
                        )
                        matcher.add_track(track)
                        identified_count += 1
                        logger.info(f"Found track: {track.song_name} by {track.artist} (Confidence: {track.confidence:.1f}%)")
                else:
                    logger.debug(f"No music detected in segment {i+1}")
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Failed to parse ACRCloud response: {str(e)}")
                continue
                
        logger.info(f"\nTrack identification completed:")
        logger.info(f"- Segments analyzed: {total_segments}")
        logger.info(f"- Raw tracks identified: {identified_count}")
        
        merged_tracks = matcher.merge_nearby_tracks()
        logger.info(f"- Final unique tracks after merging: {len(merged_tracks)}")
        
        return merged_tracks
        
    except Exception as e:
        logger.error(f"Track identification failed: {str(e)}")
        return None

def get_mix_info(input_path: str) -> dict:
    """Extract mix information from input."""
    if input_path.startswith(('http://', 'https://')):
        # For URLs, try to get info from the downloader
        downloader = DownloaderFactory.create_downloader(input_path)
        if downloader:
            try:
                with yt_dlp.YoutubeDL() as ydl:
                    info = ydl.extract_info(input_path, download=False)
                    return {
                        'title': info.get('title', ''),
                        'artist': info.get('uploader', ''),
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'description': info.get('description', ''),
                        'duration': info.get('duration', 0)
                    }
            except Exception as e:
                logger.error(f"Failed to get mix info: {str(e)}")
    
    # For local files or fallback
    path = Path(input_path)
    return {
        'title': path.stem,
        'date': datetime.now().strftime('%Y-%m-%d')
    }

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
    
    # Get mix information
    mix_info = get_mix_info(input_path)
    if not mix_info:
        logger.error("Failed to get mix information")
        return 1
    
    # Download if URL
    if is_youtube_url(input_path):
        logger.info("Downloading YouTube video...")
        downloader = DownloaderFactory.create_downloader('youtube')
        audio_path = downloader.download(input_path)
        if not audio_path:
            logger.error("Failed to download audio")
            return 1
    else:
        audio_path = input_path
    
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
