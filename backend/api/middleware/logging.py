"""
LoggingMiddleware for FastAPI

This middleware logs incoming HTTP requests and outgoing responses for observability and debugging.
It captures request method, path, status code, duration, and optionally request/response body.

Features:
    - Logs request method, path, status, duration
    - Optionally logs request and response bodies (configurable)
    - Integrates with FastAPI's middleware stack
    - Compatible with async endpoints

Example log output:
    [INFO] Request: POST /api/agents | Status: 201 | Duration: 35ms

Configuration:
    - LOG_LEVEL: Set the logging level (default: INFO)
    - LOG_BODY: Set to True to log request/response bodies (default: False)
"""

# backend/api/middleware/logging.py (Enhanced)
import logging
import time
import json
from uuid import uuid4
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api.requests")

class EnhancedLoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced logging middleware with structured logging."""
    
    def __init__(self, app, log_body: bool = False, log_headers: bool = False):
        super().__init__(app)
        self.log_body = log_body
        self.log_headers = log_headers
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID if not exists
        request_id = getattr(request.state, 'request_id', str(uuid4()))
        request.state.request_id = request_id
        
        start_time = time.time()
        
        # Prepare request log data
        request_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "timestamp": time.time()
        }
        
        if self.log_headers:
            request_data["headers"] = dict(request.headers)
        
        # Log request body for non-GET requests
        if self.log_body and request.method not in ["GET", "HEAD", "OPTIONS"]:
            try:
                body = await request.body()
                if body:
                    request_data["body_size"] = len(body)
                    # Only log small bodies to avoid massive logs
                    if len(body) < 1000:
                        request_data["body"] = body.decode("utf-8", errors="ignore")
            except Exception as e:
                request_data["body_error"] = str(e)
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log exception and re-raise
            logger.error(
                "Request failed with exception",
                extra={
                    **request_data,
                    "exception": str(exc),
                    "duration_ms": (time.time() - start_time) * 1000
                }
            )
            raise
        
        # Prepare response log data
        duration_ms = (time.time() - start_time) * 1000
        response_data = {
            **request_data,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "response_size": response.headers.get("content-length")
        }
        
        # Determine log level based on status code
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO
        
        # Log the request/response
        logger.log(
            log_level,
            f"{request.method} {request.url.path} - {response.status_code} - {duration_ms:.2f}ms",
            extra=response_data
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (when behind proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"

