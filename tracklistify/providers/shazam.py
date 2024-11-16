"""Shazam track identification provider using shazamio."""

import logging
import numpy as np
import librosa
from typing import Dict, List, Tuple
from shazamio import Shazam
from .base import TrackIdentificationProvider, IdentificationError

logger = logging.getLogger(__name__)

class ShazamProvider(TrackIdentificationProvider):
    """Shazam track identification provider with advanced audio fingerprinting."""
    
    def __init__(self):
        """Initialize Shazam provider."""
        self.shazam = Shazam()
        
    def _extract_audio_features(self, audio_data: bytes, start_time: float = 0) -> Tuple[np.ndarray, int]:
        """
        Extract audio features for fingerprinting.
        
        Args:
            audio_data: Raw audio data bytes
            start_time: Start time in seconds for the audio segment
            
        Returns:
            Tuple of (audio segment, sample rate)
        """
        # Convert audio bytes to numpy array
        audio_array, sr = librosa.load(audio_data, sr=None)
        
        # Calculate start sample
        start_sample = int(start_time * sr)
        
        # Take a 10-second segment for analysis
        segment_length = 10 * sr
        audio_segment = audio_array[start_sample:start_sample + segment_length]
        
        # Apply pre-emphasis filter to boost high frequencies
        pre_emphasis = 0.97
        emphasized_signal = np.append(audio_segment[0], audio_segment[1:] - pre_emphasis * audio_segment[:-1])
        
        # Extract mel-frequency cepstral coefficients (MFCCs)
        mfccs = librosa.feature.mfcc(y=emphasized_signal, sr=sr, n_mfcc=13)
        
        # Extract spectral centroid
        spectral_centroids = librosa.feature.spectral_centroid(y=emphasized_signal, sr=sr)[0]
        
        # Normalize and combine features
        mfccs_normalized = (mfccs - np.mean(mfccs)) / np.std(mfccs)
        centroids_normalized = (spectral_centroids - np.mean(spectral_centroids)) / np.std(spectral_centroids)
        
        # Create enhanced audio segment
        enhanced_segment = np.concatenate([
            emphasized_signal,
            np.repeat(centroids_normalized, len(emphasized_signal) // len(centroids_normalized))
        ])
        
        return enhanced_segment, sr
        
    async def identify_track(self, audio_data: bytes, start_time: float = 0) -> Dict:
        """
        Identify a track using enhanced audio fingerprinting.
        
        Args:
            audio_data: Raw audio data bytes
            start_time: Start time in seconds for the audio segment
            
        Returns:
            Dict containing track information
        """
        try:
            # Extract enhanced audio features
            enhanced_segment, sr = self._extract_audio_features(audio_data, start_time)
            
            # Generate audio fingerprint and identify
            result = await self.shazam.recognize_song(enhanced_segment)
            
            if not result or not result.get('track'):
                raise IdentificationError("No track identified by Shazam")
            
            track_info = result['track']
            
            # Calculate confidence based on multiple factors
            title_match = bool(track_info.get('title'))
            metadata_completeness = sum([
                bool(track_info.get('subtitle')),
                bool(track_info.get('sections', [{}])[0].get('metadata')),
                bool(track_info.get('genres')),
            ]) / 3.0
            
            confidence = 0.9 if title_match else 0.0
            confidence = confidence * (0.7 + 0.3 * metadata_completeness)
            
            return {
                'title': track_info.get('title', ''),
                'artist': track_info.get('subtitle', ''),
                'album': track_info.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', ''),
                'year': track_info.get('sections', [{}])[0].get('metadata', [{}])[1].get('text', ''),
                'genre': track_info.get('genres', {}).get('primary', ''),
                'confidence': confidence,
                'provider': 'shazam',
                'provider_id': track_info.get('key', ''),
                'audio_features': {
                    'duration': len(enhanced_segment) / sr,
                    'sample_rate': sr,
                }
            }
            
        except Exception as e:
            logger.error(f"Shazam identification error: {str(e)}")
            raise IdentificationError(f"Failed to identify track with Shazam: {str(e)}")
    
    async def enrich_metadata(self, track_info: Dict) -> Dict:
        """
        Enrich track metadata with additional Shazam information.
        
        Args:
            track_info: Basic track information
            
        Returns:
            Dict containing enriched track information
        """
        if not track_info.get('provider_id'):
            return track_info
            
        try:
            # Get detailed track info from Shazam
            details = await self.shazam.track_about(track_info['provider_id'])
            
            # Extract additional audio features if available
            audio_features = {
                'bpm': details.get('hub', {}).get('bpm', ''),
                'key': details.get('hub', {}).get('key', ''),
                'time_signature': details.get('hub', {}).get('timeSignature', ''),
                'mode': details.get('hub', {}).get('mode', ''),
                'danceability': details.get('hub', {}).get('danceability', ''),
                'energy': details.get('hub', {}).get('energy', ''),
            }
            
            # Enrich with additional metadata
            track_info.update({
                'album_art': details.get('images', {}).get('coverart', ''),
                'isrc': details.get('hub', {}).get('isrc', ''),
                'label': details.get('hub', {}).get('label', ''),
                'audio_features': {**track_info.get('audio_features', {}), **audio_features},
            })
            
            return track_info
            
        except Exception as e:
            logger.warning(f"Failed to enrich metadata from Shazam: {str(e)}")
            return track_info
