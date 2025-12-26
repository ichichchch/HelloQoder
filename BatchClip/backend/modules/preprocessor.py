"""
Preprocessor Module
Handles proxy generation and video splitting (by time/rules)
All video manipulation is done through FFmpeg
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from config import settings
from modules.dam import AssetManager


class Preprocessor:
    """
    Handles video preprocessing including:
    - Proxy generation (lower resolution copies for faster editing)
    - Video splitting by time intervals
    - Video metadata extraction
    """
    
    def __init__(self):
        self.temp_dir = settings.processing_temp_dir
        self.ffmpeg_path = settings.ffmpeg_path
        self.proxy_resolution = settings.proxy_resolution
        self.segment_duration = settings.default_segment_duration
        self.asset_manager = AssetManager()
        settings.ensure_directories()
    
    def _run_ffmpeg(self, args: List[str], timeout: int = 3600) -> subprocess.CompletedProcess:
        """
        Run FFmpeg command with given arguments
        
        Args:
            args: FFmpeg arguments (excluding ffmpeg binary itself)
            timeout: Command timeout in seconds
            
        Returns:
            Completed process result
        """
        cmd = [self.ffmpeg_path] + args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
    
    def _run_ffprobe(self, input_path: str) -> Dict[str, Any]:
        """
        Run FFprobe to get video metadata
        
        Args:
            input_path: Path to the video file
            
        Returns:
            Dictionary containing video metadata
        """
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            input_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"FFprobe failed: {result.stderr}")
        
        return json.loads(result.stdout)
    
    def extract_metadata(self, input_path: str) -> Dict[str, Any]:
        """
        Extract video metadata using FFprobe
        
        Args:
            input_path: Path to the video file
            
        Returns:
            Simplified metadata dictionary
        """
        probe_data = self._run_ffprobe(input_path)
        
        # Find video stream
        video_stream = None
        audio_stream = None
        
        for stream in probe_data.get("streams", []):
            if stream.get("codec_type") == "video" and video_stream is None:
                video_stream = stream
            elif stream.get("codec_type") == "audio" and audio_stream is None:
                audio_stream = stream
        
        format_info = probe_data.get("format", {})
        
        metadata = {
            "duration": float(format_info.get("duration", 0)),
            "size_bytes": int(format_info.get("size", 0)),
            "format_name": format_info.get("format_name", ""),
            "bit_rate": int(format_info.get("bit_rate", 0)),
        }
        
        if video_stream:
            metadata.update({
                "resolution": f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
                "width": video_stream.get("width", 0),
                "height": video_stream.get("height", 0),
                "fps": eval(video_stream.get("r_frame_rate", "0/1")) if "/" in video_stream.get("r_frame_rate", "0") else 0,
                "video_codec": video_stream.get("codec_name", ""),
            })
        
        if audio_stream:
            metadata.update({
                "audio_codec": audio_stream.get("codec_name", ""),
                "audio_sample_rate": int(audio_stream.get("sample_rate", 0)),
                "audio_channels": audio_stream.get("channels", 0),
            })
        
        return metadata
    
    def generate_proxy(
        self,
        asset_id: str,
        input_path: str,
        resolution: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a lower resolution proxy video for faster editing
        
        Args:
            asset_id: The unique asset identifier
            input_path: Path to the original video file
            resolution: Target height resolution (default from config)
            
        Returns:
            Dictionary containing proxy generation result
        """
        resolution = resolution or self.proxy_resolution
        
        # Create proxy directory
        proxy_dir = self.temp_dir / asset_id / "proxy"
        proxy_dir.mkdir(parents=True, exist_ok=True)
        
        # Output path
        proxy_path = proxy_dir / "proxy.mp4"
        
        # Log start
        self.asset_manager.append_log(asset_id, {
            "event": "proxy_generation_start",
            "timestamp": datetime.now().isoformat(),
            "target_resolution": resolution
        })
        
        # FFmpeg command for proxy generation
        args = [
            "-i", str(input_path),
            "-vf", f"scale=-2:{resolution}",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-y",
            str(proxy_path)
        ]
        
        try:
            result = self._run_ffmpeg(args)
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg proxy generation failed: {result.stderr}")
            
            # Extract proxy metadata
            proxy_metadata = self.extract_metadata(str(proxy_path))
            
            # Update asset metadata
            self.asset_manager.update_metadata(asset_id, {
                "proxy_path": str(proxy_path),
                "proxy_resolution": resolution,
                "has_proxy": True
            })
            
            # Log completion
            self.asset_manager.append_log(asset_id, {
                "event": "proxy_generation_complete",
                "timestamp": datetime.now().isoformat(),
                "proxy_path": str(proxy_path),
                "proxy_metadata": proxy_metadata
            })
            
            return {
                "success": True,
                "proxy_path": str(proxy_path),
                "metadata": proxy_metadata
            }
            
        except Exception as e:
            self.asset_manager.append_log(asset_id, {
                "event": "proxy_generation_failed",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
            raise
    
    def split_video(
        self,
        asset_id: str,
        input_path: str,
        segment_duration: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Split video into segments by time duration
        
        Args:
            asset_id: The unique asset identifier
            input_path: Path to the video file
            segment_duration: Duration of each segment in seconds
            
        Returns:
            Dictionary containing split results
        """
        segment_duration = segment_duration or self.segment_duration
        
        # Create segments directory
        segments_dir = self.temp_dir / asset_id / "segments"
        segments_dir.mkdir(parents=True, exist_ok=True)
        
        # Log start
        self.asset_manager.append_log(asset_id, {
            "event": "video_split_start",
            "timestamp": datetime.now().isoformat(),
            "segment_duration": segment_duration
        })
        
        # FFmpeg command for splitting
        output_pattern = str(segments_dir / "segment_%03d.mp4")
        
        args = [
            "-i", str(input_path),
            "-c", "copy",
            "-map", "0",
            "-segment_time", str(segment_duration),
            "-f", "segment",
            "-reset_timestamps", "1",
            output_pattern
        ]
        
        try:
            result = self._run_ffmpeg(args)
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg split failed: {result.stderr}")
            
            # Get list of segments
            segments = sorted(segments_dir.glob("segment_*.mp4"))
            segment_info = []
            
            for i, seg_path in enumerate(segments):
                seg_metadata = self.extract_metadata(str(seg_path))
                segment_info.append({
                    "index": i,
                    "path": str(seg_path),
                    "duration": seg_metadata.get("duration", 0),
                    "size_bytes": seg_metadata.get("size_bytes", 0)
                })
            
            # Update asset metadata
            self.asset_manager.update_metadata(asset_id, {
                "segments_dir": str(segments_dir),
                "segment_count": len(segments),
                "is_split": True
            })
            
            # Log completion
            self.asset_manager.append_log(asset_id, {
                "event": "video_split_complete",
                "timestamp": datetime.now().isoformat(),
                "segment_count": len(segments),
                "segments": segment_info
            })
            
            return {
                "success": True,
                "segments_dir": str(segments_dir),
                "segment_count": len(segments),
                "segments": segment_info
            }
            
        except Exception as e:
            self.asset_manager.append_log(asset_id, {
                "event": "video_split_failed",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
            raise
    
    def preprocess_video(
        self,
        asset_id: str,
        input_path: str,
        generate_proxy: bool = True,
        split: bool = False,
        proxy_resolution: Optional[int] = None,
        segment_duration: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Complete preprocessing pipeline for a video
        
        Args:
            asset_id: The unique asset identifier
            input_path: Path to the video file
            generate_proxy: Whether to generate a proxy
            split: Whether to split the video
            proxy_resolution: Target proxy resolution
            segment_duration: Segment duration for splitting
            
        Returns:
            Dictionary containing preprocessing results
        """
        results = {
            "asset_id": asset_id,
            "input_path": input_path
        }
        
        # Extract and save original metadata
        try:
            metadata = self.extract_metadata(input_path)
            self.asset_manager.update_metadata(asset_id, metadata)
            results["metadata"] = metadata
        except Exception as e:
            results["metadata_error"] = str(e)
        
        # Generate proxy if requested
        if generate_proxy:
            try:
                proxy_result = self.generate_proxy(asset_id, input_path, proxy_resolution)
                results["proxy"] = proxy_result
            except Exception as e:
                results["proxy_error"] = str(e)
        
        # Split video if requested
        if split:
            try:
                split_result = self.split_video(asset_id, input_path, segment_duration)
                results["split"] = split_result
            except Exception as e:
                results["split_error"] = str(e)
        
        # Update status
        self.asset_manager.update_metadata(asset_id, {"status": "preprocessed"})
        
        return results


# Global instance
preprocessor = Preprocessor()
