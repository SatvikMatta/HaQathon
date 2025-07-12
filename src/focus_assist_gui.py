"""
Focus Assist - Modern AI-Powered Pomodoro Timer
A completely redesigned GUI with task management, dark mode, and modern aesthetics
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pomodoro import PomodoroTimer, Task, TaskStatus, TimerState, TerminalOutput
from pomodoro.constants import (
    DEMO_WORK_SECONDS, DEMO_SHORT_BREAK_SECONDS, DEMO_LONG_BREAK_SECONDS,
    DEMO_SNAPSHOT_INTERVAL, DEFAULT_WORK_SECONDS, DEFAULT_SHORT_BREAK_SECONDS,
    DEFAULT_LONG_BREAK_SECONDS, DEFAULT_SNAPSHOT_INTERVAL
)

# Modern Color Themes
class Theme:
    """Modern color themes for light and dark modes"""
    
    # Light Theme
    LIGHT = {
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F8F9FA',
        'bg_tertiary': '#E9ECEF',
        'card_bg': '#FFFFFF',
        'primary': '#FF6B6B',
        'primary_hover': '#FF5252',
        'secondary': '#4ECDC4',
        'secondary_hover': '#26A69A',
        'accent': '#45B7D1',
        'accent_hover': '#2196F3',
        'text_primary': '#2C3E50',
        'text_secondary': '#34495E',
        'text_muted': '#7F8C8D',
        'success': '#2ECC71',
        'warning': '#F39C12',
        'error': '#E74C3C',
        'border': '#E1E8ED',
        'shadow': '#00000010'
    }
    
    # Dark Theme
    DARK = {
        'bg_primary': '#1A1A1A',
        'bg_secondary': '#2D2D2D',
        'bg_tertiary': '#404040',
        'card_bg': '#2D2D2D',
        'primary': '#FF6B6B',
        'primary_hover': '#FF5252',
        'secondary': '#4ECDC4',
        'secondary_hover': '#26A69A',
        'accent': '#45B7D1',
        'accent_hover': '#2196F3',
        'text_primary': '#FFFFFF',
        'text_secondary': '#E0E0E0',
        'text_muted': '#B0B0B0',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'error': '#F44336',
        'border': '#404040',
        'shadow': '#00000030'
    }

class TaskCard(ctk.CTkFrame):
    """Custom task card widget with modern design"""
    
    def __init__(self, parent, task: Task, theme: Dict[str, str], 
                 on_edit_callback=None, on_delete_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.task = task
        self.theme = theme
        self.on_edit_callback = on_edit_callback
        self.on_delete_callback = on_delete_callback
        
        self.configure(
            fg_color=theme['card_bg'],
            corner_radius=12,
            border_width=1,
            border_color=theme['border']
        )
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create task card widgets"""
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Main container
        container = ctk.CTkFrame(self, fg_color='transparent')
        container.pack(fill='both', expand=True, padx=15, pady=12)
        
        # Header with title and actions
        header = ctk.CTkFrame(container, fg_color='transparent')
        header.pack(fill='x', pady=(0, 8))
        
        # Task title
        title_label = ctk.CTkLabel(
            header,
            text=self.task.title,
            font=ctk.CTkFont(size=16, weight='bold'),
            text_color=self.theme['text_primary'],
            anchor='w'
        )
        title_label.pack(side='left', fill='x', expand=True)
        
        # Status indicator
        status_colors = {
            TaskStatus.NOT_STARTED: self.theme['text_muted'],
            TaskStatus.IN_PROGRESS: self.theme['primary'],
            TaskStatus.COMPLETED: self.theme['success'],
            TaskStatus.PAUSED: self.theme['warning']
        }
        
        status_label = ctk.CTkLabel(
            header,
            text=f"● {self.task.status.value.replace('_', ' ').title()}",
            font=ctk.CTkFont(size=12, weight='bold'),
            text_color=status_colors.get(self.task.status, self.theme['text_muted'])
        )
        status_label.pack(side='right', padx=(10, 0))
        
        # Description (if available)
        if self.task.description:
            desc_label = ctk.CTkLabel(
                container,
                text=self.task.description,
                font=ctk.CTkFont(size=13),
                text_color=self.theme['text_secondary'],
                anchor='w',
                wraplength=400
            )
            desc_label.pack(fill='x', pady=(0, 8))
        
        # Progress section
        progress_frame = ctk.CTkFrame(container, fg_color='transparent')
        progress_frame.pack(fill='x', pady=(0, 8))
        
        # Progress bar
        progress_value = self.task.completed_pomodoros / self.task.estimated_pomodoros if self.task.estimated_pomodoros > 0 else 0
        progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=200,
            height=8,
            progress_color=self.theme['primary'],
            fg_color=self.theme['bg_tertiary']
        )
        progress_bar.set(progress_value)
        progress_bar.pack(side='left', fill='x', expand=True)
        
        # Progress text
        progress_text = ctk.CTkLabel(
            progress_frame,
            text=f"{self.task.completed_pomodoros}/{self.task.estimated_pomodoros} 🍅",
            font=ctk.CTkFont(size=12, weight='bold'),
            text_color=self.theme['primary']
        )
        progress_text.pack(side='right', padx=(10, 0))
        
        # Actions
        actions_frame = ctk.CTkFrame(container, fg_color='transparent')
        actions_frame.pack(fill='x')
        
        # Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️ Edit",
            width=70,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color='transparent',
            text_color=self.theme['accent'],
            hover_color=self.theme['bg_tertiary'],
            command=self.edit_task
        )
        edit_btn.pack(side='left')
        
        # Delete button with trash icon
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=35,
            height=28,
            font=ctk.CTkFont(size=14),
            fg_color='transparent',
            text_color=self.theme['error'],
            hover_color=self.theme['bg_tertiary'],
            command=self.delete_task
        )
        delete_btn.pack(side='right')
        
    def edit_task(self):
        """Handle task editing"""
        if self.on_edit_callback:
            self.on_edit_callback(self.task)
            
    def delete_task(self):
        """Handle task deletion"""
        if self.on_delete_callback:
            self.on_delete_callback(self.task)

