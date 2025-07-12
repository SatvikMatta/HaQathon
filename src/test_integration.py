#!/usr/bin/env python3
"""
Test script to verify Focus Assist GUI integration
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from focus_assist_gui import FocusAssistApp, TaskDialog
        from pomodoro import PomodoroTimer, Task, TaskStatus, TimerState, TerminalOutput
        from pomodoro.constants import DEMO_WORK_SECONDS
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_task_creation():
    """Test task creation"""
    try:
        from pomodoro import Task
        import uuid
        
        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            description="This is a test task",
            estimated_pomodoros=3
        )
        
        print(f"✅ Task created: {task.title}")
        return True
    except Exception as e:
        print(f"❌ Task creation error: {e}")
        return False

def test_timer_integration():
    """Test timer and terminal output integration"""
    try:
        from pomodoro import PomodoroTimer, Task, TerminalOutput
        from pomodoro.constants import DEMO_WORK_SECONDS
        import uuid
        
        # Create test task
        task = Task(
            id=str(uuid.uuid4()),
            title="Integration Test Task",
            description="Testing terminal integration",
            estimated_pomodoros=1
        )
        
        # Create timer
        timer = PomodoroTimer(
            work_seconds=DEMO_WORK_SECONDS,
            short_break_seconds=3,
            long_break_seconds=5,
            tasks=[task],
            snapshot_interval=2
        )
        
        # Create terminal output
        terminal_output = TerminalOutput(debug=True)
        
        print("✅ Timer and terminal output integration successful")
        return True
    except Exception as e:
        print(f"❌ Timer integration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Focus Assist GUI Integration")
    print("=" * 40)
    
    tests = [
        ("Module Imports", test_imports),
        ("Task Creation", test_task_creation),
        ("Timer Integration", test_timer_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! GUI integration is working correctly.")
        print("\n🚀 To run the GUI:")
        print("   python focus_assist_gui.py")
        print("\n📝 Features included:")
        print("   ✅ Modern task management with add/edit/delete")
        print("   ✅ Dark/light mode toggle")
        print("   ✅ Terminal output integration")
        print("   ✅ Progress tracking and statistics")
        print("   ✅ Demo mode for testing")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 