"""Settings for Umbra Backend"""

from enum import Enum
from logging import basicConfig

from pydantic_settings import BaseSettings


class LogLevel(Enum):
    """Log Level Enum"""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"


CANOPY_URL = "https://canopy.umbra.space"
CANOPY_API_URL = "https://api.canopy.umbra.space"
CANOPY_API_SANDBOX_URL = "https://api.canopy.prod.umbra-sandbox.space"


class Settings(BaseSettings):
    """Settings for Umbra Backend"""

    fastapi_host: str = "localhost"
    fastapi_port: int = 8001
    loglevel: LogLevel = LogLevel.INFO
    database: str = "sqlite://"
    canopy_token: str | None = None
    canopy_api_url: str = CANOPY_API_SANDBOX_URL
    canopy_url: str = CANOPY_URL
    feasibility_timeout: int = 10

    @property
    def fastapi_url(self):
        if self.fastapi_port == 80 or self.fastapi_port == 443:
            return self.fastapi_host
        return f"{self.fastapi_host}:{self.fastapi_port}"

    @classmethod
    def load(cls) -> "Settings":
        """Load method to get settings"""
        settings = Settings()
        basicConfig(level=settings.loglevel.value)
        return settings
