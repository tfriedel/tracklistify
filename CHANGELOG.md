# Changelog

All notable changes to Tracklistify will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Comprehensive test suite for track identification
- Input validation for track metadata
- Error handling for invalid audio files
- Edge case handling for confidence thresholds
- Chronological track ordering
- Testing documentation in README.md
- AI guidelines documentation
- Changelog tracking
- Code quality improvements

### Changed
- Improved Track class with strict validation
- Enhanced TrackMatcher with better error handling
- Refined confidence threshold handling
- More robust MP3 format validation

### Fixed
- Track timestamp ordering
- Confidence threshold validation
- Track metadata validation
- Audio file format validation

## [0.3.6] - 2024-03-19

### Fixed
- Fixed track timing calculation using MP3 metadata for accurate timestamps
- Adjusted default segment length to 60 seconds for better track identification
- Removed redundant acrcloud-py dependency in favor of pyacrcloud

### Added
- Added mutagen dependency for MP3 metadata handling
- Added total mix length display in track identification output

### Changed
- Improved segment timing calculation to use actual audio duration
- Enhanced logging with proper time formatting (HH:MM:SS)
- Updated requirements.txt for better dependency management

## [0.3.5] - 2024-01-15

### Fixed
- YouTube download functionality
- Import error handling for yt-dlp
- Downloader factory creation
- Mix information extraction order

### Changed
- Better error messages for missing dependencies
- Improved YouTube URL handling
- More robust downloader initialization
- Cleaner error handling flow

## [0.3.4] - 2024-01-15

### Added
- URL validation and cleaning functionality
- Support for various YouTube URL formats
- Automatic backslash stripping from URLs
- URL unescaping for encoded characters

### Changed
- Improved URL handling in main program
- Enhanced error messages for invalid URLs
- Better logging of URL processing steps
- Cleaner YouTube URL reconstruction

### Fixed
- Issue with backslashes in URLs
- Problems with URL-encoded characters
- Inconsistent YouTube URL formats
- Invalid URL handling

## [0.3.3] - 2024-01-15

### Added
- Comprehensive error handling system with specific exception types
- Retry mechanism with exponential backoff for API calls
- Timeout handling for long-running operations
- Custom exceptions for different error scenarios
- Detailed error logging and reporting

### Changed
- Enhanced API calls with retry logic
- Improved download operations with timeout handling
- Updated error messages with more context
- Added detailed error documentation

## [0.3.2] - 2024-01-15

### Added
- Enhanced logging system with colored console output
- Configurable log file output with timestamps
- Debug-level logging for development
- Custom log formatters for both console and file output

### Changed
- Updated logger module with comprehensive configuration options
- Improved log message formatting
- Added color-coding for different log levels
- Enhanced logging verbosity control

## [0.3.1] - 2024-01-15

### Added
- Enhanced track identification verbosity with detailed progress and status logging
- Comprehensive analysis summary in output files including confidence statistics
- Additional metadata in M3U playlists (artist and date information)

### Changed
- Modified track confidence handling to keep all tracks with confidence > 0
- Updated tracklist filename format to `[YYYYMMDD] Artist - Description.extension`
- Improved track merging process with more detailed debug logging
- Enhanced markdown output with analysis statistics section

### Fixed
- Filename sanitization to preserve spaces and valid punctuation
- Date format handling in filenames for consistency

## [0.3.0] - 2024-02-21

### Added
- Modular package structure with dedicated modules:
  - config.py for configuration management
  - logger.py for centralized logging
  - track.py for track identification
  - downloader.py for audio downloads
- Type hints throughout the codebase
- Proper package installation with setup.py
- Development environment setup
- Comprehensive logging system with file output
- Factory pattern for platform-specific downloaders

### Changed
- Restructured project into proper Python package
- Improved configuration using dataclasses
- Enhanced error handling and logging
- Updated documentation with new structure
- Improved code organization and maintainability

### Fixed
- FFmpeg path detection on different platforms
- Package dependencies and versions
- Installation process

## [0.2.0] - 2024-02-21

### Added
- Enhanced track identification algorithm with confidence-based filtering
- New track merging logic to handle duplicate detections
- Dedicated tracklists directory for organized output
- Additional configuration options in .env for fine-tuning:
  - MIN_CONFIDENCE for match threshold
  - TIME_THRESHOLD for track merging
  - MIN_TRACK_LENGTH for filtering
  - MAX_DUPLICATES for duplicate control
- Improved JSON output format with detailed track information
- Better timestamp handling in track identification

### Changed
- Updated .env.example with new configuration options
- Improved README documentation with output format examples
- Enhanced error handling in track identification process
- Optimized FFmpeg integration

### Fixed
- Duplicate track detection issues
- Timestamp accuracy in track listing
- File naming sanitization

## [0.1.0] - 2024-02-20
### Added
- Core track identification functionality
- Support for YouTube and Mixcloud platforms
- ACRCloud integration for audio recognition
- JSON export of track listings
- Command-line interface
- Configuration file support
- Detailed track information retrieval
- Timestamp tracking
- Confidence scoring
- Duplicate detection and merging
- Error handling and logging
- Documentation and usage examples

### Technical Features
- Abstract base class for stream downloaders
- Factory pattern for platform-specific downloaders
- Modular architecture for easy platform additions
- Temporary file management
- FFmpeg integration
- Configuration validation
- Progress tracking
- Error reporting

## Future Plans
### Planned Features
- Support for additional streaming platforms
- Enhanced duplicate detection algorithms
- Local audio fingerprinting
- Batch processing capabilities
- Web interface
- Playlist export to various formats
- BPM detection and matching
- DJ transition detection
- Genre classification
- Improved confidence scoring
- API rate limiting optimization
- Caching system for recognized tracks

### Technical Improvements
- Unit test coverage
- Performance optimizations
- Memory usage improvements
- Error handling enhancements
- Documentation updates
- Code refactoring
- Configuration system improvements
- Logging system enhancements
