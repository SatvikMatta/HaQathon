# Focus Assist

A Pomodoro timer with AI-powered focus tracking for Snapdragon X Elite laptops using local NPU processing.

## Features

- ✅ Customizable Pomodoro timer with work/break intervals
- ✅ Task management with progress tracking
- ✅ Clean terminal interface with progress bars
- ✅ Thread-safe architecture for future AI integration

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run GUI version
python src/focus_assist_gui.py
```

## Usage

### Simple Timer
```python
from pomodoro import PomodoroTimer, Task, TerminalOutput

tasks = [Task(id="1", title="Work on project", estimated_pomodoros=3)]
timer = PomodoroTimer(work_seconds=1500, short_break_seconds=300, 
                      long_break_seconds=900, tasks=tasks)
output = TerminalOutput()

timer.start()
while timer.state != timer.state.IDLE:
    output.update_display(timer)
```

### GUI Timer
```python
from src.focus_assist_gui import FocusAssistApp

app = FocusAssistApp()
app.run()
```

## License

Licensed under the terms in the LICENSE file.