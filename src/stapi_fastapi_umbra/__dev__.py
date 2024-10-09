#!/usr/bin/env python3

import logging
from sys import stderr

from fastapi import FastAPI

from stapi_fastapi_umbra.settings import Settings

try:
    from pydantic_settings import BaseSettings
    from uvicorn.main import run
except ImportError:
    print("install uvicorn and pydantic-settings to use the dev server", file=stderr)
    exit(1)

from stapi_fastapi.api import StapiRouter

from stapi_fastapi_umbra import UmbraBackend

logger = logging.getLogger(__name__)


class DevSettings(BaseSettings):
    port: int = 8001
    host: str = "127.0.0.1"


settings = Settings()
logger.info(f"Starting up with canopy url: {settings.canopy_api_url}")
logger.info(
    f"Starting up with canopy token: {settings.canopy_token[:8] if settings.canopy_token else None}"
)

app = FastAPI(debug=True)
app.include_router(StapiRouter(backend=UmbraBackend()).router)


def cli():
    settings = DevSettings()
    run(
        "stapi_fastapi_umbra.__dev__:app",
        reload=True,
        host=settings.host,
        port=settings.port,
    )
