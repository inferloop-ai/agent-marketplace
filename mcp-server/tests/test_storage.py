"""
Test Storage
===========

Tests for the MCP Server storage system.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
import redis.asyncio as redis

from mcp_server.storage import ContextStorage
from mcp_server.models import ContextData, ContextMetadata, ContextStatus


@pytest.fixture
def storage():
    """Create a storage instance for testing."""
    storage = ContextStorage()
    storage.redis = redis.Redis(decode_responses=True)
    yield storage
    asyncio.run(storage.redis.flushall())


@pytest.mark.asyncio
async def test_create_context(storage):
    """Test creating a new context."""
    context_data = ContextData(
        content={"key": "value"},
        version=1,
        metadata=ContextMetadata(
            agent_id="test-agent",
            agent_type="test",
            description="Test context"
        )
    )
    
    context_id = await storage.create_context(context_data)
    assert isinstance(context_id, str)
    
    # Verify context exists
    result = await storage.get_context(context_id)
    assert result is not None
    assert result.data == context_data


@pytest.mark.asyncio
async def test_get_nonexistent_context(storage):
    """Test getting a non-existent context."""
    with pytest.raises(Exception):
        await storage.get_context(str(uuid4()))


@pytest.mark.asyncio
async def test_update_context(storage):
    """Test updating a context."""
    context_data = ContextData(
        content={"key": "value"},
        version=1,
        metadata=ContextMetadata(
            agent_id="test-agent",
            agent_type="test"
        )
    )
    
    context_id = await storage.create_context(context_data)
    
    # Update context
    updated_data = ContextData(
        content={"key": "updated_value"},
        version=2,
        metadata=ContextMetadata(
            agent_id="test-agent",
            agent_type="test",
            updated_at=datetime.utcnow()
        )
    )
    
    await storage.update_context(context_id, updated_data)
    
    # Verify update
    result = await storage.get_context(context_id)
    assert result.data == updated_data


@pytest.mark.asyncio
async def test_delete_context(storage):
    """Test deleting a context."""
    context_data = ContextData(
        content={"key": "value"},
        version=1,
        metadata=ContextMetadata(
            agent_id="test-agent",
            agent_type="test"
        )
    )
    
    context_id = await storage.create_context(context_data)
    
    # Delete context
    await storage.delete_context(context_id)
    
    # Verify deletion
    with pytest.raises(Exception):
        await storage.get_context(context_id)


@pytest.mark.asyncio
async def test_context_ttl(storage):
    """Test context TTL functionality."""
    context_data = ContextData(
        content={"key": "value"},
        version=1,
        metadata=ContextMetadata(
            agent_id="test-agent",
            agent_type="test"
        )
    )
    
    # Create context with TTL
    context_id = await storage.create_context(context_data, ttl=1)
    
    # Wait for TTL to expire
    await asyncio.sleep(2)
    
    # Verify context is expired
    with pytest.raises(Exception):
        await storage.get_context(context_id)
