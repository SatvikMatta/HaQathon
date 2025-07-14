"""
Constants and configuration values for the Pomodoro timer application.
"""

# Default Timer Settings
DEFAULT_WORK_SECONDS = 25 * 60  # 25 minutes
DEFAULT_SHORT_BREAK_SECONDS = 5 * 60  # 5 minutes
DEFAULT_LONG_BREAK_SECONDS = 15 * 60  # 15 minutes
DEFAULT_POMOS_BEFORE_LONG_BREAK = 4

# Demo/Test Timer Settings
DEMO_WORK_SECONDS = 5
DEMO_SHORT_BREAK_SECONDS = 3
DEMO_LONG_BREAK_SECONDS = 8

# System Limits
MAX_TASKS_EDGE_DEVICE = 20
MAX_TASK_TITLE_LENGTH = 100
MAX_TASK_DESCRIPTION_LENGTH = 500
MAX_ESTIMATED_POMODOROS = 50

# Threading and Performance
SKIP_DISPLAY_DURATION_SECONDS = 0.5

# Basic limits
class Limits:
    MIN_TIMER_SECONDS = 1
    MAX_TIMER_SECONDS = 3600  # 1 hour
    MIN_POMODOROS = 1
    MAX_POMODOROS = 50
    MIN_WORKERS = 1
    MAX_WORKERS = 10
    MIN_QUEUE_SIZE = 1
    MAX_QUEUE_SIZE = 100

# Error messages
class ErrorMessages:
    INVALID_TASKS = "At least one task is required"
    TOO_MANY_TASKS = f"Maximum {MAX_TASKS_EDGE_DEVICE} tasks supported on edge devices"
    INVALID_POMODOROS = "estimated_pomodoros must be positive"
    INVALID_TIME_INTERVALS = "All time intervals must be positive"
    INVALID_LONG_BREAK_COUNT = "pomos_before_long_break must be positive"
    TIMER_START_ERROR = "Timer start error"
    TIMER_PAUSE_ERROR = "Timer pause error"
    TIMER_SKIP_ERROR = "Timer skip error"
 