from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MiMo API
    mimo_api_key: str = ""
    mimo_api_base: str = "https://api.xiaomimimo.com/v1"
    
    # Zhipu Embedding API
    zhipu_api_key: str = ""
    zhipu_api_base: str = "https://open.bigmodel.cn/api/paas/v4"
    zhipu_embedding_model: str = "embedding-3"
    
    # Vector Database (Milvus)
    vector_db_uri: str = "http://localhost:19530"
    milvus_collection_name: str = "psychology_knowledge"
    
    # RAG Settings
    rag_top_k: int = 5
    rag_similarity_threshold: float = 0.4
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
