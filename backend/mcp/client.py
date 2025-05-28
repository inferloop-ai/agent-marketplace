import httpx
from typing import Optional, List, Dict, Any
from .models import (
    ContextRequest, ContextResponse, ContextQuery, ContextUpdate,
    ContextData, ContextMetadata
)

class MCPClient:
    """Client for interacting with the Model Context Protocol server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the client.
        
        Args:
            base_url: Base URL of the MCP server
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
    
    async def create_context(
        self,
        data: Dict[str, Any],
        agent_id: str,
        agent_type: str,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> ContextResponse:
        """Create a new context.
        
        Args:
            data: Context data to store
            agent_id: ID of the agent
            agent_type: Type of the agent
            tags: Optional tags for the context
            description: Optional description
            
        Returns:
            ContextResponse: Response containing the created context
        """
        request = ContextRequest(
            data=data,
            tags=tags,
            description=description,
            agent_id=agent_id,
            agent_type=agent_type
        )
        
        response = await self.client.post("/contexts", json=request.dict())
        response.raise_for_status()
        return ContextResponse(**response.json())
    
    async def list_contexts(
        self,
        agent_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ContextResponse]:
        """List contexts based on query parameters.
        
        Args:
            agent_id: Filter by agent ID
            tags: Filter by tags
            created_after: Filter by creation time after
            created_before: Filter by creation time before
            limit: Number of results to return
            offset: Offset for pagination
            
        Returns:
            List[ContextResponse]: List of matching contexts
        """
        query = ContextQuery(
            agent_id=agent_id,
            tags=tags,
            created_after=created_after,
            created_before=created_before,
            limit=limit,
            offset=offset
        )
        
        response = await self.client.get("/contexts", params=query.dict())
        response.raise_for_status()
        return [ContextResponse(**ctx) for ctx in response.json()]
    
    async def get_context(self, context_id: str) -> ContextResponse:
        """Get a specific context by ID.
        
        Args:
            context_id: ID of the context to retrieve
            
        Returns:
            ContextResponse: Response containing the context
        """
        response = await self.client.get(f"/contexts/{context_id}")
        response.raise_for_status()
        return ContextResponse(**response.json())
    
    async def update_context(
        self,
        context_id: str,
        data: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> ContextResponse:
        """Update an existing context.
        
        Args:
            context_id: ID of the context to update
            data: New context data
            tags: New tags
            description: New description
            
        Returns:
            ContextResponse: Response containing the updated context
        """
        update = ContextUpdate(
            data=data,
            tags=tags,
            description=description
        )
        
        response = await self.client.put(
            f"/contexts/{context_id}",
            json=update.dict(exclude_unset=True)
        )
        response.raise_for_status()
        return ContextResponse(**response.json())
    
    async def delete_context(self, context_id: str) -> None:
        """Delete a context.
        
        Args:
            context_id: ID of the context to delete
        """
        response = await self.client.delete(f"/contexts/{context_id}")
        response.raise_for_status()
