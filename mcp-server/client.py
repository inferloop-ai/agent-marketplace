"""
MCP Server Client
================

Client library for interacting with the MCP Server API.
"""

import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from .models import ContextRequest, ContextResponse, ContextStatus


class MCPClient:
    """
    Client for interacting with the MCP Server API.
    
    Args:
        base_url: Base URL of the MCP Server
        api_key: API key for authentication
        timeout: Request timeout in seconds
    """
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout
        )

    async def health_check(self) -> Dict[str, Any]:
        """Check server health and statistics."""
        response = await self.client.get("/health")
        response.raise_for_status()
        return response.json()

    async def create_context(self, request: ContextRequest) -> ContextResponse:
        """
        Create a new context.
        
        Args:
            request: Context creation request
            
        Returns:
            ContextResponse: Created context details
        """
        response = await self.client.post("/contexts", json=request.dict())
        response.raise_for_status()
        return ContextResponse(**response.json())

    async def get_context(self, context_id: UUID) -> ContextResponse:
        """
        Get a specific context.
        
        Args:
            context_id: ID of the context to retrieve
            
        Returns:
            ContextResponse: Context details
            
        Raises:
            httpx.HTTPStatusError: If context not found (404)
        """
        response = await self.client.get(f"/contexts/{context_id}")
        response.raise_for_status()
        return ContextResponse(**response.json())

    async def list_contexts(
        self,
        agent_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ContextResponse]:
        """
        List all available contexts.
        
        Args:
            agent_id: Filter by agent ID
            agent_type: Filter by agent type
            tags: Filter by tags
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List[ContextResponse]: List of contexts
        """
        params = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "tags": tags,
            "limit": limit,
            "offset": offset
        }
        
        response = await self.client.get("/contexts", params=params)
        response.raise_for_status()
        return [ContextResponse(**ctx) for ctx in response.json()]

    async def update_context(
        self,
        context_id: UUID,
        update: Dict[str, Any]
    ) -> ContextResponse:
        """
        Update an existing context.
        
        Args:
            context_id: ID of the context to update
            update: Context update data
            
        Returns:
            ContextResponse: Updated context details
            
        Raises:
            httpx.HTTPStatusError: If context not found (404)
        """
        response = await self.client.put(
            f"/contexts/{context_id}",
            json=update
        )
        response.raise_for_status()
        return ContextResponse(**response.json())

    async def delete_context(self, context_id: UUID) -> None:
        """
        Delete a context.
        
        Args:
            context_id: ID of the context to delete
            
        Raises:
            httpx.HTTPStatusError: If context not found (404)
        """
        response = await self.client.delete(f"/contexts/{context_id}")
        response.raise_for_status()

    async def list_extensions(self) -> List[Dict[str, Any]]:
        """List all loaded extensions."""
        response = await self.client.get("/extensions")
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()