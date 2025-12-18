"""
Memory System for Psychological Counseling AI
==============================================

This module implements a comprehensive memory system that enables the AI
to remember and utilize information about users across conversations.

Memory Types:
1. Profile Memory - User preferences, communication style
2. Emotion Memory - Emotional states and trends over time
3. Event Memory - Important life events, triggers, concerns
4. Summary Memory - Session summaries for continuity
5. Insight Memory - Therapeutic insights and progress

Architecture:
- Memories are stored as text with vector embeddings for semantic search
- Each memory has a type, content, importance score, and timestamp
- Memories decay over time but important ones are preserved
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class MemoryType(str, Enum):
    """Types of memories the system can store."""
    PROFILE = "profile"          # User preferences, communication style
    EMOTION = "emotion"          # Emotional states and patterns
    EVENT = "event"              # Important life events
    CONCERN = "concern"          # Main worries and issues
    RELATIONSHIP = "relationship" # Important people in user's life
    COPING = "coping"            # Coping strategies that work/don't work
    GOAL = "goal"                # User's goals and aspirations
    INSIGHT = "insight"          # Therapeutic insights
    SUMMARY = "summary"          # Session summaries


class Memory(BaseModel):
    """A single memory unit."""
    id: str
    user_id: str
    memory_type: MemoryType
    content: str
    importance: float = 0.5      # 0-1, higher = more important
    emotion_valence: Optional[float] = None  # -1 to 1, negative to positive
    created_at: datetime = datetime.utcnow()
    last_accessed: datetime = datetime.utcnow()
    access_count: int = 0
    embedding: Optional[list[float]] = None
    
    class Config:
        use_enum_values = True


class MemoryCreateRequest(BaseModel):
    """Request to create a new memory."""
    user_id: str
    memory_type: MemoryType
    content: str
    importance: float = 0.5
    emotion_valence: Optional[float] = None


class MemorySearchRequest(BaseModel):
    """Request to search memories."""
    user_id: str
    query: str
    memory_types: Optional[list[MemoryType]] = None
    top_k: int = 5
    min_importance: float = 0.0


class MemorySearchResult(BaseModel):
    """Result of a memory search."""
    memory: Memory
    relevance_score: float


class UserMemoryProfile(BaseModel):
    """Aggregated memory profile for a user."""
    user_id: str
    total_memories: int
    memory_summary: str
    dominant_emotions: list[str]
    key_concerns: list[str]
    important_people: list[str]
    coping_strategies: list[str]
    recent_topics: list[str]


class ConversationMemoryContext(BaseModel):
    """Memory context to inject into conversation."""
    user_profile_summary: str
    relevant_memories: list[str]
    emotional_context: str
    key_reminders: list[str]
