"""
API Routes Package
"""

from fastapi import APIRouter

from api.upload import router as upload_router
from api.assets import router as assets_router
from api.processing import router as processing_router
from api.editor import router as editor_router

router = APIRouter()

# Include all sub-routers
router.include_router(upload_router, prefix="/upload", tags=["Upload"])
router.include_router(assets_router, prefix="/assets", tags=["Assets"])
router.include_router(processing_router, prefix="/processing", tags=["Processing"])
router.include_router(editor_router, prefix="/editor", tags=["Editor"])
