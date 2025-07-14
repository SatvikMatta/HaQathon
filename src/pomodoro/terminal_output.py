"""
Simple event logging terminal output for Focus Assist.
No dependencies - just prints when events are logged.
"""

import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .timer import PomodoroTimer

class TerminalOutput:
    """Simple terminal output that prints event logger updates."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self._last_print_time = 0
        print("Terminal Output - Event Logger Mode")
        print("=" * 50)
    
    def print_header(self) -> None:
        """Print simple header."""
        print("Focus Assist - Event Logging Terminal Output")
        print("Monitoring event logger for updates...")
        print("-" * 50)
        
    def update_display(self, timer: 'PomodoroTimer') -> bool:
        """Simple display update - just print current status occasionally."""
        current_time = time.time()
        
        # Print status every 5 seconds to avoid spam
        if current_time - self._last_print_time >= 5:
            self._last_print_time = current_time
            
            if timer:
                remaining = timer.get_remaining_time()
                if remaining:
                    total_seconds = int(remaining.total_seconds())
                    minutes = total_seconds // 60
                    seconds = total_seconds % 60
                    
                    state_name = timer.state.value.replace('_', ' ').title()
    
        
        return True
    
    def handle_interruption(self) -> None:
        """Handle interruption."""
        print("Timer interrupted")
    
    def cleanup_interrupted_bar(self) -> None:
        """Clean up on interruption."""
        print("Cleaning up terminal output...")
    
    def print_final_statistics(self, timer: 'PomodoroTimer') -> None:
        """Print final statistics."""
        print("Session completed!")
        if timer and hasattr(timer, 'completed_pomos'):
            print(f"Completed pomodoros: {timer.completed_pomos}")
    
    def get_stats(self) -> dict:
        """Get simple stats."""
        return {"type": "simple_event_logger"}


# Simple event logger print functions
def print_event_logged(event_type: str, **kwargs):
    """Print when an event is logged to the event logger."""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] event_type : {event_type}")
    
    # Print event data if available
    if kwargs:
        for key, value in kwargs.items():
            print(f"    {key}: {value}")
    
    print()  # Empty line for readability


def print_timer_start_event(pomodoro_length: int, break_length: int, long_break_length: int):
    """Print timer start event."""
    print_event_logged("TIMER_START", 
                      pomodoro_length=pomodoro_length,
                      break_length=break_length, 
                      long_break_length=long_break_length)


def print_pom_start_event(task_title: str, curr_pomodoro: int):
    """Print pomodoro start event."""
    print_event_logged("POM_START", 
                      task_title=task_title,
                      curr_pomodoro=curr_pomodoro)


def print_ai_snap_event(s_category: str, s_focus: str, s_is_productive: bool):
    """Print AI snapshot event."""
    print_event_logged("AI_SNAP",
                      s_category=s_category,
                      s_focus=s_focus,
                      s_is_productive=s_is_productive)


def print_pom_end_event():
    """Print pomodoro end event."""
    print_event_logged("POM_END")


def print_break_start_event():
    """Print break start event."""
    print_event_logged("BREAK_START")


def print_break_end_event():
    """Print break end event."""
    print_event_logged("BREAK_END")


def print_long_break_start_event():
    """Print long break start event."""
    print_event_logged("LONG_BREAK_START")


def print_long_break_end_event():
    """Print long break end event."""
    print_event_logged("LONG_BREAK_END") 