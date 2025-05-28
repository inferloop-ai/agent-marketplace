from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from redis import Redis
from uuid import uuid4
from typing import Optional, List
import json
from datetime import datetime, timedelta
from .models import (
    ContextRequest, ContextResponse, ContextQuery, ContextUpdate,
    ContextData, ContextMetadata
)
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Model Context Protocol Server",
    description="A scalable context management system for AI agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security settings
security = HTTPBearer()

# Redis connection
redis = Redis(host="localhost", port=6379, db=0)

# Context key prefix
CONTEXT_PREFIX = "context:"

# Authentication configuration
API_TOKENS = {
    "mcp_admin": "your-secure-token-here",  # Replace with actual secure token
    "backend_service": "your-backend-service-token"  # Token for backend service
}

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify the authentication token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        str: The authenticated agent ID
        
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    if token not in API_TOKENS:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return credentials.credentials

def get_redis():
    """Dependency for Redis connection."""
    return redis

def create_context_key(context_id: str) -> str:
    """Create a Redis key for a context."""
    return f"{CONTEXT_PREFIX}{context_id}"

def serialize_context(data: ContextData) -> str:
    """Serialize context data to JSON."""
    return json.dumps(data.dict())

def deserialize_context(data: str) -> ContextData:
    """Deserialize context data from JSON."""
    return ContextData(**json.loads(data))

@app.post("/contexts", response_model=ContextResponse)
async def create_context(
    request: ContextRequest,
    token: str = Depends(verify_token),
    redis: Redis = Depends(get_redis)
):
    """Create a new context.
    
    Args:
        request: Context creation request
        token: Authentication token
        redis: Redis connection
        
    Returns:
        ContextResponse: Response containing the created context
        
    Raises:
        HTTPException: If request fails validation
    """
    try:
        context_id = str(uuid4())
        metadata = ContextMetadata(
            agent_id=request.agent_id,
            agent_type=request.agent_type,
            tags=request.tags or [],
            description=request.description
        )
        
        context_data = ContextData(
            content=request.data,
            version=1,
            metadata=metadata
        )
        
        key = create_context_key(context_id)
        redis.set(key, serialize_context(context_data))
        
        return ContextResponse(
            id=context_id,
            data=context_data
        )
    except Exception as e:
        logger.error(f"Failed to create context: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create context: {str(e)}"
        )

@app.get("/contexts", response_model=List[ContextResponse])
async def list_contexts(
    query: ContextQuery = Depends(),
    token: str = Depends(verify_token),
    redis: Redis = Depends(get_redis)
):
    """List contexts based on query parameters.
    
    Args:
        query: Query parameters
        token: Authentication token
        redis: Redis connection
        
    Returns:
        List[ContextResponse]: List of matching contexts
    """
    try:
        keys = redis.keys(f"{CONTEXT_PREFIX}*")
        contexts = []
        
        for key in keys:
            data = redis.get(key)
            if data:
                context = deserialize_context(data)
                
                # Apply filters
                if (not query.agent_id or context.metadata.agent_id == query.agent_id) and \
                   (not query.tags or all(tag in context.metadata.tags for tag in query.tags)) and \
                   (not query.created_after or context.metadata.created_at >= query.created_after) and \
                   (not query.created_before or context.metadata.created_at <= query.created_before):
                    
                    contexts.append(ContextResponse(
                        id=key.replace(CONTEXT_PREFIX, ""),
                        data=context
                    ))
        
        # Apply pagination
        start = query.offset
        end = start + query.limit
        return contexts[start:end]
    except Exception as e:
        logger.error(f"Failed to list contexts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list contexts: {str(e)}"
        )

@app.get("/contexts/{context_id}", response_model=ContextResponse)
async def get_context(
    context_id: str,
    token: str = Depends(verify_token),
    redis: Redis = Depends(get_redis)
):
    """Get a specific context by ID.
    
    Args:
        context_id: ID of the context
        token: Authentication token
        redis: Redis connection
        
    Returns:
        ContextResponse: Response containing the context
        
    Raises:
        HTTPException: If context not found
    """
    try:
        key = create_context_key(context_id)
        data = redis.get(key)
        
        if not data:
            raise HTTPException(status_code=404, detail="Context not found")
        
        context = deserialize_context(data)
        return ContextResponse(
            id=context_id,
            data=context
        )
    except Exception as e:
        logger.error(f"Failed to get context {context_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get context {context_id}: {str(e)}"
        )

@app.put("/contexts/{context_id}", response_model=ContextResponse)
async def update_context(
    context_id: str,
    update: ContextUpdate,
    token: str = Depends(verify_token),
    redis: Redis = Depends(get_redis)
):
    """Update an existing context.
    
    Args:
        context_id: ID of the context
        update: Update data
        token: Authentication token
        redis: Redis connection
        
    Returns:
        ContextResponse: Response containing the updated context
        
    Raises:
        HTTPException: If context not found or update fails
    """
    try:
        key = create_context_key(context_id)
        data = redis.get(key)
        
        if not data:
            raise HTTPException(status_code=404, detail="Context not found")
        
        context = deserialize_context(data)
        
        # Update metadata
        context.metadata.updated_at = datetime.utcnow()
        if update.tags is not None:
            context.metadata.tags = update.tags
        if update.description is not None:
            context.metadata.description = update.description
        
        # Update content if provided
        if update.data is not None:
            context.content = update.data
            context.version += 1
        
        redis.set(key, serialize_context(context))
        return ContextResponse(
            id=context_id,
            data=context
        )
    except Exception as e:
        logger.error(f"Failed to update context {context_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update context {context_id}: {str(e)}"
        )

@app.delete("/contexts/{context_id}")
async def delete_context(
    context_id: str,
    token: str = Depends(verify_token),
    redis: Redis = Depends(get_redis)
):
    """Delete a context.
    
    Args:
        context_id: ID of the context
        token: Authentication token
        redis: Redis connection
        
    Raises:
        HTTPException: If context not found
    """
    try:
        key = create_context_key(context_id)
        if redis.delete(key) == 0:
            raise HTTPException(status_code=404, detail="Context not found")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to delete context {context_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete context {context_id}: {str(e)}"
        )
