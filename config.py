import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class TelegramConfig:
    token: str

    @property
    def is_valid(self):
        return bool(self.token and len(self.token) > 10)

@dataclass
class RedisConfig:
    host: str
    port: int
    db: int
    password: Optional[str] = None

    def connection_string(self):
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://:{self.host}:{self.port}/{self.db}"

@dataclass
class ParserConfig:
    user_agent: str
    timeout: int
    max_retries: int
    cache_ttl: int

class Config:
    """Main configuration class"""

    def __init__(self):
        #Telegram
        self.telegram = TelegramConfig(
            token=os.getenv('BOT_TOKEN', '')
        )

        #Redis
        self.redis = RedisConfig(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD')
        )

        #Parser
        self.parser = ParserConfig(
            user_agent=os.getenv('USER_AGENT', 'Mozilla/5.0'),
            timeout=int(os.getenv('REQUEST_TIMEOUT', 30)),
            max_retries=int(os.getenv('MAX_RETRIES', 3)),
            cache_ttl=int(os.getenv('CACHE_TTL', 3600))
        )

        #Mode
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'

        #Validation
        self._validate()

    def _validate(self):
        """Checking required settings"""

        if not self.telegram.is_valid:
            raise ValueError("BOT-TOKEN is not set or invalid")

    def __repr__(self):
        return f"Config(debug={self.debug})"

config = Config()