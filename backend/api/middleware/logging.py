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

import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("api.logging")

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, log_body: bool = False):
        super().__init__(app)
        self.log_body = log_body

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_body = None

        if self.log_body:
            request_body = await request.body()

        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        log_message = (
            f"{request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Duration: {process_time:.2f}ms"
        )

        if self.log_body and request_body:
            log_message += f" | Request Body: {request_body.decode(errors='replace')}"
        if self.log_body and hasattr(response, "body_iterator"):
            # body_iterator can only be read once; omitting for safety
            log_message += " | Response Body: <streamed>"

        logger.info(log_message)
        return response
