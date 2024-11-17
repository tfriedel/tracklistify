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
