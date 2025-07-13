# AI_README.md - Focus Assist Codebase Guide

## 🎯 Project Overview

**Focus Assist** is a modern Pomodoro timer application designed for the **Qualcomm Snapdragon X Elite hackathon** with local AI-powered focus detection capabilities. The project currently has a fully functional Pomodoro timer foundation with plans to integrate AI focus monitoring features.

### 🏆 Hackathon Vision
The core concept is an AI-enhanced productivity timer that helps users maintain focus by:
1. **Screenshot Analysis**: Taking periodic screenshots to perform OCR and use models like OpenAI CLIP to detect if screen content relates to specified tasks
2. **Webcam Monitoring**: Using pose estimation to check if users are looking at their laptop, detect phone usage, or other distractions
3. **Focus Analytics**: Providing detailed stats and logging to show when users got distracted and what they were doing
4. **Local AI Only**: All AI models run locally on Snapdragon X Elite NPU - no internet APIs allowed

### Current State (Phase 1 Complete)
- ✅ **Fully functional** Pomodoro timer with GUI
- ✅ **Task management system** with CRUD operations
- ✅ **Modern UI** with dark/light themes and responsive design
- ✅ **Radio button mode switching** - click Work/Break buttons to instantly switch timer states
- ✅ **Thread-safe architecture** with proper state management
- ✅ **Visual feedback system** with color-coded states and smooth transitions
- ✅ **Terminal output integration** for cross-reference
- 🔄 **AI focus detection** - ready for integration (Phase 2)

### 🎯 Next Goals (Phase 2)
- **Multiple GUI tabs** for settings and timeline stats
- **Settings tab** for configuring AI monitoring intervals, timer durations, and thresholds
- **Timeline/Stats tab** for detailed focus analytics and distraction logging
- **AI integration** with screenshot OCR and webcam pose estimation
- **Focus scoring system** with distraction detection and reporting

## 📁 File Structure & Hierarchy

```
HaQathon/
├── src/
│   ├── focus_assist_gui.py          # 🔥 MAIN GUI APPLICATION (1,707 lines)
│   ├── example.py                   # Simple terminal-based demo
│   └── pomodoro/                    # Core timer backend
│       ├── __init__.py              # Module exports
│       ├── timer.py                 # 🔥 PomodoroTimer class (384 lines)
│       ├── terminal_output.py       # Terminal display system
│       ├── display.py               # Display formatting utilities
│       ├── constants.py             # Configuration constants
│       └── utils.py                 # Utility functions
├── requirements.txt                 # Python dependencies
├── README.md                        # User documentation
└── AI_README.md                     # This file
```

## 🏗️ Architecture Overview

### Core Components

#### 1. **PomodoroTimer** (`src/pomodoro/timer.py`)
- **Purpose**: Thread-safe timer engine with state management
- **Key Features**:
  - Work/break interval management
  - Task progress tracking
  - State callbacks for GUI integration
  - Pause/resume/skip functionality
  - **Radio button integration** - skip to specific states on command

```python
class PomodoroTimer:
    # States: WORK, SHORT_BREAK, LONG_BREAK, PAUSED, SKIPPED, IDLE
    def start() -> bool              # Start/resume timer
    def pause() -> bool              # Pause current interval
    def skip() -> bool               # Skip current interval
    def skip_to_state(state) -> bool # Skip to specific state (NEW)
    def get_remaining_time()         # Get time left in current interval
    def _handle_interval_completion() # Uses target state for proper transitions
```

#### 2. **Task Management** (`src/pomodoro/timer.py`)
```python
class Task(BaseModel):           # Pydantic model for validation
    id: str
    title: str
    description: Optional[str]
    estimated_pomodoros: int     # Target number of pomodoros
    completed_pomodoros: int     # Current progress
    status: TaskStatus           # NOT_STARTED, IN_PROGRESS, COMPLETED, PAUSED
```

#### 3. **FocusAssistApp** (`src/focus_assist_gui.py`)
- **Purpose**: Main GUI application class
- **Key Features**:
  - CustomTkinter-based modern interface
  - Dark/light theme switching
  - Task CRUD operations
  - Real-time timer display
  - Threaded timer integration
  - **Interactive radio buttons** - click to instantly switch timer modes
  - **Visual state feedback** - color-coded states with smooth transitions
  - **Paused state preservation** - maintains pause state when switching modes

