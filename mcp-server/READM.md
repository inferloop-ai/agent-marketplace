# mcp-server/README.md
# Model Context Protocol (MCP) Server

An independent, scalable context management system for AI agents, designed to handle context storage, retrieval, and management across multiple AI agents and applications.

## Features

- **Context Management**: Store, retrieve, and version context data for AI agents
- **Multi-Agent Support**: Handle contexts for different agent types and instances  
- **Versioning**: Track context changes with automatic version control
- **Metadata Tracking**: Rich metadata including timestamps, tags, and descriptions
- **Async/Await**: High-performance async operations
- **Redis Storage**: Fast, scalable Redis-based storage
- **REST API**: RESTful interface for easy integration
- **Type Safety**: Full Pydantic model validation
- **Authentication**: Secure token-based authentication
- **Extensions**: Plugin system for custom functionality

## Installation

```bash
cd mcp-server
pip install -r requirements.txt
```

## Quick Start

1. Start Redis server:
```bash
redis-server
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the MCP server:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

4. Test the API:
```bash
curl http://localhost:8080/health
```

## API Documentation

Visit `http://localhost:8080/docs` for interactive API documentation.

# mcp-server/requirements.txt
# MCP Server Dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
redis==5.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.25.2
structlog==23.2.0
python-dotenv==1.0.0

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
isort==5.12.0
mypy==1.7.1

# mcp-server/.env.example
# MCP Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8080
MCP_DEBUG=true

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# Security
MCP_SECRET_KEY=your-super-secret-key-change-in-production
MCP_ADMIN_TOKEN=your-secure-admin-token
MCP_BACKEND_TOKEN=your-backend-service-token

# Logging
LOG_LEVEL=INFO

# Extensions
ENABLE_EXTENSIONS=true
EXTENSIONS_DIR=./extensions



