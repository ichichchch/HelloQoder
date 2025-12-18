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
    user_id: Optional[str] = None  # For memory system
    session_id: Optional[str] = None  # For session tracking


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    content: str
    intent: Optional[str] = None
    is_crisis: bool = False
    memories_created: int = 0  # Number of new memories extracted


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
