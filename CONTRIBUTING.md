# Contributing to Tracklistify

Thank you for your interest in contributing to Tracklistify! This document provides guidelines and setup instructions for development.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- FFmpeg (for audio processing)
- Git

#### Installing Prerequisites

##### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Install FFmpeg
brew install ffmpeg
```

##### Linux (Ubuntu/Debian)
```bash
# Install Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv

# Install FFmpeg
sudo apt install ffmpeg
```

##### Windows
1. Install Python 3.11 from [python.org](https://www.python.org/downloads/)
2. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
3. Add FFmpeg to your system PATH

### Setting Up the Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tracklistify.git
cd tracklistify
```

2. Create and activate a virtual environment:
```bash
# macOS/Linux
python3.11 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## Development Process

1. Fork the repo
2. Create a new branch from `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. Make your changes
4. Run the test suite:
   ```bash
   pytest tests/
   ```
5. Commit your changes:
   ```bash
   git commit -m "feat: add some feature"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/my-new-feature
   ```
7. Open a Pull Request

## Development Tools

### Code Style and Linting

We use several tools to maintain code quality:

- Black for code formatting
- isort for import sorting
- flake8 for style guide enforcement
- mypy for type checking

Run all linting checks:
```bash
# Format code
black .
isort .

# Run linters
flake8 .
mypy .
```

### Running Tests

We use pytest for testing. Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=tracklistify tests/
```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality. Install them:
```bash
pre-commit install
```

## Coding Standards

### Python Style Guide

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Use [Black](https://github.com/psf/black) for code formatting
* Use [isort](https://pycqa.github.io/isort/) for import sorting
* Use [flake8](https://flake8.pycqa.org/) for style guide enforcement

### Type Hints

* Use type hints for all function arguments and return values
* Use `Optional` for parameters that can be None
* Use `Union` for parameters that can be multiple types
* Use `Any` sparingly and only when absolutely necessary

Example:
```python
from typing import Dict, List, Optional

def process_tracks(
    tracks: List[Dict[str, str]],
    provider: Optional[str] = None
) -> List[Dict[str, str]]:
    """Process a list of tracks."""
    pass
```

### Documentation Style

* Use Google-style docstrings
* Include type information in docstrings
* Document exceptions that may be raised
* Include examples in docstrings when helpful

Example:
```python
def identify_track(audio_data: bytes, start_time: float = 0) -> Dict[str, Any]:
    """Identify a track from audio data.
    
    Args:
        audio_data: Raw audio data bytes
        start_time: Start time in seconds for identification
        
    Returns:
        Dict containing track information
        
    Raises:
        ProviderError: If track identification fails
        ValueError: If audio_data is invalid
        
    Example:
        >>> data = load_audio("song.mp3")
        >>> result = identify_track(data)
        >>> print(result["title"])
        "Example Song"
    """
    pass
```

### Testing

* Write unit tests for all new code
* Use pytest fixtures for test setup
* Mock external services
* Include both success and error cases
* Aim for 100% test coverage

Example:
```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_provider():
    return Mock()

def test_track_identification(mock_provider):
    with patch("tracklistify.providers.get_provider") as get_provider:
        get_provider.return_value = mock_provider
        mock_provider.identify_track.return_value = {"title": "Test"}
        
        result = identify_track(b"audio_data")
        assert result["title"] == "Test"
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

* feat: A new feature
* fix: A bug fix
* docs: Documentation only changes
* style: Changes that do not affect the meaning of the code
* refactor: A code change that neither fixes a bug nor adds a feature
* perf: A code change that improves performance
* test: Adding missing tests or correcting existing tests
* chore: Changes to the build process or auxiliary tools

Example:
```
feat(provider): add support for new music provider

- Implement provider interface
- Add configuration options
- Update documentation
- Add tests

Closes #123
```

## Development Workflow

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit them:
```bash
git add .
git commit -m "feat: add your feature"
```

Follow our commit message conventions:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- test: Test changes
- chore: Build process or auxiliary tool changes

3. Push your changes:
```bash
git push origin feature/your-feature-name
```

4. Create a Pull Request on GitHub

## Review Process

1. All code changes require review
2. Reviewers will look for:
   * Correct functionality
   * Test coverage
   * Code style
   * Documentation
   * Performance implications
3. Changes may need to be updated based on review feedback
4. Once approved, changes will be merged by maintainers

## API Keys and Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Add your API keys to `.env`:
```bash
SHAZAM_API_KEY=your_key_here
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

## Project Structure

```
tracklistify/
├── tracklistify/          # Main package
│   ├── __init__.py
│   ├── providers/        # Track identification providers
│   ├── processors/       # Audio processing modules
│   └── utils/           # Utility functions
├── tests/               # Test suite
├── docs/               # Documentation
└── examples/          # Example scripts
```

## Documentation

We use Google-style docstrings. Example:

```python
def process_audio(file_path: str, duration: int = 10) -> AudioSegment:
    """Process an audio file and return a processed segment.

    Args:
        file_path: Path to the audio file.
        duration: Duration in seconds to process.

    Returns:
        AudioSegment: Processed audio segment.

    Raises:
        FileNotFoundError: If the audio file doesn't exist.
    """
```

## Need Help?

- Check our [issues page](https://github.com/yourusername/tracklistify/issues)
- Join our [Discord community](https://discord.gg/tracklistify)
- Read our [documentation](https://tracklistify.readthedocs.io)

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

## Release Process

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create and push tag
6. Create GitHub release
7. Upload to PyPI

## Getting Help

* Join our Discord server
* Check the documentation
* Open a GitHub issue
* Contact the maintainers

## Recognition

Contributors will be:
* Listed in CONTRIBUTORS.md
* Mentioned in release notes
* Credited in documentation

Thank you for contributing to Tracklistify! 🎉
