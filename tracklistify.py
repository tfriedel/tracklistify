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
from dotenv import load_dotenv
from abc import ABC, abstractmethod

# Load environment variables
load_dotenv()

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

def get_ffmpeg_path():
    """Get the FFmpeg executable path"""
    try:
        # Try to get FFmpeg path using 'which' command
        import subprocess
        result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    # Check common locations
    common_paths = [
        '/opt/homebrew/bin/ffmpeg',  # macOS Homebrew
        '/usr/local/bin/ffmpeg',     # macOS/Linux
        '/usr/bin/ffmpeg',           # Linux
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return 'ffmpeg'  # Default to system PATH

class YoutubeDownloader(StreamDownloader):
    def __init__(self):
        ffmpeg_path = get_ffmpeg_path()
        self.ydl_opts = {
            'format': 'bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'ffmpeg_location': ffmpeg_path,
            'quiet': True,
            'no_warnings': True,
            'outtmpl': '%(title)s.%(ext)s',
            'prefer_ffmpeg': True,
            'keepvideo': False
        }
        print(f"Using FFmpeg from: {ffmpeg_path}")

    def download(self, url):
        try:
            with tempfile.NamedTemporaryFile(suffix='.%(ext)s', delete=False) as tmp_file:
                temp_path = tmp_file.name

            self.ydl_opts['outtmpl'] = temp_path
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
                # Convert the file extension to .mp3 since we're extracting audio
                mp3_path = os.path.splitext(downloaded_file)[0] + '.mp3'
                if os.path.exists(mp3_path):
                    return mp3_path
                elif os.path.exists(downloaded_file):
                    return downloaded_file
                else:
                    raise Exception("Downloaded file not found")

        except Exception as e:
            print(f"Error downloading: {str(e)}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

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
        self.tracklists_dir = os.path.join(os.getcwd(), 'tracklists')
        os.makedirs(self.tracklists_dir, exist_ok=True)

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

        # Sort results by timestamp
        sorted_results = sorted(results, key=lambda x: x['time_in_mix'])
        merged = []
        current = sorted_results[0]

        for next_match in sorted_results[1:]:
            # Calculate time difference
            current_time = sum(x * int(t) for x, t in zip([3600, 60, 1], current['time_in_mix'].split(":")))
            next_time = sum(x * int(t) for x, t in zip([3600, 60, 1], next_match['time_in_mix'].split(":")))
            time_diff = next_time - current_time

            # If same song and within threshold, update confidence
            if (current['song_name'] == next_match['song_name'] and 
                current['artist'] == next_match['artist'] and 
                time_diff <= time_threshold):
                # Update confidence with higher value
                if next_match['confidence'] > current['confidence']:
                    current['confidence'] = next_match['confidence']
            else:
                # Add current match to merged list and move to next
                if current['confidence'] >= float(os.getenv('MIN_CONFIDENCE', '70')):
                    merged.append(current)
                current = next_match

        # Add the last match if confidence is high enough
        if current['confidence'] >= float(os.getenv('MIN_CONFIDENCE', '70')):
            merged.append(current)

        return merged

    def _sanitize_filename(self, filename):
        """Sanitize filename for safe file system usage"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        # Limit length and remove trailing spaces/dots
        filename = filename.strip('. ')[:200]
        return filename

    def _get_output_path(self, mix_info):
        """Generate output path for tracklist"""
        # Create filename from mix info
        if isinstance(mix_info, dict):
            filename = f"{mix_info.get('uploader', 'Unknown')}-{mix_info.get('title', 'Untitled')}"
        else:
            filename = os.path.splitext(os.path.basename(mix_info))[0]
        
        # Sanitize filename and add timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_filename = self._sanitize_filename(filename)
        output_filename = f"{safe_filename}_{timestamp}.json"
        
        return os.path.join(self.tracklists_dir, output_filename)

    def export_results(self, results, mix_info):
        """Export results to JSON with enhanced metadata"""
        output_path = self._get_output_path(mix_info)
        
        # Enhance results with additional metadata
        output_data = {
            'mix_info': mix_info if isinstance(mix_info, dict) else {'file': mix_info},
            'analysis_date': time.strftime("%Y-%m-%d %H:%M:%S"),
            'track_count': len(results),
            'tracks': results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        
        return output_path

def load_config():
    """Load configuration from environment variables"""
    config = {
        'access_key': os.getenv('ACRCLOUD_ACCESS_KEY'),
        'access_secret': os.getenv('ACRCLOUD_ACCESS_SECRET'),
        'host': os.getenv('ACRCLOUD_HOST', 'identify-eu-west-1.acrcloud.com'),
        'timeout': int(os.getenv('ACRCLOUD_TIMEOUT', '10'))
    }
    
    validate_config(config)
    return config

def validate_config(config):
    """Validate the configuration"""
    required_keys = ['access_key', 'access_secret']
    for key in required_keys:
        if not config[key]:
            print(f"Error: Please set {key.upper()} in your .env file.")
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
            - Timestamp in mix
            - Confidence score
        """)
    
    parser.add_argument('input', help='Input file path or URL to analyze')
    parser.add_argument('-o', '--output', help='Output JSON file path', default='tracklist.json')
    parser.add_argument('-s', '--segment-length', type=int, default=int(os.getenv('SEGMENT_LENGTH', '30')),
                      help='Length of analysis segments in seconds')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Load configuration from environment
    config = load_config()
    
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
        output_path = identifier.export_results(results, args.input)
        
        if args.verbose:
            print(f"\nProcessing complete. Results saved to: {output_path}")
            print(f"\nIdentified {len(results)} tracks:")
            for track in results:
                print(f"\nTime: {track['time_in_mix']}")
                print(f"Track: {track['song_name']}")
                print(f"Artist: {track['artist']}")
                print(f"Confidence: {track['confidence']}%")
        else:
            print(f"\nIdentified {len(results)} tracks. Results saved to: {output_path}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()