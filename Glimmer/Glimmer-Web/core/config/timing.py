"""Timing configuration for GLIMMER actions."""

from dataclasses import dataclass


@dataclass
class ActionTiming:
    """Timing settings for action execution."""
    
    # Click delays
    click_delay: float = 0.1
    double_click_interval: float = 0.1
    
    # Type delays
    type_interval: float = 0.02
    type_after_delay: float = 0.2
    
    # Scroll delays
    scroll_delay: float = 0.3
    
    # Wait defaults
    default_wait: float = 2.0
    page_load_wait: float = 3.0
    
    # Navigation
    navigation_wait: float = 5.0
    
    # Screenshot
    screenshot_delay: float = 0.5  # Wait after action before screenshot


@dataclass
class TimingConfig:
    """Global timing configuration."""
    
    action: ActionTiming = None
    
    def __post_init__(self):
        if self.action is None:
            self.action = ActionTiming()


# Global timing configuration instance
TIMING_CONFIG = TimingConfig()
