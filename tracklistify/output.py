"""
Output formatting and file handling for Tracklistify.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import json
import re

from .track import Track
from .logger import logger
from .config import get_config

class TracklistOutput:
    """Handles output generation for identified tracks."""
    
    def __init__(self, tracks: List[Track], mix_info: dict):
        """Initialize output handler."""
        self.tracks = tracks
        self.mix_info = mix_info
        self.output_dir = Path.cwd()
        self._config = get_config()
        
    def save(self, format: str) -> Optional[Path]:
        """Save tracks in specified format."""
        if format == 'json':
            return self._save_json()
        elif format == 'markdown':
            return self._save_markdown()
        elif format == 'm3u':
            return self._save_m3u()
        else:
            logger.error(f"Unsupported format: {format}")
            return None

    def _save_json(self) -> Path:
        """Save tracks as JSON file with precise timing."""
        output_file = self.output_dir / self._format_filename('json')
        
        # Calculate total duration and gaps
        total_duration = sum(t.duration or 0 for t in self.tracks)
        gaps = [(i, self.tracks[i].gap_to(self.tracks[i+1])) 
                for i in range(len(self.tracks)-1)
                if self.tracks[i].gap_to(self.tracks[i+1]) > self._config.track.min_gap_threshold]
        overlaps = [(i, self.tracks[i].timing.end_time - self.tracks[i+1].timing.start_time)
                   for i in range(len(self.tracks)-1)
                   if self.tracks[i].overlaps_with(self.tracks[i+1])]
        
        data = {
            'mix_info': {
                **self.mix_info,
                'total_duration': str(timedelta(seconds=int(total_duration))),
                'track_count': len(self.tracks)
            },
            'analysis_info': {
                'timestamp': datetime.now().isoformat(),
                'track_count': len(self.tracks),
                'average_confidence': sum(t.confidence for t in self.tracks) / len(self.tracks) if self.tracks else 0,
                'min_confidence': min(t.confidence for t in self.tracks) if self.tracks else 0,
                'max_confidence': max(t.confidence for t in self.tracks) if self.tracks else 0,
                'total_duration': total_duration,
                'total_duration_formatted': str(timedelta(seconds=int(total_duration))),
                'gaps_detected': len(gaps),
                'overlaps_detected': len(overlaps),
                'timing_quality': {
                    'gaps': [
                        {
                            'position': f"Between track {i+1} and {i+2}",
                            'duration': duration,
                            'start_track': self.tracks[i].song_name,
                            'end_track': self.tracks[i+1].song_name
                        }
                        for i, duration in gaps
                    ],
                    'overlaps': [
                        {
                            'position': f"Between track {i+1} and {i+2}",
                            'duration': duration,
                            'first_track': self.tracks[i].song_name,
                            'second_track': self.tracks[i+1].song_name
                        }
                        for i, duration in overlaps
                    ]
                }
            },
            'tracks': [
                {
                    'song_name': track.song_name,
                    'artist': track.artist,
                    'time_in_mix': track.time_in_mix,
                    'confidence': track.confidence,
                    'timing': {
                        'start_time': track.timing.start_time if track.timing else None,
                        'end_time': track.timing.end_time if track.timing else None,
                        'duration': track.duration if track.timing else None,
                        'duration_formatted': track.format_duration() if track.timing else "--:--",
                        'timing_confidence': track.timing.confidence if track.timing else None
                    } if track.timing else None,
                    'gap_to_next': track.gap_to(self.tracks[i+1]) if i < len(self.tracks)-1 else None,
                    'overlaps_next': track.overlaps_with(self.tracks[i+1]) if i < len(self.tracks)-1 else None
                }
                for i, track in enumerate(self.tracks)
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Saved JSON tracklist to: {output_file}")
        logger.info(f"Analysis Summary:")
        logger.info(f"- Total tracks: {data['analysis_info']['track_count']}")
        logger.info(f"- Total duration: {data['analysis_info']['total_duration_formatted']}")
        logger.info(f"- Average confidence: {data['analysis_info']['average_confidence']:.1f}%")
        logger.info(f"- Confidence range: {data['analysis_info']['min_confidence']:.1f}% - {data['analysis_info']['max_confidence']:.1f}%")
        if gaps:
            logger.info(f"- Gaps detected: {len(gaps)}")
        if overlaps:
            logger.info(f"- Overlaps detected: {len(overlaps)}")
        return output_file

    def _save_m3u(self) -> Path:
        """Save tracks as M3U playlist with durations."""
        output_file = self.output_dir / self._format_filename('m3u')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            f.write(f"#PLAYLIST:{self.mix_info.get('title', 'Unknown Mix')}\n")
            if self.mix_info.get('artist'):
                f.write(f"#EXTALB:{self.mix_info['artist']}\n")
            
            if not self.tracks:
                f.write("#EXTINF:-1,No tracks identified\n")
                f.write("# No tracks were identified in this mix\n")
            else:
                for i, track in enumerate(self.tracks):
                    duration = int(track.duration) if track.timing else -1
                    f.write(f"#EXTINF:{duration},{track.artist} - {track.song_name}\n")
                    
                    # Add detailed timing information as comments
                    f.write(f"#EXTTIME:{track.time_in_mix}")
                    if track.timing:
                        f.write(f" (Duration: {track.format_duration()})")
                    
                    # Add gap/overlap information
                    if i < len(self.tracks) - 1:
                        if track.overlaps_with(self.tracks[i+1]):
                            overlap = track.timing.end_time - self.tracks[i+1].timing.start_time
                            f.write(f" [Overlap with next: {overlap:.1f}s]")
                        else:
                            gap = track.gap_to(self.tracks[i+1])
                            if gap and gap > self._config.track.min_gap_threshold:
                                f.write(f" [Gap to next: {gap:.1f}s]")
                    f.write("\n")
                    
                    # Add placeholder URL (since we don't have actual files)
                    f.write(f"#Generated tracklist entry for: {track.artist} - {track.song_name}\n")
        
        logger.info(f"Saved M3U playlist to: {output_file}")
        return output_file

    def _save_markdown(self) -> Path:
        """Save tracks as Markdown file with timing details."""
        output_file = self.output_dir / self._format_filename('md')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# {self.mix_info.get('title', 'Unknown Mix')}\n\n")
            
            if self.mix_info.get('artist'):
                f.write(f"**Artist:** {self.mix_info['artist']}\n")
            if self.mix_info.get('date'):
                f.write(f"**Date:** {self.mix_info['date']}\n")
            
            # Add mix duration
            total_duration = sum(t.duration or 0 for t in self.tracks)
            f.write(f"**Total Duration:** {str(timedelta(seconds=int(total_duration)))}\n")
            
            f.write("\n## Tracklist\n\n")
            
            if not self.tracks:
                f.write("*No tracks identified*\n\n")
            else:
                # Write tracks with timing information
                for i, track in enumerate(self.tracks, 1):
                    # Basic track information
                    f.write(f"{i}. **{track.time_in_mix}** - {track.artist} - {track.song_name}")
                    
                    # Add duration if available
                    if track.timing:
                        f.write(f" [{track.format_duration()}]")
                    
                    # Add confidence if low
                    if track.confidence < 80:
                        f.write(f" _(Confidence: {track.confidence:.0f}%)_")
                    
                    # Add gap or overlap information
                    if i < len(self.tracks):
                        if track.overlaps_with(self.tracks[i]):
                            overlap = track.timing.end_time - self.tracks[i].timing.start_time
                            f.write(f" [⚠️ Overlap: {overlap:.1f}s]")
                        else:
                            gap = track.gap_to(self.tracks[i])
                            if gap and gap > self._config.track.min_gap_threshold:
                                f.write(f" [⚡ Gap: {gap:.1f}s]")
                    
                    f.write("\n")
            
            # Add analysis summary
            f.write("\n## Analysis Summary\n\n")
            f.write(f"- **Total Duration:** {str(timedelta(seconds=int(total_duration)))}\n")
            f.write(f"- **Track Count:** {len(self.tracks)}\n")
            if self.tracks:
                f.write(f"- **Average Confidence:** {sum(t.confidence for t in self.tracks) / len(self.tracks):.1f}%\n")
            else:
                f.write("- **Average Confidence:** N/A\n")
            
            # Add timing quality section if there are gaps or overlaps
            gaps = [(i, self.tracks[i].gap_to(self.tracks[i+1])) 
                   for i in range(len(self.tracks)-1)
                   if self.tracks[i].gap_to(self.tracks[i+1]) > self._config.track.min_gap_threshold]
            overlaps = [(i, self.tracks[i].timing.end_time - self.tracks[i+1].timing.start_time)
                       for i in range(len(self.tracks)-1)
                       if self.tracks[i].overlaps_with(self.tracks[i+1])]
            
            if gaps or overlaps:
                f.write("\n### Timing Analysis\n\n")
                
                if gaps:
                    f.write("#### Gaps Detected\n")
                    for i, duration in gaps:
                        f.write(f"- **{self.tracks[i].time_in_mix}** - Gap of {duration:.1f}s after \"{self.tracks[i].song_name}\"\n")
                
                if overlaps:
                    f.write("\n#### Overlaps Detected\n")
                    for i, duration in overlaps:
                        f.write(f"- **{self.tracks[i].time_in_mix}** - Overlap of {duration:.1f}s between \"{self.tracks[i].song_name}\" and \"{self.tracks[i+1].song_name}\"\n")
        
        logger.info(f"Saved Markdown tracklist to: {output_file}")
        return output_file

    def _format_filename(self, extension: str) -> str:
        """Generate filename in format: [YYYYMMDD] Artist - Description.extension"""
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
