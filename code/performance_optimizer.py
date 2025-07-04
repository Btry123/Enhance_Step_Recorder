import os
import gc
import psutil
import threading
import time
from typing import List, Dict, Any, Optional, Callable
from PIL import Image
import queue
import tempfile

class PerformanceOptimizer:
    """Performance optimization: memory management, screenshot compression, background processing."""
    
    def __init__(self):
        self.memory_threshold = 80  # Percentage
        self.screenshot_quality = 85  # JPEG quality
        self.max_screenshot_size = (1920, 1080)  # Max dimensions
        self.background_queue = queue.Queue()
        self.background_thread = None
        self.running = False
        self.temp_files = []
        
    def start_background_processing(self):
        """Start background processing thread."""
        if not self.running:
            self.running = True
            self.background_thread = threading.Thread(target=self._background_worker, daemon=True)
            self.background_thread.start()
    
    def stop_background_processing(self):
        """Stop background processing thread."""
        self.running = False
        if self.background_thread:
            self.background_thread.join(timeout=5)
    
    def optimize_screenshot(self, image_path: str, output_path: str = None) -> str:
        """Optimize screenshot by compressing and resizing."""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large
                if img.size[0] > self.max_screenshot_size[0] or img.size[1] > self.max_screenshot_size[1]:
                    img.thumbnail(self.max_screenshot_size, Image.Resampling.LANCZOS)
                
                # Save with compression
                if output_path is None:
                    output_path = image_path
                
                img.save(output_path, 'JPEG', quality=self.screenshot_quality, optimize=True)
                return output_path
                
        except Exception as e:
            print(f"Error optimizing screenshot: {e}")
            return image_path
    
    def compress_screenshots_batch(self, screenshot_paths: List[str]) -> List[str]:
        """Compress multiple screenshots in batch."""
        compressed_paths = []
        
        for path in screenshot_paths:
            if os.path.exists(path):
                compressed_path = self.optimize_screenshot(path)
                compressed_paths.append(compressed_path)
        
        return compressed_paths
    
    def check_memory_usage(self) -> Dict[str, float]:
        """Check current memory usage."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024
        }
    
    def is_memory_critical(self) -> bool:
        """Check if memory usage is critical."""
        memory_info = self.check_memory_usage()
        return memory_info['percent'] > self.memory_threshold
    
    def cleanup_memory(self):
        """Clean up memory by forcing garbage collection."""
        gc.collect()
        
        # Clear temporary files
        self.cleanup_temp_files()
    
    def cleanup_temp_files(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Error removing temp file {temp_file}: {e}")
        
        self.temp_files.clear()

    def cleanup_screenshots(self, screenshot_paths: List[str]) -> int:
        """Clean up screenshot files and return count of deleted files."""
        deleted_count = 0
        
        for screenshot_path in screenshot_paths:
            try:
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
                    deleted_count += 1
            except Exception as e:
                print(f"Error deleting screenshot {screenshot_path}: {e}")
        
        return deleted_count
    
    def create_temp_file(self, suffix: str = '.tmp') -> str:
        """Create a temporary file and track it."""
        temp_file = tempfile.mktemp(suffix=suffix)
        self.temp_files.append(temp_file)
        return temp_file
    
    def add_background_task(self, task: Callable, *args, **kwargs):
        """Add a task to background processing queue."""
        self.background_queue.put((task, args, kwargs))
    
    def _background_worker(self):
        """Background worker thread."""
        while self.running:
            try:
                # Get task from queue with timeout
                task, args, kwargs = self.background_queue.get(timeout=1)
                
                # Execute task
                try:
                    task(*args, **kwargs)
                except Exception as e:
                    print(f"Error in background task: {e}")
                
                # Mark task as done
                self.background_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in background worker: {e}")
    
    def optimize_session_data(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize session data for storage."""
        optimized = session_data.copy()
        
        # Remove unnecessary data from steps
        for step in optimized.get('steps', []):
            # Keep only essential data
            essential_keys = ['step_number', 'type', 'timestamp', 'screenshot', 'description']
            step_keys = list(step.keys())
            
            for key in step_keys:
                if key not in essential_keys:
                    del step[key]
        
        return optimized
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance optimization summary."""
        memory_info = self.check_memory_usage()
        
        return {
            'memory_usage_mb': memory_info['rss_mb'],
            'memory_percent': memory_info['percent'],
            'available_memory_mb': memory_info['available_mb'],
            'background_tasks_queued': self.background_queue.qsize(),
            'temp_files_count': len(self.temp_files),
            'memory_critical': self.is_memory_critical()
        }
    
    def set_memory_threshold(self, threshold: float):
        """Set memory usage threshold."""
        self.memory_threshold = max(50, min(95, threshold))
    
    def set_screenshot_quality(self, quality: int):
        """Set screenshot compression quality."""
        self.screenshot_quality = max(10, min(100, quality))
    
    def set_max_screenshot_size(self, width: int, height: int):
        """Set maximum screenshot dimensions."""
        self.max_screenshot_size = (max(100, width), max(100, height))
    
    def monitor_performance(self, callback: Callable[[Dict[str, Any]], None], interval: int = 30):
        """Start performance monitoring."""
        def monitor_loop():
            while self.running:
                try:
                    summary = self.get_performance_summary()
                    callback(summary)
                    time.sleep(interval)
                except Exception as e:
                    print(f"Error in performance monitoring: {e}")
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread 