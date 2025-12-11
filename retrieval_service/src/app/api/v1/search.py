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


@router.post("/search/{collection}", response_model=SearchResponse, summary="Tìm kiếm trong collection", description="""
Thực hiện tìm kiếm thông tin trong một collection cụ thể sử dụng hybrid search.

**Thuật toán tìm kiếm:**
- **Lexical Search**: Sử dụng BM25 trên Elasticsearch.
- **Vector Search**: Sử dụng cosine similarity trên Qdrant.
- **Hybrid**: Kết hợp cả hai với trọng số có thể điều chỉnh.

**Tính năng nâng cao:**
- **Filters**: Lọc kết quả theo metadata.
- **Reranking**: Sắp xếp lại kết quả top-k bằng cross-encoder.
- **Pagination**: Điều chỉnh số lượng kết quả trả về.

**Ví dụ query:**
- "Cách viết unit test hiệu quả"
- "Giải thích khái niệm OOP"
""")
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
