"""
GLIMMER Agent - Main orchestration class for desktop GUI automation.

Based on System.md specification, this agent:
1. Captures screenshots of the current screen state
2. Sends them to a Vision-Language Model with the user's goal
3. Receives JSON-formatted action instructions
4. Executes the actions using desktop automation
5. Repeats until the task is complete or max steps reached
"""

import json
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from core.actions.handler import ActionHandler, ActionResult, parse_action
from core.config.prompts import get_system_prompt
from core.desktop.screenshot import get_screenshot
from core.model.client import ModelClient, ModelConfig, MessageBuilder


@dataclass
class AgentConfig:
    """Configuration for the GLIMMER Agent."""
    
    max_steps: int = 50
    lang: str = "en"
    system_prompt: Optional[str] = None
    verbose: bool = True
    capture_after_action: bool = True
    
    def __post_init__(self):
        if self.system_prompt is None:
            self.system_prompt = get_system_prompt(self.lang)


@dataclass
class StepResult:
    """Result of a single agent step."""
    
    success: bool
    finished: bool
    action_type: str
    params: dict[str, Any]
    thought: str
    confidence: str
    message: Optional[str] = None


@dataclass
class HistoryEntry:
    """Entry in the action history."""
    
    step: int
    action_type: str
    params: dict[str, Any]
    result: str  # "success" or "failure" or description


