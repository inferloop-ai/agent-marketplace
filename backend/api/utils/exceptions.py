# backend/api/utils/exceptions.py
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class CustomHTTPException(HTTPException):
    """Enhanced HTTP exception with additional context."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_type: str = "http_error",
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_type = error_type
        self.context = context or {}
        self.timestamp = datetime.utcnow()

class ValidationException(Exception):
    """Custom validation exception."""
    
    def __init__(self, errors: Dict[str, Any]):
        self.errors = errors
        super().__init__(f"Validation failed: {errors}")

class DatabaseException(Exception):
    """Custom database exception."""
    
    def __init__(self, message: str, operation: str = "unknown"):
        self.message = message
        self.operation = operation
        super().__init__(message)

class AuthenticationException(Exception):
    """Custom authentication exception."""
    
    def __init__(self, detail: str = "Authentication failed"):
        self.detail = detail
        super().__init__(detail)

class BusinessLogicException(Exception):
    """Custom business logic exception."""
    
    def __init__(self, message: str, code: str = "business_error"):
        self.message = message
        self.code = code
        super().__init__(message)

# Exception handlers
async def validation_exception_handler(request: Request, exc: ValidationException):
    """Handle validation exceptions."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Validation failed",
            "details": exc.errors,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
            "method": request.method
        }
    )

async def database_exception_handler(request: Request, exc: DatabaseException):
    """Handle database exceptions."""
    logger.error(f"Database error in {exc.operation}: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "database_error",
            "message": "A database error occurred",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

async def authentication_exception_handler(request: Request, exc: AuthenticationException):
    """Handle authentication exceptions."""
    return JSONResponse(
        status_code=401,
        content={
            "error": "authentication_error",
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

async def business_logic_exception_handler(request: Request, exc: BusinessLogicException):
    """Handle business logic exceptions."""
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.code,
            "message": exc.message,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

