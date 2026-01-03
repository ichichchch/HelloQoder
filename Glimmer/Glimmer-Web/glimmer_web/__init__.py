"""
GLIMMER Web - GUI Automation Agent Backend

GLIMMER is an intelligent GUI Agent that can perceive computer/mobile screens
and perform precise actions to help users achieve their goals.
"""

from glimmer_web.agent import GlimmerAgent, AgentConfig
from glimmer_web.actions.handler import ActionHandler
from glimmer_web.model.client import ModelClient, ModelConfig

__all__ = [
    "GlimmerAgent",
    "AgentConfig",
    "ActionHandler",
    "ModelClient",
    "ModelConfig",
]

__version__ = "0.1.0"
