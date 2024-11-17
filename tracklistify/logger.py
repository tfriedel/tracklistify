"""
Centralized logging configuration for Tracklistify.

This module provides a configured logger with:
- Console output with colored formatting
- File output with detailed information
- Different log levels for development and production
- Custom formatters for both console and file handlers
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ANSI color codes for console output
COLORS = {
    'DEBUG': '\033[36m',     # Cyan
    'INFO': '\033[32m',      # Green
    'WARNING': '\033[33m',   # Yellow
    'ERROR': '\033[31m',     # Red
    'CRITICAL': '\033[35m',  # Magenta
    'RESET': '\033[0m'       # Reset
}

class ColoredFormatter(logging.Formatter):
    """Custom formatter adding colors to console output."""
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(fmt, datefmt)
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with color."""
        # Save original levelname
        orig_levelname = record.levelname
        # Add color to levelname
        if record.levelname in COLORS:
            record.levelname = f"{COLORS[record.levelname]}{record.levelname}{COLORS['RESET']}"
        
        # Format the message
        result = super().format(record)
        
        # Restore original levelname
        record.levelname = orig_levelname
        return result

def setup_logger(
    name: str = "tracklistify",
    log_dir: Optional[Path] = None,
    verbose: bool = False
) -> logging.Logger:
    """
    Configure and return a logger instance.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        verbose: If True, set console level to DEBUG
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_format = '%(levelname)s %(message)s'
    console_handler.setFormatter(ColoredFormatter(console_format))
    logger.addHandler(console_handler)
    
    # File handler if log_dir is provided
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"tracklistify_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = '%(asctime)s [%(levelname)s] %(message)s'
        file_handler.setFormatter(logging.Formatter(file_format))
        logger.addHandler(file_handler)
        
        logger.debug(f"Log file created at: {log_file}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return setup_logger(name)

# Create default logger instance
logger = get_logger("tracklistify")

def set_verbose(verbose: bool = True):
    """Set logger verbosity level."""
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            handler.setLevel(logging.DEBUG if verbose else logging.INFO)

def add_file_logging(log_dir: Path):
    """Add file logging to the logger."""
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            return
            
    setup_logger(log_dir=log_dir)
