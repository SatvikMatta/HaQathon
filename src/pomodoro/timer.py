from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"


class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    estimated_pomodoros: int
    completed_pomodoros: int = 0
    status: TaskStatus = TaskStatus.NOT_STARTED


class TimerState(Enum):
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"
    PAUSED = "paused"
    IDLE = "idle"


class PomodoroTimer:
    def __init__(
        self,
        work_seconds: int,
        short_break_seconds: int,
        long_break_seconds: int,
        tasks: List[Task],
        snapshot_interval: int = 60,  # in seconds
        pomos_before_long_break: int = 4
    ):
        self.pomo_length = timedelta(seconds=work_seconds)
        self.short_break_length = timedelta(seconds=short_break_seconds)
        self.long_break_length = timedelta(seconds=long_break_seconds)
        self.tasks = tasks
        self.snapshot_interval = timedelta(seconds=snapshot_interval)
        self.pomos_before_long_break = pomos_before_long_break
        
        # Internal state
        self.current_task_idx: int = 0
        self.completed_pomos: int = 0
        self.state: TimerState = TimerState.IDLE
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.next_snapshot_time: Optional[datetime] = None

    def start(self) -> None:
        """Start or resume the timer."""
        now = datetime.now()
        if self.state == TimerState.PAUSED and self.end_time and self.start_time:
            # Resume from pause - adjust end_time
            remaining = self.end_time - self.start_time
            self.start_time = now
            self.end_time = now + remaining
        else:
            # Start new interval
            self.state = TimerState.WORK
            self.start_time = now
            self.end_time = now + self.pomo_length
            self.next_snapshot_time = now + self.snapshot_interval
            
            # Update task status
            if self.current_task_idx < len(self.tasks) and self.tasks[self.current_task_idx].status != TaskStatus.IN_PROGRESS:
                self.tasks[self.current_task_idx].status = TaskStatus.IN_PROGRESS

    def pause(self) -> None:
        """Pause the timer."""
        if self.state in [TimerState.WORK, TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
            self.state = TimerState.PAUSED

    def skip(self) -> None:
        """Skip the current interval (work or break)."""
        self._handle_interval_completion()

    def get_remaining_time(self) -> Optional[timedelta]:
        """Get remaining time in current interval."""
        if not self.start_time or not self.end_time or self.state == TimerState.IDLE:
            return None
        
        now = datetime.now()
        if now >= self.end_time:
            self._handle_interval_completion()
            return self.get_remaining_time()
        
        return self.end_time - now

    def should_take_snapshot(self) -> bool:
        """Check if it's time to take a snapshot for focus detection."""
        if not self.next_snapshot_time or self.state != TimerState.WORK:
            return False
        
        now = datetime.now()
        if now >= self.next_snapshot_time:
            self.next_snapshot_time = now + self.snapshot_interval
            return True
        return False

    def _get_current_interval_length(self) -> timedelta:
        """Get the length of the current interval based on state."""
        if self.state == TimerState.WORK:
            return self.pomo_length
        elif self.state == TimerState.SHORT_BREAK:
            return self.short_break_length
        elif self.state == TimerState.LONG_BREAK:
            return self.long_break_length
        return timedelta()

    def _handle_interval_completion(self) -> None:
        """Handle the completion of a work or break interval."""
        if self.state == TimerState.WORK:
            # Complete pomodoro
            self.completed_pomos += 1
            if self.current_task_idx < len(self.tasks):
                self.tasks[self.current_task_idx].completed_pomodoros += 1
                
                # Check if task is completed
                if (self.tasks[self.current_task_idx].completed_pomodoros >= 
                    self.tasks[self.current_task_idx].estimated_pomodoros):
                    self.tasks[self.current_task_idx].status = TaskStatus.COMPLETED
                    self.current_task_idx += 1
                
            # Determine break type
            if self.completed_pomos % self.pomos_before_long_break == 0:
                self.state = TimerState.LONG_BREAK
            else:
                self.state = TimerState.SHORT_BREAK
                
        else:  # After break
            if self.current_task_idx < len(self.tasks):
                self.state = TimerState.WORK
            else:
                self.state = TimerState.IDLE
                return
            
        # Start new interval
        now = datetime.now()
        self.start_time = now
        self.end_time = now + self._get_current_interval_length()
        if self.state == TimerState.WORK:
            self.next_snapshot_time = now + self.snapshot_interval 