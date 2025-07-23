import time
import redis
from fastapi import Request, HTTPException, status
from typing import Dict, Optional
import json
import hashlib

from ..core.config import settings

# Redis client for rate limiting
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class RateLimiter:
    """Production-ready rate limiting middleware"""
    
    def __init__(self):
        self.redis = redis_client
    
    async def check_rate_limit(
        self,
        request: Request,
        identifier: str,
        max_requests: int,
        window_seconds: int,
        tenant_id: Optional[str] = None
    ) -> bool:
        """Check if request is within rate limit"""
        
        # Create unique key for this identifier and endpoint
        endpoint = f"{request.method}:{request.url.path}"
        key = f"rate_limit:{identifier}:{endpoint}"
        
        if tenant_id:
            key = f"rate_limit:tenant:{tenant_id}:{identifier}:{endpoint}"
        
        current_time = int(time.time())
        window_start = current_time - window_seconds
        
        try:
            # Use Redis sorted set for sliding window
            pipe = self.redis.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, window_seconds)
            
            results = pipe.execute()
            current_requests = results[1]
            
            return current_requests < max_requests
            
        except Exception as e:
            # If Redis fails, allow the request (fail open)
            print(f"Rate limiting error: {e}")
            return True
    
    async def get_rate_limit_info(
        self,
        request: Request,
        identifier: str,
        max_requests: int,
        window_seconds: int,
        tenant_id: Optional[str] = None
    ) -> Dict[str, int]:
        """Get current rate limit status"""
        
        endpoint = f"{request.method}:{request.url.path}"
        key = f"rate_limit:{identifier}:{endpoint}"
        
        if tenant_id:
            key = f"rate_limit:tenant:{tenant_id}:{identifier}:{endpoint}"
        
        current_time = int(time.time())
        window_start = current_time - window_seconds
        
        try:
            # Clean old entries and count current
            pipe = self.redis.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            results = pipe.execute()
            
            current_requests = results[1]
            remaining = max(0, max_requests - current_requests)
            reset_time = current_time + window_seconds
            
            return {
                "limit": max_requests,
                "remaining": remaining,
                "reset": reset_time,
                "window": window_seconds
            }
            
        except Exception:
            return {
                "limit": max_requests,
                "remaining": max_requests,
                "reset": current_time + window_seconds,
                "window": window_seconds
            }


# Rate limiting configurations
RATE_LIMITS = {
    "auth": {"max_requests": 5, "window_seconds": 300},      # 5 requests per 5 minutes
    "api": {"max_requests": 100, "window_seconds": 60},      # 100 requests per minute
    "scan": {"max_requests": 10, "window_seconds": 300},     # 10 scans per 5 minutes
    "upload": {"max_requests": 20, "window_seconds": 3600},  # 20 uploads per hour
}

# Tenant-based rate limits
TENANT_RATE_LIMITS = {
    "trial": {"max_requests": 50, "window_seconds": 3600},        # 50 requests per hour
    "starter": {"max_requests": 500, "window_seconds": 3600},     # 500 requests per hour
    "professional": {"max_requests": 2000, "window_seconds": 3600}, # 2000 requests per hour
    "enterprise": {"max_requests": 10000, "window_seconds": 3600},  # 10000 requests per hour
}


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    rate_limiter = RateLimiter()
    
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/metrics"]:
        response = await call_next(request)
        return response
    
    # Get client identifier (IP address)
    client_ip = request.client.host
    
    # Determine rate limit type based on endpoint
    path = request.url.path
    if path.startswith("/api/auth"):
        limit_config = RATE_LIMITS["auth"]
    elif path.startswith("/api/scans"):
        limit_config = RATE_LIMITS["scan"]
    elif "upload" in path:
        limit_config = RATE_LIMITS["upload"]
    else:
        limit_config = RATE_LIMITS["api"]
    
    # Check rate limit
    allowed = await rate_limiter.check_rate_limit(
        request,
        client_ip,
        limit_config["max_requests"],
        limit_config["window_seconds"]
    )
    
    if not allowed:
        # Get rate limit info for headers
        rate_info = await rate_limiter.get_rate_limit_info(
            request,
            client_ip,
            limit_config["max_requests"],
            limit_config["window_seconds"]
        )
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(rate_info["limit"]),
                "X-RateLimit-Remaining": str(rate_info["remaining"]),
                "X-RateLimit-Reset": str(rate_info["reset"]),
                "Retry-After": str(rate_info["window"])
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers to response
    rate_info = await rate_limiter.get_rate_limit_info(
        request,
        client_ip,
        limit_config["max_requests"],
        limit_config["window_seconds"]
    )
    
    response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
    
    return response


async def tenant_rate_limit_check(request: Request, tenant_id: str, plan_type: str) -> bool:
    """Check tenant-specific rate limits"""
    rate_limiter = RateLimiter()
    
    # Get tenant rate limit configuration
    limit_config = TENANT_RATE_LIMITS.get(plan_type, TENANT_RATE_LIMITS["trial"])
    
    # Check tenant rate limit
    allowed = await rate_limiter.check_rate_limit(
        request,
        f"tenant:{tenant_id}",
        limit_config["max_requests"],
        limit_config["window_seconds"],
        tenant_id
    )
    
    return allowed