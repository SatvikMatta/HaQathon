from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Callable
from pydantic import BaseModel, Field, validator
import threading
import time
from dataclasses import dataclass


class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"


class Task(BaseModel):
    id: str
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    estimated_pomodoros: int = Field(..., gt=0, le=50)
    completed_pomodoros: int = Field(default=0, ge=0)
    status: TaskStatus = TaskStatus.NOT_STARTED

    @validator('estimated_pomodoros')
    def validate_pomodoros(cls, v):
        if v <= 0:
            raise ValueError('estimated_pomodoros must be positive')
        return v


class TimerState(Enum):
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"
    PAUSED = "paused"
    IDLE = "idle"


@dataclass(frozen=True)
class TimerConfig:
    """Immutable timer configuration for thread safety."""
    work_seconds: int
    short_break_seconds: int
    long_break_seconds: int
    snapshot_interval: int
    pomos_before_long_break: int

    def __post_init__(self):
        # Validate configuration
        if any(x <= 0 for x in [self.work_seconds, self.short_break_seconds, 
                               self.long_break_seconds, self.snapshot_interval]):
            raise ValueError("All time intervals must be positive")
        if self.pomos_before_long_break <= 0:
            raise ValueError("pomos_before_long_break must be positive")


class PomodoroTimer:
    """Thread-safe Pomodoro timer optimized for edge deployment."""
    
    __slots__ = ('_config', '_tasks', '_current_task_idx', '_completed_pomos', 
                 '_state', '_start_time', '_end_time', '_next_snapshot_time', 
                 '_lock', '_snapshot_callbacks', '_state_callbacks')

    def __init__(
        self,
        work_seconds: int,
        short_break_seconds: int,
        long_break_seconds: int,
        tasks: List[Task],
        snapshot_interval: int = 60,
        pomos_before_long_break: int = 4
    ):
        # Validate inputs
        if not tasks:
            raise ValueError("At least one task is required")
        if len(tasks) > 20:  # Edge device memory constraint
            raise ValueError("Maximum 20 tasks supported on edge devices")
            
        # Immutable config for thread safety
        self._config = TimerConfig(
            work_seconds=work_seconds,
            short_break_seconds=short_break_seconds,
            long_break_seconds=long_break_seconds,
            snapshot_interval=snapshot_interval,
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
        self._next_snapshot_time: Optional[float] = None
        
        # Callback systems for AI processing
        self._snapshot_callbacks: List[Callable[[], None]] = []
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

    def add_snapshot_callback(self, callback: Callable[[], None]) -> None:
        """Add callback for snapshot events (AI processing)."""
        with self._lock:
            self._snapshot_callbacks.append(callback)

    def add_state_callback(self, callback: Callable[[TimerState], None]) -> None:
        """Add callback for state changes."""
        with self._lock:
            self._state_callbacks.append(callback)

    def start(self) -> bool:
        """Start or resume the timer. Returns success status."""
        try:
            with self._lock:
                now = time.time()
                
                if self._state == TimerState.PAUSED and self._end_time and self._start_time:
                    # Resume from pause
                    remaining = self._end_time - self._start_time
                    self._start_time = now
                    self._end_time = now + remaining
                else:
                    # Start new interval
                    if self._current_task_idx >= len(self._tasks):
                        return False  # No more tasks
                    
                    self._state = TimerState.WORK
                    self._start_time = now
                    self._end_time = now + self._config.work_seconds
                    self._next_snapshot_time = now + self._config.snapshot_interval
                    
                    # Update task status
                    current_task = self._tasks[self._current_task_idx]
                    if current_task.status != TaskStatus.IN_PROGRESS:
                        current_task.status = TaskStatus.IN_PROGRESS
                
                self._notify_state_change(self._state)
                return True
                
        except Exception as e:
            # Edge device safeguard
            print(f"Timer start error: {e}")
            return False

    def pause(self) -> bool:
        """Pause the timer. Returns success status."""
        try:
            with self._lock:
                if self._state in [TimerState.WORK, TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
                    self._state = TimerState.PAUSED
                    self._notify_state_change(self._state)
                    return True
                return False
        except Exception as e:
            print(f"Timer pause error: {e}")
            return False

    def skip(self) -> bool:
        """Skip the current interval. Returns success status."""
        try:
            with self._lock:
                return self._handle_interval_completion()
        except Exception as e:
            print(f"Timer skip error: {e}")
            return False

    def get_remaining_time(self) -> Optional[timedelta]:
        """Get remaining time in current interval."""
        try:
            with self._lock:
                if not self._start_time or not self._end_time or self._state == TimerState.IDLE:
                    return None
                
                now = time.time()
                if now >= self._end_time:
                    self._handle_interval_completion()
                    return self.get_remaining_time()
                
                return timedelta(seconds=max(0, self._end_time - now))
        except Exception as e:
            print(f"Timer remaining time error: {e}")
            return None

    def should_take_snapshot(self) -> bool:
        """Check if it's time to take a snapshot. Thread-safe."""
        try:
            with self._lock:
                if (not self._next_snapshot_time or 
                    self._state != TimerState.WORK or 
                    not self._snapshot_callbacks):
                    return False
                
                now = time.time()
                if now >= self._next_snapshot_time:
                    self._next_snapshot_time = now + self._config.snapshot_interval
                    # Trigger callbacks asynchronously for performance
                    threading.Thread(target=self._trigger_snapshot_callbacks, daemon=True).start()
                    return True
                return False
        except Exception as e:
            print(f"Snapshot check error: {e}")
            return False

    def _trigger_snapshot_callbacks(self) -> None:
        """Trigger snapshot callbacks in background thread."""
        for callback in self._snapshot_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Snapshot callback error: {e}")

    def _notify_state_change(self, new_state: TimerState) -> None:
        """Notify state change callbacks."""
        for callback in self._state_callbacks:
            try:
                callback(new_state)
            except Exception as e:
                print(f"State callback error: {e}")

    def _get_current_interval_length(self) -> float:
        """Get the length of the current interval in seconds."""
        if self._state == TimerState.WORK:
            return self._config.work_seconds
        elif self._state == TimerState.SHORT_BREAK:
            return self._config.short_break_seconds
        elif self._state == TimerState.LONG_BREAK:
            return self._config.long_break_seconds
        return 0

    def _handle_interval_completion(self) -> bool:
        """Handle the completion of a work or break interval."""
        try:
            if self._state == TimerState.WORK:
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
                
            # Start new interval
            now = time.time()
            self._start_time = now
            self._end_time = now + self._get_current_interval_length()
            if self._state == TimerState.WORK:
                self._next_snapshot_time = now + self._config.snapshot_interval
            
            self._notify_state_change(self._state)
            return True
            
        except Exception as e:
            print(f"Interval completion error: {e}")
            self._state = TimerState.IDLE
            return False 