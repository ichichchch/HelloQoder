"""Timing configuration for GLIMMER actions."""

from dataclasses import dataclass


@dataclass
class ActionTiming:
    """Timing settings for action execution."""
    
    click_delay: float = 0.1
    double_click_interval: float = 0.1
    type_interval: float = 0.02
    type_after_delay: float = 0.2
    scroll_delay: float = 0.3
    default_wait: float = 2.0
    page_load_wait: float = 3.0
    navigation_wait: float = 5.0
    screenshot_delay: float = 0.5


@dataclass
class TimingConfig:
    """Global timing configuration."""
    
    action: ActionTiming = None
    
    def __post_init__(self):
        if self.action is None:
            self.action = ActionTiming()


TIMING_CONFIG = TimingConfig()
