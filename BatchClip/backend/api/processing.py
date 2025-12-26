"""
Processing API Routes
Handles video preprocessing endpoints
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from modules.preprocessor import preprocessor
from modules.upload_handler import upload_handler

router = APIRouter()


class PreprocessRequest(BaseModel):
    """Model for preprocessing request"""
    generate_proxy: bool = True
    split: bool = False
    proxy_resolution: Optional[int] = None
    segment_duration: Optional[int] = None


class ExtractMetadataRequest(BaseModel):
    """Model for metadata extraction"""
    input_path: str


@router.post("/{asset_id}/preprocess")
async def preprocess_video(
    asset_id: str,
    request: PreprocessRequest,
    background_tasks: BackgroundTasks
):
    """
    Start preprocessing for a video asset
    
    This will:
    - Extract video metadata
    - Generate a proxy (if requested)
    - Split video into segments (if requested)
    """
    try:
        # Get the upload path
        input_path = upload_handler.get_upload_path(asset_id)
        if input_path is None:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        if not input_path.exists():
            raise HTTPException(status_code=404, detail="Source file not found")
        
        # Run preprocessing (could be moved to background for large files)
        result = preprocessor.preprocess_video(
            asset_id=asset_id,
            input_path=str(input_path),
            generate_proxy=request.generate_proxy,
            split=request.split,
            proxy_resolution=request.proxy_resolution,
            segment_duration=request.segment_duration
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{asset_id}/proxy")
async def generate_proxy(
    asset_id: str,
    resolution: Optional[int] = None
):
    """Generate a proxy video for an asset"""
    try:
        input_path = upload_handler.get_upload_path(asset_id)
        if input_path is None:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        result = preprocessor.generate_proxy(
            asset_id=asset_id,
            input_path=str(input_path),
            resolution=resolution
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{asset_id}/split")
async def split_video(
    asset_id: str,
    segment_duration: Optional[int] = None
):
    """Split a video into segments"""
    try:
        input_path = upload_handler.get_upload_path(asset_id)
        if input_path is None:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        result = preprocessor.split_video(
            asset_id=asset_id,
            input_path=str(input_path),
            segment_duration=segment_duration
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{asset_id}/metadata")
async def extract_metadata(asset_id: str):
    """Extract and save metadata for a video"""
    try:
        input_path = upload_handler.get_upload_path(asset_id)
        if input_path is None:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        metadata = preprocessor.extract_metadata(str(input_path))
        
        # Save to asset
        from modules.dam import asset_manager
        asset_manager.update_metadata(asset_id, metadata)
        
        return {"success": True, "metadata": metadata}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
