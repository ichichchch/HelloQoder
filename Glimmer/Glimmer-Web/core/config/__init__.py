"""GLIMMER configuration module."""

from core.config.prompts import SYSTEM_PROMPT, get_system_prompt
from core.config.timing import TIMING_CONFIG

__all__ = [
    "SYSTEM_PROMPT",
    "get_system_prompt",
    "TIMING_CONFIG",
]
