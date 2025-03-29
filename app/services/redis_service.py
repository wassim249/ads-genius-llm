"""Redis service for caching and retrieving model completions."""

import hashlib
import json
import os

from redis.asyncio import Redis
from redis.exceptions import ConnectionError

from app.core.app_logging import get_logger

logger = get_logger(__name__)


class RedisService:
    """Service for caching and retrieving model completions using Redis."""

    def __init__(self):
        """Initialize Redis connection.

        Args:
            host: Redis server hostname
            port: Redis server port
            db: Redis database number
            password: Redis authentication password
        """
        try:
            self.redis = Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=os.getenv("REDIS_PORT", 6379),
                db=os.getenv("REDIS_DB", 0),
                password=os.getenv("REDIS_PASSWORD", None),
            )
        except ConnectionError as e:
            logger.error(f"Error initializing Redis connection: {e}")
            raise e

    async def set_completion(self, args: dict, completion: str):
        """Store a model completion in Redis cache.

        Args:
            args: Dictionary of arguments used for the completion request
            completion: The generated completion text to cache

        Returns:
            None
        """
        key = hashlib.sha256(json.dumps(args).encode()).hexdigest()
        await self.redis.set(key, completion)

    async def get_completion(self, args: dict):
        """Retrieve a cached completion from Redis.

        Args:
            args: Dictionary of arguments used for the completion request

        Returns:
            The cached completion if found, otherwise None
        """
        key = hashlib.sha256(json.dumps(args).encode()).hexdigest()
        return await self.redis.get(key)
