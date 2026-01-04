"""Desktop automation module for GLIMMER."""

from core.desktop.screenshot import get_screenshot, Screenshot
from core.desktop.input import (
    click,
    double_click,
    right_click,
    type_text,
    press_key,
    scroll,
    move_to,
)

__all__ = [
    "get_screenshot",
    "Screenshot",
    "click",
    "double_click",
    "right_click",
    "type_text",
    "press_key",
    "scroll",
    "move_to",
]
