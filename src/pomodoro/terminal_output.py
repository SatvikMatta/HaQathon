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
        
        # Set up logging level
        if debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
    
    @staticmethod
    def format_seconds(seconds: float) -> str:
        """Format seconds into a human-readable string."""
        total_seconds = int(seconds)
        if total_seconds < 60:
            return f"{total_seconds}s"
        minutes = total_seconds // 60
        remaining_seconds = total_seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    
    def create_progress_bar(self, total_seconds: int, desc: str, color: str = Fore.GREEN) -> tqdm:
        """Create a colored progress bar."""
        
        class CustomTqdm(tqdm):
            def format_meter(self, n, total, elapsed, ncols=None, prefix='', ascii=False, unit='s', 
                            unit_scale=False, rate=None, bar_format=None, postfix=None, unit_divisor=1000, **kwargs):
                # Custom formatting to use our format_seconds function
                n_fmt = TerminalOutput.format_seconds(n)
                total_fmt = TerminalOutput.format_seconds(total)
                
                # Replace the {n_fmt} and {total_fmt} in bar_format
                if bar_format:
                    bar_format = bar_format.replace('{n_fmt}', n_fmt).replace('{total_fmt}', total_fmt)
                
                return super().format_meter(n, total, elapsed, ncols, prefix, ascii, unit, 
                                          unit_scale, rate, bar_format, postfix, unit_divisor, **kwargs)
        
        return CustomTqdm(
            total=total_seconds,
            desc=f"        {color}{desc:<35}{Style.RESET_ALL}",
            bar_format="{desc} {percentage:3.0f}%|{bar:40}| {n_fmt}/{total_fmt}",
            ncols=120,
            unit='s',
            position=0,
            leave=False
        )
    
    def print_header(self):
        """Print the application header."""
        print(f"\n{Fore.CYAN}Focus Timer Progress:{Style.RESET_ALL}")
    
    def print_task_info(self, task: Task):
        """Print current task information."""
        print(f"\n{Fore.YELLOW}Current Task: {task.title} "
              f"({task.completed_pomodoros}/{task.estimated_pomodoros} pomodoros)"
              f"{Style.RESET_ALL}")
    
    def print_completed_bar(self, desc: str, total_seconds: int):
        """Print a completed progress bar."""
        print(f"        {desc.strip()} "
              f"100%|{'█' * 40}| {self.format_seconds(total_seconds)}")
    
    def print_interrupted_bar(self, desc: str, current: int, total: int):
        """Print the final state of an interrupted progress bar."""
        progress_percent = int(current * 100 / total)
        bar_fill = int(current * 40 / total)
        print(f"        {desc.strip()} "
              f"{progress_percent}%|{'█' * bar_fill}{' ' * (40 - bar_fill)}| "
              f"{self.format_seconds(current)}/{self.format_seconds(total)}")
    
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
                self.print_completed_bar(
                    self.current_progress_bar.desc, 
                    self.current_progress_bar.total
                )
            
            # Set color and description based on state
            if timer.state == TimerState.WORK:
                color = Fore.GREEN
                current_task = timer.tasks[timer.current_task_idx]
                desc = f"WORK - {current_task.title}"
                self.print_task_info(current_task)
            elif timer.state == TimerState.SHORT_BREAK:
                color = Fore.BLUE
                desc = "SHORT BREAK"
                print()
            else:  # LONG_BREAK
                color = Fore.MAGENTA
                desc = "LONG BREAK"
                print()
            
            interval_length = timer._get_current_interval_length()
            self.current_progress_bar = self.create_progress_bar(
                int(interval_length.total_seconds()),
                desc,
                color
            )
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
            self.print_interrupted_bar(
                self.current_progress_bar.desc,
                self.current_progress_bar.n,
                self.current_progress_bar.total
            )
    
    def print_final_statistics(self, timer: PomodoroTimer):
        """Print final session statistics."""
        print(f"\n{Fore.CYAN}Final Statistics:{Style.RESET_ALL}")
        print(f"Completed Pomodoros: {timer.completed_pomos}")
        
        for task in timer.tasks:
            print(f"\n{Fore.YELLOW}Task: {task.title}{Style.RESET_ALL}")
            status_color = Fore.GREEN if task.status == TaskStatus.COMPLETED else Fore.BLUE
            print(f"Status: {status_color}{task.status.value}{Style.RESET_ALL}")
            print(f"Completed Pomodoros: {task.completed_pomodoros}/{task.estimated_pomodoros}") 