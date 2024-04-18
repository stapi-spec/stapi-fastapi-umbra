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


UMBRA_API_BASE_URL = "https://api.canopy.umbra.space"


class Settings(BaseSettings):
    """Settings for Umbra Backend"""

    loglevel: LogLevel = LogLevel.INFO
    database: str = "sqlite://"
    umbra_api_url: str = UMBRA_API_BASE_URL
    feasibility_url: str = f"{UMBRA_API_BASE_URL}/tasking/feasibilities"
    stac_url: str = f"{UMBRA_API_BASE_URL}/archive/search"

    @classmethod
    def load(cls) -> "Settings":
        """Load method to get settings"""
        settings = Settings()
        basicConfig(level=settings.loglevel.value)
        return settings
