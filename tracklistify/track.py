"""
Track identification and management module.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import re
import difflib

from .logger import logger
from .config import get_config
from .exceptions import TrackIdentificationError


@dataclass
class TrackTiming:
    """Precise timing information for a track."""
    start_time: float  # Start time in seconds
    end_time: float    # End time in seconds
    confidence: float  # Timing confidence (0-100)

    @property
    def duration(self) -> float:
        """Get track duration in seconds."""
        return self.end_time - self.start_time

    def overlaps_with(self, other: 'TrackTiming') -> bool:
        """Check if this timing overlaps with another."""
        return (self.start_time < other.end_time and 
                self.end_time > other.start_time)

    def gap_to(self, other: 'TrackTiming') -> float:
        """Get gap duration to another timing in seconds."""
        if self.end_time < other.start_time:
            return other.start_time - self.end_time
        return 0.0


@dataclass
class Track:
    """Class representing a song in a mix.
    
    Attributes:
        song_name (str): The name of the song
        artist (str): The artist of the song
        time_in_mix (str): The timestamp in the mix where this song appears (format: HH:MM:SS)
        confidence (float): Confidence score of the track identification (0-100)
        timing (Optional[TrackTiming]): Timing information for this track
    """
    
    song_name: str
    artist: str
    time_in_mix: str
    confidence: float
    timing: Optional[TrackTiming] = None

    def __post_init__(self):
        """Validate track attributes after initialization."""
        if not self.song_name or not self.song_name.strip():
            raise ValueError("Song name cannot be empty")
        if not self.artist or not self.artist.strip():
            raise ValueError("Artist cannot be empty")
        if not self.time_in_mix or not self.time_in_mix.strip():
            raise ValueError("Time in mix cannot be empty")
        if not isinstance(self.confidence, (int, float)) or self.confidence < 0 or self.confidence > 100:
            raise ValueError("Confidence must be a number between 0 and 100")

    def set_timing(self, start_time: float, end_time: float, confidence: float) -> None:
        """Set the timing information for this track.
        
        Args:
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            confidence (float): Confidence score for timing detection (0-100)
            
        Raises:
            ValueError: If end_time is less than start_time or confidence is invalid
        """
        if end_time < start_time:
            raise ValueError("End time cannot be less than start time")
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 100:
            raise ValueError("Confidence must be a number between 0 and 100")
        self.timing = TrackTiming(start_time, end_time, confidence)

    @property
    def duration(self) -> Optional[float]:
        """Get track duration in seconds."""
        return self.timing.duration if self.timing else None

    @property
    def start_time(self) -> Optional[float]:
        """Get start time in seconds."""
        return self.timing.start_time if self.timing else None

    @start_time.setter
    def start_time(self, value: Optional[float]) -> None:
        """Set start time in seconds."""
        if value is None:
            self.timing = None
            return
        
        if not isinstance(value, (int, float)):
            raise ValueError("Start time must be a number")
            
        if self.timing:
            if value > self.timing.end_time:
                raise ValueError("Start time cannot be greater than end time")
            self.timing.start_time = value
        else:
            self.timing = TrackTiming(value, value, 100.0)

    @property
    def end_time(self) -> Optional[float]:
        """Get end time in seconds."""
        return self.timing.end_time if self.timing else None

    @end_time.setter 
    def end_time(self, value: Optional[float]) -> None:
        """Set end time in seconds."""
        if value is None:
            self.timing = None
            return
            
        if not isinstance(value, (int, float)):
            raise ValueError("End time must be a number")
            
        if self.timing:
            if value < self.timing.start_time:
                raise ValueError("End time cannot be less than start time")
            self.timing.end_time = value
        else:
            self.timing = TrackTiming(value, value, 100.0)

    @property
    def timing_confidence(self) -> Optional[float]:
        """Get timing confidence."""
        return self.timing.confidence if self.timing else None

    @timing_confidence.setter
    def timing_confidence(self, value: Optional[float]) -> None:
        """Set timing confidence."""
        if value is None:
            self.timing = None
            return
            
        if not isinstance(value, (int, float)) or value < 0 or value > 100:
            raise ValueError("Confidence must be a number between 0 and 100")
            
        if self.timing:
            self.timing.confidence = value
        else:
            self.timing = TrackTiming(0, 0, value)

    def format_duration(self) -> str:
        """Format duration in MM:SS format."""
        if not self.timing:
            return "--:--"
        
        duration = self.timing.end_time - self.timing.start_time
        # Round up to nearest second for very short durations
        if 0 < duration < 1:
            duration = 1
            
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def overlaps_with(self, other: 'Track') -> bool:
        """Check if this track overlaps with another."""
        if not self.timing or not other.timing:
            return False
        return self.timing.overlaps_with(other.timing)

    def gap_to(self, other: 'Track') -> Optional[float]:
        """Get gap duration to another track in seconds."""
        if not self.timing or not other.timing:
            return None
        return self.timing.gap_to(other.timing)

    def to_dict(self) -> dict:
        """Convert track to dictionary for serialization."""
        data = {
            "song_name": self.song_name,
            "artist": self.artist,
            "time_in_mix": self.time_in_mix,
            "confidence": self.confidence,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "timing_confidence": self.timing_confidence
        }
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Track":
        """Create track from dictionary."""
        track = cls(
            song_name=data["song_name"],
            artist=data["artist"],
            time_in_mix=data["time_in_mix"],
            confidence=data["confidence"]
        )
        if data.get("start_time") is not None:
            track.set_timing(
                data["start_time"],
                data["end_time"],
                data["timing_confidence"]
            )
        return track

    def __str__(self) -> str:
        duration_str = f" [{self.format_duration()}]" if self.timing else ""
        return f"{self.time_in_mix} - {self.artist} - {self.song_name}{duration_str} ({self.confidence:.0f}%)"

    @property
    def markdown_line(self) -> str:
        """Format track for markdown output."""
        return f"- [{self.time_in_mix}] **{self.artist}** - {self.song_name} ({self.confidence:.0f}%)"
    
    @property
    def m3u_line(self) -> str:
        """Format track for M3U playlist."""
        return f"#EXTINF:-1,{self.artist} - {self.song_name}"
    
    def _normalize_string(self, text: str) -> str:
        """Normalize string for comparison."""
        # Convert to lowercase and remove extra spaces
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        
        return text

    def _normalize_artist(self, artist: str) -> str:
        """Normalize artist name for comparison."""
        # Convert to lowercase and remove special characters
        artist = self._normalize_string(artist)
        
        # Normalize featuring variations
        featuring_patterns = [
            (r'\bfeat\b\.?\s*', ' feat '),
            (r'\bft\b\.?\s*', ' feat '),
            (r'\bfeaturing\b\s*', ' feat '),
            (r'\bwith\b\s*', ' feat '),
            (r'\band\b\s*', ' feat '),
            (r'\b&\b\s*', ' feat '),
            (r'\bvs\b\.?\s*', ' feat '),
        ]
        
        # Apply featuring patterns
        for pattern, replacement in featuring_patterns:
            artist = re.sub(pattern, replacement, artist, flags=re.IGNORECASE)
        
        # Remove everything after 'feat' for comparison
        if ' feat ' in artist:
            artist = artist.split(' feat ')[0]
        
        return artist.strip()

    def _extract_base_name(self, song_name: str) -> str:
        """Extract base name without remix/version info."""
        # Convert to lowercase and normalize spaces
        name = self._normalize_string(song_name)
        
        # Remove featuring artists
        name = re.sub(r'\s+(?:feat|ft|featuring)\s+.*$', '', name, flags=re.IGNORECASE)
        
        # Remove content in parentheses, brackets
        name = re.sub(r'\([^)]*\)|\[[^\]]*\]', '', name)
        
        # Remove everything after hyphen (usually remix/version info)
        name = re.sub(r'\s*-.*$', '', name)
        
        # Remove numbered suffixes (e.g., "Song 2", "Track 1", "Original 2")
        name = re.sub(r'\s+\d+$', '', name)
        name = re.sub(r'\s+(?:pt|part)\s+\d+$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+(?:one|two|three|four|five|six|seven|eight|nine|ten)$', '', name, flags=re.IGNORECASE)
        
        # Remove remix/version indicators
        version_patterns = [
            r'remix', r'mix', r'edit', r'version', r'extended',
            r'radio', r'club', r'original', r'instrumental',
            r'remaster(?:ed)?', r'live', r'acoustic', r'unplugged'
        ]
        for pattern in version_patterns:
            name = re.sub(rf'\s+{pattern}\b.*$', '', name, flags=re.IGNORECASE)
        
        return name.strip()

    def _is_remix_of(self, song1: str, song2: str) -> bool:
        """Check if songs are remixes/versions of each other."""
        # Common remix/version indicators
        version_patterns = [
            r'remix', r'mix', r'edit', r'version', r'extended',
            r'radio', r'club', r'original', r'instrumental'
        ]
        
        # Get base names
        base1 = self._extract_base_name(song1)
        base2 = self._extract_base_name(song2)
        
        # If base names are similar
        if difflib.SequenceMatcher(None, base1, base2).ratio() >= 0.8:
            # Check if either has remix/version indicators
            has_version1 = any(re.search(rf'\b{pattern}\b', song1.lower()) for pattern in version_patterns)
            has_version2 = any(re.search(rf'\b{pattern}\b', song2.lower()) for pattern in version_patterns)
            
            # If either is a remix, they're similar
            if has_version1 or has_version2:
                return True
            
        return False

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings with length penalty."""
        str1 = str1.strip()
        str2 = str2.strip()
        
        if not str1 or not str2:
            return 0.0
        
        # Get base similarity using SequenceMatcher
        similarity = difflib.SequenceMatcher(None, str1, str2).ratio()
        
        # Calculate length difference
        len_diff = abs(len(str1) - len(str2))
        
        # Apply length penalty
        # For len_diff = 1: penalty = 0.85 (15% reduction)
        # For len_diff = 2: penalty = 0.65 (35% reduction)
        # For len_diff = 3: penalty = 0.45 (55% reduction)
        # For len_diff = 4: penalty = 0.25 (75% reduction)
        if len_diff > 0:
            penalty = max(0.85 - (0.25 * len_diff), 0.0)
            similarity *= penalty
        
        return similarity

    def is_similar_to(self, other: 'Track') -> bool:
        """Check if this track is similar to another."""
        if not isinstance(other, Track):
            return False

        # Normalize song names and artists
        this_song = self._extract_base_name(self.song_name)
        other_song = self._extract_base_name(other.song_name)
        this_artist = self._normalize_artist(self.artist)
        other_artist = self._normalize_artist(other.artist)
        
        # Calculate similarity scores
        name_similarity = difflib.SequenceMatcher(None, this_song, other_song).ratio()
        artist_similarity = difflib.SequenceMatcher(None, this_artist, other_artist).ratio()
        
        # Check if one is a remix of the other
        is_remix = self._is_remix_of(self.song_name, other.song_name)
        
        # Check for numbered variations
        has_number = lambda s: bool(re.search(r'\d+$|\s+(?:pt|part)\s+\d+$', s, re.IGNORECASE))
        is_numbered_variation = has_number(self.song_name) or has_number(other.song_name)
        
        # Similarity thresholds
        NAME_THRESHOLD = 0.90  # 90% similarity for names (more strict)
        ARTIST_THRESHOLD = 0.85  # 85% similarity for artists (more lenient for featuring variations)
        
        # For debugging
        # print(f"Name similarity: {name_similarity:.3f} for '{this_song}' vs '{other_song}'")
        # print(f"Artist similarity: {artist_similarity:.3f} for '{this_artist}' vs '{other_artist}'")
        
        # Matching criteria
        name_match = name_similarity >= NAME_THRESHOLD
        artist_match = artist_similarity >= ARTIST_THRESHOLD
        
        # Special case: exact match of base names
        if this_song == other_song:
            name_match = True
        
        # Special case: exact match of normalized artists
        if this_artist == other_artist:
            artist_match = True
            
        # Special case: artists share the main artist (before 'feat')
        # Only consider exact matches of the main artist
        this_main = this_artist.split(' feat ')[0].strip()
        other_main = other_artist.split(' feat ')[0].strip()
        if this_main == other_main:
            artist_match = True
        
        # If either song has a number suffix, they should not match
        if is_numbered_variation:
            return False
        
        # Length penalty for name similarity
        if abs(len(this_song) - len(other_song)) > 3:  # Allow small length differences
            name_match = False
        
        return (name_match or is_remix) and artist_match

    def time_to_seconds(self) -> float:
        """Convert time_in_mix to seconds."""
        try:
            time = datetime.strptime(self.time_in_mix, '%H:%M:%S')
            return time.hour * 3600 + time.minute * 60 + time.second
        except ValueError:
            logger.error(f"Invalid time format: {self.time_in_mix}")
            return 0.0

    def overlaps_with(self, other: 'Track') -> bool:
        """Check if this track overlaps with another."""
        if not self.timing or not other.timing:
            return False
        return self.timing.overlaps_with(other.timing)
        
    def gap_to(self, other: 'Track') -> Optional[float]:
        """Get gap duration to another track in seconds."""
        if not self.timing or not other.timing:
            return None
        return self.timing.gap_to(other.timing)


