from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from src.config.settings import get_settings
from src.routers.query import router as query_router
from dotenv import load_dotenv
import os
load_dotenv() 
from src.routers.health import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agent-Service-RAG")

# CORS middleware - configure from environment
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = get_settings()

logger.info("Starting Agent-Service-RAG application")

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(query_router, prefix="", tags=["query"])

