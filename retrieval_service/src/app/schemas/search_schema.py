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
    collection: Literal["medical", "testing"] = Field(default="medical", description="Tên collection để tìm kiếm")
    q: str = Field(..., description="Câu truy vấn người dùng (natural language query)")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Bộ lọc metadata")
    k: int = Field(default=10, description="Số lượng kết quả muốn lấy")
    hybrid_weight: float = Field(default=0.5, description="Trọng số giữa lexical và vector search")
    rerank: bool = Field(default=False, description="Có rerank kết quả hay không")
    top_k_rerank: int = Field(default=5, description="Số lượng docs đưa vào rerank")


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

    doc_id: str
    chunk_id: str
    text: str
    score: float
    bm25_score: Optional[float] = None
    vector_sim: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    provenance: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Schema cho response của Search API.

    Attributes:
        query (str): Câu truy vấn gốc mà người dùng gửi.
        results (List[SearchResult]): Danh sách các kết quả tìm kiếm.
        meta (Dict[str, Any]): Metadata bổ sung (ví dụ: thời gian xử lý, tham số search).
    """

    query: str
    results: List[SearchResult]
    meta: Dict[str, Any]
