import hashlib
import logging
from typing import Any,Optional
from .redis_client import redis_client
from config import config

logger = logging.getLogger(__name__)

class CacheHandler:

    def __init__(self, prefix: str = 'parser'):
        self.prefix = prefix
        self.default_ttl = config.parser.cache_ttl

    def _make_key(self, identifier: str) -> str:
        if len(identifier) > 50:
            hash_obj = hashlib.md5(identifier.encode())
            identifier = hash_obj.hexdigest()
        return f"{self.prefix}:{identifier}"

    def get(self, url: str) -> Optional[Any]:
        key = self._make_key(url)
        data = redis_client.get(key)

        if data:
            logger.info(f"Cache HIT: {url[:50]}...")
            return data

        logger.info(f"Cache MISS: {url[:50]}...")
        return None

    def set(self, url: str, data: Any, ttl: int = None) -> bool:
        key = self._make_key(url)
        ttl = ttl or self.default_ttl

        result = redis_client.set(key, data, ttl)
        if result:
            logger.info(f"Data saved in cache: {url[:50]}...")
        return result

    def delete(self, url: str) -> bool:
        key = self._make_key(url)
        return redis_client.delete(key)

    def clear(self) -> int:
        pattern = f"{self.prefix}:*"
        return redis_client.clear_all()

news_cache = CacheHandler("news")
weather_cache = CacheHandler("weather")
user_cache = CacheHandler("user")

