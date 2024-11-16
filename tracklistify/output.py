"""
Output formatting and file handling for Tracklistify.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional
import json
import re
from .track import Track
from .logger import logger

class TracklistOutput:
    """Handles tracklist output in various formats."""
    
    def __init__(self, mix_info: dict):
        """
        Initialize with mix information.
        
        Args:
            mix_info: Dictionary containing mix metadata
        """
        self.mix_info = mix_info
    
    def _format_filename(self, extension: str) -> str:
        """
        Generate filename in format: [YYYYMMDD] Artist - Description.extension
        
        Args:
            extension: File extension without dot
            
        Returns:
            Formatted filename
        """
        # Get date in YYYYMMDD format
        mix_date = self.mix_info.get('date', datetime.now().strftime('%Y-%m-%d'))
        if isinstance(mix_date, str):
            try:
                mix_date = datetime.strptime(mix_date, '%Y-%m-%d').strftime('%Y%m%d')
            except ValueError:
                mix_date = datetime.now().strftime('%Y%m%d')
        
        # Get artist and description
        artist = self.mix_info.get('artist', 'Unknown Artist')
        description = self.mix_info.get('title', 'Unknown Mix')
        
        # Clean up special characters but preserve spaces and basic punctuation
        def clean_string(s: str) -> str:
            # Replace invalid filename characters with spaces
            s = re.sub(r'[<>:"/\\|?*]', ' ', s)
            # Replace multiple spaces with single space
            s = re.sub(r'\s+', ' ', s)
            # Strip leading/trailing spaces
            return s.strip()
        
        artist = clean_string(artist)
        description = clean_string(description)
        
        # Format filename
        return f"[{mix_date}] {artist} - {description}.{extension}"
    
    def save_json(self, tracks: List[Track], output_dir: Path) -> Path:
        """Save tracks as JSON file."""
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / self._format_filename('json')
        
        data = {
            'mix_info': self.mix_info,
            'track_count': len(tracks),
            'analysis_info': {
                'timestamp': datetime.now().isoformat(),
                'track_count': len(tracks),
                'average_confidence': sum(t.confidence for t in tracks) / len(tracks) if tracks else 0,
                'min_confidence': min(t.confidence for t in tracks) if tracks else 0,
                'max_confidence': max(t.confidence for t in tracks) if tracks else 0,
            },
            'tracks': [
                {
                    'song_name': track.song_name,
                    'artist': track.artist,
                    'time_in_mix': track.time_in_mix,
                    'confidence': track.confidence,
                    'duration': track.duration if hasattr(track, 'duration') else None
                }
                for track in tracks
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Saved JSON tracklist to: {output_file}")
        logger.info(f"Analysis Summary:")
        logger.info(f"- Total tracks: {data['analysis_info']['track_count']}")
        logger.info(f"- Average confidence: {data['analysis_info']['average_confidence']:.1f}%")
        logger.info(f"- Confidence range: {data['analysis_info']['min_confidence']:.1f}% - {data['analysis_info']['max_confidence']:.1f}%")
        return output_file
    
    def save_markdown(self, tracks: List[Track], output_dir: Path) -> Path:
        """Save tracks as Markdown file."""
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / self._format_filename('md')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# {self.mix_info.get('title', 'Tracklist')}\n\n")
            
            if 'artist' in self.mix_info:
                f.write(f"**Artist:** {self.mix_info['artist']}\n")
            if 'date' in self.mix_info:
                f.write(f"**Date:** {self.mix_info['date']}\n")
            if 'description' in self.mix_info:
                f.write(f"\n{self.mix_info['description']}\n")
            
            # Write analysis info
            f.write("\n## Analysis Info\n")
            f.write(f"- **Total Tracks:** {len(tracks)}\n")
            if tracks:
                avg_conf = sum(t.confidence for t in tracks) / len(tracks)
                min_conf = min(t.confidence for t in tracks)
                max_conf = max(t.confidence for t in tracks)
                f.write(f"- **Average Confidence:** {avg_conf:.1f}%\n")
                f.write(f"- **Confidence Range:** {min_conf:.1f}% - {max_conf:.1f}%\n")
            
            f.write("\n## Tracks\n\n")
            
            # Write tracks
            for track in tracks:
                f.write(f"{track.markdown_line}\n")
                
        logger.info(f"Saved Markdown tracklist to: {output_file}")
        return output_file
    
    def save_m3u(self, tracks: List[Track], output_dir: Path) -> Path:
        """Save tracks as M3U playlist."""
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / self._format_filename('m3u')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            
            # Write title comment
            f.write(f"#PLAYLIST:{self.mix_info.get('title', 'Tracklist')}\n")
            if 'artist' in self.mix_info:
                f.write(f"#EXTALB:{self.mix_info['artist']}\n")
            if 'date' in self.mix_info:
                f.write(f"#EXTGENRE:DJ Mix - {self.mix_info['date']}\n")
            
            # Write tracks
            for track in tracks:
                f.write(f"{track.m3u_line}\n")
                
        logger.info(f"Saved M3U playlist to: {output_file}")
        return output_file
