"""
Focus detection module for AI-powered attention monitoring.
Optimized for edge deployment with Snapdragon X Elite NPU.
"""

import threading
import queue
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any
from enum import Enum
import concurrent.futures
from .constants import MAX_FOCUS_DETECTOR_WORKERS, MAX_FOCUS_DETECTOR_QUEUE_SIZE, FOCUS_DETECTOR_TIMEOUT_SECONDS, ErrorMessages
from .utils import PerformanceUtils


class FocusLevel(Enum):
    FOCUSED = "focused"
    DISTRACTED = "distracted"
    AWAY = "away"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class FocusSnapshot:
    """Immutable focus detection result."""
    timestamp: float
    focus_level: FocusLevel
    confidence: float  # 0.0 to 1.0
    details: Dict[str, Any]
    processing_time_ms: float


class FocusDetector(ABC):
    """Abstract base class for focus detection implementations."""
    
    @abstractmethod
    def analyze(self) -> FocusSnapshot:
        """Analyze current focus state."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources."""
        pass


class EdgeOptimizedFocusDetector:
    """
    Thread-safe focus detector optimized for edge deployment.
    Manages multiple detection methods and resource usage.
    """
    
    def __init__(
        self,
        max_workers: int = MAX_FOCUS_DETECTOR_WORKERS,
        max_queue_size: int = MAX_FOCUS_DETECTOR_QUEUE_SIZE,
        timeout_seconds: float = FOCUS_DETECTOR_TIMEOUT_SECONDS,
        enable_screen_analysis: bool = True,
        enable_pose_detection: bool = True
    ):
        self.max_workers = max_workers
        self.timeout_seconds = timeout_seconds
        self.enable_screen_analysis = enable_screen_analysis
        self.enable_pose_detection = enable_pose_detection
        
        # Thread-safe components
        self._lock = threading.RLock()
        self._task_queue = queue.Queue(maxsize=max_queue_size)
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="focus_detector"
        )
        self._is_running = False
        self._detectors: Dict[str, FocusDetector] = {}
        self._callbacks: list[Callable[[FocusSnapshot], None]] = []
        
        # Performance monitoring
        self._stats = {
            'total_snapshots': 0,
            'successful_snapshots': 0,
            'failed_snapshots': 0,
            'avg_processing_time': 0.0
        }
        
        # Initialize detectors
        self._initialize_detectors()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)

    def _initialize_detectors(self) -> None:
        """Initialize AI detection modules."""
        try:
            if self.enable_screen_analysis:
                self._detectors['screen'] = ScreenAnalysisDetector()
            
            if self.enable_pose_detection:
                self._detectors['pose'] = PoseDetector()
                
        except Exception as e:
            self.logger.error(f"{ErrorMessages.FOCUS_DETECTOR_INIT_ERROR}: {e}")

    def start(self) -> bool:
        """Start the focus detection service."""
        try:
            with self._lock:
                if self._is_running:
                    return True
                
                self._is_running = True
                self.logger.info("Focus detector started")
                return True
                
        except Exception as e:
            self.logger.error(f"{ErrorMessages.FOCUS_DETECTOR_START_ERROR}: {e}")
            return False

    def stop(self) -> None:
        """Stop the focus detection service and cleanup resources."""
        try:
            with self._lock:
                if not self._is_running:
                    return
                
                self._is_running = False
                
                # Cleanup detectors
                for detector in self._detectors.values():
                    try:
                        detector.cleanup()
                    except Exception as e:
                        self.logger.error(f"Detector cleanup error: {e}")
                
                # Shutdown executor
                self._executor.shutdown(wait=True, timeout=self.timeout_seconds)
                
                self.logger.info("Focus detector stopped")
                
        except Exception as e:
            self.logger.error(f"Error stopping focus detector: {e}")

    def add_callback(self, callback: Callable[[FocusSnapshot], None]) -> None:
        """Add callback for focus detection results."""
        with self._lock:
            self._callbacks.append(callback)

    def request_snapshot(self) -> Optional[concurrent.futures.Future]:
        """Request async focus analysis. Returns Future or None if queue full."""
        try:
            if not self._is_running:
                return None
            
            # Submit analysis task
            future = self._executor.submit(self._perform_analysis)
            return future
            
        except Exception as e:
            self.logger.error(f"Snapshot request error: {e}")
            return None

    def _perform_analysis(self) -> Optional[FocusSnapshot]:
        """Perform focus analysis using available detectors."""
        start_time = time.time()
        
        try:
            results = []
            
            # Run detectors in parallel for speed
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(self._detectors)) as executor:
                future_to_detector = {
                    executor.submit(detector.analyze): name 
                    for name, detector in self._detectors.items()
                }
                
                for future in concurrent.futures.as_completed(
                    future_to_detector, timeout=self.timeout_seconds
                ):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        detector_name = future_to_detector[future]
                        self.logger.warning(f"Detector {detector_name} failed: {e}")
            
            # Aggregate results
            if not results:
                return self._create_unknown_snapshot(start_time)
            
            final_snapshot = self._aggregate_results(results, start_time)
            
            # Update stats
            self._update_stats(final_snapshot)
            
            # Notify callbacks
            self._notify_callbacks(final_snapshot)
            
            return final_snapshot
            
        except Exception as e:
            self.logger.error(f"Analysis error: {e}")
            self._stats['failed_snapshots'] += 1
            return self._create_unknown_snapshot(start_time)

    def _aggregate_results(self, results: list[FocusSnapshot], start_time: float) -> FocusSnapshot:
        """Combine multiple detector results into final assessment."""
        if len(results) == 1:
            return results[0]
        
        # Simple aggregation - can be enhanced with ML models
        focus_counts = {}
        total_confidence = 0.0
        combined_details = {}
        
        for result in results:
            focus_counts[result.focus_level] = focus_counts.get(result.focus_level, 0) + 1
            total_confidence += result.confidence
            combined_details.update(result.details)
        
        # Majority vote with confidence weighting
        dominant_focus = max(focus_counts.keys(), key=lambda x: focus_counts[x])
        avg_confidence = total_confidence / len(results)
        
        processing_time = (time.time() - start_time) * 1000
        
        return FocusSnapshot(
            timestamp=start_time,
            focus_level=dominant_focus,
            confidence=avg_confidence,
            details=combined_details,
            processing_time_ms=processing_time
        )

    def _create_unknown_snapshot(self, start_time: float) -> FocusSnapshot:
        """Create a fallback snapshot when analysis fails."""
        processing_time = (time.time() - start_time) * 1000
        return FocusSnapshot(
            timestamp=start_time,
            focus_level=FocusLevel.UNKNOWN,
            confidence=0.0,
            details={'error': 'Analysis failed'},
            processing_time_ms=processing_time
        )

    def _update_stats(self, snapshot: FocusSnapshot) -> None:
        """Update performance statistics."""
        with self._lock:
            self._stats['total_snapshots'] += 1
            if snapshot.focus_level != FocusLevel.UNKNOWN:
                self._stats['successful_snapshots'] += 1
            else:
                self._stats['failed_snapshots'] += 1
            
            # Update running average
            total = self._stats['total_snapshots']
            current_avg = self._stats['avg_processing_time']
            self._stats['avg_processing_time'] = (
                (current_avg * (total - 1) + snapshot.processing_time_ms) / total
            )

    def _notify_callbacks(self, snapshot: FocusSnapshot) -> None:
        """Notify registered callbacks of new results."""
        for callback in self._callbacks:
            try:
                callback(snapshot)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        with self._lock:
            return self._stats.copy()


