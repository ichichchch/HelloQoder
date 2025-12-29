"""
LightRAG service for Graph-based Retrieval-Augmented Generation.

LightRAG uses knowledge graphs to enhance retrieval quality, supporting:
- Entity-relationship extraction from documents
- Multiple query modes: naive, local, global, hybrid, mix
- Graph + vector hybrid retrieval
"""

import asyncio
import hashlib
import logging
import os
from pathlib import Path
from typing import Literal

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status

from app.config import get_settings

logger = logging.getLogger(__name__)


def _get_embedding_dim(model_name: str) -> int:
    """Get embedding dimension for a given model."""
    dim_map = {
        "text-embedding-v4": 1024,
        "text-embedding-v3": 1024,
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
        "qwen2.5-vl-embedding": 1024,
    }
    return dim_map.get(model_name, 1024)


class LightRAGService:
    """
    LightRAG service wrapper for AL Agent.
    
    Supports:
    - Document indexing with automatic entity-relationship extraction
    - Multiple query modes (naive, local, global, hybrid, mix)
    - DashScope (Qwen) and OpenAI compatible APIs
    """

    def __init__(self):
        self.settings = get_settings()
        self._rag: LightRAG | None = None
        self._initialized = False

    def _get_working_dir(self, namespace: str = "default") -> str:
        """Get working directory for a namespace."""
        base_dir = Path(self.settings.lightrag_working_dir)
        work_dir = base_dir / namespace
        work_dir.mkdir(parents=True, exist_ok=True)
        return str(work_dir)

    def _get_namespace(self, workspace_path: str) -> str:
        """Generate namespace from workspace path."""
        path_hash = hashlib.md5(workspace_path.encode()).hexdigest()[:12]
        return f"workspace_{path_hash}"

    async def _init_rag(self, namespace: str = "default") -> LightRAG:
        """Initialize LightRAG instance."""
        working_dir = self._get_working_dir(namespace)
        settings = self.settings

        # Use DashScope API Key if available, otherwise use OpenAI
        api_key = settings.dashscope_api_key or settings.openai_api_key
        api_base = settings.llm_api_base

        if not api_key:
            raise ValueError("No API key configured. Set DASHSCOPE_API_KEY or OPENAI_API_KEY.")

        # Get embedding dimension
        embedding_dim = _get_embedding_dim(settings.text_embedding_model)

        # Create LightRAG instance with OpenAI-compatible API
        rag = LightRAG(
            working_dir=working_dir,
            # LLM configuration for entity extraction
            llm_model_func=openai_complete,
            llm_model_name=settings.llm_model,
            llm_model_kwargs={
                "api_key": api_key,
                "base_url": api_base,
            },
            # Embedding configuration
            embedding_func=openai_embed,
            embedding_model_name=settings.text_embedding_model,
            embedding_model_kwargs={
                "api_key": api_key,
                "base_url": api_base,
            },
            embedding_dim=embedding_dim,
            # Storage configuration (use defaults for now)
            # Can be extended to use Milvus, Neo4j, etc.
        )

        # Initialize the pipeline
        await rag.initialize_storages()
        await initialize_pipeline_status()

        return rag

    async def get_rag(self, workspace_path: str | None = None) -> LightRAG:
        """Get or create LightRAG instance for a workspace."""
        namespace = self._get_namespace(workspace_path) if workspace_path else "default"
        return await self._init_rag(namespace)

    async def insert_documents(
        self,
        documents: list[str],
        workspace_path: str | None = None,
    ) -> dict:
        """
        Insert documents into LightRAG.
        
        Documents will be processed for:
        - Entity extraction
        - Relationship extraction
        - Knowledge graph construction
        - Vector embedding generation
        
        Args:
            documents: List of document texts to insert
            workspace_path: Optional workspace path for namespace isolation
            
        Returns:
            Statistics about the indexing operation
        """
        try:
            rag = await self.get_rag(workspace_path)

            # Insert all documents
            for doc in documents:
                await rag.ainsert(doc)

            logger.info(f"Successfully inserted {len(documents)} documents into LightRAG")

            return {
                "success": True,
                "documents_inserted": len(documents),
                "message": f"Inserted {len(documents)} documents with entity-relationship extraction",
            }

        except Exception as e:
            logger.error(f"LightRAG insert error: {e}")
            raise

    async def query(
        self,
        query: str,
        workspace_path: str | None = None,
        mode: Literal["naive", "local", "global", "hybrid", "mix"] | None = None,
        top_k: int = 5,
        only_need_context: bool = False,
    ) -> dict:
        """
        Query LightRAG with different retrieval modes.
        
        Query Modes:
        - naive: Standard vector-based retrieval (like traditional RAG)
        - local: Uses local knowledge graph context (entities + neighbors)
        - global: Uses global graph patterns and communities
        - hybrid: Combines local and global approaches
        - mix: Combines all modes with reranking (recommended when reranker is enabled)
        
        Args:
            query: The query string
            workspace_path: Optional workspace path for namespace isolation
            mode: Query mode (defaults to config value)
            top_k: Number of results to return
            only_need_context: If True, return only context without LLM generation
            
        Returns:
            Query result with answer and/or context
        """
        try:
            rag = await self.get_rag(workspace_path)
            query_mode = mode or self.settings.lightrag_query_mode

            param = QueryParam(
                mode=query_mode,
                top_k=top_k,
                only_need_context=only_need_context,
            )

            result = await rag.aquery(query, param=param)

            return {
                "success": True,
                "query": query,
                "mode": query_mode,
                "result": result,
            }

        except Exception as e:
            logger.error(f"LightRAG query error: {e}")
            raise

    async def query_with_context(
        self,
        query: str,
        workspace_path: str | None = None,
        mode: Literal["naive", "local", "global", "hybrid", "mix"] | None = None,
        top_k: int = 5,
    ) -> dict:
        """
        Query LightRAG and return only the retrieved context (without LLM generation).
        
        This is useful when you want to use the context with your own LLM.
        """
        return await self.query(
            query=query,
            workspace_path=workspace_path,
            mode=mode,
            top_k=top_k,
            only_need_context=True,
        )

    async def get_graph_stats(self, workspace_path: str | None = None) -> dict:
        """Get statistics about the knowledge graph."""
        try:
            rag = await self.get_rag(workspace_path)
            
            # Get graph statistics if available
            stats = {
                "working_dir": rag.working_dir,
                "status": "initialized",
            }

            return stats

        except Exception as e:
            logger.error(f"LightRAG stats error: {e}")
            return {"status": "error", "message": str(e)}

    def is_healthy(self) -> bool:
        """Check if LightRAG service is operational."""
        try:
            settings = self.settings
            # Check if required configuration is present
            if not (settings.dashscope_api_key or settings.openai_api_key):
                return False
            return True
        except Exception:
            return False


# Singleton instance
_lightrag_service: LightRAGService | None = None


def get_lightrag_service() -> LightRAGService:
    """Get or create the LightRAG service singleton."""
    global _lightrag_service
    if _lightrag_service is None:
        _lightrag_service = LightRAGService()
    return _lightrag_service
