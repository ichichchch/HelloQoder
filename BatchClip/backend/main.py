"""
BatchClip Backend - FastAPI Main Application
Automated video processing pipeline
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api import router as api_router


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("BatchClip Backend starting up...")
    settings.ensure_directories()
    logger.info(f"Upload directory: {settings.upload_dir}")
    logger.info(f"Output directory: {settings.final_output_dir}")
    logger.info(f"Temp directory: {settings.processing_temp_dir}")
    
    yield
    
    # Shutdown
    logger.info("BatchClip Backend shutting down...")


# Create FastAPI application
app = FastAPI(
    title="BatchClip API",
    description="Automated video processing pipeline - AI Analysis -> Automated Rough Cut -> Final Video",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "name": "BatchClip API",
        "version": "0.1.0",
        "status": "running",
        "storage_type": settings.storage_type
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "storage_type": settings.storage_type,
        "upload_dir_exists": settings.upload_dir.exists(),
        "output_dir_exists": settings.final_output_dir.exists()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
