# Model Context Protocol (MCP) Server

A scalable context management system for AI agents, designed to handle context storage, retrieval, and management across multiple AI agents.

## Features

- RESTful API for context management
- Version control for context data
- Metadata tracking (creation time, update time, tags, description)
- Efficient Redis storage
- Async client interface
- Type-safe with Pydantic models
- Pagination and filtering support
- CORS support for cross-origin requests

### 1. Agent Context Management

The MCP server provides a robust system for managing context across different AI agents. Key features include:

#### Context Creation
```python
# Create a new context for an agent
context = await mcp_client.create_context(
    data={
        "user_id": "user-123",
        "conversation_history": [],
        "user_preferences": {}
    },
    agent_id="agent-456",
    agent_type="chat",
    tags=["conversation", "active"],
    description="New conversation with user"
)
```

#### Context Updates
```python
# Update an existing context
await mcp_client.update_context(
    context_id="context-789",
    data={
        "conversation_history": [...],
        "last_message": "Hello",
        "last_response": "Hi there!"
    },
    tags=["conversation", "active"],
    description="Updated conversation history"
)
```

#### Context Retrieval
```python
# Get a specific context
context = await mcp_client.get_context("context-789")

# List contexts with filters
contexts = await mcp_client.list_contexts(
    agent_id="agent-456",
    tags=["conversation", "active"],
    limit=100,
    offset=0
)
```

### 2. Agent Authentication and Security

The MCP server implements a secure authentication system for different types of agents:

#### Authentication Tokens
```python
# Backend service token
MCP_BACKEND_TOKEN = "your-backend-service-token"

# Admin token
MCP_ADMIN_TOKEN = "your-admin-token"
```

#### Token Usage
```python
# Initialize client with authentication
async def initialize_client():
    client = MCPClient()
    await client.authenticate(MCP_BACKEND_TOKEN)
    return client
```

### 3. Agent-Specific Context Features

#### Version Control
- Each context update increments the version number
- Maintains a complete history of changes
- Supports rollback to previous versions

#### Metadata Tracking
- Automatic timestamping of context updates
- Agent-specific metadata storage
- Custom tags for categorization

#### Error Handling
- Comprehensive error logging
- Detailed error responses
- Proper HTTP status codes

## Installation

1. Install the required dependencies:
```bash
pip install fastapi uvicorn redis httpx pydantic
```

2. Ensure Redis is running on your system:
```bash
# For Linux/Mac
redis-server

# For Windows
redis-server.exe
```

## Running the Server

Start the MCP server:
```bash
uvicorn mcp.server:app --reload
```

The server will be available at `http://localhost:8000`

## API Documentation

The MCP server provides the following endpoints:

### Create Context

Create a new context:

```http
POST /contexts
Content-Type: application/json

{
    "data": {
        "key": "value",
        "another_key": "another_value"
    },
    "agent_id": "your-agent-id",
    "agent_type": "llm",
    "tags": ["chat", "user-input"],
    "description": "Context for chat conversation"
}
```

Response:
```json
{
    "id": "unique-context-id",
    "data": {
        "content": {
            "key": "value",
            "another_key": "another_value"
        },
        "version": 1,
        "metadata": {
            "created_at": "2023-05-27T24:24:01+00:00",
            "updated_at": "2023-05-27T24:24:01+00:00",
            "tags": ["chat", "user-input"],
            "description": "Context for chat conversation",
            "agent_id": "your-agent-id",
            "agent_type": "llm"
        }
    },
    "status": "success"
}
```

### Get Context

Retrieve a specific context:

```http
GET /contexts/{context_id}
```

### List Contexts

List contexts with optional filtering:

```http
GET /contexts?agent_id=your-agent-id&tags=chat,user-input&limit=50&offset=0
```

### Update Context

Update an existing context:

```http
PUT /contexts/{context_id}
Content-Type: application/json

{
    "data": {
        "updated_key": "updated_value"
    },
    "tags": ["chat", "user-input", "updated"],
    "description": "Updated context"
}
```

### Delete Context

Delete a context:

```http
DELETE /contexts/{context_id}
```

## Using the Client

The MCP server provides a Python client for easy integration:

```python
from mcp.client import MCPClient

async def main():
    # Initialize client with custom URL if needed
    client = MCPClient(base_url="http://localhost:8000")
    
    # Create context
    context = await client.create_context(
        data={"user_input": "Hello world"},
        agent_id="agent-1",
        agent_type="llm",
        tags=["chat", "user-input"]
    )
    
    # Get context
    retrieved = await client.get_context(context.id)
    
    # Update context
    await client.update_context(
        context.id,
        data={"user_input": "Updated message"},
        tags=["chat", "user-input", "updated"]
    )
    
    # List contexts
    contexts = await client.list_contexts(
        agent_id="agent-1",
        tags=["chat"],
        limit=50
    )
    
    # Delete context
    await client.delete_context(context.id)

# Run the example
import asyncio
asyncio.run(main())
```

## Context Data Structure

The MCP server uses a structured format for context data:

```python
# Context Metadata
{
    "created_at": datetime,
    "updated_at": datetime,
    "tags": List[str],
    "description": Optional[str],
    "agent_id": str,
    "agent_type": str
}

# Context Data
{
    "content": Dict[str, Any],  # The actual context data
    "version": int,            # Version number
    "metadata": ContextMetadata
}
```

## Best Practices

1. **Version Control**: Always increment the version when updating context data
2. **Tagging**: Use tags to organize and filter contexts effectively
3. **Metadata**: Include descriptive metadata for better context tracking
4. **Error Handling**: Implement proper error handling for API calls
5. **Caching**: Consider implementing caching for frequently accessed contexts

## Security Considerations

1. **Authentication**: Implement proper authentication for sensitive contexts
2. **Access Control**: Use agent_id and agent_type to control access
3. **Data Encryption**: Consider encrypting sensitive context data
4. **Audit Logging**: Implement logging for context modifications

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details