### GUI Layout (Based on Screenshot)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🎯 Focus Assist    AI-Powered Productivity Timer    🌙 Dark Mode │
├─────────────────────┬───────────────────────────────────────────┤
│                     │                                           │
│   Current Task      │                Tasks                      │
│ Select a task to    │  ┌─────────────────────────────────────┐  │
│      begin          │  │ Complete Project Proposal • Not St │  │
│                     │  │ Draft and finalize the Q4 project  │  │
│  ┌─────────────────┐ │  │ ████████████████████░░░░░░░ 0/4 🍅  │  │
│  │                 │ │  │                          Edit  🗑️  │  │
│  │     25:00       │ │  └─────────────────────────────────────┘  │
│  │                 │ │  ┌─────────────────────────────────────┐  │
│  └─────────────────┘ │  │ Code Review              • Not St   │  │
│                     │  │ Review pull requests and provide    │  │
│  ◉ Work             │  │ ████████████████████░░░░░░░ 0/2 🍅  │  │
│  ○ Short Break      │  │                          Edit  🗑️  │  │
│  ○ Long Break       │  └─────────────────────────────────────┘  │
│                     │  ┌─────────────────────────────────────┐  │
│  [START] [STOP] [SKIP] │  │ UI/UX Design             • Not St   │  │
│                     │  │ Create wireframes for the new      │  │
│                     │  │ ████████████████████░░░░░░░ 0/3 🍅  │  │
│                     │  │                          Edit  🗑️  │  │
│                     │  └─────────────────────────────────────┘  │
└─────────────────────┴───────────────────────────────────────────┘
```

## 🔄 Key Workflows

### 1. **Timer Operation**
```python
# GUI -> Timer -> GUI sync pattern
app.setup_timer()                    # Create PomodoroTimer instance
app.toggle_timer()                   # Start/pause via GUI
timer.start()                        # Backend timer starts
timer.add_state_callback(callback)   # GUI receives state updates
app.sync_tasks_from_timer()          # Keep task progress in sync

# Radio button mode switching (NEW)
app.on_mode_button_clicked(mode)     # User clicks Work/Break radio button
timer.skip_to_state(target_state)    # Skip to selected state
app.update_mode_buttons_for_state()  # Update visual feedback
```

### 2. **Task Management**
```python
# Task lifecycle in GUI
app.add_task_dialog()                # TaskDialog popup
app.edit_task(task)                  # Modify existing task
app.delete_task(task)                # Remove task with confirmation
app.select_task(index)               # Set current task for timer
```

### 3. **Theme System**
```python
# Seamless theme switching
app.toggle_dark_mode()               # User toggles
app._apply_theme_seamlessly()        # Hide window during transition
app._update_task_cards_theme()       # Update all UI components
```

## 🎨 UI Components

### Custom Widgets
- **TaskCard**: Individual task display with progress bar
- **TaskDialog**: Add/edit task popup with validation
- **Theme**: Light/dark color scheme management

### Layout Structure
- **Header**: Title, subtitle, dark mode toggle
- **Timer Panel** (Left): Current task, timer display, mode selection, controls
- **Tasks Panel** (Right): Scrollable task list with CRUD operations
- **Status Bar**: Current operation status

## 🧵 Threading Architecture

### Thread Safety
- **Timer Thread**: Runs timer loop with 1-second updates
- **GUI Thread**: Main CustomTkinter event loop
- **Terminal Thread**: Background terminal output (optional)

### Synchronization
- **Batched Updates**: `schedule_update()` system prevents UI flooding
- **State Callbacks**: Timer notifies GUI of state changes
- **Task Syncing**: `sync_tasks_from_timer()` keeps data consistent

## 📊 Data Flow

```
User Input → GUI → Timer Backend → State Change → GUI Update
    ↓
Task Management → Task Objects → Timer Integration → Progress Tracking
    ↓
Display Updates → Theme System → Component Refresh → User Feedback
```

## 🚀 Entry Points

### Shell Requirements
⚠️ **Important**: Use **PowerShell** commands, not bash. Use semicolon (`;`) for command chaining instead of `&&`.

### Running the Application
```powershell
# GUI version (main application)
cd src; python focus_assist_gui.py

