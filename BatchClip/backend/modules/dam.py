"""
Digital Asset Management (DAM) Module
Manages file-based metadata, tags, and logs for video assets
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from config import settings


class AssetManager:
    """
    Manages video assets including metadata, tags, and processing logs.
    All data is stored in JSON files alongside the media files.
    """
    
    def __init__(self):
        self.assets_dir = settings.assets_dir
        settings.ensure_directories()
    
    def _get_asset_dir(self, asset_id: str) -> Path:
        """Get the directory for a specific asset"""
        return self.assets_dir / asset_id
    
    def _get_metadata_path(self, asset_id: str) -> Path:
        """Get the metadata file path for an asset"""
        return self._get_asset_dir(asset_id) / "metadata.json"
    
    def _get_log_path(self, asset_id: str) -> Path:
        """Get the processing log file path for an asset"""
        return self._get_asset_dir(asset_id) / "processing_log.json"
    
    def save_metadata(self, asset_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Save or update metadata for an asset
        
        Args:
            asset_id: The unique asset identifier
            metadata: Dictionary containing asset metadata
            
        Returns:
            True if successful
        """
        asset_dir = self._get_asset_dir(asset_id)
        asset_dir.mkdir(parents=True, exist_ok=True)
        
        metadata_path = self._get_metadata_path(asset_id)
        
        # Add/update timestamp
        metadata["last_updated"] = datetime.now().isoformat()
        
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return True
    
    def get_metadata(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata for an asset
        
        Args:
            asset_id: The unique asset identifier
            
        Returns:
            Metadata dictionary or None if not found
        """
        metadata_path = self._get_metadata_path(asset_id)
        
        if not metadata_path.exists():
            return None
        
        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def update_metadata(self, asset_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update specific fields in asset metadata
        
        Args:
            asset_id: The unique asset identifier
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False if asset not found
        """
        metadata = self.get_metadata(asset_id)
        if metadata is None:
            return False
        
        metadata.update(updates)
        return self.save_metadata(asset_id, metadata)
    
    def append_log(self, asset_id: str, log_entry: Dict[str, Any]) -> bool:
        """
        Append a processing log entry for an asset
        
        Args:
            asset_id: The unique asset identifier
            log_entry: Dictionary containing log information
            
        Returns:
            True if successful
        """
        log_path = self._get_log_path(asset_id)
        asset_dir = self._get_asset_dir(asset_id)
        asset_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing logs or create new
        logs = []
        if log_path.exists():
            with open(log_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
        
        # Add timestamp if not present
        if "timestamp" not in log_entry:
            log_entry["timestamp"] = datetime.now().isoformat()
        
        logs.append(log_entry)
        
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        
        return True
    
    def get_logs(self, asset_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all processing logs for an asset
        
        Args:
            asset_id: The unique asset identifier
            
        Returns:
            List of log entries
        """
        log_path = self._get_log_path(asset_id)
        
        if not log_path.exists():
            return []
        
        with open(log_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def add_tags(self, asset_id: str, tags: List[str]) -> bool:
        """
        Add tags to an asset
        
        Args:
            asset_id: The unique asset identifier
            tags: List of tags to add
            
        Returns:
            True if successful
        """
        metadata = self.get_metadata(asset_id)
        if metadata is None:
            return False
        
        existing_tags = set(metadata.get("tags", []))
        existing_tags.update(tags)
        metadata["tags"] = list(existing_tags)
        
        return self.save_metadata(asset_id, metadata)
    
    def remove_tags(self, asset_id: str, tags: List[str]) -> bool:
        """
        Remove tags from an asset
        
        Args:
            asset_id: The unique asset identifier
            tags: List of tags to remove
            
        Returns:
            True if successful
        """
        metadata = self.get_metadata(asset_id)
        if metadata is None:
            return False
        
        existing_tags = set(metadata.get("tags", []))
        existing_tags -= set(tags)
        metadata["tags"] = list(existing_tags)
        
        return self.save_metadata(asset_id, metadata)
    
    def search_by_tags(self, tags: List[str], match_all: bool = False) -> List[Dict[str, Any]]:
        """
        Search assets by tags
        
        Args:
            tags: List of tags to search for
            match_all: If True, asset must have all tags; if False, any tag matches
            
        Returns:
            List of matching asset metadata
        """
        results = []
        tags_set = set(tags)
        
        if not self.assets_dir.exists():
            return results
        
        for asset_dir in self.assets_dir.iterdir():
            if asset_dir.is_dir():
                metadata = self.get_metadata(asset_dir.name)
                if metadata:
                    asset_tags = set(metadata.get("tags", []))
                    if match_all:
                        if tags_set.issubset(asset_tags):
                            results.append(metadata)
                    else:
                        if tags_set.intersection(asset_tags):
                            results.append(metadata)
        
        return results
    
    def list_assets(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all assets, optionally filtered by status
        
        Args:
            status: Optional status filter
            
        Returns:
            List of asset metadata
        """
        results = []
        
        if not self.assets_dir.exists():
            return results
        
        for asset_dir in self.assets_dir.iterdir():
            if asset_dir.is_dir():
                metadata = self.get_metadata(asset_dir.name)
                if metadata:
                    if status is None or metadata.get("status") == status:
                        results.append(metadata)
        
        return results
    
    def delete_asset(self, asset_id: str) -> bool:
        """
        Delete an asset and all its associated files
        
        Args:
            asset_id: The unique asset identifier
            
        Returns:
            True if successful
        """
        asset_dir = self._get_asset_dir(asset_id)
        
        if asset_dir.exists():
            shutil.rmtree(asset_dir, ignore_errors=True)
            return True
        
        return False
    
    def get_video_info(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get video-specific information from metadata
        
        Args:
            asset_id: The unique asset identifier
            
        Returns:
            Video info dictionary or None
        """
        metadata = self.get_metadata(asset_id)
        if metadata is None:
            return None
        
        return {
            "asset_id": asset_id,
            "duration": metadata.get("duration"),
            "resolution": metadata.get("resolution"),
            "fps": metadata.get("fps"),
            "codec": metadata.get("codec"),
            "tags": metadata.get("tags", [])
        }


# Global instance
asset_manager = AssetManager()
