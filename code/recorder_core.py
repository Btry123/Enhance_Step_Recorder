import os
import queue
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple, Any

from PIL import ImageGrab, ImageDraw, ImageFont
from pynput import mouse, keyboard

from docx import Document
from docx.shared import Inches

# Optional imports
try:
    import win32gui
except ImportError:
    win32gui = None


class RecordingSession:
    """Data class to hold recording session information."""
    
    def __init__(self):
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.steps: List[Dict[str, Any]] = []
        self.screenshots: List[str] = []
        self.statistics: Dict[str, Any] = {
            'clicks': 0,
            'keystrokes': 0,
            'notes': 0,
            'applications': set(),
            'total_steps': 0,
            'recording_duration': 0
        }
        self.metadata: Dict[str, Any] = {
            'version': '2.0',
            'created_by': 'Enhanced Step Recorder',
            'settings': {}
        }


class StepRecorderCore:
    """Core recording functionality without UI dependencies."""
    
    def __init__(self):
        # Core state
        self.recording = False
        self.paused = False
        self.step = 0
        self.start_time: Optional[datetime] = None
        
        # Data structures
        self.queue = queue.Queue()
        self.outputs: List[str] = []
        self.last_click = (100, 100)
        self.current_keystrokes: List[keyboard.Key] = []
        self.last_key_time = 0
        self.key_grouping_delay = 1000
        
        # Session data
        self.session = RecordingSession()
        
        # Listeners
        self.mouse_listener: Optional[mouse.Listener] = None
        self.kb_listener: Optional[keyboard.Listener] = None
        
        # Callbacks
        self.on_step_recorded = None
        self.on_statistics_updated = None
        self.on_recording_state_changed = None
        
        # Timer
        self.timer_running = False
        self.timer_thread: Optional[threading.Thread] = None

    def start_recording(self) -> bool:
        """Start a new recording session."""
        if self.recording:
            return False
            
        # Reset session
        self.recording = True
        self.paused = False
        self.step = 0
        self.start_time = datetime.now()
        self.session = RecordingSession()
        self.session.start_time = self.start_time
        self.session.statistics = {
            'clicks': 0,
            'keystrokes': 0,
            'notes': 0,
            'applications': set(),
            'total_steps': 0,
            'recording_duration': 0
        }

        # Start listeners
        try:
            self.mouse_listener = mouse.Listener(on_click=self._on_click)
            self.mouse_listener.start()
            self.kb_listener = keyboard.Listener(on_release=self._on_key_release)
            self.kb_listener.start()
        except Exception as e:
            self.recording = False
            raise Exception(f"Failed to start listeners: {e}")

        # Start timer
        self.start_timer()
        
        # Notify state change
        if self.on_recording_state_changed:
            self.on_recording_state_changed(True)
            
        return True

    def stop_recording(self) -> bool:
        """Stop the current recording session."""
        if not self.recording:
            return False
        
        # Record remaining keystrokes
        if self.current_keystrokes:
            self._record_keystroke_group()
        
        self.recording = False
        self.paused = False
        self.session.end_time = datetime.now()
        
        # Calculate duration
        if self.session.start_time and self.session.end_time:
            self.session.statistics['recording_duration'] = (
                self.session.end_time - self.session.start_time
            ).total_seconds()
        
        # Stop timer
        self.stop_timer()
        
        # Stop listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        if self.kb_listener:
            self.kb_listener.stop()
            self.kb_listener = None

        # Notify state change
        if self.on_recording_state_changed:
            self.on_recording_state_changed(False)
            
        return True

    def pause_recording(self) -> bool:
        """Pause the recording."""
        if not self.recording:
            return False
        
        self.paused = True
        self.pause_timer()
        return True

    def resume_recording(self) -> bool:
        """Resume the recording."""
        if not self.recording:
            return False
        
        self.paused = False
        self.resume_timer()
        return True

    def add_note(self, note_text: str) -> bool:
        """Add a note to the recording."""
        if not self.recording:
            return False
        
        self.step += 1
        self.session.statistics['total_steps'] += 1
        self.session.statistics['notes'] += 1
        
        step_data = {
            'step_number': self.step,
            'timestamp': datetime.now(),
            'type': 'note',
            'content': note_text,
            'application': self.get_active_window_title(),
            'screenshot': None
        }
        
        self.session.steps.append(step_data)
        
        # Notify step recorded
        if self.on_step_recorded:
            self.on_step_recorded(step_data)
        if self.on_statistics_updated:
            self.on_statistics_updated(self.session.statistics)
            
        return True

    def get_recording_duration(self) -> timedelta:
        """Get current recording duration."""
        if not self.start_time:
            return timedelta(0)
        
        if self.paused:
            return timedelta(seconds=self.session.statistics.get('recording_duration', 0))
        
        return datetime.now() - self.start_time

    def get_statistics(self) -> Dict[str, Any]:
        """Get current recording statistics."""
        stats = self.session.statistics.copy()
        stats['applications'] = list(stats['applications'])
        stats['current_duration'] = self.get_recording_duration().total_seconds()
        return stats

    def get_session_data(self) -> RecordingSession:
        """Get the complete session data."""
        return self.session

    def start_timer(self):
        """Start the recording timer."""
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()

    def stop_timer(self):
        """Stop the recording timer."""
        self.timer_running = False

    def pause_timer(self):
        """Pause the timer."""
        self.timer_running = False

    def resume_timer(self):
        """Resume the timer."""
        self.start_timer()

    def _timer_loop(self):
        """Timer loop for updating duration."""
        while self.timer_running and self.recording:
            if not self.paused:
                duration = self.get_recording_duration()
                self.session.statistics['recording_duration'] = duration.total_seconds()
            time.sleep(1)

    def _on_click(self, x: int, y: int, button: mouse.Button, pressed: bool):
        """Handle mouse click events."""
        if pressed and self.recording and not self.paused:
            # Record pending keystrokes
            if self.current_keystrokes:
                self._record_keystroke_group()
            
            self.last_click = (x, y)
            self.queue.put(("click", x, y, button))

    def _on_key_release(self, key: keyboard.Key):
        """Handle keyboard release events."""
        if not self.recording or self.paused:
            return
        
        # Group keystrokes
        current_time = datetime.now().timestamp() * 1000
        
        if self.current_keystrokes and (current_time - self.last_key_time) > self.key_grouping_delay:
            self._record_keystroke_group()
        
        self.current_keystrokes.append(key)
        self.last_key_time = current_time

    def _record_keystroke_group(self):
        """Record a group of keystrokes."""
        if not self.current_keystrokes:
            return
        
        self.step += 1
        self.session.statistics['total_steps'] += 1
        self.session.statistics['keystrokes'] += len(self.current_keystrokes)
        
        keystroke_text = self._keystrokes_to_text(self.current_keystrokes)
        img_path = self._capture_and_highlight(*self.last_click)
        
        step_data = {
            'step_number': self.step,
            'timestamp': datetime.now(),
            'type': 'keystroke',
            'content': keystroke_text,
            'application': self.get_active_window_title(),
            'screenshot': img_path,
            'coordinates': self.last_click,
            'keystrokes': [str(k) for k in self.current_keystrokes]
        }
        
        self.session.steps.append(step_data)
        self.session.screenshots.append(img_path)
        self.session.statistics['applications'].add(step_data['application'])
        
        # Notify step recorded
        if self.on_step_recorded:
            self.on_step_recorded(step_data)
        if self.on_statistics_updated:
            self.on_statistics_updated(self.session.statistics)
        
        self.current_keystrokes = []

    def _record_click(self, x: int, y: int, button: mouse.Button):
        """Record a mouse click."""
        self.step += 1
        self.session.statistics['total_steps'] += 1
        self.session.statistics['clicks'] += 1
        
        img_path = self._capture_and_highlight(x, y)
        
        step_data = {
            'step_number': self.step,
            'timestamp': datetime.now(),
            'type': 'click',
            'content': f"Click {button} at ({x},{y})",
            'application': self.get_active_window_title(),
            'screenshot': img_path,
            'coordinates': (x, y),
            'button': str(button)
        }
        
        self.session.steps.append(step_data)
        self.session.screenshots.append(img_path)
        self.session.statistics['applications'].add(step_data['application'])
        
        # Notify step recorded
        if self.on_step_recorded:
            self.on_step_recorded(step_data)
        if self.on_statistics_updated:
            self.on_statistics_updated(self.session.statistics)

    def process_queue(self):
        """Process the event queue."""
        while not self.queue.empty():
            kind, *data = self.queue.get()
            if kind == "click":
                x, y, button = data
                self._record_click(x, y, button)

    def _keystrokes_to_text(self, keystrokes: List[keyboard.Key]) -> str:
        """Convert keystrokes to readable text."""
        text_parts = []
        for key in keystrokes:
            key_name = self._key_to_name(key)
            if self._is_safe_for_xml(key_name) and key_name not in ['Char(19)', 'Ctrl_L', 'Shift_L', 'Alt_L']:
                text_parts.append(key_name)
        
        if not text_parts:
            special_keys = []
            for key in keystrokes:
                key_name = self._key_to_name(key)
                if key_name in ['Enter', 'Space', 'Tab', 'Backspace', 'Delete', 'Escape']:
                    special_keys.append(key_name)
            
            if special_keys:
                return f"Pressed: {', '.join(special_keys)}"
            else:
                return "Special keys pressed"
        
        return "".join(text_parts)

    def _is_safe_for_xml(self, text: str) -> bool:
        """Check if text is safe for XML."""
        if not text:
            return False
        
        for char in text:
            if ord(char) < 32 and char not in '\t\n\r':
                return False
            if ord(char) > 127 and not char.isprintable():
                return False
        
        return True

    @staticmethod
    def _key_to_name(key: keyboard.Key) -> str:
        """Convert key to readable name."""
        if hasattr(key, "char") and key.char is not None:
            if key.char == " ":
                return "Space"
            elif key.char.isprintable():
                return key.char
            else:
                return f"Char({ord(key.char)})"
        
        key_str = str(key).replace("Key.", "").replace("'", "").title()
        
        key_mapping = {
            "Enter": "Enter", "Space": "Space", "Tab": "Tab",
            "Backspace": "Backspace", "Delete": "Delete", "Escape": "Escape",
            "Shift": "Shift", "Shift_L": "Shift", "Shift_R": "Shift",
            "Ctrl": "Ctrl", "Ctrl_L": "Ctrl", "Ctrl_R": "Ctrl",
            "Alt": "Alt", "Alt_L": "Alt", "Alt_R": "Alt",
            "Up": "Up Arrow", "Down": "Down Arrow", 
            "Left": "Left Arrow", "Right": "Right Arrow"
        }
        
        return key_mapping.get(key_str, key_str)

    def _capture_and_highlight(self, x: int, y: int, key=None) -> str:
        """Capture screenshot with highlight."""
        img = ImageGrab.grab()
        draw = ImageDraw.Draw(img)
        r = 30
        draw.ellipse((x - r, y - r, x + r, y + r), outline="red", width=5)
        
        if key is not None:
            kname = self._key_to_name(key)
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except Exception:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), kname, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            box = [(x - r, y - r - th - 10), (x - r + tw + 10, y - r)]
            draw.rectangle(box, fill=(255, 255, 0, 128))
            draw.text((box[0][0] + 5, box[0][1] + 5), kname, fill="black", font=font)

        path = os.path.abspath(f"step_{self.step:04d}.png")
        img.save(path)
        self.outputs.append(path)
        return path

    @staticmethod
    def get_active_window_title() -> str:
        """Get active window title."""
        if win32gui:
            try:
                hwnd = win32gui.GetForegroundWindow()
                title = win32gui.GetWindowText(hwnd)
                return title or "Unknown App"
            except Exception:
                return "Unknown App"
        return "Unknown App"

    def cleanup(self):
        """Clean up resources."""
        if self.recording:
            self.stop_recording()
        
        # Cleanup screenshots
        for f in self.outputs:
            try:
                os.remove(f)
            except FileNotFoundError:
                pass 