"""Input control for desktop automation (mouse and keyboard)."""

import time
from typing import Optional, Literal

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

if PYAUTOGUI_AVAILABLE:
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1


def _check_pyautogui():
    if not PYAUTOGUI_AVAILABLE:
        raise RuntimeError("pyautogui is not installed. pip install pyautogui")


def _relative_to_absolute(x: int, y: int) -> tuple[int, int]:
    """Convert relative coordinates [0-1000] to absolute screen pixels."""
    _check_pyautogui()
    screen_width, screen_height = pyautogui.size()
    return int(x / 1000 * screen_width), int(y / 1000 * screen_height)


def click(x: int, y: int, relative: bool = True, 
          button: Literal["left", "right", "middle"] = "left",
          clicks: int = 1, interval: float = 0.0) -> None:
    """Click at the specified coordinates."""
    _check_pyautogui()
    if relative:
        x, y = _relative_to_absolute(x, y)
    pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=interval)


def double_click(x: int, y: int, relative: bool = True) -> None:
    """Double-click at the specified coordinates."""
    click(x, y, relative=relative, clicks=2, interval=0.1)


def right_click(x: int, y: int, relative: bool = True) -> None:
    """Right-click at the specified coordinates."""
    click(x, y, relative=relative, button="right")


def move_to(x: int, y: int, relative: bool = True, duration: float = 0.0) -> None:
    """Move the mouse to the specified coordinates."""
    _check_pyautogui()
    if relative:
        x, y = _relative_to_absolute(x, y)
    pyautogui.moveTo(x=x, y=y, duration=duration)


def type_text(text: str, interval: float = 0.0, press_enter: bool = False) -> None:
    """Type text using the keyboard."""
    _check_pyautogui()
    pyautogui.write(text, interval=interval)
    if press_enter:
        time.sleep(0.1)
        pyautogui.press("enter")


def press_key(key: str) -> None:
    """Press a keyboard key or key combination."""
    _check_pyautogui()
    if "+" in key:
        keys = [k.strip().lower() for k in key.split("+")]
        key_map = {"ctrl": "ctrl", "control": "ctrl", "alt": "alt", "shift": "shift",
                   "win": "win", "cmd": "command", "esc": "escape"}
        keys = [key_map.get(k, k) for k in keys]
        pyautogui.hotkey(*keys)
    else:
        pyautogui.press(key.lower())


def scroll(direction: Literal["up", "down", "left", "right"], amount: int = 3,
           x: Optional[int] = None, y: Optional[int] = None, relative: bool = True) -> None:
    """Scroll in the specified direction."""
    _check_pyautogui()
    if x is not None and y is not None:
        if relative:
            x, y = _relative_to_absolute(x, y)
        pyautogui.moveTo(x=x, y=y)
    
    scroll_amount = amount * 100
    if direction == "up":
        pyautogui.scroll(scroll_amount)
    elif direction == "down":
        pyautogui.scroll(-scroll_amount)
    elif direction == "left":
        pyautogui.hscroll(-scroll_amount)
    elif direction == "right":
        pyautogui.hscroll(scroll_amount)


def drag(start_x: int, start_y: int, end_x: int, end_y: int,
         relative: bool = True, duration: float = 0.5,
         button: Literal["left", "right", "middle"] = "left") -> None:
    """Drag from start coordinates to end coordinates."""
    _check_pyautogui()
    if relative:
        start_x, start_y = _relative_to_absolute(start_x, start_y)
        end_x, end_y = _relative_to_absolute(end_x, end_y)
    pyautogui.moveTo(start_x, start_y)
    time.sleep(0.1)
    pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration, button=button)
