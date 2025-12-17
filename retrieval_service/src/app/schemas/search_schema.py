# retrieval_service/src/app/schemas/search_schema.py
# -*- coding: utf-8 -*-
"""
Pydantic schemas cho Search API.

Các schema này định nghĩa cấu trúc request/response khi gọi search endpoint.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Schema cho request của Search API.

    Attributes:
        q (str): Câu truy vấn người dùng (natural language query).
        filters (Optional[Dict[str, Any]]): Bộ lọc metadata áp dụng cho kết quả.
        k (int): Số lượng kết quả mong muốn (default = 10).
        hybrid_weight (float): Trọng số kết hợp giữa lexical và vector search (default = 0.5).
        rerank (bool): Có thực hiện rerank kết quả hay không (default = False).
        top_k_rerank (int): Số lượng documents đưa vào rerank (default = 5).
    """
    collection: str = Field(default="lecture", description="Tên collection để tìm kiếm (bất kỳ tên collection hợp lệ)")
    q: str = Field(..., description="Câu truy vấn người dùng (natural language query)", example="Các triệu chứng của bệnh tiểu đường")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Bộ lọc metadata", example={"category": "diabetes", "year": 2023})
    k: int = Field(default=10, description="Số lượng kết quả muốn lấy", example=5)
    hybrid_weight: float = Field(default=0.5, description="Trọng số giữa lexical và vector search", example=0.7)
    rerank: bool = Field(default=False, description="Có rerank kết quả hay không", example=True)
    top_k_rerank: int = Field(default=5, description="Số lượng docs đưa vào rerank", example=3)


class SearchResult(BaseModel):
    """Schema cho một kết quả search.

    Attributes:
        doc_id (str): ID của tài liệu gốc.
        chunk_id (str): ID của chunk trong tài liệu.
        text (str): Nội dung văn bản của chunk.
        score (float): Điểm số tổng hợp (hoặc điểm xếp hạng cuối).
        bm25_score (Optional[float]): Điểm BM25 (nếu có).
        vector_sim (Optional[float]): Độ tương đồng vector (nếu có).
        metadata (Optional[Dict[str, Any]]): Metadata liên quan đến chunk/tài liệu.
        provenance (Optional[Dict[str, Any]]): Thông tin truy vết nguồn gốc.
    """

    doc_id: str = Field(..., description="ID tài liệu gốc", example="doc_001")
    chunk_id: str = Field(..., description="ID chunk", example="chunk_001_1")
    text: str = Field(..., description="Nội dung văn bản", example="Bệnh tiểu đường type 2 thường xuất hiện ở người lớn tuổi...")
    score: float = Field(..., description="Điểm số tổng hợp", example=0.85)
    bm25_score: Optional[float] = Field(None, description="Điểm BM25", example=0.72)
    vector_sim: Optional[float] = Field(None, description="Độ tương đồng vector", example=0.91)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata", example={"category": "programming", "source": "tutorial"})
    provenance: Optional[Dict[str, Any]] = Field(None, description="Thông tin truy vết", example={"page": 15, "paragraph": 3})


class SearchResponse(BaseModel):
    """Schema cho response của Search API.

    Attributes:
        query (str): Câu truy vấn gốc mà người dùng gửi.
        results (List[SearchResult]): Danh sách các kết quả tìm kiếm.
        meta (Dict[str, Any]): Metadata bổ sung (ví dụ: thời gian xử lý, tham số search).
    """

    query: str = Field(..., description="Câu truy vấn gốc", example="Các triệu chứng của bệnh tiểu đường")
    results: List[SearchResult] = Field(..., description="Danh sách kết quả tìm kiếm")
    meta: Dict[str, Any] = Field(..., description="Metadata bổ sung", example={"processing_time": 0.45, "total_results": 5, "collection": "testing"})
