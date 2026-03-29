from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI Template"
    debug: bool = False
    
    db_url: str
    redis_url: str

    class Config:
        env_file = ".env"

settings = Settings()