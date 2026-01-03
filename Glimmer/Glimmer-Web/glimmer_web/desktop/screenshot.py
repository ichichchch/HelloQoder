"""Screenshot capture for desktop automation."""

import base64
import io
from dataclasses import dataclass
from typing import Optional

try:
    import pyautogui
    from PIL import Image
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


@dataclass
class Screenshot:
    """Container for screenshot data."""
    
    width: int
    height: int
    base64_data: str
    image: Optional[any] = None
    
    @classmethod
    def from_pil_image(cls, img: "Image.Image") -> "Screenshot":
        """Create Screenshot from PIL Image."""
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return cls(width=img.width, height=img.height, base64_data=base64_data, image=img)


def get_screenshot(region: Optional[tuple[int, int, int, int]] = None) -> Screenshot:
    """Capture a screenshot of the screen."""
    if not PYAUTOGUI_AVAILABLE:
        raise RuntimeError("pyautogui is not installed. pip install pyautogui pillow")
    
    if region:
        img = pyautogui.screenshot(region=region)
    else:
        img = pyautogui.screenshot()
    
    return Screenshot.from_pil_image(img)


def get_screen_size() -> tuple[int, int]:
    """Get the screen dimensions."""
    if not PYAUTOGUI_AVAILABLE:
        raise RuntimeError("pyautogui is not installed.")
    return pyautogui.size()
