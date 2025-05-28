# Agent Marketplace Platform

A scalable platform for managing and orchestrating AI agents with context-aware capabilities.

## Overview

The Agent Marketplace Platform consists of three main components:

1. **MCP Server (Marketplace Control Plane)**
2. **Frontend Application**
3. **Backend Services**

### 1. MCP Server

The MCP Server is the core component responsible for managing agent contexts and extensions.

#### Key Features
- Context Management
  - Create, update, and delete contexts
  - Context versioning
  - TTL support for context expiration
  - Metadata management

- Extension System
  - Dynamic extension loading
  - Hook-based extension system
  - Extension lifecycle management
  - Custom functionality through extensions

- Storage
  - Redis-based storage
  - Context persistence
  - Efficient data retrieval
  - TTL support

- Security
  - Token-based authentication
  - API key management
  - Secure context access

### 2. Frontend Application

The frontend provides a user interface for managing agents and workflows.

#### Key Components
- **AgentWorkflowBuilder**
  - Visual workflow builder
  - Agent category management
  - Workflow execution
  - Context management UI

- **Redux State Management**
  - Auth state management
  - Workflow state management
  - UI state management

### 3. Backend Services

The backend services provide the core functionality for the platform.

#### Key Services
- **API Service**
  - REST API endpoints
  - Authentication
  - Context management
  - Extension management

- **Storage Service**
  - Redis integration
  - Data persistence
  - Cache management

## Architecture

```
agent-marketplace/
├── mcp-server/                 # MCP Server implementation
│   ├── main.py               # FastAPI server
│   ├── config.py             # Configuration management
│   ├── models.py             # Data models
│   ├── storage.py            # Storage implementation
│   ├── client.py             # Server client
│   ├── extensions/           # Extension system
│   │   ├── __init__.py      # Extension package
│   │   ├── base_extension.py # Base extension class
│   │   ├── extension_manager.py # Extension manager
│   │   └── example_extension.py # Example extension
│   └── utils.py              # Utility functions
├── frontend/                 # Frontend application
│   ├── src/                  # Source code
│   │   ├── components/       # React components
│   │   │   └── Canvas/      # Workflow builder
│   │   ├── store/           # Redux store
│   │   │   ├── authSlice.ts # Auth state
│   │   │   ├── workflowSlice.ts # Workflow state
│   │   │   └── uiSlice.ts   # UI state
│   │   ├── services/        # API services
│   │   └── hooks/           # Custom hooks
│   └── public/              # Static assets
└── backend/                 # Backend services
```

## Setup and Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Redis 6.0+

### MCP Server Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the server:
```bash
python -m mcp_server.main
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

## Configuration

### MCP Server Configuration

The server can be configured through environment variables:

```env
# Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8080
MCP_LOG_LEVEL=INFO

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# Security
MCP_SECRET_KEY=your-secret-key
MCP_ADMIN_TOKEN=your-admin-token
MCP_BACKEND_TOKEN=your-backend-token

# Context Settings
CONTEXT_TTL=86400
MAX_CONTEXT_SIZE=1048576

# Extensions
ENABLE_EXTENSIONS=true
EXTENSIONS_DIR=./extensions
```

### Frontend Configuration

The frontend can be configured through environment variables:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8080
REACT_APP_API_KEY=your-api-key

# Feature Flags
REACT_APP_ENABLE_DEBUG=true
```

## API Documentation

The API documentation is automatically generated and available at:

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

### API Endpoints

#### Context Management
- `POST /contexts` - Create a new context
- `GET /contexts/{context_id}` - Get context by ID
- `PUT /contexts/{context_id}` - Update context
- `DELETE /contexts/{context_id}` - Delete context
- `GET /contexts` - List contexts

#### Extension Management
- `GET /extensions` - List extensions
- `POST /extensions/{extension_name}/enable` - Enable extension
- `POST /extensions/{extension_name}/disable` - Disable extension

#### Health Check
- `GET /health` - Check server health

## Development

### Running Tests

```bash
# MCP Server tests
pytest tests/

# Frontend tests
npm test
```

### Building the Frontend

```bash
cd frontend
npm run build
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
- Open an issue on GitHub
- Join our Discord community
- Email support@agent-marketplace.com
