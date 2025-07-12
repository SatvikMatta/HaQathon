"""
Utility functions for the Pomodoro timer application.
"""

import time
import logging
import threading
from datetime import timedelta
from functools import wraps
from typing import Any, Callable, Optional, Union
from .constants import Limits, ErrorMessages

# Time Utilities
class TimeUtils:
    """Time formatting and calculation utilities."""
    
    @staticmethod
    def format_seconds(seconds: Union[int, float]) -> str:
        """Format seconds as human-readable time string."""
        total_seconds = int(seconds)
        if total_seconds < 60:
            return f"{total_seconds}s"
        minutes, remaining_seconds = divmod(total_seconds, 60)
        if minutes < 60:
            return f"{minutes}m {remaining_seconds}s"
        hours, remaining_minutes = divmod(minutes, 60)
        return f"{hours}h {remaining_minutes}m {remaining_seconds}s"
    
    @staticmethod
    def format_timer_display(seconds: Union[int, float]) -> str:
        """Format seconds as MM:SS for timer display."""
        total_seconds = int(seconds)
        minutes, remaining_seconds = divmod(total_seconds, 60)
        return f"{minutes:02d}:{remaining_seconds:02d}"
    
    @staticmethod
    def timedelta_to_seconds(td: timedelta) -> float:
        """Convert timedelta to seconds."""
        return td.total_seconds()
    
    @staticmethod
    def seconds_to_timedelta(seconds: Union[int, float]) -> timedelta:
        """Convert seconds to timedelta."""
        return timedelta(seconds=seconds)

# Error Handling Utilities
def safe_execute(error_message: str = "Operation failed", 
                return_value: Any = None, 
                log_errors: bool = True):
    """Decorator for safe function execution with error handling."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logging.error(f"{error_message}: {e}")
                return return_value
        return wrapper
    return decorator

def safe_execute_bool(error_message: str = "Operation failed"):
    """Decorator for functions that should return bool on error."""
    return safe_execute(error_message, False, True)

def safe_execute_none(error_message: str = "Operation failed"):
    """Decorator for functions that should return None on error."""
    return safe_execute(error_message, None, True)

# Validation Utilities
class ValidationUtils:
    """Common validation utilities."""
    
    @staticmethod
    def validate_positive_number(value: Union[int, float], 
                               name: str = "value") -> Union[int, float]:
        """Validate that a number is positive."""
        if value <= 0:
            raise ValueError(f"{name} must be positive, got {value}")
        return value
    
    @staticmethod
    def validate_range(value: Union[int, float], 
                      min_val: Union[int, float], 
                      max_val: Union[int, float],
                      name: str = "value") -> Union[int, float]:
        """Validate that a value is within a specified range."""
        if not (min_val <= value <= max_val):
            raise ValueError(f"{name} must be between {min_val} and {max_val}, got {value}")
        return value
    
    @staticmethod
    def validate_timer_seconds(seconds: Union[int, float]) -> Union[int, float]:
        """Validate timer duration in seconds."""
        return ValidationUtils.validate_range(
            seconds, Limits.MIN_TIMER_SECONDS, Limits.MAX_TIMER_SECONDS, "timer_seconds"
        )
    
    @staticmethod
    def validate_pomodoros(count: int) -> int:
        """Validate pomodoro count."""
        return ValidationUtils.validate_range(
            count, Limits.MIN_POMODOROS, Limits.MAX_POMODOROS, "pomodoros"
        )
    
    @staticmethod
    def validate_non_empty_string(value: str, name: str = "string") -> str:
        """Validate that a string is not empty."""
        if not value or not value.strip():
            raise ValueError(f"{name} cannot be empty")
        return value.strip()
    
    @staticmethod
    def validate_task_list(tasks: list) -> list:
        """Validate task list for timer."""
        if not tasks:
            raise ValueError(ErrorMessages.INVALID_TASKS)
        if len(tasks) > Limits.MAX_POMODOROS:
            raise ValueError(ErrorMessages.TOO_MANY_TASKS)
        return tasks

# Progress Bar Utilities
class ProgressBarUtils:
    """Utilities for progress bar calculations."""
    
    @staticmethod
    def calculate_progress_percent(current: Union[int, float], 
                                 total: Union[int, float]) -> int:
        """Calculate progress percentage."""
        if total <= 0:
            return 0
        return min(100, int(current * 100 / total))
    
    @staticmethod
    def calculate_bar_fill(current: Union[int, float], 
                          total: Union[int, float], 
                          bar_width: int) -> int:
        """Calculate progress bar fill width."""
        if total <= 0:
            return 0
        return min(bar_width, int(current * bar_width / total))
    
    @staticmethod
    def format_progress_description(desc: str, width: int) -> str:
        """Format progress bar description with consistent width."""
        return f"{desc:<{width}}"

# Thread Safety Utilities
class ThreadSafeCounter:
    """A simple thread-safe counter."""
    
    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.RLock()
    
    def increment(self) -> int:
        """Increment and return new value."""
        with self._lock:
            self._value += 1
            return self._value
    
    def get(self) -> int:
        """Get current value."""
        with self._lock:
            return self._value
    
    def reset(self) -> None:
        """Reset to zero."""
        with self._lock:
            self._value = 0

# Performance Utilities
class PerformanceUtils:
    """Simple performance monitoring utilities."""
    
    @staticmethod
    def time_function(func: Callable) -> Callable:
        """Decorator to time function execution."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            logging.debug(f"{func.__name__} took {(end_time - start_time) * 1000:.2f}ms")
            return result
        return wrapper
    
    @staticmethod
    def measure_time_ms(start_time: float) -> float:
        """Measure elapsed time in milliseconds."""
        return (time.time() - start_time) * 1000 