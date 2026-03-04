import redis
from app.core.config import settings
import logging
import json
from typing import Any, Optional

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                username=settings.REDIS_USERNAME,
                password=settings.REDIS_PASSWORD,
                decode_responses=settings.REDIS_DECODE_RESPONSES,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Connected to Redis successfully")
            self.enabled = True
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.enabled = False
        except Exception as e:
            logger.error(f"Redis initialization error: {e}")
            self.enabled = False

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache hit for key: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss for key: {key}")
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        if not self.enabled:
            return False

        try:
            ttl = ttl or settings.REDIS_CACHE_TTL
            json_value = json.dumps(value)
            result = self.redis_client.setex(key, ttl, json_value)
            logger.debug(f"Cached key: {key} with TTL: {ttl}s")
            return result
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False

        try:
            result = self.redis_client.delete(key)
            logger.debug(f"Deleted cache key: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.enabled:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                result = self.redis_client.delete(*keys)
                logger.debug(f"Cleared {result} cache keys matching pattern: {pattern}")
                return result
            return 0
        except Exception as e:
            logger.error(f"Redis clear pattern error: {e}")
            return 0

# Global cache instance
cache = RedisCache()