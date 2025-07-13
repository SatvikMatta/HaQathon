"""
Display formatting utilities for the Pomodoro timer application.
"""

from typing import Tuple
from colorama import Fore, Style
from .constants import Colors, GUIColors, PROGRESS_BAR_DESCRIPTION_WIDTH
from .utils import TimeUtils, ProgressBarUtils

# Import timer states (we'll need to handle this carefully to avoid circular imports)
try:
    from .timer import TimerState
except ImportError:
    # Handle case where timer module imports this module
    TimerState = None

class DisplayFormatter:
    """Handles formatting for terminal display."""
    
    @staticmethod
    def get_state_color_and_description(timer_state, current_task_title: str = "") -> Tuple[str, str]:
        """Get color and description for a timer state."""
        if not TimerState:
            return Fore.WHITE, "UNKNOWN"
            
        if timer_state == TimerState.WORK:
            return Fore.GREEN, f"WORK - {current_task_title}" if current_task_title else "WORK"
        elif timer_state == TimerState.SHORT_BREAK:
            return Fore.BLUE, "SHORT BREAK"
        elif timer_state == TimerState.LONG_BREAK:
            return Fore.MAGENTA, "LONG BREAK"
        elif timer_state == TimerState.PAUSED:
            return Fore.YELLOW, "PAUSED"
        elif timer_state == TimerState.SKIPPED:
            return Fore.RED, "SKIPPED"
        else:  # IDLE or other
            return Fore.WHITE, "IDLE"
    
    @staticmethod
    def get_paused_state_description(pre_pause_state, current_task_title: str = "") -> str:
        """Get description for paused state showing what was paused."""
        if not TimerState:
            return "PAUSED"
            
        if pre_pause_state == TimerState.WORK:
            return f"PAUSED - WORK - {current_task_title}" if current_task_title else "PAUSED - WORK"
        elif pre_pause_state == TimerState.SHORT_BREAK:
            return "PAUSED - SHORT BREAK"
        elif pre_pause_state == TimerState.LONG_BREAK:
            return "PAUSED - LONG BREAK"
        return "PAUSED"
    
    @staticmethod
    def get_skipped_state_description(pre_skip_state, current_task_title: str = "") -> str:
        """Get description for skipped state showing what was skipped."""
        if not TimerState:
            return "SKIPPED"
            
        if pre_skip_state == TimerState.WORK:
            return f"SKIPPED - WORK - {current_task_title}" if current_task_title else "SKIPPED - WORK"
        elif pre_skip_state == TimerState.SHORT_BREAK:
            return "SKIPPED - SHORT BREAK"
        elif pre_skip_state == TimerState.LONG_BREAK:
            return "SKIPPED - LONG BREAK"
        return "SKIPPED"
    
    @staticmethod
    def format_progress_bar_description(color: str, desc: str) -> str:
        """Format progress bar description with color and consistent width."""
        formatted_desc = ProgressBarUtils.format_progress_description(desc, PROGRESS_BAR_DESCRIPTION_WIDTH)
        return f"        {color}{formatted_desc}{Style.RESET_ALL}"
    
    @staticmethod
    def format_task_info(task_title: str, completed_pomos: int, estimated_pomos: int) -> str:
        """Format current task information."""
        return (f"\n{Fore.YELLOW}Current Task: {task_title} "
                f"({completed_pomos}/{estimated_pomos} pomodoros){Style.RESET_ALL}")
    
    @staticmethod
    def format_header() -> str:
        """Format the timer header."""
        return f"\n{Fore.CYAN}Focus Timer Progress:{Style.RESET_ALL}"
    
    @staticmethod
    def format_interruption_message() -> str:
        """Format interruption message."""
        return f"\n{Fore.RED}Timer stopped by user{Style.RESET_ALL}"
    

    
    @staticmethod
    def format_final_stats_header() -> str:
        """Format final statistics header."""
        return f"\n{Fore.CYAN}Final Statistics:{Style.RESET_ALL}"
    
    @staticmethod
    def format_task_status(task_title: str, status: str, completed_pomos: int, estimated_pomos: int) -> str:
        """Format task status in final statistics."""
        status_color = Fore.GREEN if status == "completed" else Fore.BLUE
        return (f"\n{Fore.YELLOW}Task: {task_title}{Style.RESET_ALL}\n"
                f"Status: {status_color}{status}{Style.RESET_ALL}\n"
                f"Completed Pomodoros: {completed_pomos}/{estimated_pomos}")

class GUIDisplayFormatter:
    """Handles formatting for GUI display."""
    
    @staticmethod
    def get_timer_color_for_state(timer_state) -> str:
        """Get GUI color for timer state."""
        if not TimerState:
            return GUIColors.TEXT
            
        color_map = {
            TimerState.WORK: GUIColors.WORK,
            TimerState.SHORT_BREAK: GUIColors.SHORT_BREAK,
            TimerState.LONG_BREAK: GUIColors.LONG_BREAK,
            TimerState.PAUSED: GUIColors.PAUSED,
            TimerState.SKIPPED: GUIColors.SKIPPED
        }
        return color_map.get(timer_state, GUIColors.TEXT)
    
    @staticmethod
    def get_mode_button_colors(current_mode: str, button_mode: str) -> Tuple[str, str]:
        """Get button colors based on current mode."""
        if current_mode == button_mode:
            return GUIColors.PRIMARY, "white"
        return "transparent", GUIColors.TEXT
    
    @staticmethod
    def format_demo_time_display(seconds: int) -> str:
        """Format time display for demo mode."""
        return TimeUtils.format_timer_display(seconds)
    
    @staticmethod
    def format_status_message(message: str, is_error: bool = False) -> str:
        """Format status message."""
        return message  # GUI handles styling differently

class ProgressBarFormatter:
    """Specialized formatter for progress bars."""
    
    @staticmethod
    def create_progress_bar_format() -> str:
        """Create the progress bar format string."""
        return "{desc} {percentage:3.0f}%|{bar:40}| {n_fmt}/{total_fmt}"
    
    @staticmethod
    def format_progress_time(seconds: float) -> str:
        """Format time for progress bar display."""
        return TimeUtils.format_seconds(seconds)
    
    @staticmethod
    def calculate_and_format_progress(current: int, total: int, desc: str) -> Tuple[int, int, str]:
        """Calculate progress values and format description."""
        percent = ProgressBarUtils.calculate_progress_percent(current, total)
        bar_fill = ProgressBarUtils.calculate_bar_fill(current, total, 40)
        formatted_desc = desc.strip()
        return percent, bar_fill, formatted_desc 