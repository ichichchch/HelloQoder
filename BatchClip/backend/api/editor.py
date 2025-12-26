"""
Editor API Routes
Handles video editing endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from modules.editor import editor, CutRule
from modules.upload_handler import upload_handler

router = APIRouter()


class ClipRequest(BaseModel):
    """Model for clip extraction request"""
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    output_name: Optional[str] = None


class RoughCutRequest(BaseModel):
    """Model for rough cut request"""
    cuts: List[List[float]]  # List of [start, end] pairs
    output_name: Optional[str] = None


class AutoRoughCutRequest(BaseModel):
    """Model for auto rough cut request"""
    keep_intro_seconds: float = 5.0
    keep_outro_seconds: float = 5.0


class ConcatenateRequest(BaseModel):
    """Model for video concatenation request"""
    input_paths: List[str]
    output_name: Optional[str] = None
    use_reencoding: bool = False


class CutRuleModel(BaseModel):
    """Model for a cutting rule"""
    name: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    keep: bool = True
    tags: Optional[List[str]] = None


class ApplyRulesRequest(BaseModel):
    """Model for applying cutting rules"""
    rules: List[CutRuleModel]


@router.post("/{asset_id}/clip")
async def extract_clip(asset_id: str, request: ClipRequest):
    """
    Extract a clip from a video
    
    Must provide either end_time or duration
    """
    try:
        input_path = upload_handler.get_upload_path(asset_id)
        if input_path is None:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        result = editor.extract_clip(
            asset_id=asset_id,
            input_path=str(input_path),
            start_time=request.start_time,
            end_time=request.end_time,
            duration=request.duration,
            output_name=request.output_name
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{asset_id}/rough-cut")
async def rough_cut(asset_id: str, request: RoughCutRequest):
    """
    Perform a rough cut on a video
    
    Provide a list of [start, end] time pairs to keep
    """
    try:
        input_path = upload_handler.get_upload_path(asset_id)
        if input_path is None:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Convert list of lists to list of tuples
        cuts = [(c[0], c[1]) for c in request.cuts]
        
        result = editor.rough_cut(
            asset_id=asset_id,
            input_path=str(input_path),
            cuts=cuts,
            output_name=request.output_name
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{asset_id}/auto-rough-cut")
async def auto_rough_cut(asset_id: str, request: AutoRoughCutRequest):
    """
    Automatically create a rough cut keeping intro and outro
    """
    try:
        input_path = upload_handler.get_upload_path(asset_id)
        if input_path is None:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        result = editor.auto_rough_cut(
            asset_id=asset_id,
            input_path=str(input_path),
            keep_intro_seconds=request.keep_intro_seconds,
            keep_outro_seconds=request.keep_outro_seconds
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{asset_id}/apply-rules")
async def apply_rules(asset_id: str, request: ApplyRulesRequest):
    """
    Apply cutting rules to extract multiple clips
    """
    try:
        input_path = upload_handler.get_upload_path(asset_id)
        if input_path is None:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Convert to CutRule objects
        rules = [
            CutRule(
                name=r.name,
                start_time=r.start_time,
                end_time=r.end_time,
                duration=r.duration,
                keep=r.keep,
                tags=r.tags
            )
            for r in request.rules
        ]
        
        result = editor.apply_rules(
            asset_id=asset_id,
            input_path=str(input_path),
            rules=rules
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{asset_id}/concatenate")
async def concatenate_videos(asset_id: str, request: ConcatenateRequest):
    """
    Concatenate multiple videos into one
    """
    try:
        result = editor.concatenate_videos(
            asset_id=asset_id,
            input_paths=request.input_paths,
            output_name=request.output_name,
            use_reencoding=request.use_reencoding
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
