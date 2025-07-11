from datetime import timedelta
import logging
import threading
from colorama import init, Fore, Style
from tqdm import tqdm
from typing import Optional
from .timer import PomodoroTimer, Task, TaskStatus, TimerState

# Initialize colorama for cross-platform color support
init()

logger = logging.getLogger(__name__)


class TerminalOutput:
    """Thread-safe terminal display optimized for edge deployment."""
    
    __slots__ = ('debug', '_current_progress_bar', '_last_timer_state', '_lock', '_stats')
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self._current_progress_bar: Optional[tqdm] = None
        self._last_timer_state: Optional[TimerState] = None
        self._lock = threading.RLock()  # Thread safety
        self._stats = {'updates': 0, 'errors': 0}  # Performance tracking
        
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    @staticmethod
    def format_seconds(seconds: float) -> str:
        """Optimized time formatting for edge devices."""
        total_seconds = int(seconds)
        if total_seconds < 60:
            return f"{total_seconds}s"
        minutes, remaining_seconds = divmod(total_seconds, 60)
        return f"{minutes}m {remaining_seconds}s"
    
    def _print_bar(self, desc: str, percent: int, bar_fill: int, current: int, total: int) -> None:
        """Thread-safe progress bar printing with minimal allocations."""
        try:
            bar_chars = '█' * bar_fill + ' ' * (40 - bar_fill)
            print(f"        {desc.strip()} {percent}%|{bar_chars}| "
                  f"{self.format_seconds(current)}/{self.format_seconds(total)}")
        except Exception as e:
            logger.error(f"Bar print error: {e}")
            self._stats['errors'] += 1
    
    def create_progress_bar(self, total_seconds: int, desc: str, color: str = Fore.GREEN) -> Optional[tqdm]:
        """Create optimized progress bar with error handling."""
        try:
            class CustomTqdm(tqdm):
                def format_meter(self, n, total, elapsed, ncols=None, prefix='', ascii=False, unit='s', 
                                unit_scale=False, rate=None, bar_format=None, postfix=None, unit_divisor=1000, **kwargs):
                    try:
                        n_fmt = TerminalOutput.format_seconds(n)
                        total_fmt = TerminalOutput.format_seconds(total)
                        if bar_format:
                            bar_format = bar_format.replace('{n_fmt}', n_fmt).replace('{total_fmt}', total_fmt)
                        return super().format_meter(n, total, elapsed, ncols, prefix, ascii, unit, 
                                                  unit_scale, rate, bar_format, postfix, unit_divisor, **kwargs)
                    except Exception:
                        return f"Progress: {int(n)}/{int(total)}"
            
            return CustomTqdm(
                total=total_seconds, 
                desc=f"        {color}{desc:<35}{Style.RESET_ALL}",
                bar_format="{desc} {percentage:3.0f}%|{bar:40}| {n_fmt}/{total_fmt}",
                ncols=120, unit='s', position=0, leave=False
            )
        except Exception as e:
            logger.error(f"Progress bar creation error: {e}")
            self._stats['errors'] += 1
            return None
    
    def print_header(self) -> None:
        """Thread-safe header printing."""
        with self._lock:
            try:
                print(f"\n{Fore.CYAN}Focus Timer Progress:{Style.RESET_ALL}")
            except Exception as e:
                logger.error(f"Header print error: {e}")
                self._stats['errors'] += 1
    
    def update_display(self, timer: PomodoroTimer) -> bool:
        """Thread-safe display update with performance optimization."""
        with self._lock:
            try:
                remaining = timer.get_remaining_time()
                if not remaining:
                    return False
                
                self._stats['updates'] += 1
                total_seconds = int(remaining.total_seconds())
                
                # Only update on state change for performance
                if timer.state != self._last_timer_state:
                    if self._current_progress_bar:
                        # Complete previous bar
                        try:
                            self._current_progress_bar.n = self._current_progress_bar.total
                            self._current_progress_bar.refresh()
                            self._current_progress_bar.close()
                            self._print_bar(self._current_progress_bar.desc, 100, 40, 
                                           self._current_progress_bar.total, self._current_progress_bar.total)
                        except Exception as e:
                            logger.error(f"Progress bar completion error: {e}")
                    
                    # Create new bar
                    color, desc = self._get_state_info(timer)
                    if timer.state == TimerState.WORK:
                        self._print_task_info(timer)
                    else:
                        print()
                    
                    interval_length = timer._get_current_interval_length()
                    self._current_progress_bar = self.create_progress_bar(
                        int(interval_length), desc, color
                    )
                    self._last_timer_state = timer.state
                
                # Update progress efficiently
                if self._current_progress_bar:
                    try:
                        interval_length = timer._get_current_interval_length()
                        self._current_progress_bar.n = int(interval_length - total_seconds)
                        self._current_progress_bar.refresh()
                    except Exception as e:
                        logger.error(f"Progress update error: {e}")
                
                return True
                
            except Exception as e:
                logger.error(f"Display update error: {e}")
                self._stats['errors'] += 1
                return False
    
    def _get_state_info(self, timer: PomodoroTimer) -> tuple[str, str]:
        """Get color and description for current state."""
        if timer.state == TimerState.WORK:
            task = timer.tasks[timer.current_task_idx]
            return Fore.GREEN, f"WORK - {task.title}"
        elif timer.state == TimerState.SHORT_BREAK:
            return Fore.BLUE, "SHORT BREAK"
        else:  # LONG_BREAK
            return Fore.MAGENTA, "LONG BREAK"
    
    def _print_task_info(self, timer: PomodoroTimer) -> None:
        """Print current task information."""
        try:
            task = timer.tasks[timer.current_task_idx]
            print(f"\n{Fore.YELLOW}Current Task: {task.title} "
                  f"({task.completed_pomodoros}/{task.estimated_pomodoros} pomodoros){Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"Task info print error: {e}")
    
    def handle_snapshot(self) -> None:
        """Thread-safe snapshot event handling."""
        try:
            logger.debug("Taking snapshot for focus detection...")
            if self.debug:
                print(f"\n{Fore.YELLOW}Snapshot taken!{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"Snapshot handling error: {e}")
    
    def handle_interruption(self) -> None:
        """Thread-safe interruption handling."""
        with self._lock:
            try:
                if self._current_progress_bar:
                    self._current_progress_bar.close()
                print(f"\n{Fore.RED}Timer stopped by user{Style.RESET_ALL}")
            except Exception as e:
                logger.error(f"Interruption handling error: {e}")
    
    def cleanup_interrupted_bar(self) -> None:
        """Thread-safe cleanup with error handling."""
        with self._lock:
            try:
                if self._current_progress_bar:
                    self._current_progress_bar.close()
                    progress_percent = min(100, int(self._current_progress_bar.n * 100 / 
                                                   max(1, self._current_progress_bar.total)))
                    bar_fill = min(40, int(self._current_progress_bar.n * 40 / 
                                          max(1, self._current_progress_bar.total)))
                    self._print_bar(self._current_progress_bar.desc, progress_percent, bar_fill,
                                   self._current_progress_bar.n, self._current_progress_bar.total)
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    def print_final_statistics(self, timer: PomodoroTimer) -> None:
        """Thread-safe final statistics with performance info."""
        with self._lock:
            try:
                print(f"\n{Fore.CYAN}Final Statistics:{Style.RESET_ALL}")
                print(f"Completed Pomodoros: {timer.completed_pomos}")
                
                for task in timer.tasks:
                    status_color = Fore.GREEN if task.status == TaskStatus.COMPLETED else Fore.BLUE
                    print(f"\n{Fore.YELLOW}Task: {task.title}{Style.RESET_ALL}")
                    print(f"Status: {status_color}{task.status.value}{Style.RESET_ALL}")
                    print(f"Completed Pomodoros: {task.completed_pomodoros}/{task.estimated_pomodoros}")
                
                # Performance stats for debugging
                if self.debug:
                    print(f"\n{Style.DIM}Performance: {self._stats['updates']} updates, "
                          f"{self._stats['errors']} errors{Style.RESET_ALL}")
                    
            except Exception as e:
                logger.error(f"Final statistics error: {e}")
    
    def get_stats(self) -> dict:
        """Get display performance statistics."""
        with self._lock:
            return self._stats.copy() 