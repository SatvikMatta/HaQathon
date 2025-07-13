from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Callable
from pydantic import BaseModel, Field, validator
import threading
import time
from dataclasses import dataclass
from .constants import MAX_TASKS_EDGE_DEVICE, MAX_TASK_TITLE_LENGTH, MAX_TASK_DESCRIPTION_LENGTH, MAX_ESTIMATED_POMODOROS, SKIP_DISPLAY_DURATION_SECONDS, ErrorMessages
from .utils import safe_execute_bool, safe_execute_none, ValidationUtils


class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"


class Task(BaseModel):
    id: str
    title: str = Field(..., min_length=1, max_length=MAX_TASK_TITLE_LENGTH)
    description: Optional[str] = Field(None, max_length=MAX_TASK_DESCRIPTION_LENGTH)
    estimated_pomodoros: int = Field(..., gt=0, le=MAX_ESTIMATED_POMODOROS)
    completed_pomodoros: int = Field(default=0, ge=0)
    status: TaskStatus = TaskStatus.NOT_STARTED

    @validator('estimated_pomodoros')
    def validate_pomodoros(cls, v):
        if v <= 0:
            raise ValueError(ErrorMessages.INVALID_POMODOROS)
        return v


class TimerState(Enum):
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"
    PAUSED = "paused"
    SKIPPED = "skipped"
    IDLE = "idle"


@dataclass(frozen=True)
class TimerConfig:
    """Immutable timer configuration for thread safety."""
    work_seconds: int
    short_break_seconds: int
    long_break_seconds: int
    pomos_before_long_break: int

    def __post_init__(self):
        # Validate configuration
        if any(x <= 0 for x in [self.work_seconds, self.short_break_seconds, 
                               self.long_break_seconds]):
            raise ValueError(ErrorMessages.INVALID_TIME_INTERVALS)
        if self.pomos_before_long_break <= 0:
            raise ValueError(ErrorMessages.INVALID_LONG_BREAK_COUNT)


