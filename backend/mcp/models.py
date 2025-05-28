from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class ContextMetadata(BaseModel):
    """Metadata about a context."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = []
    description: Optional[str] = None
    agent_id: str
    agent_type: str

class ContextData(BaseModel):
    """The actual context data."""
    content: Dict[str, Any]
    version: int = 1
    metadata: ContextMetadata

class ContextRequest(BaseModel):
    """Request to create or update context."""
    data: Dict[str, Any]
    tags: Optional[List[str]] = None
    description: Optional[str] = None

class ContextResponse(BaseModel):
    """Response containing context information."""
    id: UUID
    data: ContextData
    status: str = "success"

class ContextQuery(BaseModel):
    """Query parameters for searching contexts."""
    agent_id: Optional[str] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    limit: int = 100
    offset: int = 0

class ContextUpdate(BaseModel):
    """Request to update existing context."""
    data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
