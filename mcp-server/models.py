# mcp-server/models.py
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class ContextStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class ContextMetadata(BaseModel):
    """Metadata about a context."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    accessed_at: Optional[datetime] = None
    tags: List[str] = []
    description: Optional[str] = None
    agent_id: str
    agent_type: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    priority: int = Field(default=0, ge=0, le=10)
    status: ContextStatus = ContextStatus.ACTIVE

class ContextData(BaseModel):
    """The actual context data with versioning."""
    content: Dict[str, Any]
    version: int = 1
    metadata: ContextMetadata
    checksum: Optional[str] = None

class ContextRequest(BaseModel):
    """Request to create or update context."""
    data: Dict[str, Any]
    agent_id: str
    agent_type: str
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    priority: int = Field(default=0, ge=0, le=10)
    ttl: Optional[int] = None  # Custom TTL in seconds
    
    @validator('data')
    def validate_data_size(cls, v):
        import json
        from .config import settings
        
        data_size = len(json.dumps(v).encode('utf-8'))
        if data_size > settings.max_context_size:
            raise ValueError(f'Context data too large: {data_size} bytes')
        return v

class ContextResponse(BaseModel):
    """Response model for context operations."""
    id: UUID
    data: ContextData
    created_at: datetime
    updated_at: datetime
    accessed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    tags: List[str] = []
    description: Optional[str] = None
    agent_id: str
    agent_type: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    priority: int = Field(default=0, ge=0, le=10)
    status: ContextStatus

    @validator('expires_at', pre=True)
    def validate_expires_at(cls, v):
        """Convert timestamp to datetime if needed."""
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v)
        return v

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            UUID: lambda uid: str(uid)
        }
        schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "data": {
                    "content": {"key": "value"},
                    "version": 1
                },
                "created_at": "2023-10-01T00:00:00",
                "updated_at": "2023-10-01T00:00:00",
                "expires_at": "2023-10-02T00:00:00",
                "tags": ["example"],
                "description": "Example context",
                "agent_id": "agent-1",
                "agent_type": "llm",
                "priority": 5,
                "status": "active"
            }
        }

class ContextQuery(BaseModel):
    """Query parameters for searching contexts."""
    agent_id: Optional[str] = None
    agent_type: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[ContextStatus] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    min_priority: Optional[int] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

class ContextUpdate(BaseModel):
    """Request to update existing context."""
    data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    priority: Optional[int] = Field(default=None, ge=0, le=10)
    status: Optional[ContextStatus] = None
    ttl: Optional[int] = None

class ExtensionInfo(BaseModel):
    """Information about a loaded extension."""
    name: str
    version: str
    description: str
    enabled: bool
    hooks: List[str] = []

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    uptime: float
    redis_connected: bool
    contexts_count: int
    extensions_loaded: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
