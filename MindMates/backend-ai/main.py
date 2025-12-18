"""
MindMates AI Backend - FastAPI Application
心理健康AI伴侣 - AI服务后端
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional

from app.config import get_settings
from app.models import ChatRequest, ChatResponse, HealthResponse
from app.services.chat_service import process_chat, end_chat_session
from app.memory import get_memory_service, MemoryType

settings = get_settings()


def get_client_ip(request: Request) -> str:
    """
    Get the client's real IP address from request.
    
    Handles cases where the app is behind a reverse proxy (nginx)
    by checking X-Forwarded-For and X-Real-IP headers.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Client IP address as string
    """
    # Check for X-Forwarded-For header (used by most proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, first one is the client
        return forwarded_for.split(",")[0].strip()
    
    # Check for X-Real-IP header (used by nginx)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 MindMates AI Service starting...")
    print(f"📝 Debug mode: {settings.debug}")
    yield
    # Shutdown
    print("👋 MindMates AI Service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="MindMates AI Service",
    description="心理健康AI伴侣 - RAG服务后端",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5000", "http://8.138.89.167"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, request: Request):
    """
    Main chat endpoint for psychological counseling.
    
    This endpoint:
    1. Receives user message and conversation history
    2. Retrieves relevant memories for context (using client IP as user_id)
    3. Performs crisis detection
    4. Returns appropriate AI response
    5. Extracts and stores new memories
    
    Args:
        chat_request: ChatRequest containing message and history
        request: FastAPI Request object for getting client IP
        
    Returns:
        ChatResponse with AI response, intent, crisis status, and memories_created count
    """
    try:
        # Auto-fill user_id with client IP address
        client_ip = get_client_ip(request)
        chat_request.user_id = client_ip
        
        response = await process_chat(chat_request)
        return response
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="服务暂时不可用，请稍后重试。"
        )


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "MindMates AI Service",
        "version": "1.0.0",
        "status": "running",
        "features": ["chat", "memory", "rag", "crisis_detection"],
        "docs": "/docs" if settings.debug else "disabled"
    }


# =============================================================================
# Memory API Endpoints
# =============================================================================

class EndSessionRequest(BaseModel):
    """Request to end a chat session."""
    messages: list[dict]  # user_id will be auto-filled from client IP


class MemoryStatsResponse(BaseModel):
    """Response with memory statistics."""
    total: int
    by_type: dict
    avg_importance: float
    recent_topics: list[str]


@app.post("/api/session/end")
async def end_session(end_request: EndSessionRequest, request: Request):
    """
    End a chat session and generate summary.
    
    This should be called when the user closes a chat session
    to generate and store a summary of the conversation.
    User ID is automatically determined from client IP.
    """
    try:
        client_ip = get_client_ip(request)
        await end_chat_session(client_ip, end_request.messages)
        return {"status": "ok", "message": "Session ended successfully"}
    except Exception as e:
        print(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail="Failed to end session")


@app.get("/api/memory/stats", response_model=MemoryStatsResponse)
async def get_memory_stats(request: Request):
    """
    Get memory statistics for the current user.
    
    User ID is automatically determined from client IP.
        
    Returns:
        MemoryStatsResponse with memory statistics
    """
    try:
        client_ip = get_client_ip(request)
        memory_service = get_memory_service()
        stats = await memory_service.get_memory_stats(client_ip)
        return MemoryStatsResponse(**stats)
    except Exception as e:
        print(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get memory stats")


@app.delete("/api/memory")
async def clear_user_memories(request: Request):
    """
    Clear all memories for the current user.
    
    This is useful for GDPR compliance or user request.
    User ID is automatically determined from client IP.
        
    Returns:
        Count of deleted memories
    """
    try:
        client_ip = get_client_ip(request)
        memory_service = get_memory_service()
        count = await memory_service.clear_memories(client_ip)
        return {"status": "ok", "deleted_count": count}
    except Exception as e:
        print(f"Error clearing memories: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear memories")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
