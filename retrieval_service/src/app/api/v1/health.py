# retrieval_service/src/app/api/v1/health.py
# -*- coding: utf-8 -*-
"""
Module cung cấp endpoint health check cho service.
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
import logging

from retrieval_service.src.app.log.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Schema phản hồi của endpoint health check.

    Attributes:
        status (str): Trạng thái tổng thể của service.
        elastic (str): Trạng thái kết nối đến Elasticsearch. Giá trị có thể là
            `"ok"`, `"down"`, `"error"`, hoặc `"unknown"`.
        qdrant (str): Trạng thái kết nối đến Qdrant client. Giá trị có thể là
            `"ok"`, `"down"`, `"error"`, hoặc `"unknown"`.
        openai (str): Trạng thái kết nối đến OpenAI client. Giá trị có thể là
            `"ok"`, `"down"`, `"error"`, hoặc `"unknown"`.
    """

    status: str
    elastic: str = "unknown"
    openai: str = "unknown"
    qdrant: str = "unknown"


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    """Kiểm tra sức khoẻ của service.

    Thực hiện kiểm tra trạng thái của các thành phần phụ trợ như
    Elasticsearch, Qdrant và OpenAI client (nếu có gắn trong app state).

    Args:
        request (Request): Request hiện tại, dùng để truy xuất `app.state`.

    Returns:
        HealthResponse: Thông tin tổng quan về tình trạng service.
    """
    elastic_status = "unknown"
    openai_status = "unknown"
    qdrant_status = "unknown"

    # Kiểm tra trạng thái Elasticsearch client
    es_client = getattr(request.app.state, "elastic_client", None)
    if es_client:
        try:
            result = es_client.ping() if callable(getattr(es_client, "ping", None)) else None
            if hasattr(result, "__await__"):
                result = await result
            elastic_status = "ok" if result else "down"
        except Exception:
            elastic_status = "error"

    # Kiểm tra trạng thái OpenAI client
    openai_client = getattr(request.app.state, "openai_client", None)
    if openai_client:
        try:
            if hasattr(openai_client, "is_ready"):
                openai_status = "ok" if openai_client.is_ready() else "down"
            else:
                openai_status = "ok"
        except Exception:
            openai_status = "error"
            
    # Kiểm tra trạng thái Qdrant client
    qdrant_client = getattr(request.app.state, "qdrant_client", None)
    if qdrant_client:
        try:
            if hasattr(qdrant_client, "is_ready"):
                qdrant_status = "ok" if qdrant_client.is_ready() else "down"
            else:
                qdrant_status = "ok"
        except Exception:
            qdrant_status = "error"

    return HealthResponse(status="ok", elastic=elastic_status, openai=openai_status, qdrant=qdrant_status)
