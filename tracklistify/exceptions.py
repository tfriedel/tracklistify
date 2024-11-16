"""
Custom exceptions for Tracklistify.

This module defines specific exception types for different error scenarios
in the Tracklistify application, making error handling more precise and
informative.
"""

class TracklistifyError(Exception):
    """Base exception class for Tracklistify."""
    pass

class APIError(TracklistifyError):
    """Raised when an API request fails."""
    def __init__(self, message: str, status_code: int = None, response: str = None):
        self.status_code = status_code
        self.response = response
        super().__init__(message)

class DownloadError(TracklistifyError):
    """Raised when a download operation fails."""
    def __init__(self, message: str, url: str = None, cause: Exception = None):
        self.url = url
        self.cause = cause
        super().__init__(message)

class ConfigError(TracklistifyError):
    """Raised when there's a configuration error."""
    pass

class AudioProcessingError(TracklistifyError):
    """Raised when audio processing fails."""
    def __init__(self, message: str, file_path: str = None, cause: Exception = None):
        self.file_path = file_path
        self.cause = cause
        super().__init__(message)

class TrackIdentificationError(TracklistifyError):
    """Raised when track identification fails."""
    def __init__(self, message: str, segment: int = None, cause: Exception = None):
        self.segment = segment
        self.cause = cause
        super().__init__(message)

class ValidationError(TracklistifyError):
    """Raised when input validation fails."""
    pass

class RetryExceededError(TracklistifyError):
    """Raised when maximum retry attempts are exceeded."""
    def __init__(self, message: str, attempts: int = None, last_error: Exception = None):
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(message)

class TimeoutError(TracklistifyError):
    """Raised when an operation times out."""
    def __init__(self, message: str, timeout: float = None, operation: str = None):
        self.timeout = timeout
        self.operation = operation
        super().__init__(message)
