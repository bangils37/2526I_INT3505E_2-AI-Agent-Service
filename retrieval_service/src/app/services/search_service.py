# retrieval_service/src/app/services/search_service.py
# -*- coding: utf-8 -*-
"""
Service layer chịu trách nhiệm xử lý logic tìm kiếm.
"""
import logging
import time
from typing import List

from retrieval_service.src.app.schemas.search_schema import SearchRequest, SearchResponse, SearchResult
from retrieval_service.src.app.clients.openai_client import OpenAIEmbeddingClient
from retrieval_service.src.app.clients.qdrant_client import QdrantDB
from retrieval_service.src.app.config import QDRANT_VECTOR_SIZE
from retrieval_service.src.app.log.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class SearchService:
    """Dịch vụ cung cấp logic nghiệp vụ cho việc tìm kiếm tài liệu.

    Service này đóng vai trò trung gian giữa API và các lớp client (OpenAI, Qdrant).
    """

    def __init__(self):
        """Khởi tạo SearchService với OpenAIEmbeddingClient và QdrantDB."""
        self.openai_client = OpenAIEmbeddingClient()
        self.qdrant_client = QdrantDB(vector_size=QDRANT_VECTOR_SIZE)
        self.qdrant_client.collection_name = ""
        logger.info(f"SearchService đã được khởi tạo. Vector size: {QDRANT_VECTOR_SIZE}")

    async def search(self, req: SearchRequest) -> SearchResponse:
        """Thực hiện tìm kiếm dựa trên query của người dùng.

        Quy trình:
            1. Embed câu truy vấn bằng OpenAI.
            2. Thực hiện vector search trên Qdrant.
            3. Định dạng kết quả trả về.

        Args:
            req (SearchRequest): Request object chứa query, filters, k, rerank, v.v.

        Returns:
            SearchResponse: Response chứa danh sách kết quả và metadata.
        """
        start_time = time.time()
        logger.info(f"Nhận request tìm kiếm: query='{req.q}', k={req.k}, rerank={req.rerank}")
        
        self.qdrant_client.collection_name = req.collection

        # --- Bước 1: Embed query ---
        try:
            query_vector = await self.openai_client.embed_query(req.q)
            logger.info(f"Query được embed thành vector độ dài {len(query_vector)}")
        except Exception as e:
            logger.error(f"Lỗi embedding query: {e}")
            return SearchResponse(query=req.q, results=[], meta={"error": str(e)})

        # --- Bước 2: Vector search (with optional filters) ---
        try:
            qdrant_results = self.qdrant_client.search_points(query_vector=query_vector, limit=req.k, filters=req.filters)
            logger.info(f"Tìm thấy {len(qdrant_results)} kết quả từ Qdrant collection '{req.collection}', filters={req.filters}")
        except Exception as e:
            logger.error(f"Lỗi tìm kiếm Qdrant: {e}")
            return SearchResponse(query=req.q, results=[], meta={"error": str(e)})

        # --- Bước 3: Định dạng kết quả ---
        formatted_results: List[SearchResult] = []
        for hit in qdrant_results:
            payload = hit.payload or {}
            provenance = {
                k: v
                for k, v in {
                    "source": payload.get("source"),
                    "url": payload.get("url"),
                    "author": payload.get("author"),
                    "updated_at": payload.get("updated_at"),
                }.items()
                if v is not None
            }

            formatted_results.append(
                SearchResult(
                    doc_id=payload.get("doc_id", "N/A"),
                    chunk_id=payload.get("original_chunk_id", hit.id),
                    text=payload.get("text", ""),
                    score=hit.score,
                    bm25_score=None,
                    vector_sim=hit.score,
                    metadata=payload,
                    provenance=provenance,
                )
            )

        processing_time_ms = int((time.time() - start_time) * 1000)
        return SearchResponse(
            query=req.q,
            results=formatted_results,
            meta={
                "returned_results": len(formatted_results),
                "processing_time_ms": processing_time_ms,
                "collection": req.collection,
                "filters": req.filters,
            },
        )
