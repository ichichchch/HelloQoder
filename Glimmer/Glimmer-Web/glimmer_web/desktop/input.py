"""Input control for desktop automation (mouse and keyboard)."""

import time
from typing import Optional, Literal

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

# Configure pyautogui for safety
if PYAUTOGUI_AVAILABLE:
    pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    pyautogui.PAUSE = 0.1  # Add small delay between actions


def _check_pyautogui():
    """Check if pyautogui is available."""
    if not PYAUTOGUI_AVAILABLE:
        raise RuntimeError(
            "pyautogui is not installed. "
            "Please install it with: pip install pyautogui"
        )


def _relative_to_absolute(x: int, y: int) -> tuple[int, int]:
    """
    Convert relative coordinates [0-1000] to absolute screen pixels.
    
    Args:
        x: Relative X coordinate (0-1000)
        y: Relative Y coordinate (0-1000)
    
    Returns:
        Tuple of (absolute_x, absolute_y) in pixels.
    """
    _check_pyautogui()
    screen_width, screen_height = pyautogui.size()
    abs_x = int(x / 1000 * screen_width)
    abs_y = int(y / 1000 * screen_height)
    return abs_x, abs_y


def click(
    x: int,
    y: int,
    relative: bool = True,
    button: Literal["left", "right", "middle"] = "left",
    clicks: int = 1,
    interval: float = 0.0,
) -> None:
    """
    Click at the specified coordinates.
    
    Args:
        x: X coordinate (relative 0-1000 or absolute pixels).
        y: Y coordinate (relative 0-1000 or absolute pixels).
        relative: If True, coordinates are relative [0-1000].
        button: Mouse button to click ("left", "right", "middle").
        clicks: Number of clicks.
        interval: Time between clicks in seconds.
    """
    _check_pyautogui()
    
    if relative:
        x, y = _relative_to_absolute(x, y)
    
    pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=interval)


def double_click(x: int, y: int, relative: bool = True) -> None:
    """
    Double-click at the specified coordinates.
    
    Args:
        x: X coordinate (relative 0-1000 or absolute pixels).
        y: Y coordinate (relative 0-1000 or absolute pixels).
        relative: If True, coordinates are relative [0-1000].
    """
    click(x, y, relative=relative, clicks=2, interval=0.1)


def right_click(x: int, y: int, relative: bool = True) -> None:
    """
    Right-click at the specified coordinates.
    
    Args:
        x: X coordinate (relative 0-1000 or absolute pixels).
        y: Y coordinate (relative 0-1000 or absolute pixels).
        relative: If True, coordinates are relative [0-1000].
    """
    click(x, y, relative=relative, button="right")


def move_to(x: int, y: int, relative: bool = True, duration: float = 0.0) -> None:
    """
    Move the mouse to the specified coordinates.
    
    Args:
        x: X coordinate (relative 0-1000 or absolute pixels).
        y: Y coordinate (relative 0-1000 or absolute pixels).
        relative: If True, coordinates are relative [0-1000].
        duration: Time to move in seconds (for smooth movement).
    """
    _check_pyautogui()
    
    if relative:
        x, y = _relative_to_absolute(x, y)
    
    pyautogui.moveTo(x=x, y=y, duration=duration)


def type_text(
    text: str,
    interval: float = 0.0,
    press_enter: bool = False,
) -> None:
    """
    Type text using the keyboard.
    
    Args:
        text: Text to type.
        interval: Time between key presses in seconds.
        press_enter: If True, press Enter after typing.
    """
    _check_pyautogui()
    
    # Use write for ASCII text, typewrite for compatibility
    pyautogui.write(text, interval=interval)
    
    if press_enter:
        time.sleep(0.1)
        pyautogui.press("enter")


def press_key(key: str) -> None:
    """
    Press a keyboard key or key combination.
    
    Args:
        key: Key name or combination (e.g., "enter", "ctrl+c", "alt+tab").
             For combinations, use "+" to separate modifiers.
    
    Examples:
        press_key("enter")
        press_key("ctrl+c")
        press_key("alt+f4")
        press_key("ctrl+shift+s")
    """
    _check_pyautogui()
    
    # Handle key combinations
    if "+" in key:
        keys = key.lower().split("+")
        keys = [k.strip() for k in keys]
        
        # Map common key names
        key_map = {
            "ctrl": "ctrl",
            "control": "ctrl",
            "alt": "alt",
            "shift": "shift",
            "win": "win",
            "windows": "win",
            "cmd": "command",
            "command": "command",
            "esc": "escape",
            "escape": "escape",
            "del": "delete",
            "delete": "delete",
            "ins": "insert",
            "insert": "insert",
            "pgup": "pageup",
            "pageup": "pageup",
            "pgdn": "pagedown",
            "pagedown": "pagedown",
        }
        
        keys = [key_map.get(k, k) for k in keys]
        
        # Use hotkey for combinations
        pyautogui.hotkey(*keys)
    else:
        # Single key press
        pyautogui.press(key.lower())


def scroll(
    direction: Literal["up", "down", "left", "right"],
    amount: int = 3,
    x: Optional[int] = None,
    y: Optional[int] = None,
    relative: bool = True,
) -> None:
    """
    Scroll in the specified direction.
    
    Args:
        direction: Direction to scroll ("up", "down", "left", "right").
        amount: Number of scroll units (1-10 recommended).
        x: Optional X coordinate for scroll location.
        y: Optional Y coordinate for scroll location.
        relative: If True, coordinates are relative [0-1000].
    """
    _check_pyautogui()
    
    # Move to position if specified
    if x is not None and y is not None:
        if relative:
            x, y = _relative_to_absolute(x, y)
        pyautogui.moveTo(x=x, y=y)
    
    # Scroll amount (positive = up/right, negative = down/left)
    scroll_amount = amount * 100  # Scale for smooth scrolling
    
    if direction == "up":
        pyautogui.scroll(scroll_amount)
    elif direction == "down":
        pyautogui.scroll(-scroll_amount)
    elif direction == "left":
        pyautogui.hscroll(-scroll_amount)
    elif direction == "right":
        pyautogui.hscroll(scroll_amount)


def drag(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    relative: bool = True,
    duration: float = 0.5,
    button: Literal["left", "right", "middle"] = "left",
) -> None:
    """
    Drag from start coordinates to end coordinates.
    
    Args:
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        end_x: Ending X coordinate.
        end_y: Ending Y coordinate.
        relative: If True, coordinates are relative [0-1000].
        duration: Time to complete the drag in seconds.
        button: Mouse button to use for dragging.
    """
    _check_pyautogui()
    
    if relative:
        start_x, start_y = _relative_to_absolute(start_x, start_y)
        end_x, end_y = _relative_to_absolute(end_x, end_y)
    
    # Move to start position
    pyautogui.moveTo(start_x, start_y)
    time.sleep(0.1)
    
    # Perform drag
    pyautogui.drag(
        end_x - start_x,
        end_y - start_y,
        duration=duration,
        button=button,
    )
