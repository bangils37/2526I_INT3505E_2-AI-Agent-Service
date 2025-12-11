# retrieval_service/src/app/api/v1/document.py
# -*- coding: utf-8 -*-
"""
Module cung cấp các endpoint `/documents`.
Dùng để upload, kiểm tra, và xử lý tài liệu trong hệ thống.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Request, UploadFile, File, HTTPException, Form

from retrieval_service.src.app.log.logging_config import setup_logging
from retrieval_service.src.app.schemas.document_schema import (
    DocumentUploadResponse,
    DocumentIndexResponse,
    DocumentCheckResponse,
)
from retrieval_service.src.app.services.document_service import DocumentService

setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()


# -------------------------------------------------------------------------
# 1️⃣ Upload / Ghi đè tài liệu
# -------------------------------------------------------------------------
@router.put(
    "/documents/{collection}/{document_id}",
    response_model=DocumentUploadResponse,
    summary="Upload hoặc ghi đè tài liệu",
    description="""
    Upload một tài liệu mới hoặc ghi đè tài liệu hiện có vào hệ thống.

    **Cách sử dụng:**
    - Upload file trực tiếp qua multipart/form-data với field `file`.
    - Hoặc cung cấp URL để hệ thống tải tài liệu về qua field `url_download`.

    **Lưu ý:**
    - Phải cung cấp ít nhất một trong hai: `file` hoặc `url_download`.
    - Tài liệu sẽ được lưu trữ tạm thời để chuẩn bị cho bước indexing.
    - Collection phải là `medical` hoặc `testing`.
    """,
)
async def upload_document(
    collection: str,
    document_id: str,
    request: Request,
    file: UploadFile = File(None),
    url_download: str = Form(None),
) -> DocumentUploadResponse:
    """
    Upload hoặc ghi đè tài liệu lên hệ thống.

    Args:
        collection (str): Tên collection trong URL path.
        document_id (str): ID tài liệu cần upload.
        request (Request): Request hiện tại, để truy xuất `app.state`.
        file (UploadFile, optional): File jsonl được upload (multipart/form-data).
        url_download (str, optional): URL để hệ thống tải tài liệu về (application/json).
    """

    document_service: DocumentService = request.app.state.document_service

    if not document_service:
        logger.warning("DocumentService chưa được khởi tạo. Trả về kết quả mock.")
        return DocumentUploadResponse(
            success=False,
            message="DocumentService not initialized.",
            document_id=document_id,
            collection=collection,
        )

    # --- Xác định nguồn dữ liệu ---
    file_bytes = None

    if file:
        logger.info(f"Nhận upload file trực tiếp cho document_id={document_id}.")
        file_bytes = await file.read()
    elif url_download:
        logger.info(f"Tải tài liệu từ URL: {url_download}")
    else:
        raise HTTPException(status_code=400, detail="Phải cung cấp file hoặc url_download.")

    # --- Gọi service thực hiện lưu tài liệu ---
    try:
        success, message = await document_service.upload_document(
            collection=collection,
            document_id=document_id,
            file_bytes=file_bytes,
            url_download=url_download,  # ✅ truyền đúng giá trị người dùng gửi
        )

        return DocumentUploadResponse(
            success=success,
            message=message,
            document_id=document_id,
            collection=collection,
        )
    except Exception as e:
        logger.exception("Lỗi khi upload tài liệu.")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------------
# 2️⃣ Kiểm tra tài liệu đã tồn tại chưa
# -------------------------------------------------------------------------
@router.get(
    "/documents/{collection}/{document_id}",
    response_model=DocumentCheckResponse,
    summary="Kiểm tra tài liệu tồn tại",
    description="""
    Kiểm tra xem một tài liệu có tồn tại trong hệ thống hay không.

    **Trả về:**
    - `exists: true` nếu tài liệu đã được upload và sẵn sàng.
    - `exists: false` nếu tài liệu chưa tồn tại.
    """,
)
async def check_document_exists(
    collection: str, 
    document_id: str, 
    request: Request
) -> DocumentCheckResponse:
    """
    Kiểm tra xem tài liệu đã tồn tại trong hệ thống hay chưa.
    
    Args:
        collection (str): Tên collection trong Qdrant.
        document_id (str): ID tài liệu cần kiểm tra.
        request (Request): Request hiện tại, để truy xuất `app.state`.
        
    Returns:
        DocumentCheckResponse: Kết quả kiểm tra, gồm thông tin tồn tại hay không, document_id và collection.
    """
    document_service: DocumentService = request.app.state.document_service
    exists = await document_service.check_document_exists(collection, document_id)

    if exists:
        return DocumentCheckResponse(
            exists=True,
            document_id=document_id,
            collection=collection
        )
    else:
        return DocumentCheckResponse(
            exists=False,
            document_id="",
            collection=collection
        )


# -------------------------------------------------------------------------
# 3️⃣ Chunking + Indexing
# -------------------------------------------------------------------------
@router.post(
    "/documents/{collection}/{document_id}/index",
    response_model=DocumentIndexResponse,
    summary="Chunking và Indexing tài liệu",
    description="""
    Thực hiện quá trình chunking (chia nhỏ) và indexing tài liệu đã upload vào vector database.

    **Quy trình:**
    1. Parse tài liệu JSONL thành các document và metadata.
    2. Chunking nội dung thành các đoạn nhỏ phù hợp.
    3. Tạo embeddings cho các chunk.
    4. Lưu trữ vào Qdrant và Elasticsearch.

    **Lưu ý:**
    - Tài liệu phải được upload trước khi index.
    - Quá trình có thể mất thời gian tùy thuộc vào kích thước tài liệu.
    - Theo dõi tiến trình qua field `logs` trong response.
    """,
)
async def index_document(
    collection: str, 
    document_id: str, 
    request: Request
) -> DocumentIndexResponse:
    """
    Tiến hành chunking + indexing cho tài liệu đã upload.

    Args:
        collection (str): Tên collection trong Qdrant.
        document_id (str): ID tài liệu cần index.
        request (Request): Request hiện tại, để truy xuất `app.state`.
    
    Returns:
        DocumentIndexResponse: Kết quả của quá trình indexing, gồm thông tin thành công, message và logs chi tiết.
    """
    document_service: DocumentService = request.app.state.document_service
    success, message, log_steps = await document_service.index_document(
        collection=collection,
        document_id=document_id,
    )

    if not success:
        raise HTTPException(status_code=500, detail={"message": message, "logs": log_steps})

    return DocumentIndexResponse(
        success=success,
        message=message,
        document_id=document_id,
        collection=collection,
        logs=log_steps,
    )
