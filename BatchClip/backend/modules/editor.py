"""
Editor Module
Implements rule-based rough cutting and stitching logic
All video manipulation is done through FFmpeg
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from config import settings
from modules.dam import AssetManager


class CutRule:
    """Represents a cutting rule for automatic editing"""
    
    def __init__(
        self,
        name: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        duration: Optional[float] = None,
        keep: bool = True,
        tags: Optional[List[str]] = None
    ):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.keep = keep
        self.tags = tags or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "keep": self.keep,
            "tags": self.tags
        }


class Editor:
    """
    Handles video editing operations including:
    - Rule-based rough cutting
    - Video stitching/concatenation
    - Clip extraction
    """
    
    def __init__(self):
        self.temp_dir = settings.processing_temp_dir
        self.output_dir = settings.final_output_dir
        self.ffmpeg_path = settings.ffmpeg_path
        self.asset_manager = AssetManager()
        settings.ensure_directories()
        
        # Default cutting rules (can be customized)
        self.default_rules: List[CutRule] = []
    
    def _run_ffmpeg(self, args: List[str], timeout: int = 3600) -> subprocess.CompletedProcess:
        """Run FFmpeg command with given arguments"""
        cmd = [self.ffmpeg_path] + args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
    
    def add_rule(self, rule: CutRule) -> None:
        """Add a cutting rule to the default ruleset"""
        self.default_rules.append(rule)
    
    def clear_rules(self) -> None:
        """Clear all default cutting rules"""
        self.default_rules.clear()
    
    def extract_clip(
        self,
        asset_id: str,
        input_path: str,
        start_time: float,
        end_time: Optional[float] = None,
        duration: Optional[float] = None,
        output_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract a clip from a video
        
        Args:
            asset_id: The unique asset identifier
            input_path: Path to the source video
            start_time: Start time in seconds
            end_time: End time in seconds (optional if duration provided)
            duration: Duration in seconds (optional if end_time provided)
            output_name: Custom output filename
            
        Returns:
            Dictionary containing clip extraction result
        """
        # Calculate duration if not provided
        if duration is None and end_time is not None:
            duration = end_time - start_time
        
        if duration is None:
            raise ValueError("Either end_time or duration must be provided")
        
        # Create clips directory
        clips_dir = self.temp_dir / asset_id / "clips"
        clips_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename
        if output_name is None:
            output_name = f"clip_{start_time:.1f}_{start_time + duration:.1f}.mp4"
        
        output_path = clips_dir / output_name
        
        # Log start
        self.asset_manager.append_log(asset_id, {
            "event": "clip_extraction_start",
            "timestamp": datetime.now().isoformat(),
            "start_time": start_time,
            "duration": duration
        })
        
        # FFmpeg command
        args = [
            "-ss", str(start_time),
            "-i", str(input_path),
            "-t", str(duration),
            "-c", "copy",
            "-y",
            str(output_path)
        ]
        
        try:
            result = self._run_ffmpeg(args)
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg clip extraction failed: {result.stderr}")
            
            # Log completion
            self.asset_manager.append_log(asset_id, {
                "event": "clip_extraction_complete",
                "timestamp": datetime.now().isoformat(),
                "output_path": str(output_path)
            })
            
            return {
                "success": True,
                "output_path": str(output_path),
                "start_time": start_time,
                "duration": duration
            }
            
        except Exception as e:
            self.asset_manager.append_log(asset_id, {
                "event": "clip_extraction_failed",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
            raise
    
    def apply_rules(
        self,
        asset_id: str,
        input_path: str,
        rules: Optional[List[CutRule]] = None,
        video_duration: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Apply cutting rules to extract multiple clips
        
        Args:
            asset_id: The unique asset identifier
            input_path: Path to the source video
            rules: List of cutting rules (uses default if not provided)
            video_duration: Total video duration (will be auto-detected if not provided)
            
        Returns:
            Dictionary containing all extracted clips
        """
        rules = rules or self.default_rules
        
        if not rules:
            return {"success": True, "clips": [], "message": "No rules to apply"}
        
        # Log start
        self.asset_manager.append_log(asset_id, {
            "event": "rule_application_start",
            "timestamp": datetime.now().isoformat(),
            "rule_count": len(rules)
        })
        
        clips = []
        errors = []
        
        for i, rule in enumerate(rules):
            if not rule.keep:
                continue
            
            try:
                # Determine clip boundaries
                start = rule.start_time or 0
                end = rule.end_time
                duration = rule.duration
                
                clip_result = self.extract_clip(
                    asset_id=asset_id,
                    input_path=input_path,
                    start_time=start,
                    end_time=end,
                    duration=duration,
                    output_name=f"rule_{i}_{rule.name}.mp4"
                )
                
                clip_result["rule"] = rule.to_dict()
                clips.append(clip_result)
                
            except Exception as e:
                errors.append({
                    "rule_index": i,
                    "rule_name": rule.name,
                    "error": str(e)
                })
        
        # Log completion
        self.asset_manager.append_log(asset_id, {
            "event": "rule_application_complete",
            "timestamp": datetime.now().isoformat(),
            "clips_created": len(clips),
            "errors": len(errors)
        })
        
        return {
            "success": len(errors) == 0,
            "clips": clips,
            "errors": errors
        }
    
    def concatenate_videos(
        self,
        asset_id: str,
        input_paths: List[str],
        output_name: Optional[str] = None,
        use_reencoding: bool = False
    ) -> Dict[str, Any]:
        """
        Concatenate multiple videos into one
        
        Args:
            asset_id: The unique asset identifier
            input_paths: List of video file paths to concatenate
            output_name: Custom output filename
            use_reencoding: If True, re-encode for better compatibility
            
        Returns:
            Dictionary containing concatenation result
        """
        if not input_paths:
            raise ValueError("No input paths provided")
        
        # Create output directory
        output_dir = self.output_dir / asset_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if output_name is None:
            output_name = f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        output_path = output_dir / output_name
        
        # Create concat file list
        concat_file = self.temp_dir / asset_id / "concat_list.txt"
        concat_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(concat_file, "w", encoding="utf-8") as f:
            for path in input_paths:
                # Escape single quotes in path
                escaped_path = str(path).replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
        
        # Log start
        self.asset_manager.append_log(asset_id, {
            "event": "concatenation_start",
            "timestamp": datetime.now().isoformat(),
            "input_count": len(input_paths),
            "use_reencoding": use_reencoding
        })
        
        # FFmpeg command
        if use_reencoding:
            args = [
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "22",
                "-c:a", "aac",
                "-b:a", "192k",
                "-y",
                str(output_path)
            ]
        else:
            args = [
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c", "copy",
                "-y",
                str(output_path)
            ]
        
        try:
            result = self._run_ffmpeg(args)
            
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg concatenation failed: {result.stderr}")
            
            # Update asset metadata
            self.asset_manager.update_metadata(asset_id, {
                "final_output": str(output_path),
                "status": "completed"
            })
            
            # Log completion
            self.asset_manager.append_log(asset_id, {
                "event": "concatenation_complete",
                "timestamp": datetime.now().isoformat(),
                "output_path": str(output_path)
            })
            
            return {
                "success": True,
                "output_path": str(output_path)
            }
            
        except Exception as e:
            self.asset_manager.append_log(asset_id, {
                "event": "concatenation_failed",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            })
            raise
        finally:
            # Cleanup concat file
            if concat_file.exists():
                concat_file.unlink()
    
    def rough_cut(
        self,
        asset_id: str,
        input_path: str,
        cuts: List[Tuple[float, float]],
        output_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform a rough cut by extracting and concatenating specified segments
        
        Args:
            asset_id: The unique asset identifier
            input_path: Path to the source video
            cuts: List of (start_time, end_time) tuples defining segments to keep
            output_name: Custom output filename
            
        Returns:
            Dictionary containing rough cut result
        """
        if not cuts:
            raise ValueError("No cuts specified")
        
        # Log start
        self.asset_manager.append_log(asset_id, {
            "event": "rough_cut_start",
            "timestamp": datetime.now().isoformat(),
            "cut_count": len(cuts)
        })
        
        # Extract each segment
        clip_paths = []
        
        for i, (start, end) in enumerate(cuts):
            try:
                clip_result = self.extract_clip(
                    asset_id=asset_id,
                    input_path=input_path,
                    start_time=start,
                    end_time=end,
                    output_name=f"roughcut_segment_{i:03d}.mp4"
                )
                clip_paths.append(clip_result["output_path"])
            except Exception as e:
                self.asset_manager.append_log(asset_id, {
                    "event": "rough_cut_segment_failed",
                    "timestamp": datetime.now().isoformat(),
                    "segment_index": i,
                    "error": str(e)
                })
                raise
        
        # Concatenate all segments
        if output_name is None:
            output_name = f"roughcut_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        result = self.concatenate_videos(
            asset_id=asset_id,
            input_paths=clip_paths,
            output_name=output_name
        )
        
        # Log completion
        self.asset_manager.append_log(asset_id, {
            "event": "rough_cut_complete",
            "timestamp": datetime.now().isoformat(),
            "output_path": result.get("output_path")
        })
        
        return result
    
    def auto_rough_cut(
        self,
        asset_id: str,
        input_path: str,
        keep_intro_seconds: float = 5.0,
        keep_outro_seconds: float = 5.0,
        video_duration: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Automatic rough cut keeping intro and outro
        
        Args:
            asset_id: The unique asset identifier
            input_path: Path to the source video
            keep_intro_seconds: Seconds to keep from start
            keep_outro_seconds: Seconds to keep from end
            video_duration: Total video duration (auto-detected if not provided)
            
        Returns:
            Dictionary containing auto rough cut result
        """
        # Get video duration if not provided
        if video_duration is None:
            from modules.preprocessor import preprocessor
            metadata = preprocessor.extract_metadata(input_path)
            video_duration = metadata.get("duration", 0)
        
        if video_duration <= 0:
            raise ValueError("Could not determine video duration")
        
        cuts = [
            (0, keep_intro_seconds),
            (video_duration - keep_outro_seconds, video_duration)
        ]
        
        return self.rough_cut(
            asset_id=asset_id,
            input_path=input_path,
            cuts=cuts,
            output_name=f"auto_roughcut_{asset_id[:8]}.mp4"
        )


# Global instance
editor = Editor()
