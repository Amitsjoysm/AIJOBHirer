"""Redis service for caching and job queue"""
import redis
import os
from typing import Optional, Any
import json
import logging

logger = logging.getLogger(__name__)

class RedisService:
    """Redis service following Singleton pattern for connection management"""
    
    _instance: Optional['RedisService'] = None
    _client: Optional[redis.Redis] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            redis_host = os.environ.get('REDIS_HOST', 'localhost')
            redis_port = int(os.environ.get('REDIS_PORT', 6379))
            redis_db = int(os.environ.get('REDIS_DB', 0))
            
            self._client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            logger.info(f"Redis connected to {redis_host}:{redis_port}")
    
    @property
    def client(self) -> redis.Redis:
        """Get Redis client instance"""
        return self._client
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        try:
            return self._client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if expire:
                return self._client.setex(key, expire, value)
            else:
                return self._client.set(key, value)
        except Exception as e:
            logger.error(f"Redis SET error: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            return self._client.delete(key) > 0
        except Exception as e:
            logger.error(f"Redis DELETE error: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return self._client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error: {str(e)}")
            return False
    
    def ping(self) -> bool:
        """Check Redis connection health"""
        try:
            return self._client.ping()
        except Exception as e:
            logger.error(f"Redis PING error: {str(e)}")
            return False
