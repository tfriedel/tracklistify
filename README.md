# Tracklistify - DJ Mix Track Identifier

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 150">
  <g transform="translate(50, 50)">
    <rect x="10" y="30" width="10" height="40" fill="#6C5CE7"/>
    <rect x="25" y="20" width="10" height="50" fill="#6C5CE7"/>
    <rect x="40" y="35" width="10" height="35" fill="#6C5CE7"/>
    <rect x="55" y="25" width="10" height="45" fill="#6C5CE7"/>
    <text x="80" y="65" font-family="Arial" font-weight="bold" font-size="35" fill="#2D3436">tracklistify</text>
  </g>
</svg>

Unleash the power of Tracklistify! Create playlists from Livesets, DJ Mixes and Podcasts by identifying tracks using advanced audio recognition. Whether you're analyzing local MP3 files or streaming from YouTube or Mixcloud, Tracklistify provides precise timestamps, detailed track info, and confidence scores. Perfect for DJs, music enthusiasts, and content creators. 

Get started today and elevate your music experience!

## Features

- 🎵 Accurate track identification in DJ mixes
- 🌐 Support for online streaming platforms:
  - YouTube
  - Mixcloud
  - Expandable to other platforms
- ⏱️ Precise timestamp tracking for each identified song
- 📊 Confidence scores for each match
- 🎼 Detailed track information (artists, albums, labels, genres)
- 📝 JSON export of results
- 🔄 Smart duplicate detection and merging
- 🎚️ Configurable analysis parameters

## Prerequisites

- Python 3.7 or higher
- ACRCloud account (free tier available)
- FFmpeg installed on your system
- Audio files in MP3 format or valid streaming URLs

## Installation

1. Clone this repository:
```bash
git clone https://github.com/betmoar/tracklistify.git
cd tracklistify
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg:
   - Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg`

