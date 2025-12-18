"""
Memory Service Module
=====================

High-level service for memory operations in the counseling AI.
Provides context for conversations and manages memory lifecycle.
"""

from typing import Optional
from datetime import datetime, timedelta

from app.memory.models import (
    Memory,
    MemoryType,
    MemoryCreateRequest,
    ConversationMemoryContext,
)
from app.memory.store import get_memory_store
from app.memory.extractor import (
    extract_memories_from_conversation,
    generate_session_summary,
)


class MemoryService:
    """
    Service for managing user memories in psychological counseling.
    """
    
    def __init__(self):
        self.store = get_memory_store()
    
    async def get_conversation_context(
        self, 
        user_id: str, 
        current_message: str
    ) -> ConversationMemoryContext:
        """
        Get memory context to inject into conversation.
        
        Args:
            user_id: User ID
            current_message: Current user message (for relevance search)
            
        Returns:
            ConversationMemoryContext with relevant memories
        """
        # Search for relevant memories
        relevant_results = await self.store.search_memories(
            user_id=user_id,
            query=current_message,
            top_k=5,
            min_importance=0.3
        )
        
        # Build user profile summary
        profile_summary = await self._build_profile_summary(user_id)
        
        # Get emotional context
        emotional_context = await self._get_emotional_context(user_id)
        
        # Get key reminders (high importance memories)
        key_reminders = await self._get_key_reminders(user_id)
        
        # Format relevant memories as strings
        relevant_memories = [
            f"[{result.memory.memory_type}] {result.memory.content}"
            for result in relevant_results
        ]
        
        return ConversationMemoryContext(
            user_profile_summary=profile_summary,
            relevant_memories=relevant_memories,
            emotional_context=emotional_context,
            key_reminders=key_reminders
        )
    
    async def _build_profile_summary(self, user_id: str) -> str:
        """Build a summary of what we know about the user."""
        memories = await self.store.get_user_memories(user_id)
        
        if not memories:
            return "这是一位新用户，尚无历史记录。"
        
        # Collect key information by type
        concerns = []
        relationships = []
        goals = []
        coping = []
        
        for memory in memories[:20]:  # Limit to recent memories
            if memory.memory_type == MemoryType.CONCERN:
                concerns.append(memory.content)
            elif memory.memory_type == MemoryType.RELATIONSHIP:
                relationships.append(memory.content)
            elif memory.memory_type == MemoryType.GOAL:
                goals.append(memory.content)
            elif memory.memory_type == MemoryType.COPING:
                coping.append(memory.content)
        
        # Build summary
        parts = []
        
        if concerns:
            parts.append(f"主要关注点：{'; '.join(concerns[:3])}")
        if relationships:
            parts.append(f"重要关系：{'; '.join(relationships[:3])}")
        if goals:
            parts.append(f"目标：{'; '.join(goals[:2])}")
        if coping:
            parts.append(f"应对方式：{'; '.join(coping[:2])}")
        
        if parts:
            return " | ".join(parts)
        return "用户有一些历史对话，但尚未形成清晰的档案。"
    
    async def _get_emotional_context(self, user_id: str) -> str:
        """Get the user's recent emotional trajectory."""
        emotion_memories = await self.store.get_user_memories(
            user_id, 
            memory_types=[MemoryType.EMOTION]
        )
        
        if not emotion_memories:
            return "情绪状态：未知"
        
        # Get last 5 emotion records
        recent_emotions = emotion_memories[:5]
        
        # Calculate average valence
        valences = [m.emotion_valence for m in recent_emotions if m.emotion_valence is not None]
        if valences:
            avg_valence = sum(valences) / len(valences)
            
            if avg_valence < -0.5:
                trend = "近期情绪较为低落"
            elif avg_valence < 0:
                trend = "近期情绪有些波动"
            elif avg_valence < 0.5:
                trend = "近期情绪相对平稳"
            else:
                trend = "近期情绪较为积极"
            
            # Add recent emotion descriptions
            recent_desc = [m.content for m in recent_emotions[:3]]
            return f"{trend}。{' '.join(recent_desc)}"
        
        return f"近期情绪记录：{recent_emotions[0].content}"
    
    async def _get_key_reminders(self, user_id: str) -> list[str]:
        """Get high-importance memories that should always be considered."""
        memories = await self.store.get_user_memories(user_id)
        
        # Filter for high importance
        important = [m for m in memories if m.importance >= 0.7]
        
        # Sort by importance and recency
        important.sort(key=lambda m: (m.importance, m.last_accessed), reverse=True)
        
        # Return top 3 as reminders
        return [m.content for m in important[:3]]
    
    async def process_conversation_for_memories(
        self,
        user_id: str,
        user_message: str,
        assistant_message: str
    ) -> list[Memory]:
        """
        Process a conversation exchange and extract/store memories.
        
        Args:
            user_id: User ID
            user_message: User's message
            assistant_message: AI's response
            
        Returns:
            List of memories that were created
        """
        # Extract memories from conversation
        memory_requests = await extract_memories_from_conversation(
            user_message=user_message,
            assistant_message=assistant_message,
            user_id=user_id
        )
        
        # Store extracted memories
        created_memories = []
        for request in memory_requests:
            memory = await self.store.add_memory(request)
            created_memories.append(memory)
        
        return created_memories
    
    async def end_session(
        self,
        user_id: str,
        messages: list[dict]
    ) -> Optional[Memory]:
        """
        Called when a session ends. Generates and stores session summary.
        
        Args:
            user_id: User ID
            messages: All messages from the session
            
        Returns:
            Summary memory if created
        """
        summary_request = await generate_session_summary(messages, user_id)
        
        if summary_request:
            summary_memory = await self.store.add_memory(summary_request)
            print(f"[Memory] Session summary stored for user {user_id[:8]}...")
            return summary_memory
        
        return None
    
    async def get_memory_stats(self, user_id: str) -> dict:
        """Get statistics about user's memories."""
        return await self.store.get_memory_summary(user_id)
    
    async def clear_memories(self, user_id: str) -> int:
        """Clear all memories for a user (e.g., for GDPR compliance)."""
        return await self.store.clear_user_memories(user_id)


# Singleton service instance
_memory_service: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """Get the global memory service instance."""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service


def format_memory_context_for_prompt(context: ConversationMemoryContext) -> str:
    """
    Format memory context as a string to inject into the LLM prompt.
    
    Args:
        context: ConversationMemoryContext object
        
    Returns:
        Formatted string for prompt injection
    """
    parts = []
    
    # User profile
    if context.user_profile_summary:
        parts.append(f"## 用户档案\n{context.user_profile_summary}")
    
    # Emotional context
    if context.emotional_context:
        parts.append(f"## 情绪背景\n{context.emotional_context}")
    
    # Relevant memories
    if context.relevant_memories:
        memories_text = "\n".join(f"- {m}" for m in context.relevant_memories)
        parts.append(f"## 相关记忆\n{memories_text}")
    
    # Key reminders
    if context.key_reminders:
        reminders_text = "\n".join(f"⚠️ {r}" for r in context.key_reminders)
        parts.append(f"## 重要提醒\n{reminders_text}")
    
    if parts:
        return "\n\n".join(parts)
    
    return ""
