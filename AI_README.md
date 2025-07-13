# AI_README.md - Focus Assist Codebase Guide

## 🎯 Project Overview

**Focus Assist** is a modern Pomodoro timer application with a clean GUI built using CustomTkinter. The project has been **cleaned of AI focus detection features** and now focuses on core Pomodoro functionality with task management.

### Current State (Post-Cleanup)
- ✅ **Fully functional** Pomodoro timer with GUI
- ✅ **Task management system** with CRUD operations
- ✅ **Modern UI** with dark/light themes
- ✅ **Terminal output integration** for cross-reference
- ✅ **Thread-safe architecture** ready for future enhancements
- ❌ **AI focus detection removed** (was not ready for production)

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

```python
class PomodoroTimer:
    # States: WORK, SHORT_BREAK, LONG_BREAK, PAUSED, SKIPPED, IDLE
    def start() -> bool          # Start/resume timer
    def pause() -> bool          # Pause current interval
    def skip() -> bool           # Skip current interval
    def get_remaining_time()     # Get time left in current interval
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

### Running the Application
```bash
# GUI version (main application)
cd src && python focus_assist_gui.py

# Terminal version (simple demo)
cd src && python example.py
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

### Removed Features
- **AI Focus Detection**: All `focus_detector.py` related code removed
- **Snapshot System**: Timer snapshot callbacks removed
- **FocusTimerSession**: AI-integrated session management removed

### Ready for Enhancement
- **Plugin Architecture**: Timer callback system ready for extensions
- **Data Persistence**: Task system ready for database integration
- **Advanced Analytics**: Timer state tracking ready for metrics
- **Notification System**: State callbacks ready for alerts

### Testing Strategy
- Use `example.py` for basic timer functionality
- Test GUI with sample tasks (already loaded)
- Theme switching should be seamless
- Timer state transitions should be smooth

This README provides the foundation for any AI model to quickly understand and work with the Focus Assist codebase. The architecture is clean, well-structured, and ready for future enhancements. 