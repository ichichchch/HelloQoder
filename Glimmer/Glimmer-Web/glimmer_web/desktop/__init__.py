"""Desktop automation module for GLIMMER."""

from glimmer_web.desktop.screenshot import get_screenshot, Screenshot
from glimmer_web.desktop.input import (
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
