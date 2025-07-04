import os
from typing import Optional, Tuple
from PIL import ImageGrab, ImageDraw, ImageFont

try:
    import win32gui
except ImportError:
    win32gui = None

class SmartCapture:
    """Smart screenshot logic: window change, before/after, password masking."""
    def __init__(self):
        self.last_window_title: Optional[str] = None
        self.last_screenshot: Optional[str] = None

    def should_capture(self, event_type: str, current_window_title: str) -> bool:
        """Decide if a screenshot should be taken based on event and window change."""
        # Always capture on click or keystroke
        if event_type in ("click", "keystroke"):
            return True
        # Capture if window changed
        if self.last_window_title != current_window_title:
            self.last_window_title = current_window_title
            return True
        return False

    def capture_screen(self, x: int, y: int, highlight: bool = True, mask_password: bool = False, password_box: Optional[Tuple[int, int, int, int]] = None) -> str:
        """Capture screenshot, optionally highlight and mask password fields."""
        img = ImageGrab.grab()
        draw = ImageDraw.Draw(img)
        r = 30
        if highlight:
            draw.ellipse((x - r, y - r, x + r, y + r), outline="red", width=5)
        if mask_password and password_box:
            draw.rectangle(password_box, fill=(0, 0, 0))
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except Exception:
                font = ImageFont.load_default()
            pw_text = "***"
            tw, th = draw.textsize(pw_text, font=font)
            px, py, _, _ = password_box
            draw.text((px + 5, py + 5), pw_text, fill="white", font=font)
        path = os.path.abspath(f"smartcap_{id(self)}.png")
        img.save(path)
        self.last_screenshot = path
        return path

    def detect_password_field(self, window_title: str, keystrokes: list) -> bool:
        """Basic heuristic: if window title or keystrokes suggest password entry."""
        # This is a naive check; real detection would require UI automation
        if "password" in window_title.lower():
            return True
        # If many asterisks or dots typed
        if keystrokes and all(k in ('*', '•', '.') for k in keystrokes[-5:]):
            return True
        return False

    @staticmethod
    def get_active_window_title() -> str:
        if win32gui:
            try:
                hwnd = win32gui.GetForegroundWindow()
                title = win32gui.GetWindowText(hwnd)
                return title or "Unknown App"
            except Exception:
                return "Unknown App"
        return "Unknown App" 