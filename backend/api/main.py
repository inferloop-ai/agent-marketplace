"""
Agent Workflow Builder - Main FastAPI Application

This is the main entry point for the Agent Workflow Builder API.
It sets up the FastAPI application with all routes, middleware, and configuration.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Import configuration and database
from config.settings import settings
from config.database import database, engine, metadata
from config.logging import setup_logging

# Import middleware
from middleware.auth import AuthMiddleware
from middleware.cors import setup_cors
from middleware.logging import LoggingMiddleware
from middleware.rate_limit import RateLimitMiddleware

# Import routes
from routes import (
    workflows,
    agents, 
    auth,
    executions,
    templates,
    integrations
)

# Import utilities
from utils.exceptions import (
    CustomHTTPException,
    ValidationException,
    DatabaseException,
    AuthenticationException
)

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting Agent Workflow Builder API...")
    
    # Connect to database
    try:
        await database.connect()
        logger.info("✅ Database connected successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    # Initialize database tables (if needed)
    try:
        metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database table initialization warning: {e}")
    
    # Additional startup tasks
    logger.info("✅ API startup completed")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Agent Workflow Builder API...")
    await database.disconnect()
    logger.info("✅ Database disconnected")
    logger.info("✅ API shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="Agent Workflow Builder API",
    description="""
    🤖 **Agent Workflow Builder API**
    
    A powerful API for creating, managing, and executing AI agent workflows.
    
    ## Features
    
    * 🎨 **Visual Workflow Builder** - Create workflows with drag-and-drop interface
    * 🤖 **Multi-Framework Support** - LangChain, CrewAI, AutoGen integration
    * ⚡ **Real-time Execution** - Live workflow monitoring and execution
    * 🔒 **Enterprise Security** - JWT authentication and role-based access
    * 🔗 **Extensive Integrations** - Connect to databases, APIs, and cloud services
    * 📊 **Analytics & Monitoring** - Performance metrics and execution tracking
    
    ## Quick Start
    
    1. **Authenticate** - Get your JWT token from `/auth/login`
    2. **Create Workflow** - Use `/workflows/` to create your first workflow
    3. **Add Agents** - Configure agents with `/agents/`
    4. **Execute** - Run your workflow with `/executions/`
    
    ## Support
    
    - 📚 [Documentation](https://docs.agent-workflow-builder.com)
    - 🐛 [Report Issues](https://github.com/agent-workflow-builder/issues)
    - 💬 [Community](https://discord.gg/agent-workflow-builder)
    """,
    version="1.0.0",
    terms_of_service="https://agent-workflow-builder.com/terms",
    contact={
        "name": "Agent Workflow Builder Team",
        "url": "https://agent-workflow-builder.com/support",
        "email": "support@agent-workflow-builder.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
    openapi_url="/openapi.json" if settings.environment != "production" else None,
)

# =============================================================================
# MIDDLEWARE SETUP
# =============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware (security)
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )

# Custom Middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    """Handle custom HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_type,
            "message": exc.detail,
            "request_id": getattr(request.state, "request_id", None),
            "timestamp": exc.timestamp.isoformat(),
        }
    )

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    """Handle validation exceptions."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Validation failed",
            "details": exc.errors,
            "request_id": getattr(request.state, "request_id", None),
        }
    )

@app.exception_handler(DatabaseException)
async def database_exception_handler(request: Request, exc: DatabaseException):
    """Handle database exceptions."""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "database_error",
            "message": "A database error occurred",
            "request_id": getattr(request.state, "request_id", None),
        }
    )

@app.exception_handler(AuthenticationException)
async def auth_exception_handler(request: Request, exc: AuthenticationException):
    """Handle authentication exceptions."""
    return JSONResponse(
        status_code=401,
        content={
            "error": "authentication_error",
            "message": exc.detail,
            "request_id": getattr(request.state, "request_id", None),
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle standard HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail,
            "request_id": getattr(request.state, "request_id", None),
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None),
        }
    )

# =============================================================================
# ROUTE REGISTRATION
# =============================================================================

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring and load balancers.
    """
    try:
        # Check database connectivity
        await database.fetch_one("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": "1.0.0",
        "environment": settings.environment,
        "database": db_status,
        "timestamp": "2024-01-01T00:00:00Z",  # Use actual timestamp
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    Root endpoint with API information.
    """
    return {
        "message": "🤖 Agent Workflow Builder API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "running"
    }

# Include API routes with prefixes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(executions.router, prefix="/executions", tags=["Executions"])
app.include_router(templates.router, prefix="/templates", tags=["Templates"])
app.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])

# Static files (if needed)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# =============================================================================
# DEVELOPMENT SERVER
# =============================================================================

if __name__ == "__main__":
    # This is only used for development
    # In production, use: uvicorn main:app --host 0.0.0.0 --port 8000
    
    logger.info("🚀 Starting development server...")
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
        log_level="info" if settings.environment == "development" else "warning",
        access_log=settings.environment == "development",
        workers=1 if settings.environment == "development" else 4,
    )