# Terminal version (simple demo)
cd src; python example.py
```

### Key Classes to Understand
1. **`FocusAssistApp`** - Main GUI controller
2. **`PomodoroTimer`** - Core timer logic
3. **`Task`** - Task data model
4. **`TaskCard`** - GUI task representation
5. **`TerminalOutput`** - Terminal display system

## 🔧 Configuration

### Timer Settings (in `constants.py`)
```python
DEFAULT_WORK_SECONDS = 25 * 60        # 25 minutes
DEFAULT_SHORT_BREAK_SECONDS = 5 * 60   # 5 minutes
DEFAULT_LONG_BREAK_SECONDS = 15 * 60   # 15 minutes
DEFAULT_POMOS_BEFORE_LONG_BREAK = 4    # Long break frequency
```

### GUI Themes (in `focus_assist_gui.py`)
```python
Theme.LIGHT = {
    'bg_primary': '#FFFFFF',
    'primary': '#FF6B6B',
    'text_primary': '#2C3E50',
    # ... more colors
}

Theme.DARK = {
    'bg_primary': '#0D1117',
    'primary': '#FF6B6B', 
    'text_primary': '#F0F6FC',
    # ... more colors
}
```

## 🐛 Common Debug Areas

### 1. **Timer Synchronization Issues**
- Check `sync_tasks_from_timer()` calls
- Verify state callbacks are properly registered
- Look for race conditions in `timer_loop()`

### 2. **Theme Switching Problems**
- Check `_apply_theme_seamlessly()` window hiding
- Verify all UI components update in `_apply_theme_immediate()`
- Look for widget recreation vs. update balance

### 3. **Task Management Bugs**
- Verify task index management during deletion
- Check task status updates from timer
- Look for UI refresh issues in `_refresh_tasks_immediate()`

### 4. **Performance Issues**
- Check `schedule_update()` batching system
- Look for excessive widget recreation
- Verify thread cleanup on app close

## 📝 Notes for Future Development

### 🚀 Development Roadmap

#### Phase 2: Multi-Tab GUI Enhancement
- **Settings Tab**: Configure timer durations, AI monitoring intervals, focus thresholds
- **Timeline/Stats Tab**: Visual analytics showing focus patterns, distraction events, productivity metrics
- **Enhanced task management**: Categories, priority levels, time estimates vs actual
- **Export functionality**: Focus reports, productivity summaries

#### Phase 3: AI Integration (Hackathon Core)
- **Screenshot OCR**: Periodic screen capture with text extraction and task relevance analysis
- **CLIP Model Integration**: Use OpenAI CLIP or Qualcomm-optimized models for screen content understanding
- **Webcam Pose Estimation**: Real-time detection of user attention and distraction indicators
- **Focus Scoring Algorithm**: Combine multiple AI signals into focus quality metrics
- **Distraction Logging**: Detailed timeline of focus breaks with context

#### Phase 4: Advanced Analytics
- **Machine Learning Models**: Local training on user patterns for personalized focus insights
- **Prediction System**: Anticipate focus breaks and suggest optimal break timing
- **Adaptive Timers**: Adjust work/break durations based on individual focus patterns
- **Gamification**: Focus streaks, achievements, and productivity challenges

### Architecture Ready for Enhancement
- **Callback System**: Timer state callbacks ready for AI event triggers
- **Thread-Safe Design**: Ready for parallel AI processing threads
- **State Management**: Comprehensive state tracking for AI analysis
- **Visual Feedback**: Color-coded system expandable for AI alerts
- **Data Persistence**: Task system ready for focus metrics storage

### Testing Strategy
- Use `example.py` for basic timer functionality
- Test GUI with sample tasks (already loaded)
- Theme switching should be seamless
- Timer state transitions should be smooth
- **Radio button testing**: Click mode buttons during different timer states
- **Pause state preservation**: Verify paused state maintained when switching modes

## 🎯 Current Development Status

**Phase 1 Complete** ✅
- Core Pomodoro timer functionality with full GUI
- Task management system with CRUD operations
- Interactive radio buttons for instant mode switching
- Visual state feedback and theme system
- Thread-safe architecture with proper state management

**Phase 2 Major Progress** ✅
- **Multi-tab GUI Implementation**: Complete Settings and Stats tabs with navigation
- **AI Monitoring System**: Timer snapshot intervals with configurable check-in frequency
- **Comprehensive Settings Management**: Timer durations, AI settings, accountability modes, appearance
- **Settings Persistence**: JSON-based save/load system for user preferences
- **Theme System Overhaul**: Seamless dark/light mode transitions with comprehensive widget updates
- **Progress Bar Enhancements**: Improved visual contrast and "slot" visibility in dark mode
- **UI Polish**: Better spacing, tooltips, validation, and user feedback
- **Theme Transition Issues RESOLVED**: Fixed settings widget background and text color updates ✅

**Current Issues Resolved** ✅
- ~~Settings Widget Color Bug~~: **FIXED** - Settings widgets now correctly update colors during theme transitions
- ~~Settings Background Bug~~: **FIXED** - Settings tab backgrounds now properly switch between light/dark themes  
- ~~Settings Text Color Bug~~: **FIXED** - All text labels in settings now update theme colors correctly
- **Theme System Reliability**: **COMPLETE** - Dark/light mode switching works seamlessly across all tabs

**Next Priority: Stats Tab Implementation** 🎯
- **Timeline/Stats Tab**: Design and implement detailed focus analytics and distraction logging
- **Focus Session History**: Display past pomodoro sessions with completion data
- **Productivity Metrics**: Show daily/weekly statistics and focus patterns
- **Visual Analytics**: Charts and graphs for focus trends and productivity insights
- **Export Functionality**: Allow users to export focus reports and productivity summaries

**Hackathon Goal: Phase 3** 🎯
- Local AI integration with screenshot OCR and webcam monitoring
- Focus detection and distraction logging
- Real-time productivity insights

## 🆕 Recent Implementation Details

### Theme System - FULLY RESOLVED ✅
```python
# Complete theme switching implementation with all issues fixed
def _update_settings_tab_theme(self, error_list: list):
    # Direct frame updates using stored references - FIXED
    settings_frames = [
        ('timer_settings_frame', 'Timer Settings Frame'),
        ('ai_settings_frame', 'AI Settings Frame'),
        ('accountability_settings_frame', 'Accountability Settings Frame'),
        ('appearance_settings_frame', 'Appearance Settings Frame')
    ]
    
    # Background colors - FIXED
    for frame_attr, frame_name in settings_frames:
        frame = getattr(self, frame_attr)
        self._safe_widget_update(frame, frame_name, {
            'fg_color': self.current_theme['card_bg']
        }, error_list)
        
        # Text colors - FIXED
        for child in frame.winfo_children():
            if isinstance(child, ctk.CTkLabel):
                child.configure(text_color=appropriate_theme_color)
