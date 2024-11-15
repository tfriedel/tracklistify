import os
import time
from pydub import AudioSegment
from acrcloud.recognizer import ACRCloudRecognizer
from datetime import timedelta
import json
import yt_dlp
import requests
import tempfile
import urllib.parse
import argparse
import sys
import configparser
from abc import ABC, abstractmethod

class StreamDownloader(ABC):
    """Abstract base class for stream downloaders"""
    @abstractmethod
    def download(self, url):
        """Download stream and return path to temporary file"""
        pass

    @abstractmethod
    def get_stream_info(self, url):
        """Get stream metadata"""
        pass

class YoutubeDownloader(StreamDownloader):
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True
        }

    def download(self, url):
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            temp_path = tmp_file.name
            
        self.ydl_opts['outtmpl'] = temp_path
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([url])
            
        return temp_path

    def get_stream_info(self, url):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title'),
                'uploader': info.get('uploader'),
                'duration': info.get('duration'),
                'description': info.get('description')
            }

class MixcloudDownloader(StreamDownloader):
    def __init__(self):
        self.api_base = "https://api.mixcloud.com"

    def download(self, url):
        # Convert URL to API URL
        cloudcast = urllib.parse.urlparse(url).path
        api_url = f"{self.api_base}{cloudcast}stream"
        
        # Download stream
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            response = requests.get(api_url, stream=True)
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            return tmp_file.name

    def get_stream_info(self, url):
        cloudcast = urllib.parse.urlparse(url).path
        api_url = f"{self.api_base}{cloudcast}"
        response = requests.get(api_url)
        data = response.json()
        return {
            'title': data.get('name'),
            'uploader': data.get('user', {}).get('name'),
            'duration': data.get('audio_length'),
            'description': data.get('description')
        }

class StreamFactory:
    """Factory for creating appropriate stream downloader"""
    @staticmethod
    def get_downloader(url):
        if 'youtube.com' in url or 'youtu.be' in url:
            return YoutubeDownloader()
        elif 'mixcloud.com' in url:
            return MixcloudDownloader()
        else:
            raise ValueError("Unsupported streaming platform")

class MixTrackIdentifier:
    def __init__(self, config):
        """Initialize with ACRCloud credentials"""
        self.config = {
            'access_key': config['access_key'],
            'access_secret': config['access_secret'],
            'host': config.get('host', 'identify-eu-west-1.acrcloud.com'),
            'timeout': int(config.get('timeout', 10))
        }
        self.recognizer = ACRCloudRecognizer(self.config)
  
    def split_mix(self, mix_path, segment_length=30):
        """Split the mix into segments for analysis"""
        mix_audio = AudioSegment.from_mp3(mix_path)
        segments = []
        
        if not os.path.exists("temp_segments"):
            os.makedirs("temp_segments")
            
        for i in range(0, len(mix_audio), segment_length * 1000):
            segment = mix_audio[i:i + (segment_length + 5) * 1000]
            segment_path = f"temp_segments/segment_{i}.mp3"
            segment.export(segment_path, format="mp3")
            segments.append({
                "path": segment_path,
                "start_time": i
            })
            
        return segments

    def identify_stream(self, url, segment_length=30):
        """
        Identify tracks in an online stream
        """
        print(f"Processing stream: {url}")
        
        try:
            # Get appropriate downloader
            downloader = StreamFactory.get_downloader(url)
            
            # Get stream info
            stream_info = downloader.get_stream_info(url)
            print(f"Analyzing: {stream_info['title']} by {stream_info['uploader']}")
            
            # Download stream to temporary file
            temp_file = downloader.download(url)
            
            # Process the downloaded file
            results = self.identify_tracks(temp_file, segment_length)
            
            # Add stream information to results
            for result in results:
                result['stream_info'] = stream_info
            
            # Clean up
            os.remove(temp_file)
            
            return results
            
        except Exception as e:
            print(f"Error processing stream: {str(e)}")
            return []

    def identify_tracks(self, mix_path, segment_length=30):
        """Identify tracks in a mix file"""
        print(f"Analyzing mix: {mix_path}")
        
        segments = self.split_mix(mix_path, segment_length)
        results = []
        
        for segment in segments:
            response = self.recognizer.recognize_by_file(segment["path"], 0)
            
            try:
                data = json.loads(response)
                
                if 'status' in data and data['status']['code'] == 0:
                    music = data['metadata']['music'][0]
                    result = {
                        "song_name": music['title'],
                        "artist": music['artists'][0]['name'],
                        "album": music.get('album', {}).get('name', ''),
                        "label": music.get('label', ''),
                        "genres": [g['name'] for g in music.get('genres', [])],
                        "time_in_mix": str(timedelta(milliseconds=segment["start_time"])),
                        "confidence": music.get('score', 100)
                    }
                    results.append(result)
                    print(f"Identified: {result['song_name']} by {result['artist']}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error processing segment: {str(e)}")
                continue
        
        # Clean up temporary files
        for segment in segments:
            os.remove(segment["path"])
        os.rmdir("temp_segments")
        
        return self._merge_nearby_matches(results)
    
    def _merge_nearby_matches(self, results, time_threshold=60):
        """Merge nearby matches of the same song"""
        if not results:
            return []
            
        merged = []
        current_match = results[0]
        
        for next_match in results[1:]:
            current_time = sum(x * int(t) for x, t in zip([3600, 60, 1], current_match["time_in_mix"].split(":")))
            next_time = sum(x * int(t) for x, t in zip([3600, 60, 1], next_match["time_in_mix"].split(":")))
            
            if (next_time - current_time <= time_threshold and 
                next_match["song_name"] == current_match["song_name"]):
                if next_match["confidence"] > current_match["confidence"]:
                    current_match["confidence"] = next_match["confidence"]
            else:
                merged.append(current_match)
                current_match = next_match
                
        merged.append(current_match)
        return merged
    
    def export_results(self, results, output_path):
        """Export results to JSON"""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)

