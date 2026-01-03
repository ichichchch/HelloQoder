"""
Model client for GLIMMER AI inference using OpenAI-compatible API.
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
    lang: str = "en"


@dataclass
class ModelResponse:
    """Response from the AI model."""
    thought: str
    action_type: str
    params: dict[str, Any]
    confidence: str
    raw_content: str
    raw_json: Optional[dict[str, Any]] = None
    time_to_first_token: Optional[float] = None
    total_time: Optional[float] = None


class ModelClient:
    """Client for interacting with OpenAI-compatible vision-language models."""
    
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()
        self.client = OpenAI(base_url=self.config.base_url, api_key=self.config.api_key)
    
    def request(self, messages: list[dict[str, Any]]) -> ModelResponse:
        """Send a request to the model."""
        start_time = time.time()
        time_to_first_token = None
        
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
                if not first_token_received:
                    time_to_first_token = time.time() - start_time
                    first_token_received = True
                print(content, end="", flush=True)
        
        print()
        total_time = time.time() - start_time
        
        response = self._parse_response(raw_content)
        response.time_to_first_token = time_to_first_token
        response.total_time = total_time
        
        return response
    
    def _parse_response(self, content: str) -> ModelResponse:
        """Parse the model response into structured format."""
        content = content.strip()
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
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                try:
                    data = json.loads(content[json_start:json_end])
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
        return {"role": "system", "content": content}
    
    @staticmethod
    def create_user_message(text: str, image_base64: Optional[str] = None) -> dict[str, Any]:
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
        return {"role": "assistant", "content": content}
    
    @staticmethod
    def build_goal_message(goal: str, history: Optional[list[dict[str, Any]]] = None) -> str:
        parts = [f"**GOAL:** {goal}"]
        if history:
            parts.append(f"**HISTORY:** {json.dumps(history, ensure_ascii=False, indent=2)}")
        parts.append("**SCREENSHOT:** (attached)")
        return "\n\n".join(parts)
    
    @staticmethod
    def remove_images_from_message(message: dict[str, Any]) -> dict[str, Any]:
        if isinstance(message.get("content"), list):
            message["content"] = [item for item in message["content"] if item.get("type") == "text"]
        return message
