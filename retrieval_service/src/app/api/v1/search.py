# retrieval_service/src/app/api/v1/search.py
# -*- coding: utf-8 -*-
"""
Module cung cấp endpoint `/search`.
"""

import logging
from fastapi import APIRouter, Request

from retrieval_service.src.app.log.logging_config import setup_logging
from retrieval_service.src.app.services.search_service import SearchService
from retrieval_service.src.app.schemas.search_schema import SearchRequest, SearchResponse

setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/search/{collection}", response_model=SearchResponse)
async def search_in_collection(collection: str, req: SearchRequest, request: Request) -> SearchResponse:
    """
    Thực hiện tìm kiếm trong 1 collection cụ thể.

    Args:
        collection (str): Tên collection trong URL path.
        req (SearchRequest): Request body chứa query và tham số tìm kiếm.
        request (Request): Request hiện tại.
    """
    search_service: SearchService = request.app.state.search_service

    if search_service:
        # Gán collection vào req để tái sử dụng logic cũ
        req.collection = collection
        return await search_service.search(req)

    logger.warning("SearchService chưa được khởi tạo. Trả về kết quả mock.")
    return SearchResponse(
        query=req.q,
        results=[],
        meta={
            "warning": "SearchService not initialized.",
            "collection": collection
        },
    )
