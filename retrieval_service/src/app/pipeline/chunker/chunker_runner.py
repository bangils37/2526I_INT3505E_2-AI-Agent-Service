# retrieval_service/src/app/pipeline/chunker/chunker_runner.py
# -*- coding: utf-8 -*-
"""
Module để chạy chunking tài liệu markdown thành các đoạn nhỏ hơn (chunks)
dựa trên cấu trúc heading.
Sử dụng HeadingChunker để thực hiện chunking.
"""

import argparse
import json
import logging
import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from retrieval_service.src.app.schemas.corpus_schema import Chunk
from retrieval_service.src.app.pipeline.chunker.corpus import parse_markdown_to_corpus
from retrieval_service.src.app.pipeline.chunker.heading_chunker import HeadingChunker
from retrieval_service.src.app.log.logging_config import setup_logging
from retrieval_service.src.app.config import (
    CHUNK_SIZE,
    MAX_HEADING_LEVELS,
    MAX_ROW_WORDS,
    DOCUMENTS_DIR,
    CHUNKS_DIR,
)

# ------------------------------
# Khởi tạo logging
# ------------------------------
setup_logging()
logger = logging.getLogger(__name__)


def _read_document_file(document_dir: str, doc_id: str) -> str:
    """Đọc file markdown document_dir/doc/<doc_id>.md.

    Args:
        document_dir (str): Thư mục chứa tài liệu.
        doc_id (str): ID tài liệu.

    Returns:
        str: Nội dung file markdown.

    Raises:
        FileNotFoundError: Nếu file không tồn tại.
        Exception: Các lỗi IO khác.
    """
    doc_path = os.path.normpath(os.path.join(document_dir, "doc", f"{doc_id}.md"))
    logger.debug("Đọc file markdown tại: %s", os.path.abspath(doc_path))
    with open(doc_path, "r", encoding="utf-8") as fh:
        return fh.read()


def chunking(
    document_dir: str,
    chunk_dir: str,
    doc_id: str,
    L: int = CHUNK_SIZE,
    max_row_words: int = MAX_ROW_WORDS,
) -> bool:
    """Chunking một document markdown và lưu ra chunks + metadata.

    Args:
        document_dir (str): Thư mục chứa document gốc.
        chunk_dir (str): Thư mục lưu chunks.
        doc_id (str): ID tài liệu.
        L (int, optional): Kích thước chunk (tokens). Defaults to CHUNK_SIZE.
        max_row_words (int, optional): Số từ tối đa mỗi dòng. Defaults to MAX_ROW_WORDS.

    Returns:
        bool: True nếu thành công, False nếu có lỗi.
    """
    # ------------------------------
    # Chuẩn bị thư mục output
    # ------------------------------
    doc_out_dir = os.path.normpath(os.path.join(chunk_dir, "doc"))
    meta_out_dir = os.path.normpath(os.path.join(chunk_dir, "metadata"))
    os.makedirs(doc_out_dir, exist_ok=True)
    os.makedirs(meta_out_dir, exist_ok=True)

    # ------------------------------
    # Helper: tạo metadata cho 1 chunk
    # ------------------------------
    def metadata_for_chunk(chunk: Chunk, chunk_idx: int) -> Dict:
        metadata_filepath = os.path.normpath(os.path.join(document_dir, "metadata", f"{doc_id}.json"))
        doc_metadata = {}
        try:
            with open(metadata_filepath, "r", encoding="utf-8") as mf:
                doc_metadata = json.load(mf)
                logger.info("Tải metadata document từ: %s", os.path.abspath(metadata_filepath))
        except FileNotFoundError:
            logger.debug("Không tìm thấy metadata document: %s", os.path.abspath(metadata_filepath))
        except Exception as e:
            logger.warning("Lỗi đọc metadata document %s: %s", metadata_filepath, e)

        meta = dict(doc_metadata) if isinstance(doc_metadata, dict) else {}
        chunk_id = f"{doc_id}_chunk{chunk_idx+1:03d}"
        meta.update({
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "chunk_index": chunk_idx,
            "token_count": len(chunk.text.split()),
            "section_title": getattr(chunk, "main_heading", "") or "",
            "extracted_at": datetime.now().isoformat(),
            "embedding_model": "",
            "hash": hashlib.sha256(chunk.text.encode("utf-8")).hexdigest(),
        })
        return meta

    # ------------------------------
    # Helper: lưu chunk + metadata
    # ------------------------------
    def save_chunk_and_meta(chunk: Chunk, chunk_idx: int) -> None:
        chunk_filename = f"{doc_id}_chunk{chunk_idx+1:03d}.md"
        chunk_filepath = os.path.normpath(os.path.join(doc_out_dir, chunk_filename))
        with open(chunk_filepath, "w", encoding="utf-8") as cf:
            cf.write(chunk.text)
        logger.info("Saved chunk %d -> %s", chunk_idx+1, os.path.abspath(chunk_filepath))

        meta = metadata_for_chunk(chunk, chunk_idx)
        meta_filename = f"{doc_id}_chunk{chunk_idx+1:03d}.json"
        meta_filepath = os.path.normpath(os.path.join(meta_out_dir, meta_filename))
        with open(meta_filepath, "w", encoding="utf-8") as mf:
            json.dump(meta, mf, ensure_ascii=False, indent=2)
        logger.info("Saved chunk metadata %d -> %s", chunk_idx+1, os.path.abspath(meta_filepath))

    # ------------------------------
    # Thực thi chunking
    # ------------------------------
    try:
        md_text = _read_document_file(document_dir, doc_id)
    except Exception as e:
        logger.error("Không thể đọc file document %s: %s", doc_id, e)
        return False

    corpus = parse_markdown_to_corpus(md_text, max_row_words=max_row_words)
    chunker = HeadingChunker(corpus, L=L, max_heading_levels=MAX_HEADING_LEVELS)
    chunks = chunker.run()

    logger.info("Document %s -> %d chunks", doc_id, len(chunks))

    for i, chunk in enumerate(chunks):
        try:
            save_chunk_and_meta(chunk, i)
        except Exception as e:
            logger.error("Lỗi lưu chunk %s idx=%d: %s", doc_id, i, e)
            return False

    return True