class FocusAssistApp:
    """Main application class for Focus Assist"""
    
    def __init__(self):
        # Initialize CustomTkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # App state
        self.is_dark_mode = False
        self.current_theme = Theme.LIGHT
        self.tasks: List[Task] = []
        self.current_task_index = 0
        self.timer: Optional[PomodoroTimer] = None
        self.timer_thread: Optional[threading.Thread] = None
        self.terminal_output: Optional[TerminalOutput] = None
        self.terminal_thread: Optional[threading.Thread] = None
        self.is_timer_running = False
        self.is_demo_mode = True  # Start in demo mode for testing
        
        # UI optimization
        self.task_cards: List[TaskCard] = []
        self.pending_updates = set()  # Track pending updates to batch them
        self.update_scheduled = False  # Prevent multiple update schedules
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Focus Assist - AI-Powered Pomodoro Timer")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create UI
        self.create_main_interface()
        self.apply_theme()
        
        # Load sample tasks for demo
        self.load_sample_tasks()
        
        # Initialize timer state
        self.current_timer_state = None
        
        # Start update loop
        self.start_update_loop()
        
    def create_main_interface(self):
        """Create the main application interface"""
        # Main container
        self.main_container = ctk.CTkFrame(self.root, fg_color='transparent')
        self.main_container.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        # Header
        self.create_header()
        
        # Main content area
        self.create_main_content()
        
        # Footer - REMOVED per user request
        # self.create_footer()
        
        # Status bar
        self.create_status_bar()
        
    def create_header(self):
        """Create application header"""
        header_frame = ctk.CTkFrame(self.main_container, fg_color='transparent')
        header_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo and title
        title_frame = ctk.CTkFrame(header_frame, fg_color='transparent')
        title_frame.grid(row=0, column=0, sticky='w')
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🎯 Focus Assist",
            font=ctk.CTkFont(size=28, weight='bold'),
            text_color=self.current_theme['primary']
        )
        title_label.pack(side='left')
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="AI-Powered Productivity Timer",
            font=ctk.CTkFont(size=14),
            text_color=self.current_theme['text_muted']
        )
        subtitle_label.pack(side='left', padx=(15, 0))
        
        # Controls
        controls_frame = ctk.CTkFrame(header_frame, fg_color='transparent')
        controls_frame.grid(row=0, column=1, sticky='e')
        
        # Demo mode toggle
        self.demo_mode_var = ctk.BooleanVar(value=self.is_demo_mode)
        demo_toggle = ctk.CTkSwitch(
            controls_frame,
            text="Demo Mode",
            variable=self.demo_mode_var,
            command=self.toggle_demo_mode,
            font=ctk.CTkFont(size=12),
            text_color=self.current_theme['text_secondary']
        )
        demo_toggle.pack(side='left', padx=(0, 20))
        
        # Dark mode toggle
        self.dark_mode_var = ctk.BooleanVar(value=self.is_dark_mode)
        dark_mode_toggle = ctk.CTkSwitch(
            controls_frame,
            text="Dark Mode",
            variable=self.dark_mode_var,
            command=self.toggle_dark_mode,
            font=ctk.CTkFont(size=12),
            text_color=self.current_theme['text_secondary']
        )
        dark_mode_toggle.pack(side='left')
        
    def create_main_content(self):
        """Create main content area"""
        # Left panel - Timer
        self.create_timer_panel()
        
        # Right panel - Tasks
        self.create_tasks_panel()
        
    def create_timer_panel(self):
        """Create timer panel"""
        self.timer_panel = ctk.CTkFrame(
            self.main_container,
            fg_color=self.current_theme['card_bg'],
            corner_radius=16,
            border_width=1,
            border_color=self.current_theme['border']
        )
        self.timer_panel.grid(row=1, column=0, sticky='nsew', padx=(0, 10))
        self.timer_panel.grid_columnconfigure(0, weight=1)
        
        # Timer content
        timer_content = ctk.CTkFrame(self.timer_panel, fg_color='transparent')
        timer_content.grid(row=0, column=0, sticky='nsew', padx=30, pady=30)
        timer_content.grid_columnconfigure(0, weight=1)
        
        # Current task display
        self.current_task_frame = ctk.CTkFrame(timer_content, fg_color='transparent')
        self.current_task_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        
        current_task_title = ctk.CTkLabel(
            self.current_task_frame,
            text="Current Task",
            font=ctk.CTkFont(size=14, weight='bold'),
            text_color=self.current_theme['text_muted']
        )
        current_task_title.pack()
        
        self.current_task_label = ctk.CTkLabel(
            self.current_task_frame,
            text="Select a task to begin",
            font=ctk.CTkFont(size=18, weight='bold'),
            text_color=self.current_theme['text_primary'],
            wraplength=300
        )
        self.current_task_label.pack(pady=(5, 0))
        
        # Timer display
        self.timer_display_frame = ctk.CTkFrame(
            timer_content,
            fg_color=self.current_theme['bg_secondary'],
            corner_radius=20,
            border_width=2,
            border_color=self.current_theme['primary']
        )
        self.timer_display_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        
        self.timer_label = ctk.CTkLabel(
            self.timer_display_frame,
            text="25:00",
            font=ctk.CTkFont(size=64, weight='bold'),
            text_color=self.current_theme['primary']
        )
        self.timer_label.pack(pady=40)
        
        # Store timer display frame for color updates
        self.timer_frame_ref = self.timer_display_frame
        
        # Timer mode selection
        self.mode_frame = ctk.CTkFrame(timer_content, fg_color='transparent')
        self.mode_frame.grid(row=2, column=0, sticky='ew', pady=(0, 20))
        
        self.mode_var = ctk.StringVar(value="Work")
        mode_options = ["Work", "Short Break", "Long Break"]
        self.mode_buttons = {}
        
        for i, mode in enumerate(mode_options):
            mode_btn = ctk.CTkRadioButton(
                self.mode_frame,
                text=mode,
                variable=self.mode_var,
                value=mode,
                font=ctk.CTkFont(size=14),
                text_color=self.current_theme['text_secondary']
            )
            mode_btn.pack(side='left', padx=10)
            self.mode_buttons[mode] = mode_btn
        
        # Timer controls
        controls_frame = ctk.CTkFrame(timer_content, fg_color='transparent')
        controls_frame.grid(row=3, column=0, sticky='ew')
        
        self.start_pause_btn = ctk.CTkButton(
            controls_frame,
            text="START",
            width=120,
            height=50,
            font=ctk.CTkFont(size=16, weight='bold'),
            fg_color=self.current_theme['primary'],
            hover_color=self.current_theme['primary_hover'],
            corner_radius=25,
            command=self.toggle_timer
        )
        self.start_pause_btn.pack(side='left', padx=(0, 10))
        
        self.stop_btn = ctk.CTkButton(
            controls_frame,
            text="STOP",
            width=80,
            height=50,
            font=ctk.CTkFont(size=14, weight='bold'),
            fg_color='transparent',
            text_color=self.current_theme['text_secondary'],
            hover_color=self.current_theme['bg_tertiary'],
            border_width=2,
            border_color=self.current_theme['border'],
            corner_radius=25,
            command=self.stop_timer
        )
        self.stop_btn.pack(side='left', padx=(0, 10))
        
        self.skip_btn = ctk.CTkButton(
            controls_frame,
            text="SKIP",
            width=80,
            height=50,
            font=ctk.CTkFont(size=14, weight='bold'),
            fg_color='transparent',
            text_color=self.current_theme['text_secondary'],
            hover_color=self.current_theme['bg_tertiary'],
            border_width=2,
            border_color=self.current_theme['border'],
            corner_radius=25,
            command=self.skip_timer
        )
        self.skip_btn.pack(side='left')
        
    def create_tasks_panel(self):
        """Create tasks panel"""
        self.tasks_panel = ctk.CTkFrame(
            self.main_container,
            fg_color=self.current_theme['card_bg'],
            corner_radius=16,
            border_width=1,
            border_color=self.current_theme['border']
        )
        self.tasks_panel.grid(row=1, column=1, sticky='nsew', padx=(10, 0))
        self.tasks_panel.grid_columnconfigure(0, weight=1)
        self.tasks_panel.grid_rowconfigure(1, weight=1)
        
        # Tasks header
        tasks_header = ctk.CTkFrame(self.tasks_panel, fg_color='transparent')
        tasks_header.grid(row=0, column=0, sticky='ew', padx=20, pady=(20, 0))
        tasks_header.grid_columnconfigure(0, weight=1)
        
        header_title = ctk.CTkLabel(
            tasks_header,
            text="Tasks",
            font=ctk.CTkFont(size=20, weight='bold'),
            text_color=self.current_theme['text_primary']
        )
        header_title.grid(row=0, column=0, sticky='w')
        
        add_task_btn = ctk.CTkButton(
            tasks_header,
            text="+ Add Task",
            width=100,
            height=32,
            font=ctk.CTkFont(size=12, weight='bold'),
            fg_color=self.current_theme['secondary'],
            hover_color=self.current_theme['secondary_hover'],
            corner_radius=16,
            command=self.add_task_dialog
        )
        add_task_btn.grid(row=0, column=1, sticky='e')
        
        # Tasks list with improved scrolling
        self.tasks_scroll_frame = ctk.CTkScrollableFrame(
            self.tasks_panel,
            fg_color='transparent',
            corner_radius=0,
            height=300  # Set minimum height to ensure scrolling works
        )
        self.tasks_scroll_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)
        self.tasks_scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Empty state
        self.empty_state_frame = ctk.CTkFrame(self.tasks_scroll_frame, fg_color='transparent')
        self.empty_state_frame.grid(row=0, column=0, sticky='ew', pady=50)
        
        empty_icon = ctk.CTkLabel(
            self.empty_state_frame,
            text="📋",
            font=ctk.CTkFont(size=48)
        )
        empty_icon.pack()
        
        empty_text = ctk.CTkLabel(
            self.empty_state_frame,
            text="No tasks yet\nAdd your first task to get started!",
            font=ctk.CTkFont(size=14),
            text_color=self.current_theme['text_muted'],
            justify='center'
        )
        empty_text.pack(pady=(10, 0))
        
    # Comment out the footer creation method since we removed the footer
    # def create_footer(self):
    #     """Create application footer"""
    #     footer_frame = ctk.CTkFrame(self.main_container, fg_color='transparent')
    #     footer_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(20, 0))
    #     
    #     # Stats
    #     stats_frame = ctk.CTkFrame(footer_frame, fg_color='transparent')
    #     stats_frame.pack(fill='x')
    #     
    #     self.stats_label = ctk.CTkLabel(
    #         stats_frame,
    #         text="📊 Sessions: 0 | 🍅 Pomodoros: 0 | ⏱️ Total Focus Time: 0h 0m",
    #         font=ctk.CTkFont(size=12),
    #         text_color=self.current_theme['text_muted']
    #     )
    #     self.stats_label.pack()

    def create_status_bar(self):
        """Create application status bar"""
        # Changed row from 3 to 2 since we removed the footer
        status_frame = ctk.CTkFrame(self.main_container, fg_color='transparent')
        status_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready to start - Terminal output will run in background",
            font=ctk.CTkFont(size=12),
            text_color=self.current_theme['text_muted']
        )
        self.status_label.pack()
        
    def toggle_dark_mode(self):
        """Toggle between light and dark modes"""
        self.is_dark_mode = self.dark_mode_var.get()
        self.current_theme = Theme.DARK if self.is_dark_mode else Theme.LIGHT
        
        # Update CustomTkinter appearance
        ctk.set_appearance_mode("dark" if self.is_dark_mode else "light")
        
        # Schedule efficient theme update
        self.schedule_update('theme')
        
    def toggle_demo_mode(self):
        """Toggle demo mode"""
        self.is_demo_mode = self.demo_mode_var.get()
        # Update timer if it exists
        if self.timer and not self.is_timer_running:
            self.setup_timer()
            
    def apply_theme(self):
        """Schedule theme application"""
        self.schedule_update('theme')
    
    def _apply_theme_immediate(self):
        """Apply current theme to all widgets immediately"""
        # Update root window
        self.root.configure(fg_color=self.current_theme['bg_primary'])
        
        # Update main container
        self.main_container.configure(fg_color='transparent')
        
        # Update timer panel
        self.timer_panel.configure(
            fg_color=self.current_theme['card_bg'],
            border_color=self.current_theme['border']
        )
        
        # Update tasks panel
        self.tasks_panel.configure(
            fg_color=self.current_theme['card_bg'],
            border_color=self.current_theme['border']
        )
        
        # Update timer display
        self.timer_display_frame.configure(
            fg_color=self.current_theme['bg_secondary'],
            border_color=self.current_theme['primary']
        )
        
        # Update buttons
        self.start_pause_btn.configure(
            fg_color=self.current_theme['primary'],
            hover_color=self.current_theme['primary_hover']
        )
        
        # Update task cards theme
        for task_card in self.task_cards:
            task_card.theme = self.current_theme
            task_card.needs_content_update = True
        
        # Force recreation of task cards with new theme
        self._recreate_task_cards()
        
    def load_sample_tasks(self):
        """Load sample tasks for demonstration"""
        sample_tasks = [
            {
                'title': 'Complete Project Proposal',
                'description': 'Draft and finalize the Q4 project proposal with budget estimates',
                'estimated_pomodoros': 4,
                'completed_pomodoros': 1
            },
            {
                'title': 'Code Review',
                'description': 'Review pull requests and provide feedback',
                'estimated_pomodoros': 2,
                'completed_pomodoros': 0
            },
            {
                'title': 'UI/UX Design',
                'description': 'Create wireframes for the new dashboard interface',
                'estimated_pomodoros': 3,
                'completed_pomodoros': 2
            }
        ]
        
        for task_data in sample_tasks:
            task = Task(
                id=str(uuid.uuid4()),
                title=task_data['title'],
                description=task_data['description'],
                estimated_pomodoros=task_data['estimated_pomodoros'],
                completed_pomodoros=task_data['completed_pomodoros']
            )
            self.tasks.append(task)
            
        self.schedule_update('tasks')
        
    def schedule_update(self, update_type: str):
        """Schedule an update to be batched"""
        self.pending_updates.add(update_type)
        if not self.update_scheduled:
            self.update_scheduled = True
            self.root.after_idle(self.process_pending_updates)
    
    def process_pending_updates(self):
        """Process all pending updates in a single frame"""
        if not self.pending_updates:
            self.update_scheduled = False
            return
            
        updates = self.pending_updates.copy()
        self.pending_updates.clear()
        self.update_scheduled = False
        
        # Process updates in optimal order
        if 'theme' in updates:
            self._apply_theme_immediate()
        if 'tasks' in updates:
            self._refresh_tasks_immediate()
        if 'current_task' in updates:
            self._update_current_task_immediate()
        if 'timer_colors' in updates:
            self._update_timer_colors_immediate()
    
    def refresh_tasks_display(self):
        """Schedule task display refresh"""
        self.schedule_update('tasks')
    
    def _refresh_tasks_immediate(self):
        """Efficiently refresh the tasks display"""
        # Update existing task cards instead of recreating them
        if len(self.task_cards) != len(self.tasks):
            # Only recreate if count changed
            self._recreate_task_cards()
        else:
            # Update existing cards
            for i, (task_card, task) in enumerate(zip(self.task_cards, self.tasks)):
                self._update_task_card(task_card, task, i)
    
    def _recreate_task_cards(self):
        """Recreate task cards when count changes"""
        # Clear existing task widgets
        for widget in self.tasks_scroll_frame.winfo_children():
            widget.destroy()
        self.task_cards.clear()
            
        if not self.tasks:
            # Show empty state
            empty_frame = ctk.CTkFrame(self.tasks_scroll_frame, fg_color='transparent')
            empty_frame.pack(fill='x', pady=50)
            
            empty_icon = ctk.CTkLabel(
                empty_frame,
                text="📋",
                font=ctk.CTkFont(size=48)
            )
            empty_icon.pack()
            
            empty_text = ctk.CTkLabel(
                empty_frame,
                text="No tasks yet\nAdd your first task to get started!",
                font=ctk.CTkFont(size=14),
                text_color=self.current_theme['text_muted'],
                justify='center'
            )
            empty_text.pack(pady=(10, 0))
        else:
            # Create task cards
            for i, task in enumerate(self.tasks):
                task_card = TaskCard(
                    self.tasks_scroll_frame,
                    task,
                    self.current_theme,
                    on_edit_callback=self.edit_task,
                    on_delete_callback=self.delete_task
                )
                task_card.pack(fill='x', pady=(0, 12))
                
                # Add click handler to select task
                task_card.bind("<Button-1>", lambda e, idx=i: self.select_task(idx))
                
                # Store reference and highlight current task
                self.task_cards.append(task_card)
                self._update_task_card(task_card, task, i)
    
    def _update_task_card(self, task_card: TaskCard, task: Task, index: int):
        """Update a single task card"""
        # Update task reference
        task_card.task = task
        
        # Update highlight for current task
        if index == self.current_task_index:
            task_card.configure(border_width=2, border_color=self.current_theme['primary'])
        else:
            task_card.configure(border_width=1, border_color=self.current_theme['border'])
        
        # Update task card content (recreate widgets if needed)
        if hasattr(task_card, 'needs_content_update'):
            task_card.create_widgets()
                
    def add_task_dialog(self):
        """Show dialog to add new task"""
        dialog = TaskDialog(self.root, self.current_theme, "Add New Task")
        if dialog.result:
            task = Task(
                id=str(uuid.uuid4()),
                title=dialog.result['title'],
                description=dialog.result['description'],
                estimated_pomodoros=dialog.result['estimated_pomodoros']
            )
            self.tasks.append(task)
            self.schedule_update('tasks')
            
    def edit_task(self, task: Task):
        """Edit existing task"""
        dialog = TaskDialog(
            self.root, 
            self.current_theme, 
            "Edit Task",
            task.title,
            task.description,
            task.estimated_pomodoros
        )
        if dialog.result:
            task.title = dialog.result['title']
            task.description = dialog.result['description']
            task.estimated_pomodoros = dialog.result['estimated_pomodoros']
            self.schedule_update('tasks')
            self.schedule_update('current_task')  # Update current task display
            
    def delete_task(self, task: Task):
        """Delete task"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{task.title}'?"):
            # Find the index of the task being deleted
            try:
                deleted_index = self.tasks.index(task)
                
                # Remove the task
                self.tasks.remove(task)
                
                # Adjust current task index if necessary
                if deleted_index < self.current_task_index:
                    # Deleted task was before current task, shift index down
                    self.current_task_index -= 1
                elif deleted_index == self.current_task_index:
                    # Deleted the current task, stay at same index (which now points to next task)
                    # But make sure we don't go out of bounds
                    if self.current_task_index >= len(self.tasks):
                        self.current_task_index = max(0, len(self.tasks) - 1)
                
                # Schedule batched UI updates
                self.schedule_update('current_task')
                self.schedule_update('tasks')
                
                # If timer is running, update its task list
                if self.timer and self.is_timer_running:
                    self.timer._tasks = self.tasks.copy()
                    
                # If all tasks deleted, reset
                if not self.tasks:
                    self.current_task_index = 0
                    
                self.update_status(f"Task '{task.title}' deleted")
                
            except ValueError:
                # Task not found in list (shouldn't happen)
                self.update_status("Error: Task not found")
            
    def select_task(self, index: int):
        """Select a task for the timer"""
        if 0 <= index < len(self.tasks):
            self.current_task_index = index
            self.schedule_update('current_task')
            self.schedule_update('tasks')  # To update highlighting
            
    def update_current_task_display(self):
        """Schedule current task display update"""
        self.schedule_update('current_task')
    
    def _update_current_task_immediate(self):
        """Update the current task display immediately"""
        if 0 <= self.current_task_index < len(self.tasks):
            task = self.tasks[self.current_task_index]
            self.current_task_label.configure(
                text=f"{task.title} ({task.completed_pomodoros}/{task.estimated_pomodoros} 🍅)"
            )
        else:
            self.current_task_label.configure(text="Select a task to begin")
            
    def setup_timer(self):
        """Setup timer with current tasks"""
        if not self.tasks:
            return
            
        # Get time settings based on demo mode
        if self.is_demo_mode:
            work_time = DEMO_WORK_SECONDS
            short_break = DEMO_SHORT_BREAK_SECONDS
            long_break = DEMO_LONG_BREAK_SECONDS
            snapshot_interval = DEMO_SNAPSHOT_INTERVAL
        else:
            work_time = DEFAULT_WORK_SECONDS
            short_break = DEFAULT_SHORT_BREAK_SECONDS
            long_break = DEFAULT_LONG_BREAK_SECONDS
            snapshot_interval = DEFAULT_SNAPSHOT_INTERVAL
            
        # Create timer with a copy of current tasks
        self.timer = PomodoroTimer(
            work_seconds=work_time,
            short_break_seconds=short_break,
            long_break_seconds=long_break,
            tasks=self.tasks.copy(),  # Use a copy to avoid reference issues
            snapshot_interval=snapshot_interval
        )
        
        # Create terminal output
        self.terminal_output = TerminalOutput(debug=True)
        
        # Add callbacks
        self.timer.add_state_callback(self.on_timer_state_changed)
        
        # Reset current task index to start from beginning
        self.current_task_index = 0
        self.update_current_task_display()
        
    def toggle_timer(self):
        """Toggle timer start/pause"""
        if not self.tasks:
            messagebox.showwarning("No Tasks", "Please add at least one task before starting the timer.")
            return
            
        if not self.timer:
            self.setup_timer()
            
        if not self.is_timer_running:
            # Start timer
            if self.timer.start():
                self.is_timer_running = True
                self.start_pause_btn.configure(text="PAUSE")
                
                # Set first task to IN_PROGRESS
                if 0 <= self.current_task_index < len(self.tasks):
                    self.tasks[self.current_task_index].status = TaskStatus.IN_PROGRESS
                    self.schedule_update('tasks')
                
                # Update colors for the initial timer state
                self.update_timer_colors(self.timer.state)
                self.start_timer_thread()
                self.start_terminal_output()
                self.update_status("Timer started - Terminal output running in background")
        else:
            # Check if timer is currently paused
            if self.timer.state == TimerState.PAUSED:
                # Resume timer
                if self.timer.start():
                    self.start_pause_btn.configure(text="PAUSE")
                    self.update_status("Timer resumed")
                else:
                    self.update_status("Failed to resume timer")
            else:
                # Pause timer
                if self.timer.pause():
                    self.start_pause_btn.configure(text="RESUME")
                    self.update_status("Timer paused")
                else:
                    self.update_status("Failed to pause timer")
                
    def stop_timer(self):
        """Stop the timer"""
        if self.timer:
            self.is_timer_running = False
            # Force timer to idle state
            self.timer.pause()  # This will stop the timer
            self.timer = None
            self.start_pause_btn.configure(text="START")
            self.timer_label.configure(text="25:00")
            self.update_status("Timer stopped")
            
    def skip_timer(self):
        """Skip current timer interval"""
        if self.timer and self.is_timer_running:
            self.timer.skip()
            self.update_status("Timer interval skipped")
            
    def start_timer_thread(self):
        """Start timer in separate thread"""
        if self.timer_thread and self.timer_thread.is_alive():
            return
            
        self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
        self.timer_thread.start()
        
    def timer_loop(self):
        """Main timer loop"""
        last_time_str = ""
        last_state = None
        
        while self.is_timer_running and self.timer:
            remaining_time = self.timer.get_remaining_time()
            if remaining_time:
                # Update display only if changed
                minutes, seconds = divmod(int(remaining_time.total_seconds()), 60)
                time_str = f"{minutes:02d}:{seconds:02d}"
                
                if time_str != last_time_str:
                    last_time_str = time_str
                    self.root.after(0, lambda t=time_str: self.timer_label.configure(text=t))
                
                # Update colors only if state changed
                if self.timer and self.timer.state != last_state:
                    last_state = self.timer.state
                    self.root.after(0, lambda s=last_state: self.update_timer_colors(s))
                
            time.sleep(1)
            
    def start_terminal_output(self):
        """Start terminal output in parallel"""
        # Only start if we have a timer running
        if not self.is_timer_running or not self.timer:
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
            while self.timer and self.timer.state != TimerState.IDLE:
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
            
    def on_timer_state_changed(self, state: TimerState):
        """Handle timer state changes"""
        state_text = state.value.replace('_', ' ').title()
        self.update_status(f"Timer state: {state_text}")
        
        # Update colors for new state
        self.update_timer_colors(state)
        
        # Handle work session completion
        if state == TimerState.SHORT_BREAK or state == TimerState.LONG_BREAK:
            self.on_work_session_completed()
        
        if state == TimerState.IDLE:
            self.is_timer_running = False
            self.start_pause_btn.configure(text="START")
            self.update_status("All tasks completed! Ready to start new session")
            # Reset to default colors when idle
            self.timer_label.configure(text_color=self.current_theme['primary'])
            self.timer_frame_ref.configure(border_color=self.current_theme['primary'])
            self.start_pause_btn.configure(
                fg_color=self.current_theme['primary'],
                hover_color=self.current_theme['primary_hover']
            )
        elif state == TimerState.PAUSED:
            # Update button text when paused via timer callback
            if hasattr(self, 'start_pause_btn'):
                self.start_pause_btn.configure(text="RESUME")
        elif state == TimerState.WORK:
            # Update button text when resumed/started
            if hasattr(self, 'start_pause_btn') and self.is_timer_running:
                self.start_pause_btn.configure(text="PAUSE")
                
    def on_work_session_completed(self):
        """Handle completion of a work session (pomodoro)"""
        if 0 <= self.current_task_index < len(self.tasks):
            # Update the current task's completed pomodoros
            current_task = self.tasks[self.current_task_index]
            current_task.completed_pomodoros += 1
            
            # Check if task is now complete
            if current_task.completed_pomodoros >= current_task.estimated_pomodoros:
                current_task.status = TaskStatus.COMPLETED
                self.update_status(f"Task '{current_task.title}' completed! 🎉")
                
                # Move to next incomplete task
                self.move_to_next_task()
            else:
                # Update status with progress
                self.update_status(f"Pomodoro completed! {current_task.completed_pomodoros}/{current_task.estimated_pomodoros} done")
                
            # Schedule batched UI updates
            self.schedule_update('current_task')
            self.schedule_update('tasks')
            
            # Update timer's task list to keep in sync
            if self.timer:
                self.timer._tasks = self.tasks.copy()
                
    def move_to_next_task(self):
        """Move to the next incomplete task"""
        # Find next incomplete task
        for i in range(len(self.tasks)):
            task = self.tasks[i]
            if task.status != TaskStatus.COMPLETED:
                self.current_task_index = i
                task.status = TaskStatus.IN_PROGRESS
                self.update_status(f"Starting next task: {task.title}")
                # Schedule updates for task change
                self.schedule_update('current_task')
                self.schedule_update('tasks')
                return
                
        # No more incomplete tasks
        self.current_task_index = len(self.tasks)  # Beyond array bounds to indicate completion
        self.update_status("All tasks completed! 🎉")
        self.schedule_update('current_task')
            
    def start_update_loop(self):
        """Start the GUI update loop"""
        self.update_gui()
        
    def update_gui(self):
        """Update GUI elements"""
        # Update stats - removed footer stats display but keep the calculation for internal use
        total_pomodoros = sum(task.completed_pomodoros for task in self.tasks)
        total_tasks = len(self.tasks)
        completed_tasks = len([task for task in self.tasks if task.status == TaskStatus.COMPLETED])
        
        # Remove the stats label update since we removed the footer
        # stats_text = f"📊 Tasks: {completed_tasks}/{total_tasks} | 🍅 Pomodoros: {total_pomodoros} | ⏱️ Focus Sessions: {total_pomodoros}"
        # self.stats_label.configure(text=stats_text)
        
        # Schedule next update less frequently to reduce load
        self.root.after(2000, self.update_gui)
        
    def get_state_colors(self, state: TimerState):
        """Get colors for timer display based on current state"""
        state_colors = {
            TimerState.WORK: {
                'primary': '#FF6B6B',  # Changed from green to red to match theme
                'secondary': '#FF5252',
                'display_bg': '#FFEBEE',
                'border': '#FF6B6B'
            },
            TimerState.SHORT_BREAK: {
                'primary': '#3498DB',  # Blue  
                'secondary': '#2980B9',
                'display_bg': '#EBF3FD',
                'border': '#3498DB'
            },
            TimerState.LONG_BREAK: {
                'primary': '#9B59B6',  # Purple
                'secondary': '#8E44AD',
                'display_bg': '#F4ECF7',
                'border': '#9B59B6'
            },
            TimerState.PAUSED: {
                'primary': '#F39C12',  # Orange
                'secondary': '#E67E22',
                'display_bg': '#FEF5E7',
                'border': '#F39C12'
            },
            TimerState.SKIPPED: {
                'primary': '#E74C3C',  # Red
                'secondary': '#C0392B',
                'display_bg': '#FADBD8',
                'border': '#E74C3C'
            }
        }
        
        # Default to work colors if state not found
        return state_colors.get(state, state_colors[TimerState.WORK])
    
    def update_timer_colors(self, state: TimerState):
        """Schedule timer colors update"""
        self.current_timer_state = state
        self.schedule_update('timer_colors')
    
    def _update_timer_colors_immediate(self):
        """Update timer display colors based on current state immediately"""
        if not hasattr(self, 'current_timer_state'):
            return
            
        colors = self.get_state_colors(self.current_timer_state)
        
        # Update timer label color
        self.timer_label.configure(text_color=colors['primary'])
        
        # Update timer frame border
        if hasattr(self, 'timer_frame_ref'):
            self.timer_frame_ref.configure(border_color=colors['border'])
        
        # Update start/pause button color
        self.start_pause_btn.configure(
            fg_color=colors['primary'],
            hover_color=colors['secondary']
        )
        
        # Update mode buttons to highlight current state
        self.update_mode_buttons_for_state(self.current_timer_state)
    
    def update_mode_buttons_for_state(self, state: TimerState):
        """Update mode button highlighting based on current timer state"""
        # Get colors for current state
        colors = self.get_state_colors(state)
        
        # Highlight the appropriate mode button based on state
        mode_mapping = {
            TimerState.WORK: "Work",
            TimerState.SHORT_BREAK: "Short Break", 
            TimerState.LONG_BREAK: "Long Break"
        }
        
        active_mode = mode_mapping.get(state)
        
        # Update radio button selection and colors
        if active_mode and hasattr(self, 'mode_buttons'):
            self.mode_var.set(active_mode)
            
            # Update all mode button colors
            for mode_name, mode_btn in self.mode_buttons.items():
                if mode_name == active_mode:
                    # Highlight active mode
                    mode_btn.configure(
                        fg_color=colors['primary'],
                        hover_color=colors['secondary'],
                        text_color='white'
                    )
                else:
                    # Reset inactive modes to default
                    mode_btn.configure(
                        fg_color=self.current_theme['text_muted'],
                        hover_color=self.current_theme['bg_tertiary'],
                        text_color=self.current_theme['text_secondary']
                    )
    
    def update_status(self, message: str):
        """Update status bar message"""
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=message)
        
    def run(self):
        """Run the application"""
        try:
            print("🚀 Starting Focus Assist GUI...")
            print("📱 GUI running - Check terminal for cross-reference output")
            print("🎯 Modern interface with AI-powered focus detection")
            print("=" * 50)
            
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("\n👋 Shutting down GUI...")
        finally:
            if self.terminal_output:
                self.terminal_output.cleanup_interrupted_bar()

class TaskDialog:
    """Dialog for adding/editing tasks"""
    
    def __init__(self, parent, theme: Dict[str, str], title: str, 
                 task_title: str = "", description: str = "", estimated_pomodoros: int = 1):
        self.result = None
        self.theme = theme
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.configure(fg_color=theme['bg_primary'])
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (parent.winfo_screenwidth() // 2) - (500 // 2)
        y = (parent.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        # Create form
        self.create_form(task_title, description, estimated_pomodoros)
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
    def create_form(self, task_title: str, description: str, estimated_pomodoros: int):
        """Create task form"""
        # Main frame
        main_frame = ctk.CTkFrame(self.dialog, fg_color='transparent')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Task Details",
            font=ctk.CTkFont(size=20, weight='bold'),
            text_color=self.theme['text_primary']
        )
        title_label.pack(pady=(0, 20))
        
        # Task title
        title_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        title_frame.pack(fill='x', pady=(0, 15))
        
        title_lbl = ctk.CTkLabel(
            title_frame,
            text="Task Title *",
            font=ctk.CTkFont(size=14, weight='bold'),
            text_color=self.theme['text_secondary']
        )
        title_lbl.pack(anchor='w')
        
        self.title_entry = ctk.CTkEntry(
            title_frame,
            placeholder_text="Enter task title...",
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.title_entry.pack(fill='x', pady=(5, 0))
        self.title_entry.insert(0, task_title)
        
        # Description
        desc_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        desc_frame.pack(fill='x', pady=(0, 15))
        
        desc_lbl = ctk.CTkLabel(
            desc_frame,
            text="Description (optional)",
            font=ctk.CTkFont(size=14, weight='bold'),
            text_color=self.theme['text_secondary']
        )
        desc_lbl.pack(anchor='w')
        
        self.desc_entry = ctk.CTkTextbox(
            desc_frame,
            height=80,
            font=ctk.CTkFont(size=14)
        )
        self.desc_entry.pack(fill='x', pady=(5, 0))
        self.desc_entry.insert('1.0', description)
        
        # Estimated pomodoros
        pomodoros_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        pomodoros_frame.pack(fill='x', pady=(0, 30))
        
        pomodoros_lbl = ctk.CTkLabel(
            pomodoros_frame,
            text="Estimated Pomodoros *",
            font=ctk.CTkFont(size=14, weight='bold'),
            text_color=self.theme['text_secondary']
        )
        pomodoros_lbl.pack(anchor='w')
        
        self.pomodoros_entry = ctk.CTkEntry(
            pomodoros_frame,
            placeholder_text="Enter number of pomodoros...",
            font=ctk.CTkFont(size=14),
            height=40,
            width=200
        )
        self.pomodoros_entry.pack(anchor='w', pady=(5, 0))
        self.pomodoros_entry.insert(0, str(estimated_pomodoros))
        
        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        buttons_frame.pack(fill='x')
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            width=100,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color='transparent',
            text_color=self.theme['text_secondary'],
            hover_color=self.theme['bg_tertiary'],
            border_width=2,
            border_color=self.theme['border'],
            command=self.cancel
        )
        cancel_btn.pack(side='right', padx=(10, 0))
        
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="Save Task",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight='bold'),
            fg_color=self.theme['primary'],
            hover_color=self.theme['primary_hover'],
            command=self.save
        )
        save_btn.pack(side='right')
        
        # Focus on title entry
        self.title_entry.focus()
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda event: self.save())
        self.dialog.bind('<KP_Enter>', lambda event: self.save())
        
    def save(self):
        """Save task"""
        title = self.title_entry.get().strip()
        description = self.desc_entry.get('1.0', 'end-1c').strip()
        
        try:
            estimated_pomodoros = int(self.pomodoros_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for estimated pomodoros.")
            return
            
        if not title:
            messagebox.showerror("Invalid Input", "Please enter a task title.")
            return
            
        if estimated_pomodoros <= 0:
            messagebox.showerror("Invalid Input", "Estimated pomodoros must be greater than 0.")
            return
            
        self.result = {
            'title': title,
            'description': description,
            'estimated_pomodoros': estimated_pomodoros
        }
        
        self.dialog.destroy()
        
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()

def main():
    """Main entry point"""
    try:
        app = FocusAssistApp()
        app.run()
    except Exception as e:
        print(f"Error starting Focus Assist: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 