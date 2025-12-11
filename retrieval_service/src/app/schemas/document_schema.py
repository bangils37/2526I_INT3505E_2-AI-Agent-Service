# retrieval_service/src/app/schemas/document_schema.py
# -*- coding: utf-8 -*-
"""
Pydantic schemas cho Document API.

Các schema này định nghĩa cấu trúc request/response khi upload, kiểm tra, và index tài liệu.
"""

from typing import Optional, Dict, Any, Literal, List
from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Schema cho response của endpoint PUT /documents/{collection}/{document_id}."""

    success: bool = Field(..., description="Cờ báo upload có thành công hay không.", example=True)
    message: str = Field(..., description="Thông báo kết quả upload.", example="Document uploaded successfully")
    document_id: str = Field(..., description="ID của tài liệu được upload.", example="doc_001")
    
    collection: Literal["medical", "testing"] = Field(
        default="medical",
        description="Tên collection để lưu tài liệu.",
        example="medical"
    )
    
class DocumentCheckResponse(BaseModel):
    """Schema cho response của endpoint GET /documents/{collection}/{document_id}/check."""

    exists: bool = Field(..., description="Cờ báo tài liệu có tồn tại hay không.", example=True)
    document_id: str = Field(..., description="ID của tài liệu được kiểm tra.", example="doc_001")
    collection: Literal["medical", "testing"] = Field(
        default="medical",
        description="Tên collection để lưu tài liệu.",
        example="medical"
    )

class DocumentIndexResponse(BaseModel):
    """Schema cho response của endpoint POST /documents/{collection}/{document_id}/index."""

    success: bool = Field(..., description="Cờ báo index có thành công hay không.", example=True)
    message: str = Field(..., description="Thông báo kết quả index.", example="Document indexed successfully")
    document_id: str = Field(..., description="ID của tài liệu được index.", example="doc_001")
    collection: Literal["medical", "testing"] = Field(
        default="medical",
        description="Tên collection để lưu tài liệu.",
        example="medical"
    )
    logs: Optional[List[str]] = Field(
        default=None,
        description="Thông tin chi tiết về quá trình index (nếu có).",
        example=["Parsing JSONL file...", "Chunking documents...", "Generating embeddings...", "Indexing to Qdrant and Elasticsearch"]
    )