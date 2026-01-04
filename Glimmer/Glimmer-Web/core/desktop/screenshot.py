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
    image: Optional[any] = None  # PIL Image object
    
    @classmethod
    def from_pil_image(cls, img: "Image.Image") -> "Screenshot":
        """Create Screenshot from PIL Image."""
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return cls(
            width=img.width,
            height=img.height,
            base64_data=base64_data,
            image=img,
        )


def get_screenshot(region: Optional[tuple[int, int, int, int]] = None) -> Screenshot:
    """
    Capture a screenshot of the screen.
    
    Args:
        region: Optional tuple of (left, top, width, height) for partial capture.
                If None, captures the entire screen.
    
    Returns:
        Screenshot object containing the captured image data.
    
    Raises:
        RuntimeError: If pyautogui is not available.
    """
    if not PYAUTOGUI_AVAILABLE:
        raise RuntimeError(
            "pyautogui is not installed. "
            "Please install it with: pip install pyautogui pillow"
        )
    
    # Capture screenshot
    if region:
        img = pyautogui.screenshot(region=region)
    else:
        img = pyautogui.screenshot()
    
    return Screenshot.from_pil_image(img)


def get_screen_size() -> tuple[int, int]:
    """
    Get the screen dimensions.
    
    Returns:
        Tuple of (width, height) in pixels.
    """
    if not PYAUTOGUI_AVAILABLE:
        raise RuntimeError("pyautogui is not installed.")
    
    return pyautogui.size()
