# retrieval_service/src/app/config.py
# -*- coding: utf-8 -*-
"""
Module cấu hình cho retrieval_service.

- Load biến môi trường từ file `.env` (tại thư mục backend).
- Định nghĩa class `Settings` để truy cập cấu hình ứng dụng.
- Cung cấp các biến toàn cục cho clients và services khác.
"""

import os
import logging
from dotenv import load_dotenv

from typing import List
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings

from retrieval_service.src.app.log.logging_config import setup_logging

# Load biến môi trường
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

setup_logging()
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Lớp quản lý cấu hình ứng dụng.

    Attributes:
        APP_NAME (str): Tên ứng dụng.
        VERSION (str): Phiên bản ứng dụng.
        HOST (str): Host để bind khi chạy app.
        PORT (int): Port để bind khi chạy app.
        ALLOWED_ORIGINS (List[str]): Danh sách origin cho CORS.
    """

    APP_NAME: str = Field("retrieval_service", description="Tên ứng dụng")
    VERSION: str = Field("0.1.0", description="Phiên bản ứng dụng")
    HOST: str = Field("0.0.0.0", description="Host để bind khi chạy app")
    PORT: int = Field(8000, description="Port để bind khi chạy app")
    ALLOWED_ORIGINS: List[str] = Field(
        default_factory=lambda: ["*"],
        description="Danh sách origin cho CORS",
    )


__settings = Settings()


def get_settings() -> Settings:
    """Lấy instance Settings đã khởi tạo.

    Returns:
        Settings: Đối tượng cấu hình ứng dụng.
    """
    return __settings


# Đường dẫn dữ liệu
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", "retrieval_service/data/documents")
CHUNKS_DIR = os.getenv("CHUNKS_DIR", "retrieval_service/data/chunks")

# Cấu hình chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 400))
MAX_HEADING_LEVELS = int(os.getenv("MAX_HEADING_LEVELS", 10))
MAX_ROW_WORDS = int(os.getenv("MAX_ROW_WORDS", 20))
CHUNKING_SCOPE = os.getenv("CHUNKING_SCOPE", "testing")

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT",
    "https://digit-maccatc4-eastus.cognitiveservices.azure.com/",
)
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

# Azure Embedding
ENDPOINT_TEXT3_EMBEDDING = os.getenv("ENDPOINT_TEXT3_EMBEDDING", "")
API_KEY_TEXT3_EMBEDDING = os.getenv("API_KEY_TEXT3_EMBEDDING", "")

# Redis
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
SOCKET_TIMEOUT = float(os.environ.get("SOCKET_TIMEOUT", 5.0))

# Redis Cache Keys
SESSION_REDIS_KEY = os.environ.get("SESSION_REDIS_KEY", "app:sessions")
CHAT_HISTORY_REDIS_KEY = os.environ.get("CHAT_HISTORY_REDIS_KEY", "app:chat_history")
NOTES_REDIS_KEY = os.environ.get("NOTES_REDIS_KEY", "app:notes")

# Elasticsearch
ELASTIC_URL = os.getenv("ELASTIC_URL", "http://localhost:9200")
ELASTIC_USER = os.getenv("ELASTIC_USER", "")
ELASTIC_PASS = os.getenv("ELASTIC_PASS", "")

# Qdrant
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_VECTOR_SIZE = int(os.getenv("QDRANT_VECTOR_SIZE", 1536))
QDRANT_BATCH_SIZE = int(os.getenv("QDRANT_BATCH_SIZE", 64))
