"""
Flet GUI for Focus Assist - Modern Pomofocus-inspired interface
Self-contained Flet version of the CustomTkinter GUI
"""

import flet as ft
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

class FletPomodoroGUI:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Focus Assist - AI Pomodoro Timer"
        self.page.window_width = 900
        self.page.window_height = 700
        self.page.bgcolor = GUIColors.BACKGROUND
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        
        # Timer and state
        self.timer: Optional[PomodoroTimer] = None
        self.terminal_output: Optional[TerminalOutput] = None
        self.terminal_thread: Optional[threading.Thread] = None
        self.gui_update_thread: Optional[threading.Thread] = None
        self.running = False
        self.is_running = False
        
        # UI State
        self.current_mode = "Pomodoro"
        self.timer_display = "25:00"
        self.current_task = "Time to focus!"
        
        # UI Components
        self.timer_label = None
        self.start_button = None
        self.pause_button = None
        self.skip_button = None
        self.current_task_label = None
        self.mode_buttons = {}
        
        # Setup and start
        self.setup_timer()
        self.create_interface()
        self.start_gui_updates()
    
    def setup_timer(self):
        """Setup the timer with demo tasks"""
        # Create demo tasks
        self.demo_tasks = [
            Task(
                id="1",
                title="Focus on current project",
                description="Work on the most important task",
                estimated_pomodoros=3
            ),
            Task(
                id="2",
                title="Quick review session",
                description="Review and organize work",
                estimated_pomodoros=2
            )
        ]
        
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
        self.current_interval_seconds = 25  # Default to Pomodoro (25 seconds for demo)
    
    def create_interface(self):
        """Create the main Flet interface"""
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Text("🎯 Focus Assist", size=32, weight=ft.FontWeight.BOLD, color=GUIColors.PRIMARY),
                ft.Text("DEMO MODE - Times shortened for testing", size=12, color=GUIColors.WARNING)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=20
        )
        
        # Mode selection buttons
        mode_container = ft.Container(
            content=ft.Row([
                self.create_mode_button("Pomodoro"),
                self.create_mode_button("Short Break"),
                self.create_mode_button("Long Break")
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            bgcolor=GUIColors.CARD,
            border_radius=20,
            padding=20,
            margin=ft.margin.only(bottom=20)
        )
        
        # Timer display
        self.timer_label = ft.Text(
            self.timer_display,
            size=80,
            weight=ft.FontWeight.BOLD,
            color=GUIColors.PRIMARY,
            text_align=ft.TextAlign.CENTER
        )
        
        # Control buttons
        self.start_button = ft.ElevatedButton(
            text="START",
            width=200,
            height=60,
            bgcolor=GUIColors.PRIMARY,
            color="white",
            on_click=self.toggle_timer
        )
        
        self.pause_button = ft.OutlinedButton(
            text="PAUSE",
            width=120,
            height=60,
            on_click=self.pause_timer
        )
        
        self.skip_button = ft.OutlinedButton(
            text="SKIP",
            width=120,
            height=60,
            on_click=self.skip_timer
        )
        
        controls_row = ft.Row([
            self.start_button,
            self.pause_button,
            self.skip_button
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        
        timer_container = ft.Container(
            content=ft.Column([
                self.timer_label,
                ft.Container(height=20),  # Spacer
                controls_row
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=GUIColors.CARD,
            border_radius=20,
            padding=40,
            margin=ft.margin.only(bottom=20)
        )
        
        # Current task display
        task_container = ft.Container(
            content=ft.Column([
                ft.Text("#1", size=16, weight=ft.FontWeight.BOLD, color=GUIColors.TEXT_LIGHT),
                ft.Container(height=5),
                ft.Text(self.current_task, size=18, color=GUIColors.TEXT, text_align=ft.TextAlign.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            margin=ft.margin.only(bottom=20)
        )
        
        self.current_task_label = task_container.content.controls[2]
        
        # Tasks section
        tasks_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Tasks", size=24, weight=ft.FontWeight.BOLD, color=GUIColors.TEXT)
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(height=10),
                ft.Container(
                    content=ft.TextButton(
                        text="+ Add Task",
                        on_click=self.add_task
                    ),
                    border=ft.border.all(2, GUIColors.TEXT_LIGHT),
                    border_radius=10,
                    padding=20
                )
            ], spacing=10),
            bgcolor=GUIColors.CARD,
            border_radius=20,
            padding=20,
            expand=True
        )
        
        # Status bar
        self.status_text = ft.Text("Ready to focus!", size=14, color=GUIColors.TEXT_LIGHT)
        status_container = ft.Container(
            content=self.status_text,
            padding=10
        )
        
        # Add all components to page
        self.page.add(
            header,
            mode_container,
            timer_container,
            task_container,
            tasks_container,
            status_container
        )
    
    def create_mode_button(self, mode: str) -> ft.ElevatedButton:
        """Create a mode selection button"""
        button = ft.ElevatedButton(
            text=mode,
            width=140,
            height=40,
            bgcolor=GUIColors.PRIMARY if mode == self.current_mode else "transparent",
            color="white" if mode == self.current_mode else GUIColors.TEXT,
            on_click=lambda e, m=mode: self.switch_mode(m)
        )
        self.mode_buttons[mode] = button
        return button
    
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
                        self.page.run_thread_safe(lambda: self.update_timer_display(display_time, color))
                        
                        # Update current task
                        if self.timer.current_task_idx < len(self.timer.tasks):
                            task = self.timer.tasks[self.timer.current_task_idx]
                            pause_indicator = " (PAUSED)" if self.timer.state == TimerState.PAUSED else ""
                            task_text = f"{task.title} ({task.completed_pomodoros}/{task.estimated_pomodoros} 🍅){pause_indicator}"
                            self.page.run_thread_safe(lambda: self.update_current_task(task_text))
                    else:
                        # Timer finished
                        if self.timer.state != TimerState.PAUSED:
                            self.page.run_thread_safe(self._on_timer_complete)
                elif not self.is_running:
                    # Show default display when not running
                    color = self.get_mode_color(self.current_mode)
                    self.page.run_thread_safe(lambda: self.update_timer_display(self.timer_display, color))
                    
                    default_task = "Ready to focus!" if self.current_mode == "Pomodoro" else f"Time for {self.current_mode.lower()}"
                    self.page.run_thread_safe(lambda: self.update_current_task(default_task))
                
                time.sleep(0.1)  # Update every 100ms
                
            except Exception as e:
                print(f"GUI update error: {e}")
                time.sleep(1)
    
    def update_timer_display(self, display_time: str, color: str = None):
        """Update timer display on main thread"""
        if self.timer_label:
            self.timer_label.value = display_time
            if color:
                self.timer_label.color = color
            self.page.update()
    
    def update_current_task(self, task_text: str):
        """Update current task display on main thread"""
        if self.current_task_label:
            self.current_task_label.value = task_text
            self.page.update()
    
    def get_timer_color(self, state):
        """Get color for timer display based on current state"""
        color_map = {
            TimerState.WORK: GUIColors.WORK,
            TimerState.SHORT_BREAK: GUIColors.SHORT_BREAK,
            TimerState.LONG_BREAK: GUIColors.LONG_BREAK,
            TimerState.PAUSED: GUIColors.PAUSED,
            TimerState.SKIPPED: GUIColors.SKIPPED
        }
        return color_map.get(state, GUIColors.PRIMARY)
    
    def get_mode_color(self, mode: str):
        """Get color for mode"""
        color_map = {
            "Pomodoro": GUIColors.WORK,
            "Short Break": GUIColors.SHORT_BREAK,
            "Long Break": GUIColors.LONG_BREAK
        }
        return color_map.get(mode, GUIColors.PRIMARY)
    
    def switch_mode(self, mode: str):
        """Switch between timer modes"""
        if self.is_running:
            self.update_status("Stop the timer before switching modes")
            return
        
        self.current_mode = mode
        
        # Update mode buttons
        for btn_mode, button in self.mode_buttons.items():
            if btn_mode == mode:
                button.bgcolor = self.get_mode_color(mode)
                button.color = "white"
            else:
                button.bgcolor = "transparent"
                button.color = GUIColors.TEXT
        
        # Update timer display
        mode_times = {
            "Pomodoro": f"{DEMO_WORK_SECONDS * 5 // 60:02d}:{DEMO_WORK_SECONDS * 5 % 60:02d}",
            "Short Break": f"{DEMO_SHORT_BREAK_SECONDS * 3 // 60:02d}:{DEMO_SHORT_BREAK_SECONDS * 3 % 60:02d}",
            "Long Break": f"{DEMO_LONG_BREAK_SECONDS * 2 // 60:02d}:{DEMO_LONG_BREAK_SECONDS * 2 % 60:02d}"
        }
        
        self.timer_display = mode_times.get(mode, "25:00")
        color = self.get_mode_color(mode)
        
        # Update start button color
        self.start_button.bgcolor = color
        
        self.update_timer_display(self.timer_display, color)
        self.page.update()
        
        self.update_status(f"Switched to {mode} mode")
    
    def toggle_timer(self, e):
        """Toggle timer start/stop"""
        if not self.is_running:
            # Start timer
            self.is_running = True
            self.start_button.text = "STOP"
            self.start_button.bgcolor = GUIColors.SKIPPED  # Red color for stop
            
            # Start timer session
            self._create_timer_session()
            
            # Start terminal output
            self.start_terminal_output()
            
            self.update_status("Timer started!")
        else:
            # Stop timer
            self.is_running = False
            self.start_button.text = "START"
            self.start_button.bgcolor = self.get_mode_color(self.current_mode)
            
            if self.timer:
                self.timer.pause()
            
            self.update_status("Timer stopped")
        
        self.page.update()
    
    def _create_timer_session(self):
        """Create a new timer session"""
        try:
            # Reset timer with current mode
            mode_configs = {
                "Pomodoro": DEMO_WORK_SECONDS * 5,
                "Short Break": DEMO_SHORT_BREAK_SECONDS * 3,
                "Long Break": DEMO_LONG_BREAK_SECONDS * 2
            }
            
            work_seconds = mode_configs["Pomodoro"]
            
            self.timer = PomodoroTimer(
                work_seconds=work_seconds,
                short_break_seconds=mode_configs["Short Break"],
                long_break_seconds=mode_configs["Long Break"],
                tasks=self.demo_tasks,
                snapshot_interval=DEMO_SNAPSHOT_INTERVAL * 2,
            )
            
            # Add callbacks
            self.timer.add_state_callback(self.on_timer_state_change)
            
            # Start the timer
            self.timer.start()
            
        except Exception as e:
            self.update_status(f"Error starting timer: {e}")
    
    def pause_timer(self, e):
        """Pause the timer"""
        if self.timer and self.is_running:
            self.timer.pause()
            self.update_status("Timer paused")
    
    def skip_timer(self, e):
        """Skip current interval"""
        if self.timer and self.is_running:
            self.timer.skip()
            self.update_status("Interval skipped")
    
    def add_task(self, e):
        """Add a new task (placeholder)"""
        self.update_status("Add task feature coming soon!")
    
    def on_timer_state_change(self, new_state: TimerState):
        """Handle timer state changes"""
        state_messages = {
            TimerState.WORK: "Focus time! 🎯",
            TimerState.SHORT_BREAK: "Short break time! ☕",
            TimerState.LONG_BREAK: "Long break time! 🧘",
            TimerState.PAUSED: "Timer paused ⏸️",
            TimerState.SKIPPED: "Interval skipped ⏭️"
        }
        
        message = state_messages.get(new_state, "Timer state changed")
        self.page.run_thread_safe(lambda: self.update_status(message))
    
    def _on_timer_complete(self):
        """Handle timer completion"""
        self.is_running = False
        self.start_button.text = "START"
        self.start_button.bgcolor = self.get_mode_color(self.current_mode)
        self.update_status("Timer session completed! 🎉")
        self.page.update()
    
    def start_terminal_output(self):
        """Start terminal output in parallel"""
        if not self.is_running or not self.timer:
            return
        
        if self.terminal_thread and self.terminal_thread.is_alive():
            return
        
        self.terminal_thread = threading.Thread(target=self.terminal_loop, daemon=True)
        self.terminal_thread.start()
    
    def terminal_loop(self):
        """Run terminal output loop"""
        if not self.terminal_output or not self.timer:
            return
        
        print("\n🖥️  Terminal Output (Cross-reference with Flet GUI):")
        print("=" * 50)
        
        self.terminal_output.print_header()
        
        try:
            while self.running and self.is_running and self.timer.state != TimerState.IDLE:
                self.terminal_output.update_display(self.timer)
                
                if self.timer.should_take_snapshot():
                    self.terminal_output.handle_snapshot()
                
                time.sleep(0.1)
        except Exception as e:
            print(f"Terminal loop error: {e}")
        finally:
            print("🖥️  Terminal output stopped")
    
    def update_status(self, message: str):
        """Update status message"""
        if self.status_text:
            self.status_text.value = message
            self.page.update()
    
    def cleanup(self):
        """Cleanup resources"""
        self.running = False
        if self.timer:
            self.timer.pause()

def main(page: ft.Page):
    """Main entry point for Flet app"""
    gui = FletPomodoroGUI(page)
    
    # Handle page close
    def page_close(e):
        gui.cleanup()
    
    page.on_window_event = page_close

if __name__ == "__main__":
    print("🚀 Starting Flet Focus Assist GUI...")
    print("📱 This will open in your default web browser")
    print("🔄 Terminal output will appear here while GUI runs in browser")
    
    # Run the Flet app
    ft.app(target=main, view=ft.WEB_BROWSER, port=8080) 