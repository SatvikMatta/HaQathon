from pomodoro import PomodoroTimer, Task, TerminalOutput
from pomodoro.constants import DEMO_WORK_SECONDS, DEMO_SHORT_BREAK_SECONDS, DEMO_LONG_BREAK_SECONDS
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)


def main(debug: bool = False):
    """Main example demonstrating the Pomodoro timer with terminal output."""
    
    # Create demo tasks
    demo_tasks = [
        Task(
            id="1",
            title="Setup project structure",
            description="Create initial files and folders",
            estimated_pomodoros=5
        ),
        Task(
            id="2",
            title="Implement core features",
            description="Basic functionality implementation",
            estimated_pomodoros=1
        )
    ]

    # Create timer with demo intervals
    timer = PomodoroTimer(
        work_seconds=DEMO_WORK_SECONDS,
        short_break_seconds=DEMO_SHORT_BREAK_SECONDS,
        long_break_seconds=DEMO_LONG_BREAK_SECONDS,
        tasks=demo_tasks
    )

    # Create terminal output handler
    output = TerminalOutput(debug=debug)
    
    # Start the session
    output.print_header()
    timer.start()
    
    try:
        # Main timer loop
        while timer.state != timer.state.IDLE:
            # Update display
            output.update_display(timer)
            
            
            
            # Small sleep to prevent high CPU usage
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        output.handle_interruption()
        timer.pause()
    finally:
        output.cleanup_interrupted_bar()

    # Print session results
    output.print_final_statistics(timer)


if __name__ == "__main__":
    # Set debug=True to see detailed logging
    main(debug=False) 