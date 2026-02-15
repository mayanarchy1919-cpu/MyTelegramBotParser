import redis
import json
import logging
from typing import Any,Optional
from config import config

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.name = None
        self.connect()

    def connect(self):
        try:
            self.client = redis.Redis(
                host=config.redis.host,
                port=config.redis.port,
                db=config.redis.db,
                password=config.redis.password,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=5
            )

            self.client.ping()
            logger.info(f"Redis connected: {config.redis.host}:{config.redis.port}")
        except redis.ConnectionError as e:
            logger.error(f"Error connecting to Redis: {e}")
            self.client = None
        except Exception as e:
            logger.error(f"Unknown error: {e}")
            self.client = None

    def is_connected(self) -> bool:
        if not self.client:
            return False

        try:
            return self.client.ping()
        except:
            return False

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        if not self.is_connected():
            return False

        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)

            if ttl:
                return self.client.setex(key,ttl, value)
            else:
                return self.client.set(key, value)

        except Exception as e:
            logger.error(f"Saving error {key}: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        if not self.is_connected():
            return None

        try:
            value = self.client.get(key)
            if value and value.startswith(('{','[')):
                try:
                    return json.loads(value)
                except:
                    pass
            return value
        except Exception as e:
            logger.error(f"Error receiving {key}: {e}")
            return None

    def delete(self, *keys: str) -> bool:
        if not self.is_connected():
            return False
        try:
            return bool(self.client.delete(*keys))
        except Exception as e:
            logger.error(f"Error removal {e}")
            return False

    def exists(self, key: str) -> bool:
        if not self.is_connected():
            return False
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Error checking {e}")
            return False

    def clear_all(self, pattern: str = "*") -> int:
        if not self.is_connected():
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clear: {e}")
            return 0

redis_client = RedisClient()

