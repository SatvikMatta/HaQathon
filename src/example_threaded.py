"""
Advanced example demonstrating threaded AI-powered focus detection.
Optimized for edge deployment on Snapdragon X Elite devices.
"""

from pomodoro import (
    PomodoroTimer, Task, TerminalOutput, 
    EdgeOptimizedFocusDetector, FocusSnapshot, FocusLevel
)
import time
import logging
import signal
import sys
from typing import Optional

# Set up optimized logging for edge devices
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)


class FocusTimerSession:
    """Integrated timer session with AI-powered focus tracking."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.timer: Optional[PomodoroTimer] = None
        self.output: Optional[TerminalOutput] = None
        self.focus_detector: Optional[EdgeOptimizedFocusDetector] = None
        self.running = False
        
        # Performance tracking
        self.session_stats = {
            'total_snapshots': 0,
            'focused_time': 0.0,
            'distracted_time': 0.0,
            'session_start': 0.0
        }

    def setup_session(self, work_seconds: int = 10, short_break_seconds: int = 5, 
                     long_break_seconds: int = 8, snapshot_interval: int = 3) -> bool:
        """Set up timer session with AI focus detection."""
        try:
            # Create demo tasks optimized for edge devices
            demo_tasks = [
                Task(
                    id="1",
                    title="Deep work session",
                    description="Focus on high-priority tasks",
                    estimated_pomodoros=3
                ),
                Task(
                    id="2", 
                    title="Code review and testing",
                    description="Review and test recent changes",
                    estimated_pomodoros=2
                )
            ]

            # Initialize timer with debug intervals (in seconds)
            self.timer = PomodoroTimer(
                work_seconds=work_seconds,
                short_break_seconds=short_break_seconds,
                long_break_seconds=long_break_seconds,
                tasks=demo_tasks,
                snapshot_interval=snapshot_interval,
            )

            # Initialize terminal output
            self.output = TerminalOutput(debug=self.debug)
            
            # Initialize AI focus detector (optimized for edge)
            self.focus_detector = EdgeOptimizedFocusDetector(
                max_workers=2,  # Limited for edge devices
                timeout_seconds=3.0,  # Fast inference required
                enable_screen_analysis=True,
                enable_pose_detection=True
            )
            
            # Set up AI callbacks
            self.timer.add_snapshot_callback(self._handle_snapshot_request)
            self.focus_detector.add_callback(self._handle_focus_result)
            
            logger.info("Session setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Session setup failed: {e}")
            return False

    def start_session(self) -> None:
        """Start the focus-assisted Pomodoro session."""
        if not all([self.timer, self.output, self.focus_detector]):
            logger.error("Session not properly initialized")
            return
        
        # Type assertions for linter
        assert self.timer is not None
        assert self.output is not None
        assert self.focus_detector is not None
        
        self.running = True
        self.session_stats['session_start'] = time.time()
        
        # Start AI processing
        if not self.focus_detector.start():
            logger.warning("Focus detector failed to start - continuing without AI")
        
        # Print header
        self.output.print_header()
        
        # Start timer
        if not self.timer.start():
            logger.error("Failed to start timer")
            return
        
        logger.info("Focus session started")
        
        try:
            # Main session loop
            while self.running and self.timer.state != self.timer.state.IDLE:
                # Update display
                if not self.output.update_display(self.timer):
                    time.sleep(0.1)  # Brief pause on update failure
                    continue
                
                # Handle manual snapshot requests
                if self.timer.should_take_snapshot():
                    self.output.handle_snapshot()
                
                # Efficient sleep to prevent high CPU usage
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("Session interrupted by user")
            self.output.handle_interruption()
            self.timer.pause()
        finally:
            self._cleanup_session()

    def _handle_snapshot_request(self) -> None:
        """Handle AI snapshot request from timer."""
        if not self.focus_detector or not self.running:
            return
        
        try:
            # Request async AI analysis
            future = self.focus_detector.request_snapshot()
            if future:
                self.session_stats['total_snapshots'] += 1
                logger.debug("AI snapshot requested")
            else:
                logger.warning("Snapshot request failed - detector busy")
                
        except Exception as e:
            logger.error(f"Snapshot request error: {e}")

    def _handle_focus_result(self, snapshot: FocusSnapshot) -> None:
        """Handle AI focus detection results."""
        try:
            # Update session statistics
            if snapshot.focus_level == FocusLevel.FOCUSED:
                self.session_stats['focused_time'] += 1.0
            elif snapshot.focus_level == FocusLevel.DISTRACTED:
                self.session_stats['distracted_time'] += 1.0
            
            # Log results in debug mode
            if self.debug:
                logger.info(f"Focus: {snapshot.focus_level.value} "
                           f"(confidence: {snapshot.confidence:.2f}, "
                           f"processing: {snapshot.processing_time_ms:.1f}ms)")
                
        except Exception as e:
            logger.error(f"Focus result handling error: {e}")

    def _cleanup_session(self) -> None:
        """Clean up session resources."""
        try:
            if self.focus_detector:
                self.focus_detector.stop()
            
            if self.output:
                self.output.cleanup_interrupted_bar()
                self._print_session_summary()
                
            logger.info("Session cleanup complete")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def _print_session_summary(self) -> None:
        """Print comprehensive session summary."""
        if not all([self.timer, self.output]):
            return
        
        # Type assertions for linter
        assert self.timer is not None
        assert self.output is not None
        
        # Standard timer statistics
        self.output.print_final_statistics(self.timer)
        
        # AI focus statistics
        if self.session_stats['total_snapshots'] > 0:
            total_analysis_time = (self.session_stats['focused_time'] + 
                                 self.session_stats['distracted_time'])
            
            if total_analysis_time > 0:
                focus_percentage = (self.session_stats['focused_time'] / 
                                  total_analysis_time * 100)
                
                print(f"\n📊 Focus Analysis:")
                print(f"   Snapshots taken: {self.session_stats['total_snapshots']}")
                print(f"   Focus percentage: {focus_percentage:.1f}%")
        
        # Performance statistics in debug mode
        if self.debug:
            detector_stats = self.focus_detector.get_stats() if self.focus_detector else {}
            output_stats = self.output.get_stats()
            
            print(f"\n🔧 Performance Stats:")
            print(f"   AI processing: {detector_stats}")
            print(f"   Display updates: {output_stats}")

    def stop_session(self) -> None:
        """Gracefully stop the session."""
        self.running = False


def signal_handler(session: FocusTimerSession):
    """Handle shutdown signals gracefully."""
    def handler(signum, frame):
        logger.info("Shutdown signal received")
        session.stop_session()
        sys.exit(0)
    return handler


def main(debug: bool = False):
    """Main entry point for threaded focus timer."""
    session = FocusTimerSession(debug=debug)
    
    # Set up signal handling for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler(session))
    signal.signal(signal.SIGTERM, signal_handler(session))
    
    # Setup and run session
    if not session.setup_session():
        logger.error("Failed to setup session")
        return 1
    
    logger.info("Starting AI-powered focus session...")
    session.start_session()
    
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-powered Pomodoro timer")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()
    
    exit_code = main(debug=args.debug)
    sys.exit(exit_code) 