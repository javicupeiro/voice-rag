from pydantic_settings import BaseSettings
import sys
import logging

class Settings(BaseSettings):
    """
    Manages application settings.
    It automatically reads from environment variables.
    """
    SQLITE_DB_PATH: str = "data/chunks.db"
    CHROMA_DB_PATH: str = "data/chroma_db"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()

# Centralized Logging Configuration 
logging.basicConfig(
    level=settings.LOG_LEVEL.upper(),
    stream=sys.stdout,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)