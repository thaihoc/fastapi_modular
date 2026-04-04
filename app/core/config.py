from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "FastAPI Module-based Template"
    debug: bool = False
    log_level: str = "INFO"

    auth_jwks: str
    
    db_url: str

    cache_prefix: str = "appcache"
    redis_cache_url: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()

import logging

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(levelname)s --> %(message)s :: (%(name)s:%(filename)s:%(lineno)d) :: (%(asctime)s)',
)