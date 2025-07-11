# Focus Assist

A Pomodoro timer with AI-powered focus tracking for Snapdragon X Elite laptops using local NPU processing.

## Features

- ✅ Customizable Pomodoro timer with work/break intervals
- ✅ Task management with progress tracking
- ✅ Clean terminal interface with progress bars
- ✅ Thread-safe architecture for AI integration
- ✅ Edge-optimized focus detection system
- 🔄 AI-powered focus detection (ready for integration):
  - Screen content analysis (OCR + image classification)
  - Webcam pose estimation and distraction detection
- 🔄 Local processing using Qualcomm AI Hub models

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run simple demo
python src/example.py

# Run AI-powered demo (debug mode)
python src/example_threaded.py --debug
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

### AI-Powered Timer
```python
from pomodoro import EdgeOptimizedFocusDetector, FocusTimerSession

session = FocusTimerSession(debug=True)
session.setup_session(work_seconds=10, snapshot_interval=3)  # Debug values
session.start_session()
```

## License

Licensed under the terms in the LICENSE file.