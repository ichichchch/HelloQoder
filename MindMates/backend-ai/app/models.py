from pydantic import BaseModel
from typing import Optional


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str  # "user", "assistant", "system"
    content: str


class ChatRequest(BaseModel):
    """Request for chat endpoint."""
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    content: str
    intent: Optional[str] = None
    is_crisis: bool = False


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
