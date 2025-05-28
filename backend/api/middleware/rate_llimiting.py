# backend/api/middleware/rate_limiting.py (Enhanced)
import time
import logging
from typing import Dict, Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with Redis backend."""
    
    def __init__(
        self,
        app,
        redis_url: str = "redis://localhost:6379/0",
        requests_per_minute: int = 100,
        burst_requests: int = 20,
        enable_rate_limiting: bool = True
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_requests = burst_requests
        self.enable_rate_limiting = enable_rate_limiting
        self.redis_client = None
        self.redis_url = redis_url
        
        # Fallback in-memory storage
        self.in_memory_storage: Dict[str, list] = {}
    
    async def connect_redis(self):
        """Connect to Redis if available."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Rate limiting using Redis backend")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory rate limiting: {e}")
            self.redis_client = None
    
    async def dispatch(self, request: Request, call_next):
        if not self.enable_rate_limiting:
            return await call_next(request)
        
        # Initialize Redis connection if needed
        if self.redis_client is None and self.redis_url:
            await self.connect_redis()
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        allowed = await self._check_rate_limit(client_id)
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "limit": self.requests_per_minute,
                    "window": "1 minute"
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        response = await call_next(request)
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Use authenticated user ID if available
        if hasattr(request.state, 'user') and request.state.user:
            return f"user:{request.state.user.id}"
        
        # Use IP address as fallback
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = getattr(request.client, "host", "unknown")
        
        return f"ip:{ip}"
    
    async def _check_rate_limit(self, client_id: str) -> bool:
        """Check if request is within rate limit."""
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        if self.redis_client:
            return await self._check_rate_limit_redis(client_id, current_time, window_start)
        else:
            return await self._check_rate_limit_memory(client_id, current_time, window_start)
    
    async def _check_rate_limit_redis(self, client_id: str, current_time: float, window_start: float) -> bool:
        """Redis-based rate limiting."""
        try:
            key = f"rate_limit:{client_id}"
            
            # Remove old entries
            await self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            request_count = await self.redis_client.zcard(key)
            
            if request_count >= self.requests_per_minute:
                return False
            
            # Add current request
            await self.redis_client.zadd(key, {str(current_time): current_time})
            await self.redis_client.expire(key, 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis rate limiting error: {e}")
            # Fallback to allow request
            return True
    
    async def _check_rate_limit_memory(self, client_id: str, current_time: float, window_start: float) -> bool:
        """In-memory rate limiting."""
        if client_id not in self.in_memory_storage:
            self.in_memory_storage[client_id] = []
        
        # Clean old entries
        self.in_memory_storage[client_id] = [
            timestamp for timestamp in self.in_memory_storage[client_id]
            if timestamp > window_start
        ]
        
        # Check limit
        if len(self.in_memory_storage[client_id]) >= self.requests_per_minute:
            return False
        
        # Add current request
        self.in_memory_storage[client_id].append(current_time)
        return True
