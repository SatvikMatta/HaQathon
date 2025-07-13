#!/usr/bin/env python3
"""
Test script to verify AI snapshot synchronization with display clock
"""

import sys
import os
import time
import threading
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pomodoro import PomodoroTimer, Task, TaskStatus, TimerState

def test_ai_snapshot_sync():
    """Test that AI snapshots are synchronized with display clock"""
    print("🧪 Testing AI Snapshot Synchronization")
    print("=" * 50)
    
    # Create a simple task
    task = Task(
        id="test-task",
        title="Test Task",
        description="Testing AI snapshot sync",
        estimated_pomodoros=1
    )
    
    # Create timer with 20 second work time and 3 second AI intervals
    timer = PomodoroTimer(
        work_seconds=20,
        short_break_seconds=5,
        long_break_seconds=10,
        tasks=[task],
        ai_checkin_interval_seconds=3
    )
    
    # Track AI snapshots
    snapshot_times = []
    
    def ai_callback():
        elapsed = time.time() - start_time
        remaining = timer.get_remaining_time()
        if remaining:
            remaining_sec = remaining.total_seconds()
            elapsed_display = 20 - remaining_sec
        else:
            elapsed_display = 0
        
        snapshot_times.append((elapsed, elapsed_display))
        print(f"🤖 AI Snapshot #{len(snapshot_times)}: Real={elapsed:.1f}s, Display={elapsed_display:.1f}s")
    
    timer.add_ai_snapshot_callback(ai_callback)
    
    # Start timer
    start_time = time.time()
    print(f"⏰ Starting timer at {datetime.now().strftime('%H:%M:%S')}")
    timer.start()
    
    # Test sequence:
    # 1. Run for 5 seconds (should get 1 snapshot at 3s)
    # 2. Pause for 3 seconds
    # 3. Resume and run for 10 more seconds (should get snapshots at 6s, 9s, 12s, 15s, 18s)
    
    def simulate_timer_loop():
        """Simulate the GUI timer loop that calls get_remaining_time()"""
        while timer.state != TimerState.IDLE:
            remaining = timer.get_remaining_time()
            if remaining:
                remaining_sec = remaining.total_seconds()
                if remaining_sec <= 0:
                    break
            time.sleep(0.1)  # Check every 100ms like the GUI
    
    # Start timer loop in background
    timer_thread = threading.Thread(target=simulate_timer_loop, daemon=True)
    timer_thread.start()
    
    print("📊 Phase 1: Running for 5 seconds...")
    time.sleep(5)
    
    print("⏸️  Phase 2: Pausing for 3 seconds...")
    timer.pause()
    time.sleep(3)
    
    print("▶️  Phase 3: Resuming...")
    timer.start()
    time.sleep(12)  # Run longer to get all expected snapshots
    
    # Stop timer
    timer.pause()
    
    print("🏁 Test completed!")
    print(f"📈 Total snapshots: {len(snapshot_times)}")
    
    # Verify snapshots are at correct intervals based on display time
    print("\n🔍 Snapshot Analysis:")
    expected_display_times = [3, 6, 9, 12, 15, 18]
    
    for i, (real_time, display_time) in enumerate(snapshot_times):
        if i < len(expected_display_times):
            expected = expected_display_times[i]
            tolerance = 0.5  # Allow 0.5 second tolerance
            if abs(display_time - expected) <= tolerance:
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            print(f"  Snapshot {i+1}: Display={display_time:.1f}s, Expected={expected}s {status}")
        else:
            print(f"  Snapshot {i+1}: Display={display_time:.1f}s (unexpected)")
    
    if len(snapshot_times) == len(expected_display_times):
        print("\n🎉 SUCCESS: AI snapshots are properly synchronized with display clock!")
    else:
        print(f"\n⚠️  WARNING: Expected {len(expected_display_times)} snapshots, got {len(snapshot_times)}")
    
    print("\n📋 Expected behavior:")
    print("- Snapshots should occur at display times: 3s, 6s, 9s, 12s, 15s, 18s")
    print("- Pausing should NOT reset the snapshot timer")
    print("- Snapshots should continue from where they left off after resume")

if __name__ == "__main__":
    test_ai_snapshot_sync() 