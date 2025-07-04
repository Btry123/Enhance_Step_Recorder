import time
from collections import deque, Counter
from typing import List, Tuple, Dict, Any

class Analytics:
    """Mouse & keyboard analytics: movement, drag, scroll, shortcuts, typing speed, errors."""
    def __init__(self):
        self.mouse_moves: List[Tuple[float, int, int]] = []  # (timestamp, x, y)
        self.mouse_drags: List[Tuple[float, int, int]] = []
        self.mouse_scrolls: List[Tuple[float, int, int, int]] = []  # (timestamp, x, y, delta)
        self.keyboard_events: List[Tuple[float, str]] = []  # (timestamp, key)
        self.shortcut_events: List[Tuple[float, str]] = []
        self.typing_times: deque = deque(maxlen=20)
        self.last_key_time: float = 0
        self.error_patterns: List[str] = []
        self.backspace_count: int = 0

    def record_mouse_move(self, x: int, y: int):
        self.mouse_moves.append((time.time(), x, y))

    def record_mouse_drag(self, x: int, y: int):
        self.mouse_drags.append((time.time(), x, y))

    def record_mouse_scroll(self, x: int, y: int, delta: int):
        self.mouse_scrolls.append((time.time(), x, y, delta))

    def record_key(self, key: str):
        now = time.time()
        self.keyboard_events.append((now, key))
        # Typing speed
        if self.last_key_time:
            self.typing_times.append(now - self.last_key_time)
        self.last_key_time = now
        # Error pattern: backspace
        if key.lower() == 'backspace':
            self.backspace_count += 1
            if self.backspace_count > 3:
                self.error_patterns.append(f"Repeated backspace at {time.strftime('%H:%M:%S', time.localtime(now))}")
        else:
            self.backspace_count = 0
        # Shortcut detection
        self._detect_shortcut()

    def _detect_shortcut(self):
        # Look for recent Ctrl/Alt/Shift + key combos
        if len(self.keyboard_events) < 2:
            return
        last_two = self.keyboard_events[-2:]
        keys = [k for t, k in last_two]
        if ('ctrl' in keys[0].lower() or 'alt' in keys[0].lower() or 'shift' in keys[0].lower()) and len(keys[1]) == 1:
            combo = f"{keys[0]}+{keys[1]}"
            self.shortcut_events.append((time.time(), combo))

    def get_typing_speed(self) -> float:
        if not self.typing_times:
            return 0.0
        avg = sum(self.typing_times) / len(self.typing_times)
        return 1.0 / avg if avg > 0 else 0.0  # chars per second

    def get_mouse_distance(self) -> float:
        if len(self.mouse_moves) < 2:
            return 0.0
        dist = 0.0
        for i in range(1, len(self.mouse_moves)):
            _, x1, y1 = self.mouse_moves[i-1]
            _, x2, y2 = self.mouse_moves[i]
            dist += ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
        return dist

    def get_shortcut_counts(self) -> Dict[str, int]:
        combos = [combo for t, combo in self.shortcut_events]
        return dict(Counter(combos))

    def get_error_patterns(self) -> List[str]:
        return self.error_patterns.copy()

    def get_summary(self) -> Dict[str, Any]:
        return {
            'typing_speed_cps': round(self.get_typing_speed(), 2),
            'mouse_distance_px': int(self.get_mouse_distance()),
            'shortcut_counts': self.get_shortcut_counts(),
            'error_patterns': self.get_error_patterns(),
            'mouse_moves': len(self.mouse_moves),
            'mouse_drags': len(self.mouse_drags),
            'mouse_scrolls': len(self.mouse_scrolls),
        } 