"""
Tests for retry mechanism.
"""

import time
import pytest
from unittest.mock import Mock, patch
import asyncio
from tracklistify.retry import retry, with_timeout
from tracklistify.exceptions import RetryExceededError, TimeoutError

def test_retry_success():
    """Test successful retry after failures."""
    mock_func = Mock()
    mock_func.side_effect = [ValueError("Fail"), ValueError("Fail"), "success"]
    
    @retry(max_attempts=3, base_delay=0.1)
    def test_func():
        return mock_func()
    
    result = test_func()
    assert result == "success"
    assert mock_func.call_count == 3

def test_retry_all_failures():
    """Test retry exhaustion with all failures."""
    mock_func = Mock(side_effect=ValueError("Persistent failure"))
    
    @retry(max_attempts=3, base_delay=0.1)
    def test_func():
        return mock_func()
    
    with pytest.raises(RetryExceededError) as exc_info:
        test_func()
    
    assert mock_func.call_count == 3
    assert "Maximum retry attempts (3) exceeded" in str(exc_info.value)

def test_retry_timeout():
    """Test retry timeout."""
    mock_func = Mock(side_effect=ValueError("Slow operation"))
    
    @retry(max_attempts=5, base_delay=0.1, timeout=0.3)
    def test_func():
        time.sleep(0.2)  # Simulate slow operation
        return mock_func()
    
    with pytest.raises(TimeoutError) as exc_info:
        test_func()
    
    assert "Operation timed out" in str(exc_info.value)

def test_retry_callback():
    """Test retry callback function."""
    mock_func = Mock()
    mock_func.side_effect = [ValueError("Fail"), ValueError("Fail"), "success"]
    mock_callback = Mock()
    
    @retry(max_attempts=3, base_delay=0.1, on_retry=mock_callback)
    def test_func():
        return mock_func()
    
    result = test_func()
    assert result == "success"
    assert mock_callback.call_count == 2  # Called twice for two retries

def test_retry_multiple_exceptions():
    """Test retry with multiple exception types."""
    mock_func = Mock()
    mock_func.side_effect = [ValueError("Value error"), TypeError("Type error"), "success"]
    
    @retry(max_attempts=3, base_delay=0.1, exceptions=[ValueError, TypeError])
    def test_func():
        return mock_func()
    
    result = test_func()
    assert result == "success"
    assert mock_func.call_count == 3

def test_retry_unexpected_exception():
    """Test retry with unexpected exception type."""
    mock_func = Mock(side_effect=KeyError("Unexpected error"))
    
    @retry(max_attempts=3, base_delay=0.1, exceptions=ValueError)
    def test_func():
        return mock_func()
    
    with pytest.raises(KeyError):
        test_func()
    
    assert mock_func.call_count == 1  # Should not retry for unexpected exception

@pytest.mark.asyncio
async def test_with_timeout_success():
    """Test successful operation within timeout."""
    @with_timeout(1.0)
    async def fast_operation():
        return "success"
    
    result = await fast_operation()
    assert result == "success"

@pytest.mark.asyncio
async def test_with_timeout_exceeded():
    """Test timeout exceeded."""
    @with_timeout(0.1)
    async def slow_operation():
        await asyncio.sleep(0.2)
        return "success"
    
    with pytest.raises(TimeoutError):  
        await slow_operation()