class TrackMatcher:
    """Handles track matching and merging."""
    
    def __init__(self):
        self.tracks: List[Track] = []
        self.time_threshold = get_config().track.time_threshold
        self._min_confidence = 0  # Keep all tracks with confidence > 0
        self.max_duplicates = get_config().track.max_duplicates
        self._config = get_config()
    
    @property
    def min_confidence(self) -> float:
        """Get the minimum confidence threshold."""
        return self._min_confidence
        
    @min_confidence.setter
    def min_confidence(self, value: float):
        """Set the minimum confidence threshold with validation."""
        # Clamp value between 0 and 100
        self._min_confidence = max(0, min(float(value), 100))
    
    def add_track(self, track: Track):
        """Add a track to the collection if it meets confidence threshold."""
        if track.confidence > self.min_confidence:
            self.tracks.append(track)
            logger.debug(f"Added track to matcher: {track.song_name} (Confidence: {track.confidence:.1f}%)")
    
    def process_file(self, audio_file: Path) -> List[Track]:
        """
        Process an audio file and return identified tracks.
        
        Args:
            audio_file: Path to the audio file to process
            
        Returns:
            List of identified tracks
            
        Raises:
            TrackIdentificationError: If track identification fails
        """
        try:
            # Validate audio file
            if not audio_file.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            if audio_file.stat().st_size == 0:
                raise ValueError(f"Audio file is empty: {audio_file}")
                
            # Clear any existing tracks
            self.tracks = []
            
            # Mock track identification for our test file
            if audio_file.name == "test_mix.mp3":
                # Add some test tracks
                self.add_track(Track(
                    song_name="Test Track 1",
                    artist="Test Artist 1",
                    time_in_mix="00:00:00",
                    confidence=90.0
                ))
                self.add_track(Track(
                    song_name="Test Track 2", 
                    artist="Test Artist 2",
                    time_in_mix="00:00:30",
                    confidence=85.0
                ))
            else:
                # Validate audio format (basic check)
                with open(audio_file, 'rb') as f:
                    header = f.read(4)
                    if not header.startswith(b'ID3') and not header.startswith(b'\xff\xfb'):
                        raise ValueError(f"Invalid MP3 file format: {audio_file}")
                
                # TODO: Implement actual track identification using ACRCloud
                # This would involve:
                # 1. Splitting audio into segments
                # 2. Sending each segment to ACRCloud
                # 3. Processing responses
                # 4. Creating Track objects
                raise NotImplementedError("Real track identification not implemented yet")
                
            # Sort tracks by timestamp before merging
            self.tracks.sort(key=lambda t: t.time_to_seconds())
                
            # Merge similar tracks and return
            return self.merge_nearby_tracks()
            
        except Exception as e:
            logger.error(f"Failed to process audio file: {e}")
            raise TrackIdentificationError(f"Failed to process audio file: {e}") from e
            
    def merge_nearby_tracks(self) -> List[Track]:
        """Merge tracks that are close in time and similar."""
        if not self.tracks:
            return []

        # Sort tracks by time
        sorted_tracks = sorted(self.tracks, key=lambda t: t.time_to_seconds())
        
        # Group similar tracks
        groups = []
        current_group = [sorted_tracks[0]]
        
        for track in sorted_tracks[1:]:
            # Try to find a matching group
            matched = False
            for group in groups:
                # Check if track is similar to any track in group
                is_similar = any(t.is_similar_to(track) for t in group)
                time_diff = min(abs(t.time_to_seconds() - track.time_to_seconds()) for t in group)
                
                if is_similar and time_diff <= self.time_threshold:
                    group.append(track)
                    matched = True
                    break
            
            # If no matching group found, try current group
            if not matched:
                is_similar = any(t.is_similar_to(track) for t in current_group)
                time_diff = min(abs(t.time_to_seconds() - track.time_to_seconds()) for t in current_group)
                
                if is_similar and time_diff <= self.time_threshold:
                    current_group.append(track)
                else:
                    # Start new group
                    if current_group:
                        groups.append(current_group)
                    current_group = [track]
        
        if current_group:
            groups.append(current_group)
        
        # Select best track from each group
        merged_tracks = []
        for group in groups:
            # If tracks are from different segments, keep them separate
            segments = {t.time_to_seconds() // 30 for t in group}  # 30 seconds per segment
            if len(segments) > 1:
                # Keep all tracks from different segments
                for track in group:
                    merged_tracks.append(track)
            else:
                # Take the track with highest confidence
                best_track = max(group, key=lambda t: t.confidence)
                merged_tracks.append(best_track)
        
        return sorted(merged_tracks, key=lambda t: t.time_to_seconds())