class PomodoroTimer:
    """Thread-safe Pomodoro timer optimized for edge deployment."""
    
    __slots__ = ('_config', '_tasks', '_current_task_idx', '_completed_pomos', 
                 '_state', '_start_time', '_end_time', 
                 '_lock', '_state_callbacks', '_pre_pause_state', '_paused_remaining',
                 '_pre_skip_state', '_skipped_remaining', '_skip_display_shown')

    def __init__(
        self,
        work_seconds: int,
        short_break_seconds: int,
        long_break_seconds: int,
        tasks: List[Task],
        pomos_before_long_break: int = 4
    ):
        # Validate inputs
        ValidationUtils.validate_task_list(tasks)
        if len(tasks) > MAX_TASKS_EDGE_DEVICE:
            raise ValueError(ErrorMessages.TOO_MANY_TASKS)
            
        # Immutable config for thread safety
        self._config = TimerConfig(
            work_seconds=work_seconds,
            short_break_seconds=short_break_seconds,
            long_break_seconds=long_break_seconds,
            pomos_before_long_break=pomos_before_long_break
        )
        
        # State variables with thread lock
        self._lock = threading.RLock()
        self._tasks = tasks.copy()  # Defensive copy
        self._current_task_idx = 0
        self._completed_pomos = 0
        self._state = TimerState.IDLE
        self._start_time: Optional[float] = None  # Use timestamp for performance
        self._end_time: Optional[float] = None
        self._pre_pause_state: Optional[TimerState] = None
        self._paused_remaining: Optional[float] = None
        self._pre_skip_state: Optional[TimerState] = None
        self._skipped_remaining: Optional[float] = None
        self._skip_display_shown: bool = False
        
        # Callback systems
        self._state_callbacks: List[Callable[[TimerState], None]] = []

    @property
    def state(self) -> TimerState:
        """Thread-safe state access."""
        with self._lock:
            return self._state

    @property
    def current_task_idx(self) -> int:
        """Thread-safe task index access."""
        with self._lock:
            return self._current_task_idx

    @property
    def completed_pomos(self) -> int:
        """Thread-safe completed pomodoros access."""
        with self._lock:
            return self._completed_pomos

    @property
    def tasks(self) -> List[Task]:
        """Thread-safe tasks access (returns copy)."""
        with self._lock:
            return self._tasks.copy()



    def add_state_callback(self, callback: Callable[[TimerState], None]) -> None:
        """Add callback for state changes."""
        with self._lock:
            self._state_callbacks.append(callback)

    def start(self) -> bool:
        """Start or resume the timer. Returns success status."""
        try:
            with self._lock:
                now = time.time()
                
                if self._state == TimerState.PAUSED and self._paused_remaining is not None:
                    # Resume from pause - use stored remaining time
                    self._start_time = now
                    self._end_time = now + self._paused_remaining
                    # Restore the previous state (what we were doing before pause)
                    if self._pre_pause_state is not None:
                        self._state = self._pre_pause_state
                    else:
                        self._state = TimerState.WORK  # Default fallback
                    # Clear pause state
                    self._paused_remaining = None
                    self._pre_pause_state = None
                    
                    # Ensure task status is IN_PROGRESS when resuming work
                    if self._state == TimerState.WORK and self._current_task_idx < len(self._tasks):
                        current_task = self._tasks[self._current_task_idx]
                        current_task.status = TaskStatus.IN_PROGRESS
                else:
                    # Start new interval
                    if self._current_task_idx >= len(self._tasks):
                        return False  # No more tasks
                    
                    self._state = TimerState.WORK
                    self._start_time = now
                    self._end_time = now + self._config.work_seconds
                    
                    # Update task status to IN_PROGRESS
                    current_task = self._tasks[self._current_task_idx]
                    current_task.status = TaskStatus.IN_PROGRESS
                
                self._notify_state_change(self._state)
                return True
                
        except Exception as e:
            # Edge device safeguard
            print(f"{ErrorMessages.TIMER_START_ERROR}: {e}")
            return False

    def pause(self) -> bool:
        """Pause the timer. Returns success status."""
        try:
            with self._lock:
                if self._state in [TimerState.WORK, TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
                    # Store the current state and remaining time before pausing
                    self._pre_pause_state = self._state
                    if self._end_time and self._start_time:
                        now = time.time()
                        self._paused_remaining = max(0, self._end_time - now)
                    self._state = TimerState.PAUSED
                    self._notify_state_change(self._state)
                    return True
                return False
        except Exception as e:
            print(f"{ErrorMessages.TIMER_PAUSE_ERROR}: {e}")
            return False

    def skip(self) -> bool:
        """Skip the current interval. Returns success status."""
        try:
            with self._lock:
                if self._state in [TimerState.WORK, TimerState.SHORT_BREAK, TimerState.LONG_BREAK, TimerState.PAUSED]:
                    # Handle skipping while paused
                    if self._state == TimerState.PAUSED:
                        # Use the pre-pause state and remaining time
                        self._pre_skip_state = self._pre_pause_state if self._pre_pause_state else TimerState.WORK
                        self._skipped_remaining = self._paused_remaining if self._paused_remaining else 0
                    else:
                        # Store the current state and remaining time before skipping
                        self._pre_skip_state = self._state
                        if self._end_time and self._start_time:
                            now = time.time()
                            self._skipped_remaining = max(0, self._end_time - now)
                    
                    # Set to SKIPPED state for display
                    self._state = TimerState.SKIPPED
                    self._skip_display_shown = False  # Reset display flag
                    self._notify_state_change(self._state)
                    
                    # Set end time to allow SKIPPED display to be visible
                    self._end_time = time.time() + SKIP_DISPLAY_DURATION_SECONDS
                    
                    return True
                return False
        except Exception as e:
            print(f"{ErrorMessages.TIMER_SKIP_ERROR}: {e}")
            return False

    def get_remaining_time(self) -> Optional[timedelta]:
        """Get remaining time in current interval."""
        try:
            with self._lock:
                if not self._start_time or not self._end_time or self._state == TimerState.IDLE:
                    return None
                
                # If paused, return the stored remaining time
                if self._state == TimerState.PAUSED:
                    if self._paused_remaining is not None:
                        return timedelta(seconds=max(0, self._paused_remaining))
                    else:
                        # Fallback calculation if paused_remaining not stored
                        now = time.time()
                        return timedelta(seconds=max(0, self._end_time - now))
                
                # If skipped, handle display and completion
                if self._state == TimerState.SKIPPED:
                    now = time.time()
                    if now >= self._end_time and self._skip_display_shown:
                        # Complete the skip after display period
                        self._handle_interval_completion()
                        return self.get_remaining_time()
                    else:
                        # Mark that we've shown the skip display
                        self._skip_display_shown = True
                        # Return the stored remaining time at skip point
                        if self._skipped_remaining is not None:
                            return timedelta(seconds=max(0, self._skipped_remaining))
                        else:
                            return timedelta(seconds=0)  # Fallback for skipped
                
                now = time.time()
                if now >= self._end_time:
                    self._handle_interval_completion()
                    return self.get_remaining_time()
                
                return timedelta(seconds=max(0, self._end_time - now))
        except Exception as e:
            print(f"Timer remaining time error: {e}")
            return None



    def _notify_state_change(self, new_state: TimerState) -> None:
        """Notify state change callbacks."""
        for callback in self._state_callbacks:
            try:
                callback(new_state)
            except Exception as e:
                print(f"State callback error: {e}")

    def _get_current_interval_length(self) -> float:
        """Get the length of the current interval in seconds."""
        # Handle SKIPPED state by using the pre-skip state
        actual_state = self._state
        if self._state == TimerState.SKIPPED and self._pre_skip_state:
            actual_state = self._pre_skip_state
            
        if actual_state == TimerState.WORK:
            return self._config.work_seconds
        elif actual_state == TimerState.SHORT_BREAK:
            return self._config.short_break_seconds
        elif actual_state == TimerState.LONG_BREAK:
            return self._config.long_break_seconds
        return 0

    def _handle_interval_completion(self) -> bool:
        """Handle the completion of a work or break interval."""
        try:
            # Determine the actual state that was being executed (handle SKIPPED)
            actual_state = self._state
            if self._state == TimerState.SKIPPED and self._pre_skip_state:
                actual_state = self._pre_skip_state
            
            if actual_state == TimerState.WORK:
                # Complete pomodoro
                self._completed_pomos += 1
                if self._current_task_idx < len(self._tasks):
                    current_task = self._tasks[self._current_task_idx]
                    current_task.completed_pomodoros += 1
                    
                    # Check if task is completed
                    if current_task.completed_pomodoros >= current_task.estimated_pomodoros:
                        current_task.status = TaskStatus.COMPLETED
                        self._current_task_idx += 1
                    
                # Determine break type
                if self._completed_pomos % self._config.pomos_before_long_break == 0:
                    self._state = TimerState.LONG_BREAK
                else:
                    self._state = TimerState.SHORT_BREAK
                    
            else:  # After break
                if self._current_task_idx < len(self._tasks):
                    self._state = TimerState.WORK
                else:
                    self._state = TimerState.IDLE
                    self._notify_state_change(self._state)
                    return True
            
            # Clear skip state since we've handled completion
            self._pre_skip_state = None
            self._skipped_remaining = None
            self._skip_display_shown = False
                
            # Start new interval
            now = time.time()
            self._start_time = now
            self._end_time = now + self._get_current_interval_length()
            
            self._notify_state_change(self._state)
            return True
            
        except Exception as e:
            print(f"Interval completion error: {e}")
            self._state = TimerState.IDLE
            return False 