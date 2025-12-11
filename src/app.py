from fastapi import FastAPI
import logging
from src.config.settings import get_settings
from src.routers.query import router as query_router

from src.routers.health import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agent-Service-RAG")

settings = get_settings()

logger.info("Starting Agent-Service-RAG application")

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(query_router, prefix="", tags=["query"])

