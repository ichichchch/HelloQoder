"""
BatchClip Backend Configuration
Uses Pydantic BaseSettings to load configuration from .env file
"""

from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Storage Paths
    processing_temp_dir: Path = Path("./temp")
    final_output_dir: Path = Path("./output")
    upload_dir: Path = Path("./uploads")
    assets_dir: Path = Path("./assets")
    
    # Storage Backend
    storage_type: Literal["local", "oss"] = "local"
    
    # Logging
    log_level: str = "INFO"
    
    # FFmpeg
    ffmpeg_path: str = "ffmpeg"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Processing Settings
    max_upload_size_mb: int = 500
    proxy_resolution: int = 720
    default_segment_duration: int = 60
    
    def ensure_directories(self) -> None:
        """Create all required directories if they don't exist"""
        for dir_path in [
            self.processing_temp_dir,
            self.final_output_dir,
            self.upload_dir,
            self.assets_dir
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Convert max upload size to bytes"""
        return self.max_upload_size_mb * 1024 * 1024


# Global settings instance
settings = Settings()
