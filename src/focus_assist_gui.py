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
from PIL import Image

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pomodoro import PomodoroTimer, Task, TaskStatus, TimerState, TerminalOutput
from pomodoro.constants import (
    DEMO_WORK_SECONDS, DEMO_SHORT_BREAK_SECONDS, DEMO_LONG_BREAK_SECONDS,
    DEFAULT_WORK_SECONDS, DEFAULT_SHORT_BREAK_SECONDS,
    DEFAULT_LONG_BREAK_SECONDS
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
        'bg_primary': '#0D1117',      # GitHub dark background
        'bg_secondary': '#161B22',    # Slightly lighter for panels
        'bg_tertiary': '#21262D',     # Even lighter for tertiary elements
        'card_bg': '#21262D',         # Card background - distinct from primary
        'primary': '#FF6B6B',
        'primary_hover': '#FF5252',
        'secondary': '#4ECDC4',
        'secondary_hover': '#26A69A',
        'accent': '#45B7D1',
        'accent_hover': '#2196F3',
        'text_primary': '#F0F6FC',    # Slightly off-white for better readability
        'text_secondary': '#E6EDF3',  # Very light gray
        'text_muted': '#7D8590',      # Proper muted gray
        'success': '#3FB950',         # GitHub green
        'warning': '#D29922',         # GitHub amber
        'error': '#F85149',           # GitHub red
        'border': '#30363D',          # Proper dark border
        'shadow': '#00000080'         # More pronounced shadow
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
        
        # Cache for widget references to optimize updates
        self.progress_bar = None
        self.progress_text = None
        self.status_label = None
        self.title_label = None
        
        # Force explicit color configuration for both light and dark themes
        self.configure(
            fg_color=theme['card_bg'],
            corner_radius=12,
            border_width=1,
            border_color=theme['border']
        )
        
        # Update immediately to ensure colors are applied
        self.update_idletasks()
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create task card widgets"""
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Force background color update
        self.configure(
            fg_color=self.theme['card_bg'],
            border_color=self.theme['border']
        )
        
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
        
        self.status_label = ctk.CTkLabel(
            header,
            text=f"● {self.task.status.value.replace('_', ' ').title()}",
            font=ctk.CTkFont(size=12, weight='bold'),
            text_color=status_colors.get(self.task.status, self.theme['text_muted'])
        )
        self.status_label.pack(side='right', padx=(10, 0))
        
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
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=200,
            height=8,
            progress_color=self.theme['primary'],
            fg_color=self.theme['bg_tertiary']
        )
        self.progress_bar.set(progress_value)
        self.progress_bar.pack(side='left', fill='x', expand=True)
        
        # Progress text
        self.progress_text = ctk.CTkLabel(
            progress_frame,
            text=f"{self.task.completed_pomodoros}/{self.task.estimated_pomodoros} 🍅",
            font=ctk.CTkFont(size=12, weight='bold'),
            text_color=self.theme['primary']
        )
        self.progress_text.pack(side='right', padx=(10, 0))
        
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
    
    def update_progress_only(self):
        """Efficiently update only progress-related widgets without full recreation"""
        if not (self.progress_bar and self.progress_text and self.status_label):
            # Fallback to full recreation if widgets aren't cached
            self.create_widgets()
            return
        
        try:
            # Update progress bar with current theme colors
            progress_value = self.task.completed_pomodoros / self.task.estimated_pomodoros if self.task.estimated_pomodoros > 0 else 0
            self.progress_bar.set(progress_value)
            self.progress_bar.configure(
                progress_color=self.theme['primary'],
                fg_color=self.theme['bg_tertiary']
            )
            
            # Update progress text with current theme color
            self.progress_text.configure(
                text=f"{self.task.completed_pomodoros}/{self.task.estimated_pomodoros} 🍅",
                text_color=self.theme['primary']
            )
            
            # Update status with current theme colors
            status_colors = {
                TaskStatus.NOT_STARTED: self.theme['text_muted'],
                TaskStatus.IN_PROGRESS: self.theme['primary'],
                TaskStatus.COMPLETED: self.theme['success'],
                TaskStatus.PAUSED: self.theme['warning']
            }
            
            self.status_label.configure(
                text=f"● {self.task.status.value.replace('_', ' ').title()}",
                text_color=status_colors.get(self.task.status, self.theme['text_muted'])
            )
        except Exception:
            # If any update fails, fallback to full recreation
            self.create_widgets()

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
        # Demo mode removed - use normal timings
        
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
        
        # Load logo
        self.load_logo()
        
        # Initialize and load settings
        self.initialize_settings()
        if self.load_settings_from_file():
            # Apply loaded dark mode setting
            self.is_dark_mode = self.settings['appearance']['dark_mode']
            self.current_theme = Theme.DARK if self.is_dark_mode else Theme.LIGHT
            ctk.set_appearance_mode("dark" if self.is_dark_mode else "light")
        
        # Create UI
        self.create_main_interface()
        self.apply_theme()
        
        # Load sample tasks for demo
        self.load_sample_tasks()
        
        # Initialize timer state
        self.current_timer_state = None
        self.last_active_state = TimerState.WORK  # Track last non-paused state for radio buttons
        
        # Start update loop
        self.start_update_loop()
        
        # Set initial state colors to match work mode (default)
        self.root.after(100, self._apply_initial_state_colors)
        
    def load_logo(self):
        """Load the Focus Assist logo"""
        try:
            # Get the logo path relative to the src directory
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logo", "Focus_Assist.png")
            
            if os.path.exists(logo_path):
                # Load and resize the image
                pil_image = Image.open(logo_path)
                # Resize to fit nicely in the header (28x28 pixels)
                pil_image = pil_image.resize((28, 28), Image.Resampling.LANCZOS)
                
                # Create CTkImage
                self.logo_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(28, 28)
                )
            else:
                print(f"Logo not found at: {logo_path}")
                self.logo_image = None
        except Exception as e:
            print(f"Error loading logo: {e}")
            self.logo_image = None
        
    def _apply_initial_state_colors(self):
        """Apply initial state colors to match work mode"""
        # Set initial timer state and update colors
        self.current_timer_state = TimerState.WORK
        self.update_mode_buttons_for_state(TimerState.WORK)
        self._update_timer_colors_immediate()
        
    def create_main_interface(self):
        """Create the main application interface"""
        # Main container
        self.main_container = ctk.CTkFrame(self.root, fg_color='transparent')
        self.main_container.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(2, weight=0)  # Status bar - no expansion
        
        # Header
        self.create_header()
        
        # Main content area with tabs
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
        
    def create_header(self):
        """Create application header with integrated tabs"""
        # Main header container with background
        header_container = ctk.CTkFrame(
            self.main_container,
            fg_color=self.current_theme['bg_secondary'],
            corner_radius=16,
            border_width=1,
            border_color=self.current_theme['border'],
            height=110
        )
        header_container.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        header_container.grid_columnconfigure(1, weight=1)
        header_container.grid_propagate(False)  # Maintain fixed height
        
        # Top row - Title and controls
        top_row = ctk.CTkFrame(header_container, fg_color='transparent')
        top_row.grid(row=0, column=0, columnspan=2, sticky='ew', padx=25, pady=(12, 8))
        top_row.grid_columnconfigure(1, weight=1)
        
        # Logo and title
        title_frame = ctk.CTkFrame(top_row, fg_color='transparent')
        title_frame.grid(row=0, column=0, sticky='w')
        
        # Logo image (if available)
        if hasattr(self, 'logo_image') and self.logo_image is not None:
            self.logo_label = ctk.CTkLabel(
                title_frame,
                image=self.logo_image,
                text=""
            )
            self.logo_label.pack(side='left', padx=(0, 8))
        
        # Title text container
        title_text_frame = ctk.CTkFrame(title_frame, fg_color='transparent')
        title_text_frame.pack(side='left')
        
        self.title_label = ctk.CTkLabel(
            title_text_frame,
            text="Focus Assist",
            font=ctk.CTkFont(size=26, weight='bold'),
            text_color=self.current_theme['primary']
        )
        self.title_label.pack(anchor='w')
        
        # Controls
        controls_frame = ctk.CTkFrame(top_row, fg_color='transparent')
        controls_frame.grid(row=0, column=1, sticky='e')
        
        # Settings button with icon
        self.settings_button = ctk.CTkButton(
            controls_frame,
            text="⚙️ Settings",
            width=95,
            height=30,
            font=ctk.CTkFont(size=11, weight='bold'),
            fg_color='transparent',
            hover_color=self.current_theme['bg_tertiary'],
            text_color=self.current_theme['text_secondary'],
            border_width=1,
            border_color=self.current_theme['border'],
            corner_radius=8,
            command=lambda: self.switch_tab("Settings")
        )
        self.settings_button.pack(side='left', padx=(0, 12))
        
        # Dark mode toggle removed - now in settings tab
        
        # Bottom row - Navigation tabs
        self.nav_frame = ctk.CTkFrame(header_container, fg_color='transparent')
        self.nav_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=25, pady=(0, 15))
        
        # Create integrated tab buttons
        self.create_navigation_tabs()
        
    def create_navigation_tabs(self):
        """Create navigation tabs integrated into header"""
        # Tab buttons container
        tabs_container = ctk.CTkFrame(self.nav_frame, fg_color='transparent')
        tabs_container.pack(side='left')
        
        # Create custom tab buttons (only Timer and Stats, Settings is in top-right)
        self.nav_buttons = {}
        self.current_tab = "Timer"
        
        tab_names = ["Timer", "Stats"]
        for i, tab_name in enumerate(tab_names):
            button = ctk.CTkButton(
                tabs_container,
                text=tab_name,
                width=120,
                height=36,
                font=ctk.CTkFont(size=14, weight='bold'),
                corner_radius=12,
                command=lambda name=tab_name: self.switch_tab(name)
            )
            button.pack(side='left', padx=(0, 10) if i < len(tab_names) - 1 else (0, 0))
            self.nav_buttons[tab_name] = button
            
        # Update button styles for initial state
        self.update_tab_buttons()
        
    def switch_tab(self, tab_name):
        """Switch to the specified tab"""
        if tab_name == self.current_tab:
            return
            
        self.current_tab = tab_name
        self.update_tab_buttons()
        
        # Hide all content frames
        if hasattr(self, 'timer_content'):
            self.timer_content.grid_remove()
        if hasattr(self, 'stats_content'):
            self.stats_content.grid_remove()
        if hasattr(self, 'settings_content'):
            self.settings_content.grid_remove()
            
        # Show selected content
        if tab_name == "Timer":
            self.timer_content.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        elif tab_name == "Stats":
            self.stats_content.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        elif tab_name == "Settings":
            self.settings_content.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
            
    def update_tab_buttons(self):
        """Update tab button styles based on current selection"""
        # Update main navigation buttons (Timer, Stats)
        for tab_name, button in self.nav_buttons.items():
            if tab_name == self.current_tab:
                # Active tab
                button.configure(
                    fg_color=self.current_theme['primary'],
                    hover_color=self.current_theme['primary_hover'],
                    text_color="white"
                )
            else:
                # Inactive tab
                button.configure(
                    fg_color='transparent',
                    hover_color=self.current_theme['bg_tertiary'],
                    text_color=self.current_theme['text_secondary'],
                    border_width=1,
                    border_color=self.current_theme['border']
                )
        
        # Update settings button in top-right
        if hasattr(self, 'settings_button'):
            if self.current_tab == "Settings":
                # Active settings
                self.settings_button.configure(
                    fg_color=self.current_theme['primary'],
                    hover_color=self.current_theme['primary_hover'],
                    text_color="white",
                    border_width=0
                )
            else:
                # Inactive settings
                self.settings_button.configure(
                    fg_color='transparent',
                    hover_color=self.current_theme['bg_tertiary'],
                    text_color=self.current_theme['text_secondary'],
                    border_width=1,
                    border_color=self.current_theme['border']
                )
        
    def create_main_content(self):
        """Create main content area with custom tab content"""
        # Create main content container with less bottom padding
        self.content_container = ctk.CTkFrame(self.main_container, fg_color='transparent')
        self.content_container.grid(row=1, column=0, sticky='nsew', pady=(0, 5))
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        
        # Create individual content frames
        self.create_timer_content()
        self.create_stats_content()
        self.create_settings_content()
        
        # Show timer content by default
        self.timer_content.grid(row=0, column=0, sticky='nsew', padx=20, pady=10)
        
    def create_timer_content(self):
        """Create content for the Timer tab"""
        # Create timer content frame
        self.timer_content = ctk.CTkFrame(self.content_container, fg_color='transparent')
        self.timer_content.grid_columnconfigure(1, weight=1)
        self.timer_content.grid_rowconfigure(0, weight=1)
        
        # Create timer and tasks panels within the timer content
        self.create_timer_panel()
        self.create_tasks_panel()
        
    def create_stats_content(self):
        """Create content for the Stats tab"""
        # Create stats content frame
        self.stats_content = ctk.CTkFrame(self.content_container, fg_color='transparent')
        self.stats_content.grid_columnconfigure(0, weight=1)
        self.stats_content.grid_rowconfigure(0, weight=1)
        
        # Placeholder content for stats tab
        stats_frame = ctk.CTkFrame(
            self.stats_content,
            fg_color=self.current_theme['bg_secondary'],
            corner_radius=16,
            border_width=1,
            border_color=self.current_theme['border']
        )
        stats_frame.grid(row=0, column=0, sticky='nsew')
        
        # Coming soon message
        coming_soon_label = ctk.CTkLabel(
            stats_frame,
            text="📊 Focus Analytics & Timeline\n\nComing Soon!\n\nThis tab will show:\n• Focus session history\n• Productivity metrics\n• Distraction patterns\n• Daily/weekly statistics",
            font=ctk.CTkFont(size=16),
            text_color=self.current_theme['text_primary'],
            justify='center'
        )
        coming_soon_label.pack(expand=True, pady=50)
        
    def create_settings_content(self):
        """Create content for the Settings tab"""
        # Create settings content frame
        self.settings_content = ctk.CTkFrame(self.content_container, fg_color='transparent')
        self.settings_content.grid_columnconfigure(0, weight=1)
        self.settings_content.grid_rowconfigure(0, weight=1)
        
        # Create scrollable settings frame
        settings_scroll = ctk.CTkScrollableFrame(
            self.settings_content,
            fg_color=self.current_theme['bg_secondary'],
            corner_radius=16,
            border_width=1,
            border_color=self.current_theme['border']
        )
        settings_scroll.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        settings_scroll.grid_columnconfigure(0, weight=1)
        
        # Settings header
        header_frame = ctk.CTkFrame(settings_scroll, fg_color='transparent')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(20, 30))
        
        settings_title = ctk.CTkLabel(
            header_frame,
            text="⚙️ Settings & Configuration",
            font=ctk.CTkFont(size=28, weight='bold'),
            text_color=self.current_theme['text_primary']
        )
        settings_title.pack()
        
        # Initialize settings if not exists
        if not hasattr(self, 'settings'):
            self.initialize_settings()
        
        # Create settings sections
        self.create_timer_settings_section(settings_scroll)
        self.create_ai_settings_section(settings_scroll)
        self.create_accountability_settings_section(settings_scroll)
        self.create_appearance_settings_section(settings_scroll)
        
        # Save button
        save_frame = ctk.CTkFrame(settings_scroll, fg_color='transparent')
        save_frame.grid(row=5, column=0, sticky='ew', pady=(30, 20))
        
        save_btn = ctk.CTkButton(
            save_frame,
            text="💾 Save Settings",
            width=200,
            height=50,
            font=ctk.CTkFont(size=16, weight='bold'),
            fg_color=self.current_theme['primary'],
            hover_color=self.current_theme['primary_hover'],
            corner_radius=15,
            command=self.save_settings
        )
        save_btn.pack(pady=10)
    
    def initialize_settings(self):
        """Initialize default settings"""
        self.settings = {
            'timer': {
                'work_minutes': 25,
                'short_break_minutes': 5,
                'long_break_minutes': 15
            },
            'ai': {
                'checkin_interval_seconds': 30
            },
            'accountability': {
                'mode': 'casual'  # casual, active, strict
            },
            'appearance': {
                'dark_mode': False
            }
        }
        
    def create_timer_settings_section(self, parent):
        """Create timer settings section"""
        section_frame = ctk.CTkFrame(parent, fg_color=self.current_theme['card_bg'], corner_radius=12)
        section_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20), padx=20)
        section_frame.grid_columnconfigure(1, weight=1)
        
        # Section header
        header_label = ctk.CTkLabel(
            section_frame,
            text="🍅 Timer Settings",
            font=ctk.CTkFont(size=20, weight='bold'),
            text_color=self.current_theme['text_primary']
        )
        header_label.grid(row=0, column=0, columnspan=2, sticky='w', padx=20, pady=(20, 15))
        
        # Work duration
        work_label = ctk.CTkLabel(
            section_frame,
            text="Work Duration:",
            font=ctk.CTkFont(size=14),
            text_color=self.current_theme['text_secondary']
        )
        work_label.grid(row=1, column=0, sticky='w', padx=20, pady=5)
        
        work_frame = ctk.CTkFrame(section_frame, fg_color='transparent')
        work_frame.grid(row=1, column=1, sticky='ew', padx=20, pady=5)
        
        self.work_minutes_slider = ctk.CTkSlider(
            work_frame,
            from_=15,
            to=60,
            number_of_steps=45,
            width=200,
            command=self.update_work_minutes_label
        )
        self.work_minutes_slider.set(self.settings['timer']['work_minutes'])
        self.work_minutes_slider.pack(side='left', padx=(0, 10))
        
        self.work_minutes_label = ctk.CTkLabel(
            work_frame,
            text=f"{self.settings['timer']['work_minutes']} min",
            font=ctk.CTkFont(size=12),
            text_color=self.current_theme['text_primary'],
            width=60
        )
        self.work_minutes_label.pack(side='left')
        
        # Short break duration
        short_break_label = ctk.CTkLabel(
            section_frame,
            text="Short Break:",
            font=ctk.CTkFont(size=14),
            text_color=self.current_theme['text_secondary']
        )
        short_break_label.grid(row=2, column=0, sticky='w', padx=20, pady=5)
        
        short_break_frame = ctk.CTkFrame(section_frame, fg_color='transparent')
        short_break_frame.grid(row=2, column=1, sticky='ew', padx=20, pady=5)
        
        self.short_break_slider = ctk.CTkSlider(
            short_break_frame,
            from_=3,
            to=15,
            number_of_steps=12,
            width=200,
            command=self.update_short_break_label
        )
        self.short_break_slider.set(self.settings['timer']['short_break_minutes'])
        self.short_break_slider.pack(side='left', padx=(0, 10))
        
        self.short_break_label = ctk.CTkLabel(
            short_break_frame,
            text=f"{self.settings['timer']['short_break_minutes']} min",
            font=ctk.CTkFont(size=12),
            text_color=self.current_theme['text_primary'],
            width=60
        )
        self.short_break_label.pack(side='left')
        
        # Long break duration
        long_break_label = ctk.CTkLabel(
            section_frame,
            text="Long Break:",
            font=ctk.CTkFont(size=14),
            text_color=self.current_theme['text_secondary']
        )
        long_break_label.grid(row=3, column=0, sticky='w', padx=20, pady=(5, 20))
        
        long_break_frame = ctk.CTkFrame(section_frame, fg_color='transparent')
        long_break_frame.grid(row=3, column=1, sticky='ew', padx=20, pady=(5, 20))
        
        self.long_break_slider = ctk.CTkSlider(
            long_break_frame,
            from_=10,
            to=30,
            number_of_steps=20,
            width=200,
            command=self.update_long_break_label
        )
        self.long_break_slider.set(self.settings['timer']['long_break_minutes'])
        self.long_break_slider.pack(side='left', padx=(0, 10))
        
        self.long_break_label = ctk.CTkLabel(
            long_break_frame,
            text=f"{self.settings['timer']['long_break_minutes']} min",
            font=ctk.CTkFont(size=12),
            text_color=self.current_theme['text_primary'],
            width=60
        )
        self.long_break_label.pack(side='left')
        
    def create_ai_settings_section(self, parent):
        """Create AI settings section"""
        section_frame = ctk.CTkFrame(parent, fg_color=self.current_theme['card_bg'], corner_radius=12)
        section_frame.grid(row=2, column=0, sticky='ew', pady=(0, 20), padx=20)
        section_frame.grid_columnconfigure(1, weight=1)
        
        # Section header
        header_label = ctk.CTkLabel(
            section_frame,
            text="🤖 AI Monitoring Settings",
            font=ctk.CTkFont(size=20, weight='bold'),
            text_color=self.current_theme['text_primary']
        )
        header_label.grid(row=0, column=0, columnspan=2, sticky='w', padx=20, pady=(20, 15))
        
        # Check-in interval
        checkin_label = ctk.CTkLabel(
            section_frame,
            text="Check-in Interval:",
            font=ctk.CTkFont(size=14),
            text_color=self.current_theme['text_secondary']
        )
        checkin_label.grid(row=1, column=0, sticky='w', padx=20, pady=(5, 20))
        
        checkin_frame = ctk.CTkFrame(section_frame, fg_color='transparent')
        checkin_frame.grid(row=1, column=1, sticky='ew', padx=20, pady=(5, 20))
        
        self.checkin_slider = ctk.CTkSlider(
            checkin_frame,
            from_=30,
            to=300,
            number_of_steps=54,
            width=200,
            command=self.update_checkin_label
        )
        self.checkin_slider.set(self.settings['ai']['checkin_interval_seconds'])
        self.checkin_slider.pack(side='left', padx=(0, 10))
        
        self.checkin_label = ctk.CTkLabel(
            checkin_frame,
            text=f"{self.settings['ai']['checkin_interval_seconds']}s",
            font=ctk.CTkFont(size=12),
            text_color=self.current_theme['text_primary'],
            width=60
        )
        self.checkin_label.pack(side='left')
        
    def create_accountability_settings_section(self, parent):
        """Create accountability settings section"""
        section_frame = ctk.CTkFrame(parent, fg_color=self.current_theme['card_bg'], corner_radius=12)
        section_frame.grid(row=3, column=0, sticky='ew', pady=(0, 20), padx=20)
        section_frame.grid_columnconfigure(1, weight=1)
        
        # Section header with tooltip
        header_frame = ctk.CTkFrame(section_frame, fg_color='transparent')
        header_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=20, pady=(20, 15))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="⚖️ Accountability Mode",
            font=ctk.CTkFont(size=20, weight='bold'),
            text_color=self.current_theme['text_primary']
        )
        header_label.pack(side='left')
        
        # Tooltip button
        tooltip_btn = ctk.CTkButton(
            header_frame,
            text="?",
            width=25,
            height=25,
            font=ctk.CTkFont(size=12, weight='bold'),
            fg_color=self.current_theme['accent'],
            hover_color=self.current_theme['accent_hover'],
            corner_radius=12,
            command=self.show_accountability_tooltip
        )
        tooltip_btn.pack(side='left', padx=(10, 0))
        
        # Mode selection
        mode_label = ctk.CTkLabel(
            section_frame,
            text="Mode:",
            font=ctk.CTkFont(size=14),
            text_color=self.current_theme['text_secondary']
        )
        mode_label.grid(row=1, column=0, sticky='w', padx=20, pady=(5, 20))
        
        mode_frame = ctk.CTkFrame(section_frame, fg_color='transparent')
        mode_frame.grid(row=1, column=1, sticky='ew', padx=20, pady=(5, 20))
        
        self.accountability_mode = ctk.CTkOptionMenu(
            mode_frame,
            values=["casual", "active", "strict"],
            width=200,
            font=ctk.CTkFont(size=14),
            fg_color=self.current_theme['bg_tertiary'],
            button_color=self.current_theme['primary'],
            button_hover_color=self.current_theme['primary_hover'],
            text_color=self.current_theme['text_primary']
        )
        self.accountability_mode.set(self.settings['accountability']['mode'])
        self.accountability_mode.pack(side='left')
        
    def create_appearance_settings_section(self, parent):
        """Create appearance settings section"""
        section_frame = ctk.CTkFrame(parent, fg_color=self.current_theme['card_bg'], corner_radius=12)
        section_frame.grid(row=4, column=0, sticky='ew', pady=(0, 20), padx=20)
        section_frame.grid_columnconfigure(1, weight=1)
        
        # Section header
        header_label = ctk.CTkLabel(
            section_frame,
            text="🎨 Appearance",
            font=ctk.CTkFont(size=20, weight='bold'),
            text_color=self.current_theme['text_primary']
        )
        header_label.grid(row=0, column=0, columnspan=2, sticky='w', padx=20, pady=(20, 15))
        
        # Dark mode toggle
        dark_mode_label = ctk.CTkLabel(
            section_frame,
            text="Dark Mode:",
            font=ctk.CTkFont(size=14),
            text_color=self.current_theme['text_secondary']
        )
        dark_mode_label.grid(row=1, column=0, sticky='w', padx=20, pady=(5, 20))
        
        dark_mode_frame = ctk.CTkFrame(section_frame, fg_color='transparent')
        dark_mode_frame.grid(row=1, column=1, sticky='ew', padx=20, pady=(5, 20))
        
        self.settings_dark_mode_var = ctk.BooleanVar(value=self.settings['appearance']['dark_mode'])
        self.settings_dark_mode_toggle = ctk.CTkSwitch(
            dark_mode_frame,
            text="Enable Dark Mode",
            variable=self.settings_dark_mode_var,
            font=ctk.CTkFont(size=12),
            text_color=self.current_theme['text_secondary']
        )
        self.settings_dark_mode_toggle.pack(side='left')
        
    def update_work_minutes_label(self, value):
        """Update work minutes label"""
        minutes = int(value)
        self.work_minutes_label.configure(text=f"{minutes} min")
        
    def update_short_break_label(self, value):
        """Update short break label"""
        minutes = int(value)
        self.short_break_label.configure(text=f"{minutes} min")
        
    def update_long_break_label(self, value):
        """Update long break label"""
        minutes = int(value)
        self.long_break_label.configure(text=f"{minutes} min")
        
    def update_checkin_label(self, value):
        """Update checkin interval label"""
        seconds = int(value)
        self.checkin_label.configure(text=f"{seconds}s")
        
    def show_accountability_tooltip(self):
        """Show accountability mode tooltip"""
        tooltip_text = (
            "Accountability Mode Explanations:\n\n"
            "🟢 Casual: Just reports focus/distraction data to you\n\n"
            "🟡 Active: Reduces break time based on distraction time\n\n"
            "🔴 Strict: Advanced penalties and interventions\n"
            "    (Future implementation)"
        )
        
        # Create tooltip window
        tooltip = ctk.CTkToplevel(self.root)
        tooltip.title("Accountability Mode Help")
        tooltip.geometry("450x250")
        tooltip.resizable(False, False)
        tooltip.configure(fg_color=self.current_theme['bg_primary'])
        
        # Center tooltip
        tooltip.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.root.winfo_screenheight() // 2) - (250 // 2)
        tooltip.geometry(f"450x250+{x}+{y}")
        
        # Content
        content_frame = ctk.CTkFrame(tooltip, fg_color='transparent')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tooltip_label = ctk.CTkLabel(
            content_frame,
            text=tooltip_text,
            font=ctk.CTkFont(size=14),
            text_color=self.current_theme['text_primary'],
            justify='left'
        )
        tooltip_label.pack(pady=(0, 20))
        
        close_btn = ctk.CTkButton(
            content_frame,
            text="Got it!",
            width=100,
            height=35,
            font=ctk.CTkFont(size=12, weight='bold'),
            fg_color=self.current_theme['primary'],
            hover_color=self.current_theme['primary_hover'],
            command=tooltip.destroy
        )
        close_btn.pack()
        
    def save_settings(self):
        """Save all settings"""
        # Update settings dictionary
        self.settings['timer']['work_minutes'] = int(self.work_minutes_slider.get())
        self.settings['timer']['short_break_minutes'] = int(self.short_break_slider.get())
        self.settings['timer']['long_break_minutes'] = int(self.long_break_slider.get())
        self.settings['ai']['checkin_interval_seconds'] = int(self.checkin_slider.get())
        self.settings['accountability']['mode'] = self.accountability_mode.get()
        self.settings['appearance']['dark_mode'] = self.settings_dark_mode_var.get()
        
        # Apply dark mode change if needed
        if self.settings['appearance']['dark_mode'] != self.is_dark_mode:
            self.is_dark_mode = self.settings['appearance']['dark_mode']
            self.current_theme = Theme.DARK if self.is_dark_mode else Theme.LIGHT
            ctk.set_appearance_mode("dark" if self.is_dark_mode else "light")
            self._apply_theme_seamlessly()
        
        # Save to file (optional - for persistence)
        self.save_settings_to_file()
        
        # Show confirmation
        self.update_status("Settings saved successfully!")
        
    def save_settings_to_file(self):
        """Save settings to JSON file"""
        try:
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def load_settings_from_file(self):
        """Load settings from JSON file"""
        try:
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to handle missing keys
                    self.initialize_settings()
                    for category, values in loaded_settings.items():
                        if category in self.settings:
                            self.settings[category].update(values)
                    return True
        except Exception as e:
            print(f"Error loading settings: {e}")
        return False
        
    def create_timer_panel(self):
        """Create timer panel"""
        self.timer_panel = ctk.CTkFrame(
            self.timer_content,
            fg_color=self.current_theme['bg_secondary'],
            corner_radius=16,
            border_width=1,
            border_color=self.current_theme['border']
        )
        self.timer_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        self.timer_panel.grid_columnconfigure(0, weight=1)
        
        # Timer content
        timer_content = ctk.CTkFrame(self.timer_panel, fg_color='transparent')
        timer_content.grid(row=0, column=0, sticky='nsew', padx=30, pady=30)
        timer_content.grid_columnconfigure(0, weight=1)
        
        # Current task display with fixed height buffer
        self.current_task_frame = ctk.CTkFrame(timer_content, fg_color='transparent', height=80)
        self.current_task_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        self.current_task_frame.grid_propagate(False)  # Prevent frame from shrinking
        
        self.current_task_title = ctk.CTkLabel(
            self.current_task_frame,
            text="Current Task",
            font=ctk.CTkFont(size=14, weight='bold'),
            text_color=self.current_theme['text_muted']
        )
        self.current_task_title.pack()
        
        self.current_task_label = ctk.CTkLabel(
            self.current_task_frame,
            text="Select a task to begin",
            font=ctk.CTkFont(size=16, weight='bold'),
            text_color=self.current_theme['text_primary'],
            wraplength=280,
            height=40  # Fixed height to prevent vertical expansion
        )
        self.current_task_label.pack(pady=(5, 0))
        
        # Timer display
        self.timer_display_frame = ctk.CTkFrame(
            timer_content,
            fg_color=self.current_theme['primary'],
            corner_radius=20,
            border_width=0,
            border_color=self.current_theme['primary']
        )
        self.timer_display_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        
        # Get initial timer display from settings
        initial_minutes = self.settings['timer']['work_minutes']
        initial_time = f"{initial_minutes}:00"
        
        self.timer_label = ctk.CTkLabel(
            self.timer_display_frame,
            text=initial_time,
            font=ctk.CTkFont(size=64, weight='bold'),
            text_color="white"
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
                text_color=self.current_theme['text_secondary'],
                width=100,  # Fixed width to prevent expansion when bolding
                command=lambda m=mode: self.on_mode_button_clicked(m)
            )
            mode_btn.pack(side='left', padx=10)
            self.mode_buttons[mode] = mode_btn
        
        # Timer controls
        controls_frame = ctk.CTkFrame(timer_content, fg_color='transparent')
        controls_frame.grid(row=3, column=0, sticky='ew')
        
        # Center the buttons by using a wrapper frame
        button_container = ctk.CTkFrame(controls_frame, fg_color='transparent')
        button_container.pack(expand=True)
        
        self.start_pause_btn = ctk.CTkButton(
            button_container,
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
            button_container,
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
            button_container,
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
            self.timer_content,
            fg_color=self.current_theme['bg_secondary'],
            corner_radius=16,
            border_width=1,
            border_color=self.current_theme['border']
        )
        self.tasks_panel.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
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
            height=300,  # Set minimum height to ensure scrolling works
            scrollbar_fg_color='transparent',  # Make scrollbar transparent
            scrollbar_button_color=self.current_theme['text_muted'],
            scrollbar_button_hover_color=self.current_theme['primary']
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
        
        self.empty_text = ctk.CTkLabel(
            self.empty_state_frame,
            text="No tasks yet\nAdd your first task to get started!",
            font=ctk.CTkFont(size=14),
            text_color=self.current_theme['text_muted'],
            justify='center'
        )
        self.empty_text.pack(pady=(10, 0))
        
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
        # Row 2 for tabs, so status bar is row 3 - reduce padding
        status_frame = ctk.CTkFrame(self.main_container, fg_color='transparent')
        status_frame.grid(row=2, column=0, sticky='ew', pady=(5, 0))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready to start - Terminal output will run in background",
            font=ctk.CTkFont(size=11),
            text_color=self.current_theme['text_muted']
        )
        self.status_label.pack()
        
    # Dark mode toggle moved to settings tab - handled by save_settings method
        
    def _apply_theme_seamlessly(self):
        """Apply theme changes seamlessly with window hiding for instant transition"""
        # Hide window during theme transition to prevent flickering
        self.root.withdraw()
        
        try:
            # Batch all theme updates together
            self._apply_theme_immediate()
            
            # Force all updates to be processed immediately
            self.root.update_idletasks()
            
            # Small delay to ensure all changes are rendered
            self.root.after(1, self._show_window_after_theme_change)
            
        except Exception as e:
            print(f"Theme transition error: {e}")
            # Ensure window is shown even if there's an error
            self.root.deiconify()
    
    def _show_window_after_theme_change(self):
        """Show window after theme change is complete"""
        self.root.deiconify()
        # Ensure window is brought to front
        self.root.lift()
        self.root.focus_force()
        
    # Demo mode removed - no longer needed
            
    def apply_theme(self):
        """Schedule theme application"""
        self.schedule_update('theme')
    
    def _apply_theme_immediate(self):
        """Apply current theme to all widgets immediately with optimized updates"""
        # Disable updates during theme change to prevent partial rendering
        self.root.configure(cursor="watch")  # Show loading cursor
        
        # Update root window
        self.root.configure(fg_color=self.current_theme['bg_primary'])
        
        # Update main container
        self.main_container.configure(fg_color='transparent')
        
        # Update header container
        if hasattr(self, 'header_container'):
            # Find and update the header container
            for child in self.main_container.winfo_children():
                if isinstance(child, ctk.CTkFrame) and child.winfo_height() > 100:  # Likely the header
                    child.configure(
                        fg_color=self.current_theme['bg_secondary'],
                        border_color=self.current_theme['border']
                    )
                    break
        
        # Update header elements
        if hasattr(self, 'title_label'):
            self.title_label.configure(text_color=self.current_theme['primary'])
        # Dark mode toggle moved to settings tab
        
        # Update navigation tabs and settings button
        if hasattr(self, 'nav_buttons'):
            self.update_tab_buttons()
        
        # Update settings button theme
        if hasattr(self, 'settings_button'):
            if self.current_tab == "Settings":
                self.settings_button.configure(
                    fg_color=self.current_theme['primary'],
                    hover_color=self.current_theme['primary_hover'],
                    text_color="white"
                )
            else:
                self.settings_button.configure(
                    fg_color='transparent',
                    hover_color=self.current_theme['bg_tertiary'],
                    text_color=self.current_theme['text_secondary'],
                    border_color=self.current_theme['border']
                )
        
        # Update timer panel
        self.timer_panel.configure(
            fg_color=self.current_theme['bg_secondary'],
            border_color=self.current_theme['border']
        )
        
        # Update tasks panel
        self.tasks_panel.configure(
            fg_color=self.current_theme['bg_secondary'],
            border_color=self.current_theme['border']
        )
        
        # Update tasks header
        for widget in self.tasks_panel.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        child.configure(text_color=self.current_theme['text_primary'])
                    elif isinstance(child, ctk.CTkButton):
                        child.configure(
                            fg_color=self.current_theme['secondary'],
                            hover_color=self.current_theme['secondary_hover']
                        )
        
        # Update tasks scroll frame background and scrollbar colors to prevent dark blocks
        self.tasks_scroll_frame.configure(
            fg_color='transparent',
            scrollbar_button_color=self.current_theme['text_muted'],
            scrollbar_button_hover_color=self.current_theme['primary']
        )
        
        # Update timer display - don't force primary color here, let state colors handle it
        # self.timer_display_frame colors will be set by _update_timer_colors_immediate()
        
        # Update timer label
        self.timer_label.configure(text_color="white")
        
        # Update text labels in current task display
        if hasattr(self, 'current_task_title'):
            self.current_task_title.configure(text_color=self.current_theme['text_muted'])
        
        if hasattr(self, 'current_task_label'):
            self.current_task_label.configure(text_color=self.current_theme['text_primary'])
        
        # Update buttons
        self.start_pause_btn.configure(
            fg_color=self.current_theme['primary'],
            hover_color=self.current_theme['primary_hover']
        )
        
        # Update mode buttons with proper colors for visibility
        for mode_name, mode_btn in self.mode_buttons.items():
            mode_btn.configure(
                text_color=self.current_theme['text_primary'],
                hover_color=self.current_theme['bg_tertiary']
            )
        
        # Update status bar
        if hasattr(self, 'status_label'):
            self.status_label.configure(text_color=self.current_theme['text_muted'])
        
        # Update empty state text if it exists
        if hasattr(self, 'empty_text'):
            self.empty_text.configure(text_color=self.current_theme['text_muted'])
        
        # Efficiently update task cards without full recreation
        self._update_task_cards_theme()
        
        # Update timer colors if there's a current state
        if hasattr(self, 'current_timer_state') and self.current_timer_state is not None:
            self._update_timer_colors_immediate()
        else:
            # If no current state, default to primary colors
            self.timer_display_frame.configure(
                fg_color=self.current_theme['primary'],
                border_color=self.current_theme['primary']
            )
        
        # Restore normal cursor
        self.root.configure(cursor="")
    
    def _update_task_cards_theme(self):
        """Efficiently update task card themes without full recreation"""
        for task_card in self.task_cards:
            # Update task card theme
            task_card.theme = self.current_theme
            
            # Update card container colors with proper border highlighting
            task_index = self.task_cards.index(task_card)
            is_current = (task_index == self.current_task_index)
            
            # Force complete color update - first destroy and recreate for theme change
            task_card.destroy()
            
        # Completely recreate all task cards with new theme
        self.task_cards.clear()
        self._recreate_task_cards()
        
    def load_sample_tasks(self):
        """Load sample tasks for demonstration"""
        sample_tasks = [
            {
                'title': 'Complete Project Proposal',
                'description': 'Draft and finalize the Q4 project proposal with budget estimates',
                'estimated_pomodoros': 4,
                'completed_pomodoros': 0
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
                'completed_pomodoros': 0
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
            self.empty_state_frame = ctk.CTkFrame(self.tasks_scroll_frame, fg_color='transparent')
            self.empty_state_frame.pack(fill='x', pady=50)
            
            empty_icon = ctk.CTkLabel(
                self.empty_state_frame,
                text="📋",
                font=ctk.CTkFont(size=48)
            )
            empty_icon.pack()
            
            self.empty_text = ctk.CTkLabel(
                self.empty_state_frame,
                text="No tasks yet\nAdd your first task to get started!",
                font=ctk.CTkFont(size=14),
                text_color=self.current_theme['text_muted'],
                justify='center'
            )
            self.empty_text.pack(pady=(10, 0))
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
        
        # Update the task card's visual elements (progress, status, etc.)
        task_card.update_progress_only()
        
        # Update highlight for current task
        if index == self.current_task_index:
            task_card.configure(border_width=2, border_color=self.current_theme['primary'])
        else:
            task_card.configure(border_width=1, border_color=self.current_theme['border'])
        
        # Efficiently update only progress-related widgets when possible
        # Falls back to full recreation if needed
        task_card.update_progress_only()
                
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
            
            # If timer is running, update the timer's task list
            if self.timer and self.is_timer_running:
                # Update the timer's task list with the new task
                with self.timer._lock:
                    self.timer._tasks = self.tasks.copy()
                self.update_status(f"Added task '{task.title}' to active timer session")
            else:
                self.update_status(f"Added task '{task.title}'")
            
            self.schedule_update('tasks')
            
    def edit_task(self, task: Task):
        """Edit existing task"""
        dialog = TaskDialog(
            self.root, 
            self.current_theme, 
            "Edit Task",
            task.title,
            task.description or "",  # Fix: Handle None description
            task.estimated_pomodoros
        )
        if dialog.result:
            task.title = dialog.result['title']
            task.description = dialog.result['description']
            task.estimated_pomodoros = dialog.result['estimated_pomodoros']
            
            # If timer is running, update the timer's task list
            if self.timer and self.is_timer_running:
                # Update the timer's task list with the edited task
                with self.timer._lock:
                    self.timer._tasks = self.tasks.copy()
                self.update_status(f"Updated task '{task.title}' in active timer session")
            else:
                self.update_status(f"Updated task '{task.title}'")
            
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
                
                # If timer is running, update the timer's task list
                if self.timer and self.is_timer_running:
                    # Update the timer's task list with the updated tasks
                    with self.timer._lock:
                        self.timer._tasks = self.tasks.copy()
                        # Update the timer's current task index if needed
                        if self.timer._current_task_idx >= len(self.tasks):
                            self.timer._current_task_idx = max(0, len(self.tasks) - 1)
                        elif self.timer._current_task_idx != self.current_task_index:
                            self.timer._current_task_idx = self.current_task_index
                    
                # If all tasks deleted, reset and stop timer
                if not self.tasks:
                    self.current_task_index = 0
                    # Stop the timer if it's running since there are no tasks
                    if self.timer and self.is_timer_running:
                        self.stop_timer()
                    
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
        """Update the current task display immediately with proper text truncation"""
        if 0 <= self.current_task_index < len(self.tasks):
            task = self.tasks[self.current_task_index]
            task_text = f"{task.title} ({task.completed_pomodoros}/{task.estimated_pomodoros} 🍅)"
            
            # Truncate long task titles to prevent layout issues
            max_length = 50  # Adjust based on your font size and container width
            if len(task_text) > max_length:
                task_text = task_text[:max_length-3] + "..."
            
            self.current_task_label.configure(text=task_text)
        else:
            self.current_task_label.configure(text="Select a task to begin")
            
    def setup_timer(self):
        """Setup timer with current tasks"""
        if not self.tasks:
            return
            
        # Use settings for timer durations
        work_time = self.settings['timer']['work_minutes'] * 60
        short_break = self.settings['timer']['short_break_minutes'] * 60
        long_break = self.settings['timer']['long_break_minutes'] * 60
            
        # Create timer with a copy of current tasks
        self.timer = PomodoroTimer(
            work_seconds=work_time,
            short_break_seconds=short_break,
            long_break_seconds=long_break,
            tasks=self.tasks.copy()  # Use a copy to avoid reference issues
        )
        
        # Sync timer's current task index with GUI's selection
        if hasattr(self.timer, '_current_task_idx'):
            self.timer._current_task_idx = self.current_task_index
        
        # Create terminal output
        self.terminal_output = TerminalOutput(debug=True)
        
        # Add callbacks
        self.timer.add_state_callback(self.on_timer_state_changed)
        
        # Sync initial state from timer
        self.sync_tasks_from_timer()
        
    def toggle_timer(self):
        """Toggle timer start/pause"""
        if not self.tasks:
            messagebox.showwarning("No Tasks", "Please add at least one task before starting the timer.")
            return
            
        # Setup timer if it doesn't exist or if it was cleared after completion
        if not self.timer:
            self.setup_timer()
            
        # Fix: Add null check for timer
        if not self.timer:
            self.update_status("Failed to setup timer")
            return
            
        if not self.is_timer_running:
            # Start timer
            if self.timer.start():
                self.is_timer_running = True
                self.start_pause_btn.configure(text="PAUSE")
                
                # Sync task state from timer (timer updates task status internally)
                self.sync_tasks_from_timer()
                
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
                    
                    # Sync task status when resuming
                    self.sync_tasks_from_timer()
                    
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
            
            # Reset timer display to settings default
            reset_minutes = self.settings['timer']['work_minutes']
            reset_time = f"{reset_minutes}:00"
            self.timer_label.configure(text=reset_time)
            
            # Reset to default work mode colors
            self.current_timer_state = TimerState.WORK
            self.last_active_state = TimerState.WORK
            self.update_mode_buttons_for_state(TimerState.WORK)
            self._update_timer_colors_immediate()
            
            self.update_status("Timer stopped")
            
    def skip_timer(self):
        """Skip current timer interval"""
        if self.timer and self.is_timer_running:
            # Skip the current interval
            self.timer.skip()
            
            # Don't update colors immediately - let the state change callback handle it
            # This prevents the jarring red color flash since we removed SKIPPED state colors
            self.update_status("Timer interval skipped")
            
    def on_mode_button_clicked(self, mode: str):
        """Handle mode button clicks - skip to the selected state"""
        if not self.timer or not self.is_timer_running:
            # If timer isn't running, just update the visual selection
            return
        
        # Map mode names to TimerState values
        mode_to_state = {
            "Work": TimerState.WORK,
            "Short Break": TimerState.SHORT_BREAK,
            "Long Break": TimerState.LONG_BREAK
        }
        
        target_state = mode_to_state.get(mode)
        if not target_state:
            return
            
        # Check if we're already in the target state
        if self.timer.state == target_state:
            return
            
        # Skip to the target state using the same logic as skip button
        # The radio button selection will update naturally when the state changes
        # through the on_timer_state_changed callback with the same delay as timer
        if self.timer.skip_to_state(target_state):
            # Use same status update pattern as skip button
            self.update_status(f"Timer switched to {mode}")
        else:
            self.update_status(f"Failed to switch to {mode}")
            
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
        sync_counter = 0
        
        while self.is_timer_running and self.timer:
            remaining_time = self.timer.get_remaining_time()
            if remaining_time:
                # Update display only if changed
                total_seconds = int(remaining_time.total_seconds())
                minutes, seconds = int(total_seconds // 60), int(total_seconds % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"
                
                if time_str != last_time_str:
                    last_time_str = time_str
                    self.root.after(0, lambda t=time_str: self.timer_label.configure(text=t))
                
                # Update colors only if state changed
                if self.timer and self.timer.state != last_state:
                    last_state = self.timer.state
                    self.root.after(0, lambda s=last_state: self.update_timer_colors(s))
                
                # Periodic sync to ensure GUI stays synchronized with timer
                sync_counter += 1
                if sync_counter >= 10:  # Every 10 seconds
                    sync_counter = 0
                    self.root.after(0, self.sync_tasks_from_timer)
                
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
                

                
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Terminal loop error: {e}")
        finally:
            print("🖥️  Terminal output stopped")
            
    def on_timer_state_changed(self, state: TimerState):
        """Handle timer state changes"""
        state_text = state.value.replace('_', ' ').title()
        self.update_status(f"Timer state: {state_text}")
        
        # Track last active state for radio button highlighting when paused
        if state in [TimerState.WORK, TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
            self.last_active_state = state
        elif state == TimerState.PAUSED:
            # When paused, check if timer has updated _pre_pause_state (from skip_to_state)
            if self.timer and hasattr(self.timer, '_pre_pause_state') and self.timer._pre_pause_state:
                # Update last_active_state to reflect the new paused state
                self.last_active_state = self.timer._pre_pause_state
        
        # Sync tasks from timer on every state change to keep GUI updated
        self.sync_tasks_from_timer()
        
        # Process any pending task updates immediately for timer state changes
        if 'tasks' in self.pending_updates:
            self.process_pending_updates()
        
        # Update colors for new state
        self.update_timer_colors(state)
        
        # Handle work session completion
        if state == TimerState.SHORT_BREAK or state == TimerState.LONG_BREAK:
            self.on_work_session_completed()
        
        if state == TimerState.IDLE:
            # All tasks completed - reset timer but keep it ready for new tasks
            self.is_timer_running = False
            
            # Stop the timer but don't destroy it - we'll recreate it when needed
            if self.timer:
                self.timer.pause()  # Stop the timer
                self.timer = None  # Clear the timer to force recreation on next start
            
            # Reset UI elements
            self.start_pause_btn.configure(text="START")
            
            # Reset timer display to settings default
            reset_minutes = self.settings['timer']['work_minutes']
            reset_time = f"{reset_minutes}:00"
            self.timer_label.configure(text=reset_time)
            
            # Reset to default work mode colors and state
            self.current_timer_state = TimerState.WORK
            self.last_active_state = TimerState.WORK
            self.update_mode_buttons_for_state(TimerState.WORK)
            self._update_timer_colors_immediate()
            
            self.update_status("All tasks completed! Timer reset and ready to start new session 🎉")
        elif state == TimerState.PAUSED:
            # Update button text when paused via timer callback
            if hasattr(self, 'start_pause_btn'):
                self.start_pause_btn.configure(text="RESUME")
        elif state == TimerState.WORK:
            # Update button text when resumed/started
            if hasattr(self, 'start_pause_btn') and self.is_timer_running:
                self.start_pause_btn.configure(text="PAUSE")
                
    def on_work_session_completed(self):
        """Handle completion of a work session (pomodoro) - sync from timer"""
        # The timer handles all task completion logic internally
        # GUI should only sync the updated tasks from timer and update display
        if self.timer:
            # Sync tasks from timer (timer is the source of truth)
            self.sync_tasks_from_timer()
            
            # Update UI to reflect changes
            self.schedule_update('current_task')
            self.schedule_update('tasks')
            
            # Update status with current progress
            if 0 <= self.current_task_index < len(self.tasks):
                current_task = self.tasks[self.current_task_index]
                if current_task.status == TaskStatus.COMPLETED:
                    self.update_status(f"Task '{current_task.title}' completed! 🎉")
                else:
                    self.update_status(f"Pomodoro completed! {current_task.completed_pomodoros}/{current_task.estimated_pomodoros} done")
            else:
                self.update_status("All tasks completed! 🎉")
    
    def sync_tasks_from_timer(self):
        """Sync tasks and current task index from timer (timer is source of truth)"""
        if not self.timer:
            return
            
        # Get updated tasks from timer (this returns a copy)
        updated_timer_tasks = self.timer.tasks
        
        # Force complete sync by updating ALL task properties
        changes_made = False
        for i, timer_task in enumerate(updated_timer_tasks):
            if i < len(self.tasks):
                gui_task = self.tasks[i]
                # Always check and update all properties
                if (gui_task.completed_pomodoros != timer_task.completed_pomodoros or 
                    gui_task.status != timer_task.status):
                    changes_made = True
                    gui_task.completed_pomodoros = timer_task.completed_pomodoros
                    gui_task.status = timer_task.status
                    
        # Sync current task index
        if self.current_task_index != self.timer.current_task_idx:
            changes_made = True
            self.current_task_index = self.timer.current_task_idx
            
        # Always force refresh for timer state changes to ensure display is current
        self._refresh_tasks_immediate()
        self._update_current_task_immediate()
                
    def move_to_next_task(self):
        """Move to the next incomplete task - deprecated, timer handles this internally"""
        # This method is deprecated since timer handles task transitions internally
        # Just sync from timer to get the updated state
        self.sync_tasks_from_timer()
        self.schedule_update('current_task')
        self.schedule_update('tasks')
            
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
                'primary': '#F39C12',  # Orange (same as pause)
                'secondary': '#E67E22',
                'display_bg': '#FEF5E7',
                'border': '#F39C12'
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
        # Fix: Add null check for current_timer_state
        if not hasattr(self, 'current_timer_state') or self.current_timer_state is None:
            return
            
        colors = self.get_state_colors(self.current_timer_state)
        
        # Update timer label color - keep white text
        self.timer_label.configure(text_color="white")
        
        # Update timer frame background and border
        if hasattr(self, 'timer_frame_ref'):
            self.timer_frame_ref.configure(
                fg_color=colors['primary'],
                border_color=colors['border']
            )
        
        # Update start/pause button color
        self.start_pause_btn.configure(
            fg_color=colors['primary'],
            hover_color=colors['secondary']
        )
        
        # Update mode buttons to highlight current state
        self.update_mode_buttons_for_state(self.current_timer_state)
    
    def update_mode_buttons_for_state(self, state: TimerState):
        """Update mode button highlighting based on current timer state"""
        # Fix: Add null check for state
        if state is None:
            return
        
        # Determine which state to highlight on radio buttons
        display_state = state
        use_pause_colors = False
        
        # If paused or skipped, show the last active state but with pause colors
        if state in [TimerState.PAUSED, TimerState.SKIPPED]:
            display_state = self.last_active_state
            use_pause_colors = True
            
        # Get colors for display
        if use_pause_colors:
            colors = self.get_state_colors(TimerState.PAUSED)  # Use pause colors (yellow/orange)
        else:
            colors = self.get_state_colors(display_state)
        
        # Highlight the appropriate mode button based on display state
        mode_mapping = {
            TimerState.WORK: "Work",
            TimerState.SHORT_BREAK: "Short Break", 
            TimerState.LONG_BREAK: "Long Break"
        }
        
        active_mode = mode_mapping.get(display_state)
        
        # Update radio button selection and colors
        if active_mode and hasattr(self, 'mode_buttons'):
            self.mode_var.set(active_mode)
            
            # Update all mode button colors properly for radio buttons
            for mode_name, mode_btn in self.mode_buttons.items():
                if mode_name == active_mode:
                    # Highlight active mode with appropriate color (normal state or pause color)
                    mode_btn.configure(
                        text_color=colors['primary'],
                        font=ctk.CTkFont(size=13, weight='bold'),  # Smaller bold font to prevent expansion
                        fg_color=colors['primary'],  # Set radio button selector color to match state
                        hover_color=colors['secondary']
                    )
                else:
                    # Reset inactive modes to default with proper visibility
                    mode_btn.configure(
                        text_color=self.current_theme['text_muted'],
                        font=ctk.CTkFont(size=14, weight='normal'),
                        fg_color=self.current_theme['text_muted'],  # Default selector color
                        hover_color=self.current_theme['bg_tertiary']
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
        
        # Create dialog window with better sizing
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("550x650")  # Increased height to show buttons
        self.dialog.resizable(False, False)
        self.dialog.configure(fg_color=theme['bg_primary'])
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (parent.winfo_screenwidth() // 2) - (550 // 2)
        y = (parent.winfo_screenheight() // 2) - (650 // 2)
        self.dialog.geometry(f"550x650+{x}+{y}")
        
        # Create form
        self.create_form(task_title, description, estimated_pomodoros)
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
    def create_form(self, task_title: str, description: str, estimated_pomodoros: int):
        """Create task form with improved layout"""
        # Main frame with better padding
        main_frame = ctk.CTkFrame(self.dialog, fg_color='transparent')
        main_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Title with improved styling
        title_label = ctk.CTkLabel(
            main_frame,
            text="Task Details",
            font=ctk.CTkFont(size=24, weight='bold'),
            text_color=self.theme['text_primary']
        )
        title_label.pack(pady=(0, 30))
        
        # Task title section
        title_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_lbl = ctk.CTkLabel(
            title_frame,
            text="Task Title *",
            font=ctk.CTkFont(size=16, weight='bold'),
            text_color=self.theme['text_secondary']
        )
        title_lbl.pack(anchor='w', pady=(0, 8))
        
        self.title_entry = ctk.CTkEntry(
            title_frame,
            placeholder_text="Enter task title...",
            font=ctk.CTkFont(size=14),
            height=45,
            fg_color=self.theme['card_bg'],
            text_color=self.theme['text_primary'],
            placeholder_text_color=self.theme['text_muted']
        )
        self.title_entry.pack(fill='x')
        self.title_entry.insert(0, task_title)
        
        # Description section
        desc_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        desc_frame.pack(fill='x', pady=(0, 20))
        
        desc_lbl = ctk.CTkLabel(
            desc_frame,
            text="Description (optional)",
            font=ctk.CTkFont(size=16, weight='bold'),
            text_color=self.theme['text_secondary']
        )
        desc_lbl.pack(anchor='w', pady=(0, 8))
        
        self.desc_entry = ctk.CTkTextbox(
            desc_frame,
            height=80,
            font=ctk.CTkFont(size=14),
            fg_color=self.theme['card_bg'],
            text_color=self.theme['text_primary']
        )
        self.desc_entry.pack(fill='x')
        self.desc_entry.insert('1.0', description)
        
        # Estimated pomodoros section
        pomodoros_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        pomodoros_frame.pack(fill='x', pady=(0, 40))
        
        pomodoros_lbl = ctk.CTkLabel(
            pomodoros_frame,
            text="Estimated Pomodoros *",
            font=ctk.CTkFont(size=16, weight='bold'),
            text_color=self.theme['text_secondary']
        )
        pomodoros_lbl.pack(anchor='w', pady=(0, 8))
        
        self.pomodoros_entry = ctk.CTkEntry(
            pomodoros_frame,
            placeholder_text="Enter number of pomodoros...",
            font=ctk.CTkFont(size=14),
            height=45,
            width=250,
            fg_color=self.theme['card_bg'],
            text_color=self.theme['text_primary'],
            placeholder_text_color=self.theme['text_muted']
        )
        self.pomodoros_entry.pack(anchor='w')
        self.pomodoros_entry.insert(0, str(estimated_pomodoros))
        
        # Buttons section with better layout and spacing
        buttons_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        buttons_frame.pack(fill='x', pady=(40, 20))
        
        # Save button (primary action) - properly sized
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Save Task",
            width=350,
            height=50,
            font=ctk.CTkFont(size=18, weight='bold'),
            fg_color=self.theme['primary'],
            hover_color=self.theme['primary_hover'],
            text_color='white',
            corner_radius=15,
            command=self.save
        )
        save_btn.pack(pady=(0, 15))
        
        # Cancel button (secondary action) - same size as save button
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ Cancel",
            width=350,
            height=50,
            font=ctk.CTkFont(size=18),
            fg_color=self.theme['bg_tertiary'],
            text_color=self.theme['text_primary'],
            hover_color=self.theme['border'],
            border_width=2,
            border_color=self.theme['border'],
            corner_radius=15,
            command=self.cancel
        )
        cancel_btn.pack()
        
        # Focus on title entry
        self.title_entry.focus()
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda event: self.save())
        self.dialog.bind('<KP_Enter>', lambda event: self.save())
        
    def save(self):
        """Save task with improved validation and error handling"""
        title = self.title_entry.get().strip()
        description = self.desc_entry.get('1.0', 'end-1c').strip()
        
        try:
            estimated_pomodoros = int(self.pomodoros_entry.get().strip())
        except ValueError:
            self.show_error("Invalid Input", "Please enter a valid number for estimated pomodoros.")
            return
            
        if not title:
            self.show_error("Invalid Input", "Please enter a task title.")
            return
            
        if estimated_pomodoros <= 0:
            self.show_error("Invalid Input", "Estimated pomodoros must be greater than 0.")
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
        
    def show_error(self, title: str, message: str):
        """Show error message with proper theming"""
        # Create error dialog with current theme
        error_dialog = ctk.CTkToplevel(self.dialog)
        error_dialog.title(title)
        error_dialog.geometry("400x150")
        error_dialog.configure(fg_color=self.theme['bg_primary'])
        error_dialog.resizable(False, False)
        
        # Make error dialog modal
        error_dialog.transient(self.dialog)
        error_dialog.grab_set()
        
        # Center error dialog
        error_dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (150 // 2)
        error_dialog.geometry(f"400x150+{x}+{y}")
        
        # Error content
        error_frame = ctk.CTkFrame(error_dialog, fg_color='transparent')
        error_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        error_label = ctk.CTkLabel(
            error_frame,
            text=message,
            font=ctk.CTkFont(size=14),
            text_color=self.theme['text_primary'],
            wraplength=350
        )
        error_label.pack(pady=(0, 20))
        
        ok_btn = ctk.CTkButton(
            error_frame,
            text="OK",
            width=100,
            height=35,
            font=ctk.CTkFont(size=14, weight='bold'),
            fg_color=self.theme['primary'],
            hover_color=self.theme['primary_hover'],
            command=error_dialog.destroy
        )
        ok_btn.pack()
        
        # Focus on OK button
        ok_btn.focus()
        
        # Bind Enter key to close
        error_dialog.bind('<Return>', lambda event: error_dialog.destroy())
        error_dialog.bind('<KP_Enter>', lambda event: error_dialog.destroy())

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