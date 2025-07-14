"""
Event logging system for Focus Assist session analytics.
Thread-safe logging of timer events with relative timestamps.
"""

import threading
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import time


@dataclass(frozen=True)
class SessionEvent:
    """Immutable event record with relative timestamp"""
    event_type: str  # Changed from EventType enum to string
    relative_time: float  # Seconds from start of current interval
    data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary format for stats processing"""
        result = {
            'event_type': self.event_type,
            'relative_time': self.relative_time,
            **self.data
        }
        return result


class SessionEventLogger:
    """Thread-safe session event logger with relative timestamps"""
    
    def __init__(self):
        self._events: List[SessionEvent] = []
        self._lock = threading.Lock()
        self._session_start_time: Optional[float] = None
        self._current_interval_start: Optional[float] = None
        
    def _get_relative_time(self) -> float:
        """Get relative time from start of current interval"""
        if self._current_interval_start is None:
            return 0.0
        return time.time() - self._current_interval_start
    
    def _log_event(self, event_type: str, **kwargs) -> None:
        """Log an event with relative timestamp"""
        relative_time = self._get_relative_time()
        event = SessionEvent(
            event_type=event_type,
            relative_time=relative_time,
            data=kwargs
        )
        
        with self._lock:
            self._events.append(event)
            
            # Print "event added" and entire event list
            print("event added")
            print("Current event logger list:")
            for i, evt in enumerate(self._events, 1):
                print(f"  {i}. event_type: {evt.event_type}")
                for key, value in evt.data.items():
                    print(f"     {key}: {value}")
            print()  # Empty line for readability
    
    def log_timer_start(self, pomodoro_length: int, break_length: int, long_break_length: int) -> None:
        """Log timer start - sets session baseline"""
        now = time.time()
        self._session_start_time = now
        self._current_interval_start = now  # Timer start is 00:00
        
        self._log_event(
            "TIMER_START",
            pomodoro_length=pomodoro_length,
            break_length=break_length,
            long_break_length=long_break_length
        )
    
    def log_pom_start(self, task_title: str, curr_pomodoro: int) -> None:
        """Log pomodoro start - resets interval baseline"""
        self._current_interval_start = time.time()  # Pom start is 00:00
        
        self._log_event(
            "POM_START",
            task_title=task_title,
            curr_pomodoro=curr_pomodoro
        )
    
    def log_ai_snap(self, s_category: str, s_focus: str, s_is_productive: bool) -> None:
        """Log AI snapshot - uses relative time from current interval start"""
        self._log_event(
            "AI_SNAP",
            s_category=s_category,
            s_focus=s_focus,
            s_is_productive=s_is_productive
        )
    
    def log_pom_end(self) -> None:
        """Log pomodoro end (no additional fields)"""
        self._log_event("POM_END")
    
    def log_break_start(self) -> None:
        """Log short break start - resets interval baseline"""
        self._current_interval_start = time.time()  # Break start is 00:00
        
        self._log_event("BREAK_START")
    
    def log_break_end(self) -> None:
        """Log short break end (no additional fields)"""
        self._log_event("BREAK_END")
    
    def log_long_break_start(self) -> None:
        """Log long break start - resets interval baseline"""
        self._current_interval_start = time.time()  # Long break start is 00:00
        
        self._log_event("LONG_BREAK_START")
    
    def log_long_break_end(self) -> None:
        """Log long break end (no additional fields)"""
        self._log_event("LONG_BREAK_END")
    
    def get_event_count(self) -> int:
        """Get total number of events logged"""
        with self._lock:
            return len(self._events)
    
    def get_session_duration(self) -> float:
        """Get total session duration in seconds"""
        if self._session_start_time is None:
            return 0.0
        return time.time() - self._session_start_time
    
    def get_events_as_dicts(self) -> List[Dict[str, Any]]:
        """Get all events as dictionaries for stats processing"""
        with self._lock:
            return [event.to_dict() for event in self._events]
    
    def print_session_summary(self) -> None:
        """Print formatted session summary"""
        with self._lock:
            if not self._events:
                print("No events logged in this session.")
                return
            
            duration = self.get_session_duration()
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            
            print("============================================================")
            print("FOCUS ASSIST SESSION EVENT LOG")
            print("============================================================")
            print(f"Total Events: {len(self._events)}")
            print(f"Session Duration: {minutes}m {seconds}s")
            print("------------------------------------------------------------")
            
            for i, event in enumerate(self._events, 1):
                print(f"  {i}. {event.event_type}")
                
                # Print event data
                for key, value in event.data.items():
                    print(f"     {key}: {value}")
            
            print("============================================================")
            print("End of Session Log")


# Self-test functionality
def _test_event_logger():
    """Test the event logger functionality and print field specifications"""
    print("\nEVENT TYPE FIELD SPECIFICATIONS:")
    print("=" * 70)
    print("Event Type\t\tFields")
    print("-" * 70)
    print("TIMER_START\t\tpomodoro_length, break_length, long_break_length")
    print("POM_START\t\ttask_title, curr_pomodoro")
    print("AI_SNAP\t\t\ts_category, s_focus, s_is_productive")
    print("POM_END\t\t\t(no additional fields)")
    print("BREAK_START\t\t(no additional fields)")
    print("BREAK_END\t\t(no additional fields)")
    print("LONG_BREAK_START\t(no additional fields)")
    print("LONG_BREAK_END\t\t(no additional fields)")
    print("=" * 70)
    print("\nTESTING EVENT LOGGER:\n")
    
    logger = SessionEventLogger()
    
    # Test timer start
    logger.log_timer_start(pomodoro_length=1500, break_length=300, long_break_length=900)
    
    # Simulate some delay
    time.sleep(0.1)
    
    # Test pom start
    logger.log_pom_start(task_title="Test Task", curr_pomodoro=1)
    
    # Simulate AI snapshots at 30-second intervals
    time.sleep(0.1)
    logger.log_ai_snap(s_category="WORK", s_focus="high", s_is_productive=True)
    
    time.sleep(0.1)
    logger.log_ai_snap(s_category="DISTRACTION", s_focus="low", s_is_productive=False)
    
    # Test pom end
    logger.log_pom_end()
    
    # Test break start
    logger.log_break_start()
    time.sleep(0.1)
    
    # Test break end
    logger.log_break_end()
    
    # Test long break start
    logger.log_long_break_start()
    time.sleep(0.1)
    
    # Test long break end
    logger.log_long_break_end()
    
    # Print summary
    logger.print_session_summary()
    
    # Test dictionary conversion for stats processing
    print("\nTESTING DICTIONARY CONVERSION:")
    print("=" * 50)
    events_as_dicts = logger.get_events_as_dicts()
    for i, event_dict in enumerate(events_as_dicts, 1):
        print(f"Event {i}: {event_dict}")


if __name__ == "__main__":
    print("Testing SessionEventLogger...")
    _test_event_logger() 