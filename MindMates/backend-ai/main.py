"""
MindMates AI Backend - FastAPI Application
心理健康AI伴侣 - AI服务后端
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.models import ChatRequest, ChatResponse, HealthResponse
from app.services.chat_service import process_chat

settings = get_settings()


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
    allow_origins=["http://localhost:5173", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for psychological counseling.
    
    This endpoint:
    1. Receives user message and conversation history
    2. Performs crisis detection
    3. Returns appropriate AI response
    
    Args:
        request: ChatRequest containing message and history
        
    Returns:
        ChatResponse with AI response, intent, and crisis status
    """
    try:
        response = await process_chat(request)
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
        "docs": "/docs" if settings.debug else "disabled"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
