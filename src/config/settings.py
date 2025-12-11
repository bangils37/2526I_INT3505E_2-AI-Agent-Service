from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

logger.info("Loading environment variables from .env")


class Settings(BaseSettings):
    RETRIEVAL_SERVICE_URL: str = Field(default="http://localhost:8010")
    LMS_BACKEND_URL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = Field(default="gemma-3-27b-it")
    DEFAULT_TOP_K: int = Field(default=5)

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
