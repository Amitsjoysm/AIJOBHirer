"""Rate limiting middleware for API protection"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
import os

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute", "1000/hour"],
    storage_uri=f"redis://{os.environ.get('REDIS_HOST', 'localhost')}:{os.environ.get('REDIS_PORT', '6379')}/1"
)

# Rate limit tiers for different endpoints
class RateLimits:
    """Rate limit configurations"""
    
    # Authentication endpoints (more restrictive)
    AUTH = "10/minute"
    
    # Public endpoints (job listings, applications)
    PUBLIC = "30/minute"
    
    # Protected endpoints (dashboard, management)
    PROTECTED = "100/minute"
    
    # Heavy operations (AI generation, resume parsing)
    HEAVY = "20/minute"
    
    # Email sending
    EMAIL = "50/hour"
