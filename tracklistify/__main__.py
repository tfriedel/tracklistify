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
        
        for start in range(0, total_length, segment_length):
            segment = audio_data[start:start + segment_length]
            result = recognizer.recognize_by_filebuffer(segment, 0)
            
            try:
                data = json.loads(result)
                if data['status']['code'] == 0:
                    for music in data['metadata']['music']:
                        track = Track(
                            song_name=music['title'],
                            artist=music['artists'][0]['name'],
                            time_in_mix=str(datetime.fromtimestamp(start // 1000).strftime('%H:%M:%S')),
                            confidence=float(music['score'])
                        )
                        matcher.add_track(track)
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Failed to parse ACRCloud response: {str(e)}")
                continue
                
        return matcher.merge_nearby_tracks()
        
    except Exception as e:
        logger.error(f"Track identification failed: {str(e)}")
        return None

def save_tracklist(tracks: List[Track], input_path: str):
    """Save identified tracks to JSON file."""
    output_dir = Path('tracklists')
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = Path(input_path).stem
    output_file = output_dir / f"{filename}_{timestamp}.json"
    
    data = {
        'mix_info': {
            'title': filename,
            'analysis_date': datetime.now().isoformat(),
        },
        'track_count': len(tracks),
        'tracks': [
            {
                'song_name': track.song_name,
                'artist': track.artist,
                'time_in_mix': track.time_in_mix,
                'confidence': track.confidence
            }
            for track in tracks
        ]
    }
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)
        
    logger.info(f"\nResults saved to: {output_file}")

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
    
    # Identify tracks
    tracks = identify_tracks(input_path)
    if not tracks:
        logger.error("No tracks identified")
        return
        
    # Save results
    save_tracklist(tracks, input_path)
    
    # Display results
    logger.info(f"\nIdentified {len(tracks)} tracks:\n")
    for track in tracks:
        logger.info(f"Time: {track.time_in_mix}")
        logger.info(f"Track: {track.song_name}")
        logger.info(f"Artist: {track.artist}")
        logger.info(f"Confidence: {track.confidence:.0f}%\n")

if __name__ == '__main__':
    main()