def create_config_file(config_path):
    """Create a default configuration file"""
    config = configparser.ConfigParser()
    config['ACRCloud'] = {
        'access_key': 'your_access_key_here',
        'access_secret': 'your_access_secret_here',
        'host': 'identify-eu-west-1.acrcloud.com',
        'timeout': '10'
    }
    
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    
    print(f"Created default configuration file at: {config_path}")
    print("Please edit the file and add your ACRCloud credentials.")
    sys.exit(1)

def load_config(config_path):
    """Load configuration from file"""
    if not os.path.exists(config_path):
        create_config_file(config_path)
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    if 'ACRCloud' not in config:
        print("Error: Invalid configuration file format.")
        sys.exit(1)
    
    return dict(config['ACRCloud'])

def validate_config(config):
    """Validate the configuration"""
    required_keys = ['access_key', 'access_secret']
    for key in required_keys:
        if key not in config or config[key] == f'your_{key}_here':
            print(f"Error: Please set your {key} in the configuration file.")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="""
            DJ Mix Track Identifier - Analyze and identify tracks in DJ mixes and live streams.
                    
            This tool can process:
            - Local audio files (MP3)
            - YouTube videos/streams
            - Mixcloud mixes
                    
            It provides detailed track information including:
            - Track name and artist
            - Timestamp in the mix
            - Album and label information
            - Genre tags
            - Confidence scores
            """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'input',
        help='Input file path or URL to analyze'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output JSON file path (default: tracklist.json)',
        default='tracklist.json'
    )
    
    parser.add_argument(
        '-c', '--config',
        help='Path to configuration file (default: ~/.mix-identifier/config.ini)',
        default=os.path.expanduser('~/.mix-identifier/config.ini')
    )
    
    parser.add_argument(
        '-s', '--segment-length',
        help='Length of analysis segments in seconds (default: 30)',
        type=int,
        default=30
    )
    
    parser.add_argument(
        '-v', '--verbose',
        help='Enable verbose output',
        action='store_true'
    )
    
    parser.add_argument(
        '--init-config',
        help='Create a new configuration file',
        action='store_true'
    )
    
    formats = parser.add_argument_group('Supported Formats')
    formats.add_argument(
        '--list-formats',
        help='List supported file formats and platforms',
        action='store_true'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle special commands
    if args.list_formats:
        print("""
            Supported Formats and Platforms:

            Local Files:
            - MP3 audio files

            Streaming Platforms:
            - YouTube (youtube.com, youtu.be)
            - Mixcloud (mixcloud.com)

            File format requirements:
            - Local files must be in MP3 format
            - Streams will be automatically converted
        """)
        sys.exit(0)
    
    # Create config directory if it doesn't exist
    os.makedirs(os.path.dirname(args.config), exist_ok=True)
    
    # Handle config initialization
    if args.init_config:
        create_config_file(args.config)
        sys.exit(0)
    
    # Load and validate configuration
    config = load_config(args.config)
    validate_config(config)
    
    # Initialize identifier
    identifier = MixTrackIdentifier(config)
    
    try:
        # Process input
        if args.verbose:
            print(f"Processing input: {args.input}")
        
        # Determine if input is URL or local file
        if args.input.startswith(('http://', 'https://')):
            results = identifier.identify_stream(args.input, args.segment_length)
        else:
            if not os.path.exists(args.input):
                print(f"Error: File not found: {args.input}")
                sys.exit(1)
            results = identifier.identify_tracks(args.input, args.segment_length)
        
        # Export results
        identifier.export_results(results, args.output)
        
        if args.verbose:
            print(f"\nProcessing complete. Results saved to: {args.output}")
            print(f"\nIdentified {len(results)} tracks:")
            for track in results:
                print(f"\nTime: {track['time_in_mix']}")
                print(f"Track: {track['song_name']}")
                print(f"Artist: {track['artist']}")
                print(f"Confidence: {track['confidence']}%")
        else:
            print(f"\nIdentified {len(results)} tracks. Results saved to: {args.output}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()