from pomodoro import PomodoroTimer, Task, TerminalOutput
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
        work_seconds=5,        # 5 sec work for demo
        short_break_seconds=3, # 3 sec short break
        long_break_seconds=8,  # 8 sec long break
        tasks=demo_tasks,
        snapshot_interval=5,   # check every 5 sec
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
            
            # Handle snapshot events
            if timer.should_take_snapshot():
                output.handle_snapshot()
            
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
    # Set debug=True to see snapshot logging
    main(debug=False) 