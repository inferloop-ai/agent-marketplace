# rag-pipeline/models.py
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

class ChunkingStrategy(str, Enum):
    FIXED = "fixed"
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"
    DOCUMENT_BASED = "document_based"

class VectorStore(str, Enum):
    QDRANT = "qdrant"
    CHROMA = "chroma"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    FAISS = "faiss"

class DocumentMetadata(BaseModel):
    """Metadata for a processed document."""
    filename: str
    file_type: str
    file_size: int
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    
    # Content metadata
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    language: Optional[str] = None
    
    # Custom metadata
    tags: List[str] = []
    category: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None
    
    # Processing metadata
    chunk_count: int = 0
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE
    embedding_model: str = ""
    vector_store: VectorStore = VectorStore.QDRANT

class DocumentChunk(BaseModel):
    """A chunk of processed document."""
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    chunk_index: int
    content: str
    
    # Position metadata
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    page_number: Optional[int] = None
    
    # Chunk metadata
    word_count: int
    char_count: int
    embedding: Optional[List[float]] = None
    
    # Context
    previous_chunk: Optional[str] = None
    next_chunk: Optional[str] = None
    
    @validator('content')
    def validate_content(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Chunk content cannot be empty')
        return v.strip()

class ProcessingJob(BaseModel):
    """Document processing job."""
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    status: DocumentStatus = DocumentStatus.PENDING
    
    # Processing parameters
    collection_name: str
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Progress tracking
    total_chunks: int = 0
    processed_chunks: int = 0
    failed_chunks: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0

class DocumentUpload(BaseModel):
    """Document upload request."""
    collection_name: str
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE
    chunk_size: int = Field(default=1000, ge=100, le=4000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)
    
    # Optional metadata
    tags: List[str] = []
    category: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None
    
    @validator('chunk_overlap')
    def validate_chunk_overlap(cls, v, values):
        if 'chunk_size' in values and v >= values['chunk_size']:
            raise ValueError('Chunk overlap must be less than chunk size')
        return v

class DocumentResponse(BaseModel):
    """Document processing response."""
    document_id: UUID
    filename: str
    status: DocumentStatus
    metadata: DocumentMetadata
    job_id: Optional[UUID] = None
    
    # Processing results
    chunks_created: int = 0
    processing_time_seconds: Optional[float] = None
    
    # URLs for accessing
    chunks_url: Optional[str] = None
    download_url: Optional[str] = None

class SearchRequest(BaseModel):
    """Search request for RAG pipeline."""
    query: str
    collection_name: str
    
    # Search parameters
    top_k: int = Field(default=5, ge=1, le=100)
    score_threshold: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Hybrid search
    enable_hybrid: bool = True
    hybrid_alpha: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Filtering
    filters: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    date_range: Optional[Dict[str, datetime]] = None
    
    # Reranking
    enable_reranking: bool = True
    rerank_top_k: Optional[int] = None
    
    @validator('query')
    def validate_query(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Query cannot be empty')
        return v.strip()

class SearchResult(BaseModel):
    """Individual search result."""
    chunk_id: UUID
    document_id: UUID
    content: str
    score: float
    
    # Metadata
    filename: str
    page_number: Optional[int] = None
    chunk_index: int
    
    # Context
    context_before: Optional[str] = None
    context_after: Optional[str] = None
    
    # Document metadata
    tags: List[str] = []
    category: Optional[str] = None
    author: Optional[str] = None

class SearchResponse(BaseModel):
    """Search response from RAG pipeline."""
    query: str
    results: List[SearchResult]
    
    # Search metadata
    total_results: int
    search_time_ms: float
    collection_name: str
    
    # Search parameters used
    top_k: int
    hybrid_search_used: bool
    reranking_used: bool

class CollectionInfo(BaseModel):
    """Information about a document collection."""
    name: str
    document_count: int
    chunk_count: int
    total_size_bytes: int
    
    # Collection metadata
    created_at: datetime
    updated_at: datetime
    embedding_model: str
    vector_store: VectorStore
    
    # Statistics
    avg_chunk_size: float
    languages: List[str] = []
    categories: List[str] = []
    tags: List[str] = []

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    uptime: float
    
    # Component health
    vector_store_connected: bool
    database_connected: bool
    redis_connected: bool
    
    # Statistics
    total_documents: int
    total_chunks: int
    active_jobs: int
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
