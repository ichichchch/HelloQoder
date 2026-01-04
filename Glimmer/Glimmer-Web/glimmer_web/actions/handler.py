"""
Action handler for GLIMMER GUI Agent.

Handles execution of actions based on System.md specification:
- CLICK: Click on a specific point
- TYPE: Type text into focused field
- SCROLL: Scroll the page
- WAIT: Wait for page load or animation
- NAVIGATE: Go to a URL (Browser only)
- FINISH: Task completed or impossible to proceed
"""

import json
import time
import webbrowser
from dataclasses import dataclass
from typing import Any, Callable, Literal, Optional

from glimmer_web.config.timing import TIMING_CONFIG
from glimmer_web.desktop import (
    click,
    double_click,
    right_click,
    type_text,
    press_key,
    scroll,
    get_screenshot,
)


@dataclass
class ActionResult:
    """Result of an action execution."""
    
    success: bool
    should_finish: bool
    message: Optional[str] = None
    screenshot_after: Optional[Any] = None  # Screenshot after action


class ActionHandler:
    """
    Handles execution of actions from AI model output.
    
    Supports actions defined in System.md:
    - CLICK, TYPE, SCROLL, WAIT, NAVIGATE, FINISH
    
    Also supports extended actions from Agent.md:
    - click, double_click, right_click, type, scroll, key, wait
    """
    
    def __init__(
        self,
        confirmation_callback: Optional[Callable[[str], bool]] = None,
        capture_after_action: bool = True,
    ):
        """
        Initialize the action handler.
        
        Args:
            confirmation_callback: Optional callback for sensitive action confirmation.
            capture_after_action: Whether to capture screenshot after each action.
        """
        self.confirmation_callback = confirmation_callback or self._default_confirmation
        self.capture_after_action = capture_after_action
    
    def execute(self, action: dict[str, Any]) -> ActionResult:
        """
        Execute an action from the AI model.
        
        Args:
            action: The action dictionary from the model.
                   Expected format: {"action_type": "...", "params": {...}}
        
        Returns:
            ActionResult indicating success and whether to finish.
        """
        # Support both System.md format and Agent.md format
        action_type = action.get("action_type") or action.get("action")
        params = action.get("params", {})
        
        if action_type is None:
            return ActionResult(
                success=False,
                should_finish=False,
                message="No action_type specified",
            )
        
        # Normalize action type to uppercase
        action_type_upper = action_type.upper()
        
        # Get handler method
        handler_method = self._get_handler(action_type_upper)
        
        if handler_method is None:
            # Try lowercase handlers (Agent.md format)
            handler_method = self._get_handler_lowercase(action_type.lower())
        
        if handler_method is None:
            return ActionResult(
                success=False,
                should_finish=False,
                message=f"Unknown action type: {action_type}",
            )
        
        try:
            result = handler_method(params)
            
            # Capture screenshot after action if enabled
            if self.capture_after_action and not result.should_finish:
                time.sleep(TIMING_CONFIG.action.screenshot_delay)
                try:
                    result.screenshot_after = get_screenshot()
                except Exception:
                    pass  # Ignore screenshot errors
            
            return result
            
        except Exception as e:
            return ActionResult(
                success=False,
                should_finish=False,
                message=f"Action failed: {e}",
            )
    
    def _get_handler(self, action_type: str) -> Optional[Callable]:
        """Get the handler method for System.md action types."""
        handlers = {
            "CLICK": self._handle_click,
            "TYPE": self._handle_type,
            "SCROLL": self._handle_scroll,
            "WAIT": self._handle_wait,
            "NAVIGATE": self._handle_navigate,
            "FINISH": self._handle_finish,
        }
        return handlers.get(action_type)
    
    def _get_handler_lowercase(self, action_type: str) -> Optional[Callable]:
        """Get the handler method for Agent.md action types."""
        handlers = {
            "click": self._handle_click_simple,
            "double_click": self._handle_double_click,
            "right_click": self._handle_right_click,
            "type": self._handle_type_simple,
            "scroll": self._handle_scroll_simple,
            "key": self._handle_key,
            "wait": self._handle_wait_simple,
        }
        return handlers.get(action_type)
    
    # ==================== System.md Handlers ====================
    
    def _handle_click(self, params: dict) -> ActionResult:
        """
        Handle CLICK action (System.md format).
        
        Params:
            box_2d: [x1, y1, x2, y2] - Bounding box of element to click.
        """
        box_2d = params.get("box_2d")
        if not box_2d or len(box_2d) != 4:
            return ActionResult(False, False, "Invalid box_2d parameter")
        
        # Calculate center point of the bounding box
        x1, y1, x2, y2 = box_2d
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        click(center_x, center_y, relative=True)
        time.sleep(TIMING_CONFIG.action.click_delay)
        
        return ActionResult(True, False)
    
    def _handle_type(self, params: dict) -> ActionResult:
        """
        Handle TYPE action (System.md format).
        
        Params:
            box_2d: Optional [x1, y1, x2, y2] - Click to focus first.
            text: String content to type.
            submit: Boolean - Press Enter after typing.
        """
        text = params.get("text", "")
        submit = params.get("submit", False)
        box_2d = params.get("box_2d")
        
        # Click to focus if box_2d is provided
        if box_2d and len(box_2d) == 4:
            x1, y1, x2, y2 = box_2d
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            click(center_x, center_y, relative=True)
            time.sleep(TIMING_CONFIG.action.click_delay)
        
        # Type the text
        type_text(text, interval=TIMING_CONFIG.action.type_interval, press_enter=submit)
        time.sleep(TIMING_CONFIG.action.type_after_delay)
        
        return ActionResult(True, False)
    
    def _handle_scroll(self, params: dict) -> ActionResult:
        """
        Handle SCROLL action (System.md format).
        
        Params:
            direction: "up" | "down"
            distance: null for one page, or "long"
        """
        direction = params.get("direction", "down")
        distance = params.get("distance")
        
        # Determine scroll amount
        if distance == "long":
            amount = 10
        else:
            amount = 3  # Default one page
        
        scroll(direction=direction, amount=amount)
        time.sleep(TIMING_CONFIG.action.scroll_delay)
        
        return ActionResult(True, False)
    
    def _handle_wait(self, params: dict) -> ActionResult:
        """
        Handle WAIT action (System.md format).
        
        Params:
            seconds: int - Number of seconds to wait.
        """
        seconds = params.get("seconds", TIMING_CONFIG.action.default_wait)
        time.sleep(seconds)
        
        return ActionResult(True, False)
    
    def _handle_navigate(self, params: dict) -> ActionResult:
        """
        Handle NAVIGATE action (System.md format).
        
        Params:
            url: String - URL to navigate to.
        """
        url = params.get("url", "")
        if not url:
            return ActionResult(False, False, "No URL provided")
        
        # Ensure URL has protocol
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            webbrowser.open(url)
            time.sleep(TIMING_CONFIG.action.navigation_wait)
            return ActionResult(True, False)
        except Exception as e:
            return ActionResult(False, False, f"Failed to navigate: {e}")
    
    def _handle_finish(self, params: dict) -> ActionResult:
        """
        Handle FINISH action (System.md format).
        
        Params:
            status: "success" | "failure"
            summary: String - Summary of what was accomplished.
        """
        status = params.get("status", "success")
        summary = params.get("summary", "Task completed")
        
        success = status == "success"
        return ActionResult(
            success=success,
            should_finish=True,
            message=summary,
        )
    
    # ==================== Agent.md Handlers ====================
    
    def _handle_click_simple(self, params: dict) -> ActionResult:
        """Handle click action (Agent.md format)."""
        coordinate = params.get("coordinate")
        if not coordinate or len(coordinate) != 2:
            return ActionResult(False, False, "Invalid coordinate parameter")
        
        x, y = coordinate
        click(x, y, relative=True)
        time.sleep(TIMING_CONFIG.action.click_delay)
        
        return ActionResult(True, False)
    
    def _handle_double_click(self, params: dict) -> ActionResult:
        """Handle double_click action (Agent.md format)."""
        coordinate = params.get("coordinate")
        if not coordinate or len(coordinate) != 2:
            return ActionResult(False, False, "Invalid coordinate parameter")
        
        x, y = coordinate
        double_click(x, y, relative=True)
        time.sleep(TIMING_CONFIG.action.click_delay)
        
        return ActionResult(True, False)
    
    def _handle_right_click(self, params: dict) -> ActionResult:
        """Handle right_click action (Agent.md format)."""
        coordinate = params.get("coordinate")
        if not coordinate or len(coordinate) != 2:
            return ActionResult(False, False, "Invalid coordinate parameter")
        
        x, y = coordinate
        right_click(x, y, relative=True)
        time.sleep(TIMING_CONFIG.action.click_delay)
        
        return ActionResult(True, False)
    
    def _handle_type_simple(self, params: dict) -> ActionResult:
        """Handle type action (Agent.md format)."""
        text = params.get("text", "")
        enter = params.get("enter", False)
        
        type_text(text, interval=TIMING_CONFIG.action.type_interval, press_enter=enter)
        time.sleep(TIMING_CONFIG.action.type_after_delay)
        
        return ActionResult(True, False)
    
    def _handle_scroll_simple(self, params: dict) -> ActionResult:
        """Handle scroll action (Agent.md format)."""
        direction = params.get("direction", "down")
        step = params.get("step", 3)
        
        scroll(direction=direction, amount=step)
        time.sleep(TIMING_CONFIG.action.scroll_delay)
        
        return ActionResult(True, False)
    
    def _handle_key(self, params: dict) -> ActionResult:
        """Handle key action (Agent.md format)."""
        key_name = params.get("key_name", "")
        if not key_name:
            return ActionResult(False, False, "No key_name provided")
        
        press_key(key_name)
        time.sleep(TIMING_CONFIG.action.click_delay)
        
        return ActionResult(True, False)
    
    def _handle_wait_simple(self, params: dict) -> ActionResult:
        """Handle wait action (Agent.md format)."""
        seconds = params.get("seconds", TIMING_CONFIG.action.default_wait)
        time.sleep(seconds)
        
        return ActionResult(True, False)
    
    @staticmethod
    def _default_confirmation(message: str) -> bool:
        """Default confirmation callback using console input."""
        response = input(f"Confirm action: {message}\n(Y/N): ")
        return response.upper() == "Y"


def parse_action(response: str) -> dict[str, Any]:
    """
    Parse action from model response.
    
    Args:
        response: Raw response string from the model (should be JSON).
    
    Returns:
        Parsed action dictionary.
    
    Raises:
        ValueError: If the response cannot be parsed as JSON.
    """
    response = response.strip()
    
    # Remove markdown code blocks if present
    if response.startswith("```json"):
        response = response[7:]
    if response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]
    
    response = response.strip()
    
    try:
        action = json.loads(response)
        return action
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse action as JSON: {e}")
