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

    success: bool = Field(..., description="Cờ báo upload có thành công hay không.")
    message: str = Field(..., description="Thông báo kết quả upload.")
    document_id: str = Field(..., description="ID của tài liệu được upload.")
    
    collection: Literal["medical", "testing"] = Field(
        default="medical",
        description="Tên collection để lưu tài liệu."
    )
    
class DocumentCheckResponse(BaseModel):
    """Schema cho response của endpoint GET /documents/{collection}/{document_id}/check."""

    exists: bool = Field(..., description="Cờ báo tài liệu có tồn tại hay không.")
    document_id: str = Field(..., description="ID của tài liệu được kiểm tra.")
    collection: Literal["medical", "testing"] = Field(
        default="medical",
        description="Tên collection để lưu tài liệu."
    )

class DocumentIndexResponse(BaseModel):
    """Schema cho response của endpoint POST /documents/{collection}/{document_id}/index."""

    success: bool = Field(..., description="Cờ báo index có thành công hay không.")
    message: str = Field(..., description="Thông báo kết quả index.")
    document_id: str = Field(..., description="ID của tài liệu được index.")
    collection: Literal["medical", "testing"] = Field(
        default="medical",
        description="Tên collection để lưu tài liệu."
    )
    logs: Optional[List[str]] = Field(
        default=None,
        description="Thông tin chi tiết về quá trình index (nếu có)."
    )