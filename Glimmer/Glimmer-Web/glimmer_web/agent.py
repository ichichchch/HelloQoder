"""
GLIMMER Agent - Main orchestration class for desktop GUI automation.
"""

import json
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from glimmer_web.actions.handler import ActionHandler, ActionResult, parse_action
from glimmer_web.config.prompts import get_system_prompt
from glimmer_web.desktop.screenshot import get_screenshot
from glimmer_web.model.client import ModelClient, ModelConfig, MessageBuilder


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
    result: str


class GlimmerAgent:
    """GLIMMER - GUI Automation Agent powered by Vision-Language Models."""
    
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
        """Run the agent to complete a task."""
        self._context = []
        self._history = []
        self._step_count = 0
        
        if self.agent_config.verbose:
            print("=" * 60)
            print("🤖 GLIMMER - GUI Automation Agent")
            print("=" * 60)
            print(f"📋 GOAL: {goal}")
            print("=" * 60)
        
        while self._step_count < self.agent_config.max_steps:
            result = self._execute_step(goal)
            if result.finished:
                if self.agent_config.verbose:
                    status = "✅ SUCCESS" if result.success else "❌ FAILED"
                    print(f"\n🎉 {status}: {result.message or 'Task completed'}")
                return result.message or "Task completed"
        
        return f"Max steps ({self.agent_config.max_steps}) reached"
    
    def step(self, goal: Optional[str] = None) -> StepResult:
        """Execute a single step of the agent."""
        if len(self._context) == 0 and not goal:
            raise ValueError("Goal is required for the first step")
        if goal is None and self._history:
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
            print(f"\n📸 Step {self._step_count}: Capturing screen...")
        
        try:
            screenshot = get_screenshot()
        except Exception as e:
            if self.agent_config.verbose:
                print(f"❌ Screenshot failed: {e}")
            return StepResult(
                success=False, finished=True, action_type="FINISH",
                params={"status": "failure"}, thought="", confidence="LOW",
                message=f"Failed to capture screenshot: {e}",
            )
        
        is_first = len(self._context) == 0
        if is_first:
            self._context.append(MessageBuilder.create_system_message(self.agent_config.system_prompt))
        
        history_list = [
            {"step": h.step, "action": h.action_type, "result": h.result}
            for h in self._history
        ]
        
        text_content = MessageBuilder.build_goal_message(
            goal=goal, history=history_list if history_list else None,
        )
        self._context.append(MessageBuilder.create_user_message(
            text=text_content, image_base64=screenshot.base64_data,
        ))
        
        if self.agent_config.verbose:
            print("\n💭 Thinking...\n" + "-" * 50)
        
        try:
            response = self.model_client.request(self._context)
        except Exception as e:
            if self.agent_config.verbose:
                traceback.print_exc()
            return StepResult(
                success=False, finished=True, action_type="FINISH",
                params={"status": "failure"}, thought="", confidence="LOW",
                message=f"Model error: {e}",
            )
        
        if self.agent_config.verbose:
            print("-" * 50)
            print(f"💭 Thought: {response.thought}")
            print(f"🎯 Action: {response.action_type}")
            print(f"📊 Params: {json.dumps(response.params, ensure_ascii=False)}")
            print(f"🔮 Confidence: {response.confidence}")
        
        self._context[-1] = MessageBuilder.remove_images_from_message(self._context[-1])
        
        action_dict = {"action_type": response.action_type, "params": response.params}
        
        if self.agent_config.verbose:
            print(f"\n⚡ Executing: {response.action_type}...")
        
        try:
            result = self.action_handler.execute(action_dict)
        except Exception as e:
            if self.agent_config.verbose:
                traceback.print_exc()
            result = ActionResult(success=False, should_finish=False, message=str(e))
        
        self._history.append(HistoryEntry(
            step=self._step_count, action_type=response.action_type,
            params=response.params, result="success" if result.success else f"failed: {result.message}",
        ))
        
        self._context.append(MessageBuilder.create_assistant_message(response.raw_content))
        
        if self.agent_config.verbose:
            status = "✅" if result.success else "❌"
            print(f"{status} Action result: {'Success' if result.success else result.message}")
        
        return StepResult(
            success=result.success, finished=result.should_finish,
            action_type=response.action_type, params=response.params,
            thought=response.thought, confidence=response.confidence,
            message=result.message,
        )
    
    @property
    def context(self) -> list[dict[str, Any]]:
        return self._context.copy()
    
    @property
    def history(self) -> list[HistoryEntry]:
        return self._history.copy()
    
    @property
    def step_count(self) -> int:
        return self._step_count
