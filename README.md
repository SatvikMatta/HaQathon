# Focus Assist

A Pomodoro timer application with AI-powered focus tracking capabilities, designed to run on Snapdragon X Elite laptops utilizing the NPU for local AI processing.

## Features (Planned)

- Customizable Pomodoro timer with work and break intervals
- Task management with estimated and actual Pomodoro counts
- Local AI-powered focus detection using:
  - Screen content analysis (OCR + image classification)
  - Webcam-based pose estimation and distraction detection
- Detailed focus statistics and analytics
- All AI processing runs locally using Qualcomm AI Hub optimized models

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the example script:
   ```bash
   python src/example.py
   ```

## Project Structure

```
src/
  pomodoro/
    timer.py      - Core Pomodoro timer implementation
  example.py      - Example usage of the timer
```

## Development Status

- [x] Core Pomodoro timer functionality
- [ ] AI-powered focus detection
- [ ] Screen content analysis
- [ ] Webcam-based pose estimation
- [ ] Statistics and analytics dashboard
- [ ] GUI interface

## License

This project is licensed under the terms of the LICENSE file included in the repository.