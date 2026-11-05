"""Session memory store using Redis for short-term agent memory."""
import redis.asyncio as aioredis
import json
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class SessionMemoryStore:
    """Short-term agent memory backed by Redis with TTL."""

    SESSION_TTL_SECONDS = 3600  # 1 hour

    def __init__(self):
        self._redis = None

    async def _get_redis(self):
        if self._redis is None:
            self._redis = await aioredis.from_url(settings.REDIS_URL)
        return self._redis

    async def set(self, session_id: str, key: str, value: Any) -> None:
        redis = await self._get_redis()
        full_key = f"session:{session_id}:{key}"
        await redis.set(full_key, json.dumps(value), ex=self.SESSION_TTL_SECONDS)

    async def get(self, session_id: str, key: str) -> Any:
        redis = await self._get_redis()
        full_key = f"session:{session_id}:{key}"
        data = await redis.get(full_key)
        return json.loads(data) if data else None

    async def get_all(self, session_id: str) -> dict:
        redis = await self._get_redis()
        pattern = f"session:{session_id}:*"
        keys = await redis.keys(pattern)
        result = {}
        for key in keys:
            data = await redis.get(key)
            if data:
                sub_key = key.decode().split(":", 2)[-1]
                result[sub_key] = json.loads(data)
        return result

    async def delete(self, session_id: str) -> None:
        redis = await self._get_redis()
        pattern = f"session:{session_id}:*"
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)


from typing import Any
