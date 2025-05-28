# mcp-server/main.py
import time
import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import settings
from .models import (
    ContextRequest, ContextResponse, ContextQuery, ContextUpdate,
    ContextData, ContextMetadata, HealthResponse, ExtensionInfo
)
from .storage import storage
from .extensions import extension_manager

# Setup logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # Startup
    logger.info("🚀 Starting MCP Server...")
    
    try:
        await storage.connect()
        logger.info("✅ Storage connected")
        
        if settings.enable_extensions:
            await extension_manager.load_extensions()
            logger.info(f"✅ Loaded {len(extension_manager.extensions)} extensions")
        
        app.state.start_time = time.time()
        logger.info("✅ MCP Server started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start MCP Server: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down MCP Server...")
    await storage.disconnect()
    logger.info("✅ MCP Server shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Model Context Protocol Server",
    description="Independent, scalable context management for AI agents",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify authentication token."""
    token = credentials.credentials
    
    valid_tokens = [settings.admin_token, settings.backend_token]
    if token not in valid_tokens:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return token

# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check Redis connection
        redis_connected = await storage.redis.ping() if storage.redis else False
        
        # Get stats
        stats = await storage.get_stats()
        
        # Calculate uptime
        uptime = time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0
        
        return HealthResponse(
            status="healthy" if redis_connected else "degraded",
            version="2.0.0",
            uptime=uptime,
            redis_connected=redis_connected,
            contexts_count=stats.get("contexts_active", 0),
            extensions_loaded=len(extension_manager.extensions),
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

# Context management endpoints
@app.post("/contexts", response_model=ContextResponse)
async def create_context(
    request: ContextRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Create a new context."""
    try:
        context_id = uuid4()
        
        # Create metadata
        metadata = ContextMetadata(
            agent_id=request.agent_id,
            agent_type=request.agent_type,
            tags=request.tags or [],
            description=request.description,
            session_id=request.session_id,
            user_id=request.user_id,
            priority=request.priority
        )
        
        # Create context data
        context_data = ContextData(
            content=request.data,
            version=1,
            metadata=metadata
        )
        
        # Store context
        success = await storage.store_context(context_id, context_data, request.ttl)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store context")
        
        # Run extensions
        if settings.enable_extensions:
            background_tasks.add_task(
                extension_manager.trigger_hook,
                "context_created",
                context_id=str(context_id),
                context_data=context_data
            )
        
        # Calculate expiry
        expires_at = None
        if request.ttl:
            expires_at = datetime.utcnow().timestamp() + request.ttl
        elif settings.context_ttl > 0:
            expires_at = datetime.utcnow().timestamp() + settings.context_ttl
        
        return ContextResponse(
            id=context_id,
            data=context_data,
            expires_at=datetime.fromtimestamp(expires_at) if expires_at else None
        )
        
    except Exception as e:
        logger.error(f"Failed to create context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contexts/{context_id}", response_model=ContextResponse)
async def get_context(
    context_id: UUID,
    token: str = Depends(verify_token)
):
    """Get a context by ID."""
    try:
        context_data = await storage.get_context(context_id)
        
        if not context_data:
            raise HTTPException(status_code=404, detail="Context not found")
        
        return ContextResponse(
            id=context_id,
            data=context_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get context {context_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/contexts", response_model=List[ContextResponse])
async def search_contexts(
    agent_id: Optional[str] = None,
    agent_type: Optional[str] = None,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    tags: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    token: str = Depends(verify_token)
):
    """Search contexts by criteria."""
    try:
        # Parse tags
        tag_list = tags.split(",") if tags else None
        
        # Search contexts
        context_ids = await storage.search_contexts(
            agent_id=agent_id,
            agent_type=agent_type,
            tags=tag_list,
            limit=limit,
            offset=offset
        )
        
        # Get context data
        results = []
        for context_id in context_ids:
            context_data = await storage.get_context(context_id)
            if context_data:
                results.append(ContextResponse(
                    id=context_id,
                    data=context_data
                ))
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to search contexts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/contexts/{context_id}", response_model=ContextResponse)
async def update_context(
    context_id: UUID,
    update: ContextUpdate,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Update an existing context."""
    try:
        # Update context
        context_data = await storage.update_context(
            context_id, 
            update.dict(exclude_unset=True)
        )
        
        if not context_data:
            raise HTTPException(status_code=404, detail="Context not found")
        
        # Run extensions
        if settings.enable_extensions:
            background_tasks.add_task(
                extension_manager.trigger_hook,
                "context_updated",
                context_id=str(context_id),
                context_data=context_data
            )
        
        return ContextResponse(
            id=context_id,
            data=context_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update context {context_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/contexts/{context_id}")
async def delete_context(
    context_id: UUID,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Delete a context."""
    try:
        # Get context for extensions
        context_data = await storage.get_context(context_id) if settings.enable_extensions else None
        
        # Delete context
        success = await storage.delete_context(context_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Context not found")
        
        # Run extensions
        if settings.enable_extensions and context_data:
            background_tasks.add_task(
                extension_manager.trigger_hook,
                "context_deleted",
                context_id=str(context_id),
                context_data=context_data
            )
        
        return {"status": "success", "message": "Context deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete context {context_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Extension management
@app.get("/extensions", response_model=List[ExtensionInfo])
async def list_extensions(token: str = Depends(verify_token)):
    """List loaded extensions."""
    if not settings.enable_extensions:
        return []
    
    return [
        ExtensionInfo(
            name=ext.name,
            version=ext.version,
            description=ext.description,
            enabled=ext.enabled,
            hooks=list(ext.hooks.keys())
        )
        for ext in extension_manager.extensions.values()
    ]

@app.post("/extensions/{extension_name}/enable")
async def enable_extension(
    extension_name: str,
    token: str = Depends(verify_token)
):
    """Enable an extension."""
    if not settings.enable_extensions:
        raise HTTPException(status_code=400, detail="Extensions disabled")
    
    success = await extension_manager.enable_extension(extension_name)
    if not success:
        raise HTTPException(status_code=404, detail="Extension not found")
    
    return {"status": "success", "message": f"Extension {extension_name} enabled"}

@app.post("/extensions/{extension_name}/disable")
async def disable_extension(
    extension_name: str,
    token: str = Depends(verify_token)
):
    """Disable an extension."""
    if not settings.enable_extensions:
        raise HTTPException(status_code=400, detail="Extensions disabled")
    
    success = await extension_manager.disable_extension(extension_name)
    if not success:
        raise HTTPException(status_code=404, detail="Extension not found")
    
    return {"status": "success", "message": f"Extension {extension_name} disabled"}

# Statistics
@app.get("/stats")
async def get_stats(token: str = Depends(verify_token)):
    """Get server statistics."""
    try:
        stats = await storage.get_stats()
        
        return {
            "server": {