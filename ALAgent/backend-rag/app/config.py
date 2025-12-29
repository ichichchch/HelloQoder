from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI / DashScope
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    dashscope_api_key: str = Field(default="", env="DASHSCOPE_API_KEY")
    
    # Embedding Models (支持多模态：图片、视频)
    # 文本向量化模型
    text_embedding_model: str = Field(default="text-embedding-v4", env="TEXT_EMBEDDING_MODEL")
    # 多模态向量化模型（支持图片、视频）
    multimodal_embedding_model: str = Field(default="qwen2.5-vl-embedding", env="MULTIMODAL_EMBEDDING_MODEL")
    # 向量维度
    text_embedding_dim: int = Field(default=1024, env="TEXT_EMBEDDING_DIM")
    multimodal_embedding_dim: int = Field(default=1024, env="MULTIMODAL_EMBEDDING_DIM")
    
    # LLM 配置 (用于 LightRAG 知识图谱提取)
    llm_model: str = Field(default="qwen-plus", env="LLM_MODEL")
    llm_api_base: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1", env="LLM_API_BASE")
    
    # LightRAG 配置
    lightrag_working_dir: str = Field(default="./lightrag_data", env="LIGHTRAG_WORKING_DIR")
    lightrag_query_mode: Literal["naive", "local", "global", "hybrid", "mix"] = Field(
        default="hybrid", env="LIGHTRAG_QUERY_MODE"
    )
    # LightRAG 知识图谱存储后端: json | neo4j | mongodb | postgres
    lightrag_graph_storage: str = Field(default="json", env="LIGHTRAG_GRAPH_STORAGE")
    # LightRAG 向量存储后端: milvus | faiss | chroma | qdrant
    lightrag_vector_storage: str = Field(default="milvus", env="LIGHTRAG_VECTOR_STORAGE")
    
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
    port: int = Field(default=8228, env="PORT")
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
