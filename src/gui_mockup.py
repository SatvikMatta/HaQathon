"""
GUI Mockup for Focus Assist - Modern Pomofocus-inspired interface
Integrates with existing timer code while running terminal output in parallel
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
import os
from datetime import timedelta
from typing import Optional

# Add src directory to path to import existing modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pomodoro import PomodoroTimer, Task, TerminalOutput, TimerState
from pomodoro.constants import GUIColors, DEMO_WORK_SECONDS, DEMO_SHORT_BREAK_SECONDS, DEMO_LONG_BREAK_SECONDS, DEMO_SNAPSHOT_INTERVAL
from pomodoro.utils import TimeUtils
from pomodoro.display import GUIDisplayFormatter

# Using constants for modern color scheme
COLORS = {
    'primary': GUIColors.PRIMARY,
    'primary_dark': GUIColors.PRIMARY_DARK,
    'background': GUIColors.BACKGROUND,
    'card': GUIColors.CARD,
    'text': GUIColors.TEXT,
    'text_light': GUIColors.TEXT_LIGHT,
    'success': GUIColors.SUCCESS,
    'warning': GUIColors.WARNING,
    'work': GUIColors.WORK,
    'short_break': GUIColors.SHORT_BREAK,
    'long_break': GUIColors.LONG_BREAK,
    'paused': GUIColors.PAUSED,
    'skipped': GUIColors.SKIPPED
}

class ModernPomodoroGUI:
    def __init__(self):
        # Initialize CustomTkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Focus Assist - AI Pomodoro Timer")
        self.root.geometry("800x600")
        self.root.configure(fg_color=COLORS['background'])
        
        # Timer and terminal integration
        self.timer: Optional[PomodoroTimer] = None
        self.terminal_output: Optional[TerminalOutput] = None
        self.terminal_thread: Optional[threading.Thread] = None
        self.gui_update_thread: Optional[threading.Thread] = None
        self.running = False
        
        # UI State
        self.current_mode = "Pomodoro"
        self.timer_display = "25:00"
        self.current_task = "Time to focus!"
        
        # Create UI
        self.create_interface()
        self.setup_timer()
        
        # Start GUI update loop
        self.start_gui_updates()
        
    def create_interface(self):
        """Create the main interface matching pomofocus design"""
        
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS['background'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🎯 Focus Assist", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['primary']
        )
        title_label.pack(side="left")
        
        # Demo note
        demo_label = ctk.CTkLabel(
            header_frame, 
            text="DEMO MODE - Times shortened for testing", 
            font=ctk.CTkFont(size=10),
            text_color=COLORS['warning']
        )
        demo_label.pack(side="right")
        
        # Mode selection (Pomodoro, Short Break, Long Break)
        mode_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['card'], corner_radius=20)
        mode_frame.pack(fill="x", pady=(0, 30))
        
        mode_inner = ctk.CTkFrame(mode_frame, fg_color="transparent")
        mode_inner.pack(pady=20)
        
        # Mode buttons
        self.mode_buttons = {}
        modes = ["Pomodoro", "Short Break", "Long Break"]
        
        for i, mode in enumerate(modes):
            btn = ctk.CTkButton(
                mode_inner,
                text=mode,
                width=120,
                height=35,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=COLORS['primary'] if mode == self.current_mode else "transparent",
                text_color="white" if mode == self.current_mode else COLORS['text'],
                hover_color=COLORS['primary_dark'],
                command=lambda m=mode: self.switch_mode(m)
            )
            btn.pack(side="left", padx=10)
            self.mode_buttons[mode] = btn
        
        # Timer display
        timer_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['card'], corner_radius=20)
        timer_frame.pack(fill="x", pady=(0, 20))
        
        timer_inner = ctk.CTkFrame(timer_frame, fg_color="transparent")
        timer_inner.pack(pady=40)
        
        # Large timer display
        self.timer_label = ctk.CTkLabel(
            timer_inner,
            text=self.timer_display,
            font=ctk.CTkFont(size=72, weight="bold"),
            text_color=COLORS['primary']
        )
        self.timer_label.pack(pady=(0, 20))
        
        # Control buttons
        controls_frame = ctk.CTkFrame(timer_inner, fg_color="transparent")
        controls_frame.pack()
        
        self.start_button = ctk.CTkButton(
            controls_frame,
            text="START",
            width=200,
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            corner_radius=25,
            command=self.toggle_timer
        )
        self.start_button.pack(side="left", padx=5)
        
        self.pause_button = ctk.CTkButton(
            controls_frame,
            text="PAUSE",
            width=100,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            text_color=COLORS['text'],
            hover_color=COLORS['background'],
            border_width=2,
            border_color=COLORS['text_light'],
            corner_radius=25,
            command=self.pause_timer
        )
        self.pause_button.pack(side="left", padx=5)
        
        self.skip_button = ctk.CTkButton(
            controls_frame,
            text="SKIP",
            width=100,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            text_color=COLORS['text'],
            hover_color=COLORS['background'],
            border_width=2,
            border_color=COLORS['text_light'],
            corner_radius=25,
            command=self.skip_timer
        )
        self.skip_button.pack(side="left", padx=5)
        
        # Current task display
        task_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        task_frame.pack(fill="x", pady=(0, 20))
        
        task_label = ctk.CTkLabel(
            task_frame,
            text="#1",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_light']
        )
        task_label.pack()
        
        self.current_task_label = ctk.CTkLabel(
            task_frame,
            text=self.current_task,
            font=ctk.CTkFont(size=18),
            text_color=COLORS['text']
        )
        self.current_task_label.pack(pady=(5, 0))
        
        # Tasks section
        tasks_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['card'], corner_radius=20)
        tasks_frame.pack(fill="both", expand=True)
        
        tasks_header = ctk.CTkFrame(tasks_frame, fg_color="transparent")
        tasks_header.pack(fill="x", padx=20, pady=(20, 10))
        
        tasks_title = ctk.CTkLabel(
            tasks_header,
            text="Tasks",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS['text']
        )
        tasks_title.pack(side="left")
        
        # Task list (simplified for mockup)
        self.tasks_list = ctk.CTkFrame(tasks_frame, fg_color="transparent")
        self.tasks_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Add task button
        add_task_frame = ctk.CTkFrame(
            self.tasks_list,
            fg_color="transparent",
            border_width=2,
            border_color=COLORS['text_light'],
            corner_radius=10
        )
        add_task_frame.pack(fill="x", pady=10)
        
        add_task_btn = ctk.CTkButton(
            add_task_frame,
            text="+ Add Task",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=COLORS['text_light'],
            hover_color=COLORS['background'],
            command=self.add_task
        )
        add_task_btn.pack(pady=20)
        
        # Status bar
        self.status_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready to start - Terminal output running in background",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_light']
        )
        self.status_label.pack()
        
    def setup_timer(self):
        """Initialize the timer with existing code"""
        # Create demo tasks
        self.demo_tasks = [
            Task(
                id="1",
                title="Complete GUI mockup",
                description="Build modern interface with CustomTkinter",
                estimated_pomodoros=3
            ),
            Task(
                id="2",
                title="Integrate AI focus detection",
                description="Connect focus detection to GUI",
                estimated_pomodoros=2
            )
        ]
        
        # Timer configuration for different modes (shorter for demo)
        self.timer_configs = {
            "Pomodoro": {"work_seconds": 10, "display": "25:00"},    # 10 seconds for demo
            "Short Break": {"work_seconds": 5, "display": "05:00"},  # 5 seconds for demo
            "Long Break": {"work_seconds": 8, "display": "15:00"}    # 8 seconds for demo
        }
        
        # Create timer (using shorter intervals for demo)
        self.timer = PomodoroTimer(
            work_seconds=DEMO_WORK_SECONDS * 5,        # 25 seconds for demo
            short_break_seconds=DEMO_SHORT_BREAK_SECONDS * 3,  # 9 seconds for demo
            long_break_seconds=DEMO_LONG_BREAK_SECONDS * 2,   # 16 seconds for demo
            tasks=self.demo_tasks,
            snapshot_interval=DEMO_SNAPSHOT_INTERVAL * 2,     # 10 seconds
        )
        
        # Create terminal output
        self.terminal_output = TerminalOutput(debug=True)
        
        # Add callbacks
        self.timer.add_state_callback(self.on_timer_state_change)
        
        # Timer state tracking
        self.is_running = False
        self.current_interval_seconds = 10  # Default to Pomodoro (10 seconds for demo)
        
    def start_gui_updates(self):
        """Start the GUI update loop"""
        self.running = True
        self.gui_update_thread = threading.Thread(target=self.gui_update_loop, daemon=True)
        self.gui_update_thread.start()
        
    def gui_update_loop(self):
        """Update GUI elements in a separate thread"""
        while self.running:
            try:
                if self.timer and self.is_running and self.timer.state not in [TimerState.IDLE]:
                    remaining = self.timer.get_remaining_time()
                    if remaining:
                        # Update timer display
                        minutes = int(remaining.total_seconds() // 60)
                        seconds = int(remaining.total_seconds() % 60)
                        display_time = f"{minutes:02d}:{seconds:02d}"
                        
                        # Determine color based on timer state
                        color = self.get_timer_color(self.timer.state)
                        
                        # Schedule UI update on main thread
                        self.root.after(0, self.update_timer_display, display_time, color)
                        
                        # Update mode buttons based on current state
                        self.root.after(0, self.update_mode_buttons_for_state, self.timer.state)
                        
                        # Update start/stop button color based on current state
                        self.root.after(0, self.update_start_button_color, color)
                        
                        # Update current task with pause indicator
                        if self.timer.current_task_idx < len(self.timer.tasks):
                            task = self.timer.tasks[self.timer.current_task_idx]
                            pause_indicator = " (PAUSED)" if self.timer.state == TimerState.PAUSED else ""
                            task_text = f"{task.title} ({task.completed_pomodoros}/{task.estimated_pomodoros} 🍅){pause_indicator}"
                            self.root.after(0, self.update_current_task, task_text)
                    else:
                        # Timer finished (only if not paused)
                        if self.timer.state != TimerState.PAUSED:
                            self.root.after(0, self._on_timer_complete)
                elif not self.is_running:
                    # Show default display when not running
                    # Use color based on current mode
                    if self.current_mode == "Pomodoro":
                        color = COLORS['work']
                    elif self.current_mode == "Short Break":
                        color = COLORS['short_break']
                    elif self.current_mode == "Long Break":
                        color = COLORS['long_break']
                    else:
                        color = COLORS['primary']
                    
                    self.root.after(0, self.update_timer_display, self.timer_display, color)
                    
                    # Update mode buttons to show current mode selection when not running
                    for btn_mode, btn in self.mode_buttons.items():
                        if btn_mode == self.current_mode:
                            btn.configure(fg_color=color, text_color="white")
                        else:
                            btn.configure(fg_color="transparent", text_color=COLORS['text'])
                    
                    # Update start button color to match current mode when not running
                    self.start_button.configure(fg_color=color, hover_color=color)
                    
                    default_task = "Ready to focus!" if self.current_mode == "Pomodoro" else f"Time for {self.current_mode.lower()}"
                    self.root.after(0, self.update_current_task, default_task)
                
                time.sleep(0.1)  # Update every 100ms
                
            except Exception as e:
                print(f"GUI update error: {e}")
                time.sleep(1)
                
    def update_timer_display(self, display_time, color=None):
        """Update timer display on main thread"""
        if color:
            self.timer_label.configure(text=display_time, text_color=color)
        else:
            self.timer_label.configure(text=display_time)
        
    def update_current_task(self, task_text):
        """Update current task display on main thread"""
        self.current_task_label.configure(text=task_text)
        
    def update_start_button_color(self, color):
        """Update start/stop button color based on current timer state"""
        if self.is_running:
            # When running, use the current state color for the STOP button
            self.start_button.configure(fg_color=color, hover_color=color)
        
    def get_timer_color(self, state):
        """Get color for timer display based on current state"""
        if state == TimerState.WORK:
            return COLORS['work']
        elif state == TimerState.SHORT_BREAK:
            return COLORS['short_break']
        elif state == TimerState.LONG_BREAK:
            return COLORS['long_break']
        elif state == TimerState.PAUSED:
            return COLORS['paused']
        elif state == TimerState.SKIPPED:
            return COLORS['skipped']
        else:
            return COLORS['primary']  # Default color
            
    def update_mode_buttons_for_state(self, timer_state):
        """Update mode button highlighting based on current timer state"""
        # Reset all buttons to default
        for btn_mode, btn in self.mode_buttons.items():
            btn.configure(fg_color="transparent", text_color=COLORS['text'])
        
        # Highlight based on current timer state
        if timer_state == TimerState.WORK:
            if "Pomodoro" in self.mode_buttons:
                self.mode_buttons["Pomodoro"].configure(fg_color=COLORS['work'], text_color="white")
        elif timer_state == TimerState.SHORT_BREAK:
            if "Short Break" in self.mode_buttons:
                self.mode_buttons["Short Break"].configure(fg_color=COLORS['short_break'], text_color="white")
        elif timer_state == TimerState.LONG_BREAK:
            if "Long Break" in self.mode_buttons:
                self.mode_buttons["Long Break"].configure(fg_color=COLORS['long_break'], text_color="white")
        elif timer_state == TimerState.PAUSED:
            # Show paused state on whatever was active before pause
            if self.timer and hasattr(self.timer, '_pre_pause_state') and self.timer._pre_pause_state:
                self.update_mode_buttons_for_state(self.timer._pre_pause_state)
                # Add subtle indication that we're paused
                for btn_mode, btn in self.mode_buttons.items():
                    current_color = btn.cget("fg_color")
                    if current_color != "transparent":
                        btn.configure(text_color="#FFE4B5")  # Lighter text to show paused
        elif timer_state == TimerState.SKIPPED:
            # Show skipped state on whatever was active before skip
            if self.timer and hasattr(self.timer, '_pre_skip_state') and self.timer._pre_skip_state:
                self.update_mode_buttons_for_state(self.timer._pre_skip_state)
                # Add red tint to show skipped
                for btn_mode, btn in self.mode_buttons.items():
                    current_color = btn.cget("fg_color")
                    if current_color != "transparent":
                        btn.configure(fg_color=COLORS['skipped'])
        
    def start_terminal_output(self):
        """Start terminal output in parallel"""
        # Only start if we have a timer running
        if not self.is_running or not self.timer:
            return
            
        # Don't start if already running
        if self.terminal_thread and self.terminal_thread.is_alive():
            return
            
        self.terminal_thread = threading.Thread(target=self.terminal_loop, daemon=True)
        self.terminal_thread.start()
        
    def terminal_loop(self):
        """Run terminal output loop"""
        if not self.terminal_output or not self.timer:
            return
            
        print("\n🖥️  Terminal Output (Cross-reference with GUI):")
        print("=" * 50)
        
        self.terminal_output.print_header()
        
        try:
            while self.running and self.is_running and self.timer.state != TimerState.IDLE:
                # Update terminal display
                self.terminal_output.update_display(self.timer)
                
                # Handle snapshot events
                if self.timer.should_take_snapshot():
                    self.terminal_output.handle_snapshot()
                
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Terminal loop error: {e}")
        finally:
            print("🖥️  Terminal output stopped")
            
    def switch_mode(self, mode):
        """Switch between Pomodoro modes"""
        # Don't allow switching if timer is running
        if self.is_running:
            self.update_status("Cannot switch modes while timer is running")
            return
            
        self.current_mode = mode
        
        # Update button colors
        for btn_mode, btn in self.mode_buttons.items():
            if btn_mode == mode:
                btn.configure(fg_color=COLORS['primary'], text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=COLORS['text'])
                
        # Update timer display and internal state
        config = self.timer_configs[mode]
        self.timer_display = config["display"]
        self.current_interval_seconds = config["work_seconds"]
        
        # Reset timer to IDLE state
        if self.timer:
            self.timer.pause()  # Stop if running
            self.is_running = False
            self.start_button.configure(text="START")
            self.pause_button.configure(text="PAUSE")
            
        # Update timer display with appropriate color
        if mode == "Pomodoro":
            color = COLORS['work']
        elif mode == "Short Break":
            color = COLORS['short_break']
        elif mode == "Long Break":
            color = COLORS['long_break']
        else:
            color = COLORS['primary']
        
        self.timer_label.configure(text=self.timer_display, text_color=color)
        self.start_button.configure(fg_color=color, hover_color=color)
        self.update_status(f"Switched to {mode} mode - Ready to start")
        
    def toggle_timer(self):
        """Start/stop the timer"""
        if not self.timer:
            return
            
        if not self.is_running:
            # Start timer - create new session for current mode
            self._create_timer_session()
            success = self.timer.start()
            if success:
                self.is_running = True
                self.start_button.configure(text="STOP")
                
                # Update button color to match timer state
                timer_color = self.get_timer_color(self.timer.state)
                self.start_button.configure(fg_color=timer_color, hover_color=timer_color)
                
                self.update_status(f"Timer started - {self.current_mode} mode")
                self.start_terminal_output()
            else:
                self.update_status("Failed to start timer")
        else:
            # Stop timer completely
            self.timer.pause()
            self.is_running = False
            self.start_button.configure(text="START")
            self.pause_button.configure(text="PAUSE")
            # Use color based on current mode
            if self.current_mode == "Pomodoro":
                color = COLORS['work']
            elif self.current_mode == "Short Break":
                color = COLORS['short_break']
            elif self.current_mode == "Long Break":
                color = COLORS['long_break']
            else:
                color = COLORS['primary']
                
            self.timer_label.configure(text=self.timer_display, text_color=color)
            self.start_button.configure(fg_color=color, hover_color=color)
            self.update_status("Timer stopped")
            
    def _create_timer_session(self):
        """Create a new timer session for the current mode"""
        # Create single-task timer for the current mode
        if self.current_mode == "Pomodoro":
            # Use regular pomodoro timer
            self.timer = PomodoroTimer(
                work_seconds=self.current_interval_seconds,
                short_break_seconds=5,   # 5 seconds for demo
                long_break_seconds=8,    # 8 seconds for demo
                tasks=self.demo_tasks,
                snapshot_interval=3,     # 3 seconds for demo
            )
        else:
            # Create a single-interval timer for breaks
            break_task = Task(
                id="break",
                title=f"{self.current_mode} time",
                description="Take a break and relax",
                estimated_pomodoros=1
            )
            # For breaks, we just need a simple work timer that represents break time
            self.timer = PomodoroTimer(
                work_seconds=self.current_interval_seconds,
                short_break_seconds=self.current_interval_seconds,
                long_break_seconds=self.current_interval_seconds,
                tasks=[break_task],
                snapshot_interval=2,     # 2 seconds for demo
            )
        
        # Re-add callbacks
        self.timer.add_state_callback(self.on_timer_state_change)
            
    def pause_timer(self):
        """Pause/resume the timer"""
        if not self.timer or not self.is_running:
            self.update_status("No active timer to pause")
            return
            
        if self.timer.state == TimerState.PAUSED:
            # Resume timer
            success = self.timer.start()
            if success:
                self.pause_button.configure(text="PAUSE")
                self.update_status("Timer resumed")
            else:
                self.update_status("Failed to resume timer")
        else:
            # Pause timer
            success = self.timer.pause()
            if success:
                self.pause_button.configure(text="RESUME")
                self.update_status("Timer paused")
            else:
                self.update_status("Failed to pause timer")
            
    def skip_timer(self):
        """Skip current interval"""
        if not self.timer or not self.is_running:
            self.update_status("No active timer to skip")
            return
            
        # Skip current interval and continue to next
        success = self.timer.skip()
        if success:
            self.update_status("Interval skipped - Moving to next interval")
        else:
            self.update_status("Failed to skip interval")
        
    def add_task(self):
        """Add a new task (simplified for mockup)"""
        self.update_status("Task management - Feature coming soon!")
        
    def on_timer_state_change(self, new_state: TimerState):
        """Handle timer state changes"""
        state_text = new_state.value.replace('_', ' ').title()
        self.root.after(0, self.update_status, f"Timer state: {state_text}")
        
        # Handle timer completion
        if new_state == TimerState.IDLE:
            self.root.after(0, self._on_timer_complete)
            
    def _on_timer_complete(self):
        """Handle timer completion"""
        self.is_running = False
        self.start_button.configure(text="START")
        self.pause_button.configure(text="PAUSE")
        
        # Use color based on current mode
        if self.current_mode == "Pomodoro":
            color = COLORS['work']
        elif self.current_mode == "Short Break":
            color = COLORS['short_break']
        elif self.current_mode == "Long Break":
            color = COLORS['long_break']
        else:
            color = COLORS['primary']
            
        self.timer_label.configure(text=self.timer_display, text_color=color)
        self.start_button.configure(fg_color=color, hover_color=color)
        self.update_status(f"{self.current_mode} completed! Ready to start new session")
        
    def update_status(self, message):
        """Update status bar"""
        self.status_label.configure(text=message)
        
    def run(self):
        """Start the GUI application"""
        try:
            print("🚀 Starting Focus Assist GUI Mockup...")
            print("📱 GUI running - Check terminal for cross-reference output")
            print("🎯 Modern interface inspired by pomofocus.com")
            print("=" * 50)
            
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("\n👋 Shutting down GUI...")
        finally:
            self.running = False
            if self.terminal_output:
                self.terminal_output.cleanup_interrupted_bar()


def main():
    """Main entry point for GUI mockup"""
    try:
        app = ModernPomodoroGUI()
        app.run()
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("💡 Please install customtkinter: pip install customtkinter>=5.2.0")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 