```

### Multi-Tab GUI Architecture
```python
# Navigation system with Settings, Timer, and Stats tabs
def create_navigation_tabs(self):
    # Integrated header tabs with visual feedback
    
def switch_tab(self, tab_name):
    # Seamless tab switching with content management
    
def create_settings_content(self):
    # Comprehensive settings with sliders, toggles, validation - THEME READY
    
def create_stats_content(self):
    # NEXT IMPLEMENTATION TARGET - Analytics placeholder ready for development
```

### Settings System
```python
# Persistent configuration with validation
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
```

### Theme System Improvements
```python
# Seamless theme transitions with window hiding
def _apply_theme_seamlessly(self):
    self.root.withdraw()  # Hide during transition
    self._apply_theme_immediate()  # Comprehensive updates
    self.root.deiconify()  # Show after completion
    
# Comprehensive widget updates for all tabs
def _update_settings_tab_theme(self, error_list):
    # Updates all settings widgets regardless of visibility
    
def _update_stats_tab_theme(self, error_list):
    # Updates stats tab content and labels
```

## 🐛 Current Bug Status

### Settings Widget Color Issue
**Problem**: Settings widgets (option menus, sliders, labels) don't change color when switching themes
**Evidence**: Screenshot shows settings widgets remained same color after dark→light transition
**Root Cause**: Theme update methods have syntax errors preventing proper execution
**Impact**: Settings tab appears "stuck" in one theme while rest of UI transitions properly

### Syntax Errors in Theme Code
```python
# BROKEN: Missing except clause
try:
    for widget in self.tasks_panel.winfo_children():
        # ... theme update logic
# Missing except clause causes failure

# BROKEN: Indentation issues
try:
    if condition:
        # ... logic
except Exception as e:  # Incorrect indentation
    error_list.append(f"Error: {e}")
```

### Required Fixes
1. **Fix try/except syntax** in theme update methods
2. **Add comprehensive settings widget updates** with proper color application
3. **Test theme transitions** across all tabs and widget types
4. **Resolve linter errors** that may indicate deeper issues

This README provides the foundation for any AI model to quickly understand and work with the Focus Assist codebase. The architecture is mature and ready for the next phase of development toward the hackathon's AI-powered focus detection goals. 