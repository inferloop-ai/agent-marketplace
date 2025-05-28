# rag-pipeline/config.py
import os
from typing import List, Optional, Literal
from pydantic import BaseSettings, Field, validator

class RAGSettings(BaseSettings):
    """RAG Pipeline configuration settings."""
    
    # Server
    host: str = Field(default="0.0.0.0", env="RAG_HOST")
    port: int = Field(default=8090, env="RAG_PORT")
    debug: bool = Field(default=False, env="RAG_DEBUG")
    
    # Vector Database
    qdrant_url: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, env="QDRANT_API_KEY")
    qdrant_collection_size: int = Field(default=1536, env="QDRANT_COLLECTION_SIZE")
    qdrant_distance: str = Field(default="Cosine", env="QDRANT_DISTANCE")
    
    # Alternative vector databases
    chroma_persist_directory: str = Field(default="./chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    pinecone_api_key: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    pinecone_environment: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")
    weaviate_url: str = Field(default="http://localhost:8080", env="WEAVIATE_URL")
    
    # Embeddings
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", 
        env="EMBEDDING_MODEL"
    )
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    huggingface_api_key: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    
    # Document Processing
    max_file_size: str = Field(default="50MB", env="MAX_FILE_SIZE")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    enable_ocr: bool = Field(default=False, env="ENABLE_OCR")
    ocr_language: str = Field(default="eng", env="OCR_LANGUAGE")
    
    # Search & Retrieval
    default_top_k: int = Field(default=5, env="DEFAULT_TOP_K")
    hybrid_search_alpha: float = Field(default=0.5, env="HYBRID_SEARCH_ALPHA")
    enable_reranking: bool = Field(default=True, env="ENABLE_RERANKING")
    rerank_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        env="RERANK_MODEL"
    )
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/rag_pipeline",
        env="DATABASE_URL"
    )
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Processing
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    batch_size: int = Field(default=32, env="BATCH_SIZE")
    enable_async: bool = Field(default=True, env="ENABLE_ASYNC")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    @validator('max_file_size')
    def parse_file_size(cls, v):
        """Parse file size string to bytes."""
        if isinstance(v, str):
            v = v.upper()
            if v.endswith('MB'):
                return int(v[:-2]) * 1024 * 1024
            elif v.endswith('KB'):
                return int(v[:-2]) * 1024
            elif v.endswith('GB'):
                return int(v[:-2]) * 1024 * 1024 * 1024
        return int(v)
    
    class Config:
        env_file = ".env"

settings = RAGSettings()
