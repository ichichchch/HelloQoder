"""
Model client for GLIMMER AI inference using OpenAI-compatible API.

Handles communication with Vision-Language Models and parses
JSON-formatted responses according to System.md specification.
"""

import json
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from openai import OpenAI


@dataclass
class ModelConfig:
    """Configuration for the AI model."""
    
    base_url: str = "http://localhost:8000/v1"
    api_key: str = "EMPTY"
    model_name: str = "glm-4v"
    max_tokens: int = 4096
    temperature: float = 0.1
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    extra_body: dict[str, Any] = field(default_factory=dict)
    lang: str = "en"  # Language for prompts: 'en' or 'cn'


@dataclass
class ModelResponse:
    """Response from the AI model."""
    
    thought: str
    action_type: str
    params: dict[str, Any]
    confidence: str
    raw_content: str
    raw_json: Optional[dict[str, Any]] = None
    # Performance metrics
    time_to_first_token: Optional[float] = None
    total_time: Optional[float] = None


class ModelClient:
    """
    Client for interacting with OpenAI-compatible vision-language models.
    
    Parses JSON responses according to System.md specification.
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()
        self.client = OpenAI(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
        )
    
    def request(self, messages: list[dict[str, Any]]) -> ModelResponse:
        """
        Send a request to the model.
        
        Args:
            messages: List of message dictionaries in OpenAI format.
        
        Returns:
            ModelResponse containing parsed action.
        
        Raises:
            ValueError: If the response cannot be parsed.
        """
        start_time = time.time()
        time_to_first_token = None
        
        # Use streaming for performance metrics
        stream = self.client.chat.completions.create(
            messages=messages,
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            frequency_penalty=self.config.frequency_penalty,
            extra_body=self.config.extra_body,
            stream=True,
        )
        
        raw_content = ""
        first_token_received = False
        
        for chunk in stream:
            if len(chunk.choices) == 0:
                continue
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                raw_content += content
                
                # Record time to first token
                if not first_token_received:
                    time_to_first_token = time.time() - start_time
                    first_token_received = True
                
                # Print streaming output for debugging
                print(content, end="", flush=True)
        
        print()  # Newline after streaming
        
        total_time = time.time() - start_time
        
        # Parse the JSON response
        response = self._parse_response(raw_content)
        response.time_to_first_token = time_to_first_token
        response.total_time = total_time
        
        # Print performance metrics
        print()
        print("=" * 50)
        print("⏱️  Performance Metrics:")
        print("-" * 50)
        if time_to_first_token is not None:
            print(f"Time to first token: {time_to_first_token:.3f}s")
        print(f"Total inference time: {total_time:.3f}s")
        print("=" * 50)
        
        return response
    
    def _parse_response(self, content: str) -> ModelResponse:
        """
        Parse the model response into structured format.
        
        Expects JSON with: thought, action_type, params, confidence
        
        Args:
            content: Raw response content.
        
        Returns:
            ModelResponse with parsed fields.
        """
        content = content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        
        try:
            data = json.loads(content)
            
            return ModelResponse(
                thought=data.get("thought", ""),
                action_type=data.get("action_type", ""),
                params=data.get("params", {}),
                confidence=data.get("confidence", "MEDIUM"),
                raw_content=content,
                raw_json=data,
            )
        except json.JSONDecodeError:
            # Try to extract JSON from the content
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = content[json_start:json_end]
                try:
                    data = json.loads(json_str)
                    return ModelResponse(
                        thought=data.get("thought", ""),
                        action_type=data.get("action_type", ""),
                        params=data.get("params", {}),
                        confidence=data.get("confidence", "MEDIUM"),
                        raw_content=content,
                        raw_json=data,
                    )
                except json.JSONDecodeError:
                    pass
            
            # Return empty response if parsing fails
            return ModelResponse(
                thought=content,
                action_type="FINISH",
                params={"status": "failure", "summary": "Failed to parse response"},
                confidence="LOW",
                raw_content=content,
            )


class MessageBuilder:
    """Helper class for building conversation messages."""
    
    @staticmethod
    def create_system_message(content: str) -> dict[str, Any]:
        """Create a system message."""
        return {"role": "system", "content": content}
    
    @staticmethod
    def create_user_message(
        text: str,
        image_base64: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create a user message with optional image.
        
        Args:
            text: Text content (GOAL, etc.).
            image_base64: Optional base64-encoded screenshot.
        
        Returns:
            Message dictionary.
        """
        content = []
        
        if image_base64:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_base64}"},
            })
        
        content.append({"type": "text", "text": text})
        
        return {"role": "user", "content": content}
    
    @staticmethod
    def create_assistant_message(content: str) -> dict[str, Any]:
        """Create an assistant message."""
        return {"role": "assistant", "content": content}
    
    @staticmethod
    def build_goal_message(
        goal: str,
        history: Optional[list[dict[str, Any]]] = None,
    ) -> str:
        """
        Build the GOAL message format as per System.md spec.
        
        Args:
            goal: User's specific request.
            history: List of previous steps taken.
        
        Returns:
            Formatted message string.
        """
        parts = [f"**GOAL:** {goal}"]
        
        if history:
            history_str = json.dumps(history, ensure_ascii=False, indent=2)
            parts.append(f"**HISTORY:** {history_str}")
        
        parts.append("**SCREENSHOT:** (attached)")
        
        return "\n\n".join(parts)
    
    @staticmethod
    def remove_images_from_message(message: dict[str, Any]) -> dict[str, Any]:
        """
        Remove image content from a message to save context space.
        
        Args:
            message: Message dictionary.
        
        Returns:
            Message with images removed.
        """
        if isinstance(message.get("content"), list):
            message["content"] = [
                item for item in message["content"]
                if item.get("type") == "text"
            ]
        return message