def chunking_all_document(
    collection: str,
    document_id: str,
    L: int = CHUNK_SIZE,
    max_row_words: int = MAX_ROW_WORDS,
) -> list[str]:
    """
    Thực hiện chunking cho tất cả file Markdown trong:
        <DOCUMENTS_DIR>/<collection>/cleaned/<document_id>/doc/*.md

    Kết quả chunk được lưu tại:
        <CHUNKS_DIR>/<collection>/(doc|metadata)/...

    Args:
        collection (str): Tên collection, ví dụ "medical".
        document_id (str): Tên thư mục con bên trong "cleaned" (ví dụ "gg" hoặc "batch_2025_10_10").
        L (int, optional): Kích thước mỗi chunk (theo token). Mặc định = CHUNK_SIZE.
        max_row_words (int, optional): Số từ tối đa trên mỗi dòng khi parse markdown. Mặc định = MAX_ROW_WORDS.
    """
    chunking_logs = ["--- CHUNKING PHASE ---"]
    
    logger.info(f"🔹 Bắt đầu chunking cho collection='{collection}', document_id='{document_id}'")
    chunking_logs.append(f"🔹 Bắt đầu chunking cho collection='{collection}', document_id='{document_id}'")

    # ------------------------------
    # 1️⃣ Xác định đường dẫn thư mục
    # ------------------------------
    documents_root = Path(DOCUMENTS_DIR) / collection / "cleaned" / document_id
    src_doc_dir = documents_root / "doc"
    chunk_output_root = Path(CHUNKS_DIR) / collection / document_id

    logger.info(f"📂 Nguồn: {documents_root}")
    logger.info(f"📦 Đích:  {chunk_output_root}")

    if not src_doc_dir.is_dir():
        logger.error(f"❌ Không tìm thấy thư mục nguồn: {src_doc_dir}")
        return

    # Đảm bảo thư mục output tồn tại
    (chunk_output_root / "doc").mkdir(parents=True, exist_ok=True)
    (chunk_output_root / "metadata").mkdir(parents=True, exist_ok=True)

    # ------------------------------
    # 2️⃣ Lặp qua từng file Markdown
    # ------------------------------
    md_files = sorted(src_doc_dir.glob("*.md"))
    if not md_files:
        logger.warning(f"⚠️ Không có file .md nào trong {src_doc_dir}")
        return

    success_count = 0
    failure_count = 0

    for md_path in md_files:
        doc_id = md_path.stem
        logger.info(f"➡️  Chunking file: {md_path.name}")

        try:
            success = chunking(
                document_dir=str(documents_root),
                chunk_dir=str(chunk_output_root),
                doc_id=doc_id,
                L=L,
                max_row_words=max_row_words,
            )
            if success:
                logger.info(f"✅ Chunking thành công: {doc_id}")
                success_count += 1
            else:
                logger.error(f"❌ Chunking thất bại: {doc_id}")
                failure_count += 1
        except Exception as exc:
            logger.exception(f"💥 Lỗi không xử lý được khi chunking {doc_id}: {exc}")
            failure_count += 1

    # ------------------------------
    # 3️⃣ Tổng kết kết quả
    # ------------------------------
    total = len(md_files)
    logger.info(
        f"🏁 Chunking hoàn tất: tổng {total} file | thành công {success_count} | thất bại {failure_count}"
    )
    chunking_logs.append(
        f"🏁 Chunking hoàn tất: tổng {total} file | thành công {success_count} | thất bại {failure_count}"
    )
    
    return chunking_logs


# Testing as a script
def main() -> None:
    """Entry point khi chạy trực tiếp."""
    chunking_all_document(collection="medical", document_id="small_vinmec_data_prepared")


if __name__ == "__main__":
    main()