class GlimmerAgent:
    """
    GLIMMER - GUI Automation Agent powered by Vision-Language Models.
    
    The agent perceives computer screens through screenshots and performs
    precise actions to help users achieve their goals.
    
    Args:
        model_config: Configuration for the AI model.
        agent_config: Configuration for the agent behavior.
        confirmation_callback: Optional callback for sensitive action confirmation.
    
    Example:
        >>> from core import GlimmerAgent
        >>> from core.model import ModelConfig
        >>>
        >>> model_config = ModelConfig(base_url="http://localhost:8000/v1")
        >>> agent = GlimmerAgent(model_config)
        >>> agent.run("Search for Python tutorials on Google")
    """
    
    def __init__(
        self,
        model_config: Optional[ModelConfig] = None,
        agent_config: Optional[AgentConfig] = None,
        confirmation_callback: Optional[Callable[[str], bool]] = None,
    ):
        self.model_config = model_config or ModelConfig()
        self.agent_config = agent_config or AgentConfig()
        
        self.model_client = ModelClient(self.model_config)
        self.action_handler = ActionHandler(
            confirmation_callback=confirmation_callback,
            capture_after_action=self.agent_config.capture_after_action,
        )
        
        self._context: list[dict[str, Any]] = []
        self._history: list[HistoryEntry] = []
        self._step_count = 0
    
    def run(self, goal: str) -> str:
        """
        Run the agent to complete a task.
        
        Args:
            goal: Natural language description of the task (GOAL).
        
        Returns:
            Final message from the agent.
        """
        self._context = []
        self._history = []
        self._step_count = 0
        
        if self.agent_config.verbose:
            print("=" * 60)
            print("🤖 GLIMMER - GUI Automation Agent")
            print("=" * 60)
            print(f"📋 GOAL: {goal}")
            print("=" * 60)
        
        # Execute steps until finished or max steps reached
        while self._step_count < self.agent_config.max_steps:
            result = self._execute_step(goal)
            
            if result.finished:
                if self.agent_config.verbose:
                    print()
                    print("🎉 " + "=" * 56)
                    status = "✅ SUCCESS" if result.success else "❌ FAILED"
                    print(f"{status}: {result.message or 'Task completed'}")
                    print("=" * 60)
                
                return result.message or "Task completed"
        
        return f"Max steps ({self.agent_config.max_steps}) reached"
    
    def step(self, goal: Optional[str] = None) -> StepResult:
        """
        Execute a single step of the agent.
        
        Useful for manual control or debugging.
        
        Args:
            goal: Task description (only needed for first step).
        
        Returns:
            StepResult with step details.
        """
        is_first = len(self._context) == 0
        
        if is_first and not goal:
            raise ValueError("Goal is required for the first step")
        
        if goal is None and self._history:
            # Use the goal from history context
            goal = "Continue previous task"
        
        return self._execute_step(goal or "")
    
    def reset(self) -> None:
        """Reset the agent state for a new task."""
        self._context = []
        self._history = []
        self._step_count = 0
    
    def _execute_step(self, goal: str) -> StepResult:
        """Execute a single step of the agent loop."""
        self._step_count += 1
        
        if self.agent_config.verbose:
            print()
            print(f"📸 Step {self._step_count}: Capturing screen...")
        
        # Capture current screen state
        try:
            screenshot = get_screenshot()
        except Exception as e:
            if self.agent_config.verbose:
                print(f"❌ Screenshot failed: {e}")
            return StepResult(
                success=False,
                finished=True,
                action_type="FINISH",
                params={"status": "failure"},
                thought="",
                confidence="LOW",
                message=f"Failed to capture screenshot: {e}",
            )
        
        # Build messages
        is_first = len(self._context) == 0
        
        if is_first:
            # Add system prompt
            self._context.append(
                MessageBuilder.create_system_message(self.agent_config.system_prompt)
            )
        
        # Build user message with GOAL, HISTORY, and SCREENSHOT
        history_list = [
            {"step": h.step, "action": h.action_type, "result": h.result}
            for h in self._history
        ]
        
        text_content = MessageBuilder.build_goal_message(
            goal=goal,
            history=history_list if history_list else None,
        )
        
        self._context.append(
            MessageBuilder.create_user_message(
                text=text_content,
                image_base64=screenshot.base64_data,
            )
        )
        
        # Get model response
        if self.agent_config.verbose:
            print()
            print("💭 Thinking...")
            print("-" * 50)
        
        try:
            response = self.model_client.request(self._context)
        except Exception as e:
            if self.agent_config.verbose:
                traceback.print_exc()
            return StepResult(
                success=False,
                finished=True,
                action_type="FINISH",
                params={"status": "failure"},
                thought="",
                confidence="LOW",
                message=f"Model error: {e}",
            )
        
        if self.agent_config.verbose:
            print("-" * 50)
            print(f"💭 Thought: {response.thought}")
            print(f"🎯 Action: {response.action_type}")
            print(f"📊 Params: {json.dumps(response.params, ensure_ascii=False)}")
            print(f"🔮 Confidence: {response.confidence}")
        
        # Remove image from context to save space
        self._context[-1] = MessageBuilder.remove_images_from_message(self._context[-1])
        
        # Execute action
        action_dict = {
            "action_type": response.action_type,
            "params": response.params,
        }
        
        if self.agent_config.verbose:
            print()
            print(f"⚡ Executing: {response.action_type}...")
        
        try:
            result = self.action_handler.execute(action_dict)
        except Exception as e:
            if self.agent_config.verbose:
                traceback.print_exc()
            result = ActionResult(
                success=False,
                should_finish=False,
                message=str(e),
            )
        
        # Add to history
        self._history.append(HistoryEntry(
            step=self._step_count,
            action_type=response.action_type,
            params=response.params,
            result="success" if result.success else f"failed: {result.message}",
        ))
        
        # Add assistant response to context
        self._context.append(
            MessageBuilder.create_assistant_message(response.raw_content)
        )
        
        if self.agent_config.verbose:
            status = "✅" if result.success else "❌"
            print(f"{status} Action result: {'Success' if result.success else result.message}")
        
        return StepResult(
            success=result.success,
            finished=result.should_finish,
            action_type=response.action_type,
            params=response.params,
            thought=response.thought,
            confidence=response.confidence,
            message=result.message,
        )
    
    @property
    def context(self) -> list[dict[str, Any]]:
        """Get the current conversation context."""
        return self._context.copy()
    
    @property
    def history(self) -> list[HistoryEntry]:
        """Get the action history."""
        return self._history.copy()
    
    @property
    def step_count(self) -> int:
        """Get the current step count."""
        return self._step_count
