"""
Constants and configuration values for the Pomodoro timer application.
"""

# Default Timer Settings
DEFAULT_WORK_SECONDS = 25 * 60  # 25 minutes
DEFAULT_SHORT_BREAK_SECONDS = 5 * 60  # 5 minutes
DEFAULT_LONG_BREAK_SECONDS = 15 * 60  # 15 minutes
DEFAULT_SNAPSHOT_INTERVAL = 60  # 1 minute
DEFAULT_POMOS_BEFORE_LONG_BREAK = 4

# Demo/Test Timer Settings
DEMO_WORK_SECONDS = 5
DEMO_SHORT_BREAK_SECONDS = 3
DEMO_LONG_BREAK_SECONDS = 8
DEMO_SNAPSHOT_INTERVAL = 5

# System Limits
MAX_TASKS_EDGE_DEVICE = 20
MAX_TASK_TITLE_LENGTH = 100
MAX_TASK_DESCRIPTION_LENGTH = 500
MAX_ESTIMATED_POMODOROS = 50

# Threading and Performance
MAX_FOCUS_DETECTOR_WORKERS = 2
MAX_FOCUS_DETECTOR_QUEUE_SIZE = 10
FOCUS_DETECTOR_TIMEOUT_SECONDS = 5.0
SKIP_DISPLAY_DURATION_SECONDS = 0.5

# Display Settings
PROGRESS_BAR_WIDTH = 40
PROGRESS_BAR_COLUMNS = 120
PROGRESS_BAR_DESCRIPTION_WIDTH = 35

# Terminal Colors (using colorama)
class Colors:
    # Basic colors
    PRIMARY = '\033[91m'  # Red
    SUCCESS = '\033[92m'  # Green
    WARNING = '\033[93m'  # Yellow
    INFO = '\033[94m'     # Blue
    ERROR = '\033[91m'    # Red
    RESET = '\033[0m'     # Reset
    
    # State colors
    WORK = '\033[92m'        # Green
    SHORT_BREAK = '\033[94m' # Blue
    LONG_BREAK = '\033[95m'  # Magenta
    PAUSED = '\033[93m'      # Yellow
    SKIPPED = '\033[91m'     # Red
    IDLE = '\033[97m'        # White

# GUI Colors (modern theme)
class GUIColors:
    PRIMARY = '#DC6B6B'
    PRIMARY_DARK = '#B85555'
    BACKGROUND = '#F5F5F5'
    CARD = '#FFFFFF'
    TEXT = '#333333'
    TEXT_LIGHT = '#666666'
    SUCCESS = '#4CAF50'
    WARNING = '#FF9800'
    WORK = '#DC6B6B'
    SHORT_BREAK = '#4A90E2'
    LONG_BREAK = '#9B59B6'
    PAUSED = '#F39C12'
    SKIPPED = '#E74C3C'

# Validation Limits
class Limits:
    MIN_TIMER_SECONDS = 1
    MAX_TIMER_SECONDS = 3600  # 1 hour
    MIN_POMODOROS = 1
    MAX_POMODOROS = 50
    MIN_WORKERS = 1
    MAX_WORKERS = 10
    MIN_QUEUE_SIZE = 1
    MAX_QUEUE_SIZE = 100

# Error Messages
class ErrorMessages:
    INVALID_TASKS = "At least one task is required"
    TOO_MANY_TASKS = f"Maximum {MAX_TASKS_EDGE_DEVICE} tasks supported on edge devices"
    INVALID_POMODOROS = "estimated_pomodoros must be positive"
    INVALID_TIME_INTERVALS = "All time intervals must be positive"
    INVALID_LONG_BREAK_COUNT = "pomos_before_long_break must be positive"
    TIMER_START_ERROR = "Timer start error"
    TIMER_PAUSE_ERROR = "Timer pause error"
    TIMER_SKIP_ERROR = "Timer skip error"
    FOCUS_DETECTOR_INIT_ERROR = "Failed to initialize detectors"
    FOCUS_DETECTOR_START_ERROR = "Failed to start focus detector" 