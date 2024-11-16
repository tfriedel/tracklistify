"""
Track identification and management functionality.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from .config import config
from .logger import logger

@dataclass
class Track:
    """Represents an identified track."""
    song_name: str
    artist: str
    time_in_mix: str
    confidence: float
    
    @property
    def key(self) -> str:
        """Unique identifier for the track."""
        return f"{self.artist}-{self.song_name}"

class TrackMatcher:
    """Handles track identification and merging."""
    
    def __init__(self):
        self.tracks: List[Track] = []
        self.track_counts = {}
    
    def add_track(self, track: Track) -> bool:
        """
        Add a track to the collection if it meets confidence threshold
        and duplicate criteria.
        
        Args:
            track: Track to add
            
        Returns:
            bool: True if track was added, False if filtered out
        """
        if track.confidence < config.track.min_confidence:
            logger.debug(f"Track {track.key} filtered out due to low confidence: {track.confidence}")
            return False
            
        track_key = track.key
        count = self.track_counts.get(track_key, 0)
        
        if count >= config.track.max_duplicates:
            logger.debug(f"Track {track_key} filtered out due to too many duplicates")
            return False
            
        self.tracks.append(track)
        self.track_counts[track_key] = count + 1
        logger.info(f"Added track: {track.song_name} by {track.artist}")
        return True
        
    def merge_nearby_tracks(self) -> List[Track]:
        """
        Merge tracks that are detected multiple times within the
        time threshold window.
        
        Returns:
            List[Track]: Merged track list
        """
        if not self.tracks:
            return []
            
        # Sort tracks by time
        sorted_tracks = sorted(self.tracks, key=lambda t: t.time_in_mix)
        merged = []
        current = sorted_tracks[0]
        
        for next_track in sorted_tracks[1:]:
            if (current.key == next_track.key and
                self._time_difference(current.time_in_mix, next_track.time_in_mix) 
                <= config.track.time_threshold):
                # Merge by keeping the one with higher confidence
                if next_track.confidence > current.confidence:
                    current = next_track
            else:
                merged.append(current)
                current = next_track
                
        merged.append(current)
        return merged
        
    @staticmethod
    def _time_difference(time1: str, time2: str) -> int:
        """Calculate difference between two timestamps in seconds."""
        t1 = datetime.strptime(time1, "%H:%M:%S")
        t2 = datetime.strptime(time2, "%H:%M:%S")
        return abs(int((t2 - t1).total_seconds()))
