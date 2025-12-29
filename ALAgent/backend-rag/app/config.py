from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    embedding_model: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")
    
    # Milvus
    milvus_host: str = Field(default="localhost", env="MILVUS_HOST")
    milvus_port: int = Field(default=19530, env="MILVUS_PORT")
    milvus_user: str = Field(default="", env="MILVUS_USER")
    milvus_password: str = Field(default="", env="MILVUS_PASSWORD")
    milvus_db_name: str = Field(default="default", env="MILVUS_DB_NAME")
    
    # GitHub
    github_token: str = Field(default="", env="GITHUB_TOKEN")
    
    # Evaluation
    evaluation_dataset: str = Field(
        default="./data/evaluation/golden_dataset.json",
        env="EVALUATION_DATASET"
    )
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Chunking
    max_chunk_size: int = Field(default=1500, env="MAX_CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # Retrieval
    default_top_k: int = Field(default=5, env="DEFAULT_TOP_K")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
