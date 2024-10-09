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


CANOPY_API_BASE_URL = "https://api.canopy.umbra.space"


class Settings(BaseSettings):
    """Settings for Umbra Backend"""

    loglevel: LogLevel = LogLevel.INFO
    database: str = "sqlite://"
    canopy_token: str | None = None
    canopy_api_url: str = CANOPY_API_BASE_URL
    feasibility_timeout: int = 10

    @classmethod
    def load(cls) -> "Settings":
        """Load method to get settings"""
        settings = Settings()
        basicConfig(level=settings.loglevel.value)
        return settings
