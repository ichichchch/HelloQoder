"""
Upload Handler Module
Manages incoming files from local or cloud storage
"""

import uuid
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import UploadFile

from config import settings
from modules.dam import AssetManager


class UploadHandler:
    """Handles file uploads and manages upload lifecycle"""
    
    def __init__(self):
        self.upload_dir = settings.upload_dir
        self.asset_manager = AssetManager()
        settings.ensure_directories()
    
    async def save_upload(
        self,
        file: UploadFile,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Save an uploaded file and create its metadata
        
        Args:
            file: The uploaded file object
            tags: Optional list of tags for the asset
            
        Returns:
            Dict containing upload result with asset_id and metadata
        """
        # Generate unique asset ID
        asset_id = str(uuid.uuid4())
        
        # Get original filename and extension
        original_filename = file.filename or "unknown"
        extension = Path(original_filename).suffix.lower()
        
        # Create asset directory
        asset_dir = self.upload_dir / asset_id
        asset_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the file
        file_path = asset_dir / f"original{extension}"
        
        try:
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as e:
            # Cleanup on failure
            shutil.rmtree(asset_dir, ignore_errors=True)
            raise ValueError(f"Failed to save file: {str(e)}")
        
        # Create initial metadata
        metadata = {
            "asset_id": asset_id,
            "original_filename": original_filename,
            "file_path": str(file_path),
            "extension": extension,
            "size_bytes": len(content),
            "upload_time": datetime.now().isoformat(),
            "status": "uploaded",
            "tags": tags or [],
            "processing_log": []
        }
        
        # Save metadata
        self.asset_manager.save_metadata(asset_id, metadata)
        
        # Log the upload event
        self.asset_manager.append_log(asset_id, {
            "event": "upload_complete",
            "timestamp": datetime.now().isoformat(),
            "original_filename": original_filename,
            "size_bytes": len(content)
        })
        
        return {
            "success": True,
            "asset_id": asset_id,
            "metadata": metadata
        }
    
    async def batch_upload(
        self,
        files: List[UploadFile],
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Handle batch file uploads
        
        Args:
            files: List of uploaded file objects
            tags: Optional list of tags to apply to all assets
            
        Returns:
            Dict containing batch upload results
        """
        results = []
        errors = []
        
        for file in files:
            try:
                result = await self.save_upload(file, tags)
                results.append(result)
            except Exception as e:
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        return {
            "total": len(files),
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }
    
    def get_upload_path(self, asset_id: str) -> Optional[Path]:
        """Get the file path for an uploaded asset"""
        metadata = self.asset_manager.get_metadata(asset_id)
        if metadata and "file_path" in metadata:
            return Path(metadata["file_path"])
        return None
    
    def delete_upload(self, asset_id: str) -> bool:
        """
        Delete an uploaded file and its metadata
        
        Args:
            asset_id: The asset ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        asset_dir = self.upload_dir / asset_id
        
        if asset_dir.exists():
            shutil.rmtree(asset_dir, ignore_errors=True)
        
        # Also remove from assets directory
        return self.asset_manager.delete_asset(asset_id)
    
    def list_uploads(self) -> List[Dict[str, Any]]:
        """List all uploaded assets"""
        return self.asset_manager.list_assets()


# Global instance
upload_handler = UploadHandler()
