"""
Memory Storage Module
=====================

Handles storage and retrieval of memories using vector embeddings.
Uses in-memory storage for development, can be extended to use Redis/PostgreSQL.
"""

import uuid
from datetime import datetime
from typing import Optional
from collections import defaultdict

from app.memory.models import (
    Memory,
    MemoryType,
    MemoryCreateRequest,
    MemorySearchResult,
)
from app.rag import get_embedding_model, _cosine_similarity


class MemoryStore:
    """
    In-memory store for user memories with vector search capability.
    
    In production, this should be backed by:
    - PostgreSQL with pgvector extension, or
    - Redis with vector search, or
    - Dedicated vector database like Milvus
    """
    
    def __init__(self):
        # user_id -> list of memories
        self._memories: dict[str, list[Memory]] = defaultdict(list)
        self._embedding_model = None
    
    def _get_embedding_model(self):
        """Lazy load embedding model."""
        if self._embedding_model is None:
            self._embedding_model = get_embedding_model()
        return self._embedding_model
    
    def _compute_embedding(self, text: str) -> list[float]:
        """Compute embedding for text."""
        model = self._get_embedding_model()
        return model.embed_query(text)
    
    async def add_memory(self, request: MemoryCreateRequest) -> Memory:
        """
        Add a new memory for a user.
        
        Args:
            request: Memory creation request
            
        Returns:
            Created memory object
        """
        # Compute embedding
        embedding = self._compute_embedding(request.content)
        
        # Create memory object
        memory = Memory(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            memory_type=request.memory_type,
            content=request.content,
            importance=request.importance,
            emotion_valence=request.emotion_valence,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            access_count=0,
            embedding=embedding
        )
        
        # Check for duplicate/similar memories
        existing = self._find_similar_memory(request.user_id, embedding, threshold=0.9)
        if existing:
            # Update existing memory instead of creating duplicate
            existing.access_count += 1
            existing.last_accessed = datetime.utcnow()
            # Increase importance if mentioned again
            existing.importance = min(1.0, existing.importance + 0.1)
            print(f"[Memory] Updated existing memory: {existing.content[:50]}...")
            return existing
        
        # Add to store
        self._memories[request.user_id].append(memory)
        print(f"[Memory] Added new {request.memory_type} memory for user {request.user_id[:8]}...")
        
        return memory
    
    def _find_similar_memory(
        self, 
        user_id: str, 
        embedding: list[float], 
        threshold: float = 0.9
    ) -> Optional[Memory]:
        """Find a similar existing memory."""
        for memory in self._memories[user_id]:
            if memory.embedding:
                similarity = _cosine_similarity(embedding, memory.embedding)
                if similarity >= threshold:
                    return memory
        return None
    
    async def search_memories(
        self,
        user_id: str,
        query: str,
        memory_types: Optional[list[MemoryType]] = None,
        top_k: int = 5,
        min_importance: float = 0.0
    ) -> list[MemorySearchResult]:
        """
        Search memories by semantic similarity.
        
        Args:
            user_id: User ID to search memories for
            query: Search query
            memory_types: Optional filter by memory types
            top_k: Number of results to return
            min_importance: Minimum importance threshold
            
        Returns:
            List of memory search results sorted by relevance
        """
        user_memories = self._memories.get(user_id, [])
        if not user_memories:
            return []
        
        # Compute query embedding
        query_embedding = self._compute_embedding(query)
        
        # Score each memory
        scored_memories: list[tuple[float, Memory]] = []
        
        for memory in user_memories:
            # Filter by type
            if memory_types and memory.memory_type not in memory_types:
                continue
            
            # Filter by importance
            if memory.importance < min_importance:
                continue
            
            # Compute relevance score
            if memory.embedding:
                similarity = _cosine_similarity(query_embedding, memory.embedding)
                
                # Boost score by importance and recency
                recency_boost = self._compute_recency_boost(memory.last_accessed)
                importance_boost = memory.importance * 0.2
                
                final_score = similarity + recency_boost + importance_boost
                scored_memories.append((final_score, memory))
        
        # Sort by score
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        # Update access time for retrieved memories
        results = []
        for score, memory in scored_memories[:top_k]:
            memory.last_accessed = datetime.utcnow()
            memory.access_count += 1
            results.append(MemorySearchResult(memory=memory, relevance_score=score))
        
        return results
    
    def _compute_recency_boost(self, last_accessed: datetime) -> float:
        """Compute a boost factor based on how recently memory was accessed."""
        days_ago = (datetime.utcnow() - last_accessed).days
        if days_ago <= 1:
            return 0.1
        elif days_ago <= 7:
            return 0.05
        elif days_ago <= 30:
            return 0.02
        return 0.0
    
    async def get_user_memories(
        self, 
        user_id: str,
        memory_types: Optional[list[MemoryType]] = None
    ) -> list[Memory]:
        """Get all memories for a user, optionally filtered by type."""
        memories = self._memories.get(user_id, [])
        
        if memory_types:
            memories = [m for m in memories if m.memory_type in memory_types]
        
        # Sort by importance and recency
        memories.sort(key=lambda m: (m.importance, m.last_accessed), reverse=True)
        
        return memories
    
    async def get_memory_summary(self, user_id: str) -> dict:
        """Get a summary of user's memories by type."""
        memories = self._memories.get(user_id, [])
        
        summary = {
            "total": len(memories),
            "by_type": {},
            "avg_importance": 0.0,
            "recent_topics": []
        }
        
        if not memories:
            return summary
        
        # Count by type
        type_counts = defaultdict(int)
        for memory in memories:
            type_counts[memory.memory_type] += 1
        summary["by_type"] = dict(type_counts)
        
        # Average importance
        summary["avg_importance"] = sum(m.importance for m in memories) / len(memories)
        
        # Recent topics (last 5 memories)
        recent = sorted(memories, key=lambda m: m.created_at, reverse=True)[:5]
        summary["recent_topics"] = [m.content[:100] for m in recent]
        
        return summary
    
    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Delete a specific memory."""
        memories = self._memories.get(user_id, [])
        for i, memory in enumerate(memories):
            if memory.id == memory_id:
                del memories[i]
                return True
        return False
    
    async def clear_user_memories(self, user_id: str) -> int:
        """Clear all memories for a user. Returns count of deleted memories."""
        count = len(self._memories.get(user_id, []))
        self._memories[user_id] = []
        return count


# Global singleton instance
_memory_store: Optional[MemoryStore] = None


def get_memory_store() -> MemoryStore:
    """Get the global memory store instance."""
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore()
    return _memory_store
