"""
Upload API Routes
Handles file upload endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from modules.upload_handler import upload_handler

router = APIRouter()


@router.post("/single")
async def upload_single_file(
    file: UploadFile = File(...),
    tags: Optional[str] = Form(None)
):
    """
    Upload a single video file
    
    Args:
        file: The video file to upload
        tags: Comma-separated list of tags
    """
    try:
        tag_list = [t.strip() for t in tags.split(",")] if tags else []
        result = await upload_handler.save_upload(file, tag_list)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def upload_batch_files(
    files: List[UploadFile] = File(...),
    tags: Optional[str] = Form(None)
):
    """
    Upload multiple video files at once
    
    Args:
        files: List of video files to upload
        tags: Comma-separated list of tags to apply to all files
    """
    try:
        tag_list = [t.strip() for t in tags.split(",")] if tags else []
        result = await upload_handler.batch_upload(files, tag_list)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_uploads():
    """List all uploaded files"""
    try:
        return {"uploads": upload_handler.list_uploads()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{asset_id}")
async def delete_upload(asset_id: str):
    """Delete an uploaded file"""
    try:
        success = upload_handler.delete_upload(asset_id)
        if success:
            return {"success": True, "message": f"Asset {asset_id} deleted"}
        else:
            raise HTTPException(status_code=404, detail="Asset not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
