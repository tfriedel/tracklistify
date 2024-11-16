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
    
    # Update config with command line arguments
    if args.segment_length:
        config.track.segment_length = args.segment_length
    if args.verbose:
        config.app.verbose = True
    
    # Process input
    input_path = args.input
    if input_path.startswith(('http://', 'https://')):
        # Download from URL
        downloader = DownloaderFactory.create_downloader(input_path)
        if not downloader:
            logger.error("Unsupported URL format")
            return
            
        input_path = downloader.download(input_path)
        if not input_path:
            logger.error("Download failed")
            return
    
    # Get mix information
    mix_info = get_mix_info(input_path)
    
    # Identify tracks
    tracks = identify_tracks(input_path)
    if not tracks:
        logger.error("No tracks identified")
        return
    
    # Save results
    output = TracklistOutput(mix_info)
    output_dir = Path('tracklists')
    
    if args.formats in ['json', 'all']:
        output.save_json(tracks, output_dir)
    if args.formats in ['markdown', 'all']:
        output.save_markdown(tracks, output_dir)
    if args.formats in ['m3u', 'all']:
        output.save_m3u(tracks, output_dir)
    
    # Display results
    logger.info(f"\nIdentified {len(tracks)} tracks:\n")
    for track in tracks:
        logger.info(f"Time: {track.time_in_mix}")
        logger.info(f"Track: {track.song_name}")
        logger.info(f"Artist: {track.artist}")
        logger.info(f"Confidence: {track.confidence:.0f}%\n")

if __name__ == '__main__':
    main()
