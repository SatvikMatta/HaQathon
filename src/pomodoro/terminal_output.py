from datetime import timedelta
import logging
from colorama import init, Fore, Style
from tqdm import tqdm
from typing import Optional
from .timer import PomodoroTimer, Task, TaskStatus, TimerState

# Initialize colorama for cross-platform color support
init()

logger = logging.getLogger(__name__)


class TerminalOutput:
    """Handles terminal display and progress bars for the Pomodoro timer."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.current_progress_bar: Optional[tqdm] = None
        self.last_timer_state: Optional[TimerState] = None
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    @staticmethod
    def format_seconds(seconds: float) -> str:
        """Format seconds into a human-readable string."""
        total_seconds = int(seconds)
        if total_seconds < 60:
            return f"{total_seconds}s"
        minutes = total_seconds // 60
        remaining_seconds = total_seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    
    def _print_bar(self, desc: str, percent: int, bar_fill: int, current: int, total: int):
        """Print a progress bar with given parameters."""
        bar = '█' * bar_fill + ' ' * (40 - bar_fill)
        print(f"        {desc.strip()} {percent}%|{bar}| "
              f"{self.format_seconds(current)}/{self.format_seconds(total)}")
    
    def create_progress_bar(self, total_seconds: int, desc: str, color: str = Fore.GREEN) -> tqdm:
        """Create a colored progress bar."""
        class CustomTqdm(tqdm):
            def format_meter(self, n, total, elapsed, ncols=None, prefix='', ascii=False, unit='s', 
                            unit_scale=False, rate=None, bar_format=None, postfix=None, unit_divisor=1000, **kwargs):
                n_fmt = TerminalOutput.format_seconds(n)
                total_fmt = TerminalOutput.format_seconds(total)
                if bar_format:
                    bar_format = bar_format.replace('{n_fmt}', n_fmt).replace('{total_fmt}', total_fmt)
                return super().format_meter(n, total, elapsed, ncols, prefix, ascii, unit, 
                                          unit_scale, rate, bar_format, postfix, unit_divisor, **kwargs)
        
        return CustomTqdm(
            total=total_seconds, desc=f"        {color}{desc:<35}{Style.RESET_ALL}",
            bar_format="{desc} {percentage:3.0f}%|{bar:40}| {n_fmt}/{total_fmt}",
            ncols=120, unit='s', position=0, leave=False
        )
    
    def print_header(self):
        """Print the application header."""
        print(f"\n{Fore.CYAN}Focus Timer Progress:{Style.RESET_ALL}")
    
    def update_display(self, timer: PomodoroTimer):
        """Update the progress display based on timer state."""
        remaining = timer.get_remaining_time()
        if not remaining:
            return
        
        total_seconds = int(remaining.total_seconds())
        
        # Create new progress bar only when timer state actually changes
        if timer.state != self.last_timer_state:
            if self.current_progress_bar:
                # Complete and close the previous bar
                self.current_progress_bar.n = self.current_progress_bar.total
                self.current_progress_bar.refresh()
                self.current_progress_bar.close()
                self._print_bar(self.current_progress_bar.desc, 100, 40, 
                               self.current_progress_bar.total, self.current_progress_bar.total)
            
            # Set color and description based on state
            if timer.state == TimerState.WORK:
                color, desc = Fore.GREEN, f"WORK - {timer.tasks[timer.current_task_idx].title}"
                task = timer.tasks[timer.current_task_idx]
                print(f"\n{Fore.YELLOW}Current Task: {task.title} "
                      f"({task.completed_pomodoros}/{task.estimated_pomodoros} pomodoros){Style.RESET_ALL}")
            elif timer.state == TimerState.SHORT_BREAK:
                color, desc = Fore.BLUE, "SHORT BREAK"
                print()
            else:  # LONG_BREAK
                color, desc = Fore.MAGENTA, "LONG BREAK"
                print()
            
            interval_length = timer._get_current_interval_length()
            self.current_progress_bar = self.create_progress_bar(int(interval_length.total_seconds()), desc, color)
            self.last_timer_state = timer.state
        
        # Update progress
        if self.current_progress_bar:
            interval_length = timer._get_current_interval_length()
            self.current_progress_bar.n = int(interval_length.total_seconds() - total_seconds)
            self.current_progress_bar.refresh()
    
    def handle_snapshot(self):
        """Handle snapshot event logging."""
        logger.debug("Taking snapshot for focus detection...")
        if self.debug:
            print(f"\n{Fore.YELLOW}Snapshot taken!{Style.RESET_ALL}")
    
    def handle_interruption(self):
        """Handle timer interruption cleanup."""
        if self.current_progress_bar:
            self.current_progress_bar.close()
        print(f"\n{Fore.RED}Timer stopped by user{Style.RESET_ALL}")
    
    def cleanup_interrupted_bar(self):
        """Clean up progress bar on interruption."""
        if self.current_progress_bar:
            self.current_progress_bar.close()
            progress_percent = int(self.current_progress_bar.n * 100 / self.current_progress_bar.total)
            bar_fill = int(self.current_progress_bar.n * 40 / self.current_progress_bar.total)
            self._print_bar(self.current_progress_bar.desc, progress_percent, bar_fill,
                           self.current_progress_bar.n, self.current_progress_bar.total)
    
    def print_final_statistics(self, timer: PomodoroTimer):
        """Print final session statistics."""
        print(f"\n{Fore.CYAN}Final Statistics:{Style.RESET_ALL}")
        print(f"Completed Pomodoros: {timer.completed_pomos}")
        
        for task in timer.tasks:
            status_color = Fore.GREEN if task.status == TaskStatus.COMPLETED else Fore.BLUE
            print(f"\n{Fore.YELLOW}Task: {task.title}{Style.RESET_ALL}")
            print(f"Status: {status_color}{task.status.value}{Style.RESET_ALL}")
            print(f"Completed Pomodoros: {task.completed_pomodoros}/{task.estimated_pomodoros}") 