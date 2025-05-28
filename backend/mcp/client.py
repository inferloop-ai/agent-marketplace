import httpx
from typing import Optional, List, Dict, Any, Union
from .models import (
    ContextRequest, ContextResponse, ContextQuery, ContextUpdate,
    ContextData, ContextMetadata
)
from httpx._exceptions import HTTPError
import logging

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for interacting with the Model Context Protocol server."""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0):
        """Initialize the client.
        
        Args:
            base_url: Base URL of the MCP server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
        self._token: Optional[str] = None
    
    async def authenticate(self, token: str) -> None:
        """Set authentication token for requests.
        
        Args:
            token: Authentication token
        """
        self._token = token
        self.client.headers.update({"Authorization": f"Bearer {token}"})
    
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
            
        Raises:
            MCPError: If request fails
        """
        request = ContextRequest(
            data=data,
            agent_id=agent_id,
            agent_type=agent_type,
            tags=tags,
            description=description
        )
        
        try:
            response = await self.client.post(
                "/contexts",
                json=request.dict(),
                timeout=30.0
            )
            response.raise_for_status()
            return ContextResponse(**response.json())
        except HTTPError as e:
            logger.error(f"Failed to create context: {str(e)}")
            raise MCPError(f"Failed to create context: {str(e)}") from e
    
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
            
        Raises:
            MCPError: If request fails
        """
        query = ContextQuery(
            agent_id=agent_id,
            tags=tags,
            created_after=created_after,
            created_before=created_before,
            limit=limit,
            offset=offset
        )
        
        try:
            response = await self.client.get(
                "/contexts",
                params=query.dict(),
                timeout=30.0
            )
            response.raise_for_status()
            return [ContextResponse(**ctx) for ctx in response.json()]
        except HTTPError as e:
            logger.error(f"Failed to list contexts: {str(e)}")
            raise MCPError(f"Failed to list contexts: {str(e)}") from e
    
    async def get_context(self, context_id: str) -> ContextResponse:
        """Get a specific context by ID.
        
        Args:
            context_id: ID of the context to retrieve
            
        Returns:
            ContextResponse: Response containing the context
            
        Raises:
            MCPError: If request fails
        """
        try:
            response = await self.client.get(
                f"/contexts/{context_id}",
                timeout=30.0
            )
            response.raise_for_status()
            return ContextResponse(**response.json())
        except HTTPError as e:
            logger.error(f"Failed to get context {context_id}: {str(e)}")
            raise MCPError(f"Failed to get context {context_id}: {str(e)}") from e
    
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
            
        Raises:
            MCPError: If request fails
        """
        update = ContextUpdate(
            data=data,
            tags=tags,
            description=description
        )
        
        try:
            response = await self.client.put(
                f"/contexts/{context_id}",
                json=update.dict(exclude_unset=True),
                timeout=30.0
            )
            response.raise_for_status()
            return ContextResponse(**response.json())
        except HTTPError as e:
            logger.error(f"Failed to update context {context_id}: {str(e)}")
            raise MCPError(f"Failed to update context {context_id}: {str(e)}") from e
    
    async def delete_context(self, context_id: str) -> None:
        """Delete a context.
        
        Args:
            context_id: ID of the context to delete
            
        Raises:
            MCPError: If request fails
        """
        try:
            response = await self.client.delete(
                f"/contexts/{context_id}",
                timeout=30.0
            )
            response.raise_for_status()
        except HTTPError as e:
            logger.error(f"Failed to delete context {context_id}: {str(e)}")
            raise MCPError(f"Failed to delete context {context_id}: {str(e)}") from e

class MCPError(Exception):
    """Custom exception for MCP client errors."""
    pass
