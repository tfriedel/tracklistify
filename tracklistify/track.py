"""
Track identification and management module.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
import re

from .logger import logger
from .config import config

@dataclass
class Track:
    """Represents an identified track."""
    song_name: str
    artist: str
    time_in_mix: str
    confidence: float
    
    @property
    def markdown_line(self) -> str:
        """Format track for markdown output."""
        return f"- [{self.time_in_mix}] **{self.artist}** - {self.song_name} ({self.confidence:.0f}%)"
    
    @property
    def m3u_line(self) -> str:
        """Format track for M3U playlist."""
        return f"#EXTINF:-1,{self.artist} - {self.song_name}"
    
    def __str__(self) -> str:
        return f"{self.time_in_mix} - {self.artist} - {self.song_name} ({self.confidence:.0f}%)"
    
    def is_similar_to(self, other: 'Track') -> bool:
        """Check if two tracks are similar."""
        # Normalize strings for comparison
        def normalize(s: str) -> str:
            return re.sub(r'[^\w\s]', '', s.lower())
        
        this_song = normalize(self.song_name)
        this_artist = normalize(self.artist)
        other_song = normalize(other.song_name)
        other_artist = normalize(other.artist)
        
        # Check for exact matches first
        if this_song == other_song and this_artist == other_artist:
            return True
            
        # Check for substring matches
        if (this_song in other_song or other_song in this_song) and \
           (this_artist in other_artist or other_artist in this_artist):
            return True
            
        return False
    
    def time_to_seconds(self) -> int:
        """Convert time_in_mix to seconds."""
        try:
            time = datetime.strptime(self.time_in_mix, '%H:%M:%S')
            return time.hour * 3600 + time.minute * 60 + time.second
        except ValueError:
            logger.error(f"Invalid time format: {self.time_in_mix}")
            return 0

class TrackMatcher:
    """Handles track matching and merging."""
    
    def __init__(self):
        self.tracks: List[Track] = []
        self.time_threshold = config.track.time_threshold
        self.min_confidence = 0  # Keep all tracks with confidence > 0
        self.max_duplicates = config.track.max_duplicates
    
    def add_track(self, track: Track):
        """Add a track to the collection if it meets confidence threshold."""
        if track.confidence > self.min_confidence:
            self.tracks.append(track)
            logger.debug(f"Added track to matcher: {track.song_name} (Confidence: {track.confidence:.1f}%)")
    
    def merge_nearby_tracks(self) -> List[Track]:
        """Merge similar tracks that appear close together in time."""
        if not self.tracks:
            return []
            
        # Sort tracks by time
        self.tracks.sort(key=lambda t: t.time_to_seconds())
        
        merged = []
        current_group = [self.tracks[0]]
        
        logger.debug(f"\nStarting track merging process with {len(self.tracks)} tracks...")
        
        for track in self.tracks[1:]:
            last_track = current_group[-1]
            time_diff = track.time_to_seconds() - last_track.time_to_seconds()
            
            if time_diff <= self.time_threshold and track.is_similar_to(last_track):
                # Add to current group if similar and within time threshold
                if len(current_group) < self.max_duplicates:
                    current_group.append(track)
                    logger.debug(f"Grouped similar track: {track.song_name} at {track.time_in_mix}")
            else:
                # Start new group
                if current_group:
                    # Add highest confidence track from current group
                    best_track = max(current_group, key=lambda t: t.confidence)
                    if not any(best_track.is_similar_to(m) for m in merged):
                        merged.append(best_track)
                        logger.debug(f"Added merged track: {best_track.song_name} at {best_track.time_in_mix} (Confidence: {best_track.confidence:.1f}%)")
                current_group = [track]
        
        # Handle last group
        if current_group:
            best_track = max(current_group, key=lambda t: t.confidence)
            if not any(best_track.is_similar_to(m) for m in merged):
                merged.append(best_track)
                logger.debug(f"Added final merged track: {best_track.song_name} at {best_track.time_in_mix}")
        
        logger.debug(f"Track merging completed. Final track count: {len(merged)}")
        return merged
