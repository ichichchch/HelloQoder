"""GLIMMER configuration module."""

from glimmer_web.config.prompts import SYSTEM_PROMPT, get_system_prompt
from glimmer_web.config.timing import TIMING_CONFIG

__all__ = [
    "SYSTEM_PROMPT",
    "get_system_prompt",
    "TIMING_CONFIG",
]
