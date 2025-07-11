# Focus Assist

A Pomodoro timer with AI-powered focus tracking for Snapdragon X Elite laptops using local NPU processing.

## Features

- ✅ Customizable Pomodoro timer with work/break intervals
- ✅ Task management with progress tracking
- ✅ Clean terminal interface with progress bars
- 🔄 AI-powered focus detection (planned):
  - Screen content analysis (OCR + image classification)
  - Webcam pose estimation and distraction detection
- 🔄 Local processing using Qualcomm AI Hub models

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run demo
python src/example.py
```

## Usage

```python
from pomodoro import PomodoroTimer, Task, TerminalOutput

# Create tasks and timer
tasks = [Task(id="1", title="Work on project", estimated_pomodoros=3)]
timer = PomodoroTimer(work_seconds=1500, short_break_seconds=300, 
                      long_break_seconds=900, tasks=tasks)

# Use with terminal output
output = TerminalOutput()
output.print_header()
timer.start()

while timer.state != timer.state.IDLE:
    output.update_display(timer)
    if timer.should_take_snapshot():
        # Add AI processing here
        output.handle_snapshot()
```

## License

Licensed under the terms in the LICENSE file.