class ScreenAnalysisDetector(FocusDetector):
    """Screen content analysis for focus detection."""
    
    def analyze(self) -> FocusSnapshot:
        """Analyze screen content for focus indicators."""
        start_time = time.time()
        
        # Placeholder for actual screen analysis
        # In real implementation, this would:
        # 1. Take screenshot
        # 2. Run OCR to extract text
        # 3. Use NLP to classify content relevance
        # 4. Check for distracting elements (social media, etc.)
        
        processing_time = (time.time() - start_time) * 1000
        
        return FocusSnapshot(
            timestamp=start_time,
            focus_level=FocusLevel.FOCUSED,  # Placeholder
            confidence=0.8,
            details={'method': 'screen_analysis', 'content_type': 'work_related'},
            processing_time_ms=processing_time
        )
    
    def cleanup(self) -> None:
        """Clean up screen analysis resources."""
        pass


class PoseDetector(FocusDetector):
    """Pose estimation for focus detection."""
    
    def analyze(self) -> FocusSnapshot:
        """Analyze user pose for focus indicators."""
        start_time = time.time()
        
        # Placeholder for actual pose detection
        # In real implementation, this would:
        # 1. Capture webcam frame
        # 2. Run pose estimation model
        # 3. Analyze head position, eye gaze direction
        # 4. Detect distracting objects (phone, etc.)
        
        processing_time = (time.time() - start_time) * 1000
        
        return FocusSnapshot(
            timestamp=start_time,
            focus_level=FocusLevel.FOCUSED,  # Placeholder
            confidence=0.7,
            details={'method': 'pose_detection', 'head_pose': 'forward', 'eyes': 'screen'},
            processing_time_ms=processing_time
        )
    
    def cleanup(self) -> None:
        """Clean up pose detection resources."""
        pass 