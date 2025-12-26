"""
Assets API Routes
Handles digital asset management endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from modules.dam import asset_manager

router = APIRouter()


class TagsUpdate(BaseModel):
    """Model for updating tags"""
    tags: List[str]


class MetadataUpdate(BaseModel):
    """Model for updating metadata"""
    updates: dict


@router.get("/")
async def list_assets(status: Optional[str] = None):
    """
    List all assets, optionally filtered by status
    
    Args:
        status: Optional status filter (e.g., "uploaded", "preprocessed", "completed")
    """
    try:
        assets = asset_manager.list_assets(status)
        return {"assets": assets, "total": len(assets)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{asset_id}")
async def get_asset(asset_id: str):
    """Get metadata for a specific asset"""
    try:
        metadata = asset_manager.get_metadata(asset_id)
        if metadata is None:
            raise HTTPException(status_code=404, detail="Asset not found")
        return metadata
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{asset_id}/logs")
async def get_asset_logs(asset_id: str):
    """Get processing logs for an asset"""
    try:
        logs = asset_manager.get_logs(asset_id)
        return {"asset_id": asset_id, "logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{asset_id}/video-info")
async def get_video_info(asset_id: str):
    """Get video-specific information for an asset"""
    try:
        info = asset_manager.get_video_info(asset_id)
        if info is None:
            raise HTTPException(status_code=404, detail="Asset not found")
        return info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{asset_id}/tags")
async def add_tags(asset_id: str, body: TagsUpdate):
    """Add tags to an asset"""
    try:
        success = asset_manager.add_tags(asset_id, body.tags)
        if not success:
            raise HTTPException(status_code=404, detail="Asset not found")
        return {"success": True, "message": "Tags added"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{asset_id}/tags")
async def remove_tags(asset_id: str, body: TagsUpdate):
    """Remove tags from an asset"""
    try:
        success = asset_manager.remove_tags(asset_id, body.tags)
        if not success:
            raise HTTPException(status_code=404, detail="Asset not found")
        return {"success": True, "message": "Tags removed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/tags")
async def search_by_tags(
    body: TagsUpdate,
    match_all: bool = False
):
    """
    Search assets by tags
    
    Args:
        body: Tags to search for
        match_all: If True, assets must have all specified tags
    """
    try:
        results = asset_manager.search_by_tags(body.tags, match_all)
        return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{asset_id}")
async def update_metadata(asset_id: str, body: MetadataUpdate):
    """Update metadata for an asset"""
    try:
        success = asset_manager.update_metadata(asset_id, body.updates)
        if not success:
            raise HTTPException(status_code=404, detail="Asset not found")
        return {"success": True, "message": "Metadata updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{asset_id}")
async def delete_asset(asset_id: str):
    """Delete an asset and all its files"""
    try:
        success = asset_manager.delete_asset(asset_id)
        if success:
            return {"success": True, "message": f"Asset {asset_id} deleted"}
        else:
            raise HTTPException(status_code=404, detail="Asset not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
