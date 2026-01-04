"""
GLIMMER - GUI Automation Agent powered by Vision-Language Models.

GLIMMER is an intelligent GUI Agent that can perceive computer/mobile screens
and perform precise actions to help users achieve their goals.

Based on the Open-AutoGLM framework, extended for desktop/browser automation.
"""

from core.agent import GlimmerAgent, AgentConfig
from core.actions.handler import ActionHandler
from core.model.client import ModelClient, ModelConfig

__all__ = [
    "GlimmerAgent",
    "AgentConfig",
    "ActionHandler",
    "ModelClient",
    "ModelConfig",
]

__version__ = "0.1.0"
