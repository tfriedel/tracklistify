"""
Tests for output timing functionality.
"""

import unittest
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime
from tracklistify.track import Track
from tracklistify.output import TracklistOutput

class TestOutputTiming(unittest.TestCase):
    """Test cases for output timing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.tracks = [
            Track("Track 1", "Artist 1", "00:00:00", 90.0),
            Track("Track 2", "Artist 2", "00:03:00", 85.0),
            Track("Track 3", "Artist 3", "00:06:00", 95.0)
        ]
        
        # Set timing information
        self.tracks[0].set_timing(0.0, 170.0, 0.9)     # 0:00 - 2:50
        self.tracks[1].set_timing(180.0, 350.0, 0.85)  # 3:00 - 5:50
        self.tracks[2].set_timing(360.0, 530.0, 0.95)  # 6:00 - 8:50
        
        self.mix_info = {
            'title': 'Test Mix',
            'artist': 'Test Artist',
            'date': '2024-01-01'
        }
        
        # Change to temp directory
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_dir)

    def test_json_output_timing(self):
        """Test JSON output format with timing information."""
        output = TracklistOutput(self.tracks, self.mix_info)
        output_file = output.save('json')
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check timing information in JSON
        self.assertIn('timing', data['tracks'][0])
        track_timing = data['tracks'][0]['timing']
        self.assertEqual(track_timing['start_time'], 0.0)
        self.assertEqual(track_timing['end_time'], 170.0)
        self.assertEqual(track_timing['duration'], 170.0)
        self.assertEqual(track_timing['duration_formatted'], "02:50")
        self.assertEqual(track_timing['timing_confidence'], 0.9)
        
        # Check gap information
        self.assertEqual(data['tracks'][0]['gap_to_next'], 10.0)
        self.assertFalse(data['tracks'][0]['overlaps_next'])
        
        # Check analysis info
        self.assertIn('timing_quality', data['analysis_info'])
        timing_quality = data['analysis_info']['timing_quality']
        self.assertEqual(len(timing_quality['gaps']), 2)  # Two gaps between three tracks
        self.assertEqual(len(timing_quality['overlaps']), 0)

    def test_markdown_output_timing(self):
        """Test Markdown output format with timing information."""
        output = TracklistOutput(self.tracks, self.mix_info)
        output_file = output.save('markdown')
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check timing information in markdown
        self.assertIn("[02:50]", content)  # Duration of first track
        self.assertIn("Gap: 10.0s", content)  # Gap between tracks
        self.assertIn("## Analysis Summary", content)
        self.assertIn("### Timing Analysis", content)
        self.assertIn("#### Gaps Detected", content)

    def test_m3u_output_timing(self):
        """Test M3U output format with timing information."""
        output = TracklistOutput(self.tracks, self.mix_info)
        output_file = output.save('m3u')
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check timing information in M3U
        self.assertIn("#EXTINF:170,Artist 1 - Track 1", content)  # Duration in seconds
        self.assertIn("(Duration: 02:50)", content)  # Formatted duration
        self.assertIn("[Gap to next: 10.0s]", content)  # Gap information

    def test_output_with_overlaps(self):
        """Test output formats with overlapping tracks."""
        # Create overlapping tracks
        overlapping_tracks = [
            Track("Track 1", "Artist 1", "00:00:00", 90.0),
            Track("Track 2", "Artist 2", "00:03:00", 85.0)
        ]
        overlapping_tracks[0].set_timing(0.0, 190.0, 0.9)   # 0:00 - 3:10
        overlapping_tracks[1].set_timing(180.0, 360.0, 0.85)  # 3:00 - 6:00
        
        output = TracklistOutput(overlapping_tracks, self.mix_info)
        
        # Test JSON output
        json_file = output.save('json')
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check overlap information
        self.assertTrue(data['tracks'][0]['overlaps_next'])
        self.assertEqual(len(data['analysis_info']['timing_quality']['overlaps']), 1)
        
        # Test Markdown output
        md_file = output.save('markdown')
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("⚠️ Overlap:", content)
        self.assertIn("Overlaps Detected", content)
        
        # Test M3U output
        m3u_file = output.save('m3u')
        with open(m3u_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("[Overlap with next:", content)

    def test_output_without_timing(self):
        """Test output formats with tracks missing timing information."""
        tracks_no_timing = [
            Track("Track 1", "Artist 1", "00:00:00", 90.0),
            Track("Track 2", "Artist 2", "00:03:00", 85.0)
        ]
        
        output = TracklistOutput(tracks_no_timing, self.mix_info)
        
        # Test JSON output
        json_file = output.save('json')
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIsNone(data['tracks'][0]['timing'])
        
        # Test Markdown output
        md_file = output.save('markdown')
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertNotIn("[00:00]", content)
        
        # Test M3U output
        m3u_file = output.save('m3u')
        with open(m3u_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("#EXTINF:-1", content)  # -1 duration for unknown length

if __name__ == '__main__':
    unittest.main()