4. Sign up for ACRCloud:
   - Go to [ACRCloud's website](https://www.acrcloud.com/)
   - Create a free account
   - Create a new project and get your access credentials

5. Set up your environment:
   - Copy `.env.example` to `.env`
   - Add your ACRCloud credentials to `.env`:
     ```ini
     ACRCLOUD_ACCESS_KEY=your_access_key_here
     ACRCLOUD_ACCESS_SECRET=your_access_secret_here
     ACRCLOUD_HOST=identify-eu-west-1.acrcloud.com
     ACRCLOUD_TIMEOUT=10
     ```

## Command Line Usage

The application can be run from the command line with various options and arguments.

### Quick Start

1. Analyze a mix:
```bash
# Local file
python tracklistify.py path/to/mix.mp3

# YouTube URL
python tracklistify.py https://www.youtube.com/watch?v=example

# Mixcloud URL
python tracklistify.py https://www.mixcloud.com/example/mix/
```

### Command Line Options

```
usage: tracklistify.py [-h] [-o OUTPUT] [-s SEGMENT_LENGTH] [-v] input

DJ Mix Track Identifier - Analyze and identify tracks in DJ mixes and live streams.

positional arguments:
  input                 Input file path or URL to analyze

optional arguments:
  -h, --help           show this help message and exit
  -o OUTPUT, --output OUTPUT
                       Output JSON file path (default: tracklist.json)
  -s SEGMENT_LENGTH, --segment-length SEGMENT_LENGTH
                       Length of analysis segments in seconds (default: 30)
  -v, --verbose        Enable verbose output
```

## Output

The tool saves identified tracks in the `tracklists` directory. Each analysis creates a new JSON file named using the following format:
```
[Uploader]-[Title]_YYYYMMDD_HHMMSS.json
```

Example output file structure:
```json
{
    "mix_info": {
        "title": "Example Mix",
        "uploader": "DJ Example",
        "duration": 3600,
        "description": "..."
    },
    "analysis_date": "2024-02-21 15:30:45",
    "track_count": 12,
    "tracks": [
        {
            "song_name": "Example Track",
            "artist": "Example Artist",
            "time_in_mix": "00:05:30",
            "confidence": 95
        }
    ]
}
```

### Track Identification Settings

You can fine-tune the track identification accuracy using the following environment variables:

- `MIN_CONFIDENCE`: Minimum confidence score for track matches (default: 70)
- `TIME_THRESHOLD`: Time threshold in seconds for merging nearby matches (default: 60)
- `MIN_TRACK_LENGTH`: Minimum track length in seconds (default: 30)
- `MAX_DUPLICATES`: Maximum allowed duplicates of the same track (default: 2)

### Examples

1. Process a local file:
```bash
python tracklistify.py mix.mp3
```

2. Analyze a YouTube mix with verbose output:
```bash
python tracklistify.py https://youtube.com/watch?v=example -v
```

3. Use custom segment length for analysis:
```bash
python tracklistify.py mix.mp3 -s 45
```

## Project Structure

```
tracklistify/
├── tracklistify.py     # Main application file
├── requirements.txt    # Project dependencies
├── CHANGELOG.md       # Version history and changes
├── .env.example       # Example environment variables
├── .env              # Your configuration (not tracked in git)
├── README.md         # Project documentation
├── tracklists/       # Generated tracklist files
└── assets/           # Project assets
```

## Configuration

Create a configuration dictionary with your ACRCloud credentials:

```python
config = {
    'access_key': 'your_access_key',
    'access_secret': 'your_access_secret',
    'host': 'identify-eu-west-1.acrcloud.com'  # or your region's endpoint
}
```

## Usage

### Local File Analysis

```python
from mix_track_identifier import MixTrackIdentifier

# Initialize the identifier with your config
identifier = MixTrackIdentifier(config)

# Analyze a local mix file
results = identifier.identify_tracks("path/to/your/mix.mp3")
identifier.export_results(results, "tracklist.json")
```

### Streaming Source Analysis

```python
# Analyze a YouTube mix
youtube_results = identifier.identify_stream("https://www.youtube.com/watch?v=example")
identifier.export_results(youtube_results, "youtube_tracklist.json")

# Analyze a Mixcloud mix
mixcloud_results = identifier.identify_stream("https://www.mixcloud.com/example/mix/")
identifier.export_results(mixcloud_results, "mixcloud_tracklist.json")
```

### Sample Output

```json
[
    {
        "song_name": "Blue Monday",
        "artist": "New Order",
        "album": "Power, Corruption & Lies",
        "label": "Factory",
        "genres": ["Electronic", "New Wave"],
        "time_in_mix": "00:00:00",
        "confidence": 95,
        "stream_info": {
            "title": "Classic Electronic Mix",
            "uploader": "DJ Example",
            "duration": 3600,
            "description": "A journey through electronic music history"
        }
    }
]
```

## Supported Platforms

Currently supported streaming platforms:
- YouTube (including YouTube Music)
- Mixcloud

The architecture is designed to be easily extensible to support additional platforms by implementing new StreamDownloader classes.

## Adding New Platforms

To add support for a new streaming platform:

1. Create a new class that inherits from StreamDownloader
2. Implement the `download` and `get_stream_info` methods
3. Add the platform to the StreamFactory class

Example:
```python
class NewPlatformDownloader(StreamDownloader):
    def download(self, url):
        # Implementation
        pass

    def get_stream_info(self, url):
        # Implementation
        pass
```

## Rate Limiting

- ACRCloud has rate limits depending on your subscription plan
- YouTube and Mixcloud may also have their own rate limits
- Default 1-second delay between recognitions (adjustable)

## Known Limitations

1. Recognition accuracy may vary with:
   - Heavy effects or mixing techniques
   - Pitch-shifted tracks
   - Very short track segments
   - Mashups or bootlegs

2. Streaming platform limitations:
   - Some platforms may block automated downloads
   - Region-restricted content
   - Premium-only content
   - Rate limiting

3. Network dependencies:
   - Requires stable internet connection
   - Download speeds affect processing time

## License

MIT License - feel free to use this code in your projects.

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/betmoar/tracklistify/issues) page
2. Create a new issue with details about your problem
3. Include the URL if the issue is platform-specific

---

*Note: This tool is for personal use only. Please respect copyright laws, terms of service of streaming platforms, and licensing agreements when using identified track information.*