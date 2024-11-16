"""
Retry mechanism for handling transient failures.

This module provides decorators and utilities for implementing retry logic
with exponential backoff and configurable retry conditions.
"""

import time
import random
from functools import wraps
from typing import Callable, Type, Union, List, Optional
import logging

from .exceptions import RetryExceededError, TimeoutError
from .logger import logger

def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception,
    timeout: Optional[float] = None,
    on_retry: Optional[Callable] = None
):
    """
    Decorator that implements retry logic with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exceptions: Exception or list of exceptions to catch and retry
        timeout: Maximum total time to spend retrying in seconds
        on_retry: Optional callback function to call before each retry
        
    Returns:
        Decorator function
        
    Raises:
        RetryExceededError: When maximum retry attempts are exceeded
        TimeoutError: When the timeout is exceeded
    """
    if isinstance(exceptions, type):
        exceptions = [exceptions]
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            attempt = 1
            last_error = None
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                    
                except tuple(exceptions) as e:
                    last_error = e
                    
                    if attempt == max_attempts:
                        raise RetryExceededError(
                            f"Maximum retry attempts ({max_attempts}) exceeded",
                            attempts=attempt,
                            last_error=last_error
                        ) from e
                    
                    # Check timeout
                    if timeout and (time.time() - start_time) > timeout:
                        raise TimeoutError(
                            f"Operation timed out after {timeout} seconds",
                            timeout=timeout,
                            operation=func.__name__
                        ) from e
                    
                    # Calculate delay with exponential backoff and jitter
                    delay = min(base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1), max_delay)
                    
                    # Log retry attempt
                    logger.warning(
                        f"Retry attempt {attempt}/{max_attempts} for {func.__name__} "
                        f"after {delay:.2f}s. Error: {str(e)}"
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt, delay, e)
                        except Exception as callback_error:
                            logger.error(f"Error in retry callback: {str(callback_error)}")
                    
                    # Wait before retrying
                    time.sleep(delay)
                    attempt += 1
            
            # This should never be reached due to the RetryExceededError above
            return None
            
        return wrapper
    return decorator

def with_timeout(timeout: float):
    """
    Decorator that adds timeout to a function.
    
    Args:
        timeout: Maximum time in seconds to wait for function completion
        
    Returns:
        Decorator function
        
    Raises:
        TimeoutError: When the function execution exceeds the timeout
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            
            if (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"Operation timed out after {timeout} seconds",
                    timeout=timeout,
                    operation=func.__name__
                )
            
            return result
        return wrapper
    return decorator
