# retrieval_service/src/app/services/document_service.py
# -*- coding: utf-8 -*-
"""
Service layer chịu trách nhiệm xử lý upload, kiểm tra, và indexing tài liệu.
"""

import logging
import aiohttp
import os
import time
from typing import Optional, Tuple

from retrieval_service.src.app.pipeline.indexing import get_indexing_pipeline
from retrieval_service.src.app.pipeline.chunker.chunker_runner import chunking_all_document
from retrieval_service.src.app.pipeline.jsonl_converting.convert_jsonl_to_docs_and_metadata import convert_jsonl_to_docs_and_metadata
from retrieval_service.src.app.clients.openai_client import OpenAIEmbeddingClient
from retrieval_service.src.app.clients.qdrant_client import QdrantDB
from retrieval_service.src.app.config import QDRANT_VECTOR_SIZE, DOCUMENTS_DIR
from retrieval_service.src.app.log.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class DocumentService:
    """Dịch vụ quản lý vòng đời tài liệu (upload, check, chunking, indexing)."""

    def __init__(self):
        """Khởi tạo DocumentService với OpenAIEmbeddingClient và QdrantDB."""
        self.openai_client = OpenAIEmbeddingClient()
        self.qdrant_client = QdrantDB(vector_size=QDRANT_VECTOR_SIZE)
        logger.info("DocumentService đã được khởi tạo.")

    # -------------------------------------------------------------------------
    # 1️⃣ Upload / Ghi đè tài liệu
    # -------------------------------------------------------------------------
    async def upload_document(
        self,
        collection: str,
        document_id: str,
        file_bytes: Optional[bytes] = None,
        url_download: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Upload hoặc ghi đè tài liệu.

        Args:
            collection (str): Tên collection lưu trữ.
            document_id (str): ID tài liệu.
            file_bytes (bytes, optional): Nội dung file (nếu upload trực tiếp).
            url_download (str, optional): URL để tải tài liệu về.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        start = time.time()
        try:
            os.makedirs(f"{DOCUMENTS_DIR}/{collection}/raw", exist_ok=True)
            file_path = f"{DOCUMENTS_DIR}/{collection}/raw/{document_id}.jsonl"

            # --- Trường hợp 1: Upload file trực tiếp ---
            if file_bytes:
                with open(file_path, "wb") as f:
                    f.write(file_bytes)
                logger.info(f"Đã lưu file {file_path} ({len(file_bytes)} bytes)")
                return True, f"Document '{document_id}' uploaded successfully."

            # --- Trường hợp 2: Tải file từ URL ---
            elif url_download:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url_download) as resp:
                        if resp.status != 200:
                            msg = f"Không thể tải file từ URL (HTTP {resp.status})"
                            logger.error(msg)
                            return False, msg
                        content = await resp.read()
                        with open(file_path, "wb") as f:
                            f.write(content)
                        logger.info(f"Đã tải {len(content)} bytes từ {url_download}")
                        return True, f"Document '{document_id}' downloaded successfully."

            else:
                logger.warning("Không có file_bytes hoặc url_download được cung cấp.")
                return False, "Phải cung cấp file hoặc URL."

        except Exception as e:
            logger.exception(f"Lỗi khi upload tài liệu {document_id}: {e}")
            return False, str(e)
        finally:
            elapsed = int((time.time() - start) * 1000)
            logger.info(f"Upload xử lý xong sau {elapsed} ms.")

    # -------------------------------------------------------------------------
    # 2️⃣ Kiểm tra tài liệu đã tồn tại chưa
    # -------------------------------------------------------------------------
    async def check_document_exists(self, collection: str, document_id: str) -> bool:
        """
        Kiểm tra tài liệu đã tồn tại trong hệ thống chưa.

        Args:
            collection (str): Tên collection.
            document_id (str): ID tài liệu.

        Returns:
            bool: True nếu tồn tại, False nếu không.
        """
        file_path = f"{DOCUMENTS_DIR}/{collection}/raw/{document_id}.jsonl"
        exists = os.path.exists(file_path)
        logger.info(f"Kiểm tra tồn tại: {file_path} -> {exists}")
        return exists

    # -------------------------------------------------------------------------
    # 3️⃣ Chunking + Indexing
    # -------------------------------------------------------------------------
    async def index_document(
        self,
        collection: str,
        document_id: str,
    ) -> Tuple[bool, str, list]:
        """
        Tiến hành chunking + indexing tài liệu lên Qdrant.
        """
        success = False
        message = ""
        logs = []
        try: 
            convert_logs = convert_jsonl_to_docs_and_metadata(document_id=document_id, collection=collection)  # Chuyển đổi JSONL thành Markdown + Metadata
            chunking_logs = chunking_all_document(document_id=document_id, collection=collection)               # Chunking tài liệu
            index_logs = await get_indexing_pipeline().run(document_id=document_id, collection=collection)         # Indexing tài liệu lên Qdrant
            
            logs.extend(convert_logs)
            logs.extend(chunking_logs)
            logs.extend(index_logs)
            
            success = True
            message = f"Document '{document_id}' indexed successfully."
            
            return success, message, logs
        except Exception as e:
            logger.exception(f"Lỗi khi indexing tài liệu {document_id}: {e}")
            success = False
            message = f"Lỗi: {e}"
            return success, message, logs
        

