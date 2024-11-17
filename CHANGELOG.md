# Changelog

All notable changes to Tracklistify will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Support for additional platforms (Mixcloud, SoundCloud)
- Provider fallback mechanism
- Advanced error recovery strategies
- Batch processing for multiple files
- Progress bar for long operations
- CLI improvements:
  - Interactive mode
  - Configuration wizard
  - Batch processing options
- Web interface for easier usage
- Docker support
- Additional output formats:
  - CSV export
  - XML export
  - Rekordbox compatible format

## [0.5.5] - 2024-01-20

### Added
- Comprehensive test suites for all providers
  * ACRCloud provider tests
  * Shazam provider tests
  * Spotify provider tests
- New testing documentation with detailed guides
- AI development guidelines and best practices
- Enhanced documentation structure and navigation

### Changed
- Reorganized project documentation
- Updated README with better organization
- Improved cross-referencing between docs
- Enhanced test coverage requirements
  * Core functionality: 90%+
  * Provider implementations: 95%+
  * Integration tests: 80%+

### Removed
- Duplicate CONTRIBUTING.md from docs directory

### Documentation
- Created comprehensive testing guide in tests/TESTING.md
- Added detailed AI development guidelines
- Improved documentation index in docs/README.md
- Enhanced provider testing documentation
- Updated example test patterns and best practices

## [0.5.4] - 2024-03-23
### Added
- Comprehensive test suites for providers:
  - ACRCloud provider tests
  - Shazam provider tests
  - Spotify provider tests
- Test coverage for edge cases and error handling
- Mock responses and fixtures for testing
- Rate limiting and authentication tests
- Network error handling tests

### Changed
- Improved provider test organization
- Enhanced error handling in providers
- Updated test documentation
- Standardized test patterns across providers

### Fixed
- Duplicate CONTRIBUTING.md files
- Documentation cross-references
- Test coverage gaps in providers

## [0.5.3] - 2024-03-22
### Added
- Comprehensive project documentation:
  - API.md: Detailed API reference and usage examples
  - ARCHITECTURE.md: System design and component interactions
  - GETTING_STARTED.md: Installation and basic usage guide
  - CONTRIBUTING.md: Development workflow and guidelines
  - Enhanced README.md with badges and project overview
- Documentation features:
  - Code examples for common use cases
  - Architecture diagrams
  - Type hints and docstrings
  - Testing guidelines
  - Security considerations
  - Performance optimization guides
  - Deployment instructions
  - Error handling strategies

### Changed
- Reorganized documentation structure
- Enhanced code examples with async/await patterns
- Updated project status and coverage metrics
- Improved installation instructions
- Expanded troubleshooting guides
- Added detailed configuration examples, 
- Enhanced provider documentation

### Fixed
- Documentation inconsistencies
- Broken internal links
- Code example formatting
- Missing type hints in examples
- Outdated configuration examples

## [0.5.2] - 2024-03-22
### Changed
- Migrated ACRCloud to provider interface
- Enhanced provider factory with better configuration
- Improved error handling for providers
- Standardized provider timeouts

## [0.5.1] - 2024-03-22
### Added
- Comprehensive contributing guidelines (CONTRIBUTING.md)
- Detailed development environment setup instructions
- Code style and linting configuration
- Pre-commit hooks setup

### Changed
- Enhanced environment configuration template
- Expanded documentation for API keys and settings
- Improved project structure documentation

## [0.5.0] - 2024-03-22
### Added
- Enhanced Shazam integration:
  - Advanced audio fingerprinting with MFCCs
  - Spectral centroid analysis
  - Pre-emphasis filtering
  - Improved confidence scoring
  - Detailed audio features extraction
  - Extended metadata enrichment
- Audio landmark fingerprinting for track identification
- Advanced audio processing with librosa
- Shazam integration using shazamio package

## [0.4.0] - 2024-03-21
### Added
- Multiple provider support through provider interface
- Spotify integration for metadata enrichment
- Provider factory for managing multiple providers
- Comprehensive test suite for providers
- File-based caching system for API responses
- Token bucket rate limiter for API calls
- Memory-efficient chunk-based audio processing
- Retry mechanism with exponential backoff for API calls
- Timeout handling for long-running operations
- Enhanced logging system with colored console output
- Configurable log file output with timestamps
- Debug-level logging for development
- Custom log formatters for both console and file output
- Enhanced track identification verbosity
- Comprehensive analysis summary in output files
- Additional metadata in M3U playlists
- Modular package structure with dedicated modules
- Type hints throughout the codebase
- Factory pattern for platform-specific downloaders
- Enhanced track identification algorithm
- Cache configuration options:
  - CACHE_ENABLED for toggling caching
  - CACHE_DIR for cache location
  - CACHE_DURATION for cache expiration
- Rate limiting configuration:
  - RATE_LIMIT_ENABLED for toggling rate limiting
  - MAX_REQUESTS_PER_MINUTE for API throttling

### Changed
- Modular provider architecture
- Enhanced metadata enrichment
- Optimized memory usage during audio processing
- Improved Track class with strict validation
- Enhanced TrackMatcher with better error handling
- Refined confidence threshold handling
- More robust MP3 format validation
- Updated environment variable structure
- Enhanced error handling and logging
- Improved configuration management

### Fixed
- Track timestamp ordering
- Confidence threshold validation
- Track metadata validation
- Audio file format validation
- Memory leaks in audio processing
- API rate limiting issues

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
