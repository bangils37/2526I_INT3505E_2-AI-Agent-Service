# retrieval_service/src/app/pipeline/chunker/heading_chunker.py
# -*- coding: utf-8 -*-
"""
Module để chạy chunking tài liệu markdown thành các đoạn nhỏ hơn (chunks)
dựa trên cấu trúc heading.
"""

import argparse
import logging
import os
import json
import hashlib
from datetime import datetime
from typing import List, Optional, Dict

from retrieval_service.src.app.schemas.corpus_schema import Row, Corpus, Chunk
from retrieval_service.src.app.pipeline.chunker.corpus import parse_markdown_to_corpus
from retrieval_service.src.app.log.logging_config import setup_logging
from retrieval_service.src.app.config import CHUNK_SIZE, MAX_HEADING_LEVELS, MAX_ROW_WORDS, CHUNKING_SCOPE, DOCUMENTS_DIR, CHUNKS_DIR

# ---------- Logging ----------
setup_logging()
logger = logging.getLogger(__name__)


# ---------- Triển khai HeadingChunker ----------
class HeadingChunker:
    """Chunker chia tài liệu Markdown thành các đoạn (chunk) dựa trên Heading.

    Thuật toán:
        - Giữ buffer A (main_text) cho heading chính.
        - Giữ buffer B (outside_text) cho văn bản của heading khác.
        - Khi tổng token vượt quá L thì phát sinh chunk mới (emit_chunk).

    Attributes:
        corpus (Corpus): Tài liệu đã parse từ markdown.
        L (int): Ngưỡng tối đa số token trong mỗi chunk.
        max_levels (int): Số cấp heading tối đa.
        current_tokens (int): Tổng số token hiện tại trong buffer.
        A (str): Buffer văn bản của heading chính.
        B (str): Buffer văn bản ngoài heading chính.
        current_headings (List[int]): Stack heading theo level hiện tại.
        above_headings (List[int]): Danh sách các heading cha.
        chunks (List[Chunk]): Danh sách chunk đã tạo.
        main_heading (Optional[int]): Chỉ số heading chính hiện tại.
    """

    def __init__(self, corpus: Corpus, L: int = CHUNK_SIZE, max_heading_levels: int = MAX_HEADING_LEVELS):
        """Khởi tạo HeadingChunker.

        Args:
            corpus (Corpus): Đối tượng Corpus đã parse từ markdown.
            L (int, optional): Ngưỡng số token tối đa trong một chunk. Defaults to CHUNK_SIZE.
            max_heading_levels (int, optional): Số cấp heading tối đa. Defaults to MAX_HEADING_LEVELS.
        """
        self.corpus = corpus
        self.L = L
        self.max_levels = max_heading_levels

        self.current_tokens = 0
        self.A = ""
        self.B = ""

        self.current_headings = [-1] * self.max_levels
        self.above_headings: List[int] = []
        self.chunks: List[Chunk] = []

        self.main_heading: Optional[int] = None
        if self.corpus.rows:
            self.main_heading = self.corpus.rows[0].heading

    def add_heading(self, row: Row):
        """Cập nhật stack heading khi gặp một heading mới.

        Args:
            row (Row): Row là heading.
        """
        if 0 <= row.heading_type < self.max_levels:
            self.current_headings[row.heading_type] = row.heading
            for i in range(row.heading_type + 1, self.max_levels):
                self.current_headings[i] = -1
        self.above_headings.append(row.heading)

        logger.debug("Thêm heading idx=%d, type=%d", row.heading, row.heading_type)

    def add_text_to_A(self, row: Row):
        """Thêm văn bản vào buffer A (main_text).

        Args:
            row (Row): Row thuộc heading chính.
        """
        self.A = f"{self.A} {row.text}".strip()
        self.current_tokens += row.size()
        logger.debug("Thêm vào A: '%s' (tổng tokens=%d)", row.text, self.current_tokens)

    def add_text_to_B(self, row: Row):
        """Thêm văn bản vào buffer B (outside_text).

        Args:
            row (Row): Row thuộc heading khác heading chính.
        """
        self.B = f"{self.B} {row.text}".strip()
        self.current_tokens += row.size()
        logger.debug("Thêm vào B: '%s' (tổng tokens=%d)", row.text, self.current_tokens)

    def _make_headings_str(self) -> str:
        """Ghép các heading đang active thành chuỗi.

        Returns:
            str: Chuỗi headings cách nhau bằng newline.
        """
        parts = []
        for h_idx in self.above_headings:
            if 0 <= h_idx < len(self.corpus.headings):
                parts.append(self.corpus.headings[h_idx])
        return ("\n".join(parts) + "\n") if parts else ""

    def emit_chunk(self):
        """Tạo và lưu một chunk từ buffer hiện tại."""
        res = Chunk()
        res.main_heading = self.corpus.headings[self.main_heading]
        res.headings = self._make_headings_str()
        res.main_text = self.A
        res.outside_text = self.B
        res.text = res.headings + (res.main_text or "") + (
            "\n" + (res.outside_text or "") if res.outside_text else ""
        )
        self.chunks.append(res)

        logger.info("Tạo chunk mới: tokens=%d, headings=%s", self.current_tokens, res.headings.strip())

    def _rebuild_above_headings(self):
        """Xây dựng lại danh sách above_headings từ stack hiện tại."""
        self.above_headings = [h for h in self.current_headings if h != -1]

    def reset(self, idx: int, row: Row) -> int:
        """Reset lại buffer và (nếu cần) thay đổi main_heading.

        Args:
            idx (int): Chỉ số row hiện tại.
            row (Row): Row hiện tại.

        Returns:
            int: Chỉ số row để tiếp tục xử lý.
        """
        logger.debug("Reset chunk tại row idx=%d", idx)

        self.A = ""
        self.B = ""
        self.current_tokens = 0

        if row.heading == self.main_heading:
            return idx

        self.main_heading = self.corpus.rows[idx].heading

        while idx > 0 and self.corpus.rows[idx - 1].heading == self.corpus.rows[idx].heading:
            idx -= 1

        new_level = self.corpus.rows[idx].heading_type
        for i in range(new_level, self.max_levels):
            self.current_headings[i] = -1

        self._rebuild_above_headings()
        return idx

    def run(self) -> List[Chunk]:
        """Chạy chunker và trả về danh sách chunk.

        Returns:
            List[Chunk]: Danh sách các chunk được tạo.
        """
        logger.info("Bắt đầu chạy HeadingChunker với %d rows", len(self.corpus.rows))

        i = 0
        rows = self.corpus.rows
        N = len(rows)

        while i < N:
            row = rows[i]

            if self.current_tokens >= self.L:
                logger.debug("Buffer vượt quá L=%d tokens, emit chunk", self.L)
                self.emit_chunk()
                i = self.reset(i, row)
                continue

            if row.is_heading:
                self.add_heading(row)

            if row.heading == self.main_heading:
                self.add_text_to_A(row)
            else:
                self.add_text_to_B(row)

            if i == N - 1:
                self.emit_chunk()

            i += 1

        logger.info("Hoàn tất, tổng số chunk=%d", len(self.chunks))
        return self.chunks


def chunking(document_dir: str, chunk_dir: str, doc_id: str,
             L: int = CHUNK_SIZE, max_row_words: int = MAX_ROW_WORDS) -> bool:
    """Chunking một document và lưu các chunk vào file.

    Args:
        document_dir (str): Thư mục chứa document gốc.
        chunk_dir (str): Thư mục lưu kết quả chunk.
        doc_id (str): ID tài liệu (không có phần mở rộng).
        L (int, optional): Ngưỡng số token tối đa mỗi chunk. Defaults to CHUNK_SIZE.
        max_row_words (int, optional): Số từ tối đa mỗi row. Defaults to MAX_ROW_WORDS.

    Returns:
        bool: True nếu thành công, False nếu lỗi.
    """

    def metadata_for_chunk(chunk: Chunk, chunk_idx: int) -> dict:
        """Sinh metadata cho một chunk.

        Args:
            chunk (Chunk): Chunk dữ liệu.
            chunk_idx (int): Chỉ số chunk.

        Returns:
            dict: Metadata của chunk.
        """
        metadata_filepath = os.path.normpath(os.path.join(document_dir, "metadata", f"{doc_id}.json"))

        try:
            with open(metadata_filepath, "r", encoding="utf-8") as mf:
                doc_metadata = json.load(mf)
                logger.info("Đã tải metadata từ: %s", os.path.abspath(metadata_filepath))
        except Exception as e:
            logger.error("Lỗi khi đọc metadata: %s", e)
            doc_metadata = {}

        meta = doc_metadata.copy()
        chunk_id = f"{doc_id}_chunk{chunk_idx+1:03d}"
        meta.update({
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "chunk_index": chunk_idx,
            "token_count": len(chunk.text.split()),  # TODO: thay bằng tokenizer chuẩn
            "section_title": chunk.main_heading,
            "extracted_at": datetime.now().isoformat(),
            "embedding_model": "",
            "hash": hashlib.sha256(chunk.text.encode("utf-8")).hexdigest(),
        })

        return meta

    def save_chunk(chunk: Chunk, chunk_idx: int):
        """Lưu chunk và metadata ra file.

        Args:
            chunk (Chunk): Chunk dữ liệu.
            chunk_idx (int): Chỉ số chunk.
        """
        chunk_filename = f"{doc_id}_chunk{chunk_idx+1:03d}.md"
        chunk_filepath = os.path.normpath(os.path.join(chunk_dir, "doc", chunk_filename))
        with open(chunk_filepath, "w", encoding="utf-8") as cf:
            cf.write(chunk.text)
        logger.info("Lưu chunk %d vào file: %s", chunk_idx+1, os.path.abspath(chunk_filepath))

        chunk_meta = metadata_for_chunk(chunk, chunk_idx)
        meta_filename = f"{doc_id}_chunk{chunk_idx+1:03d}.json"
        meta_filepath = os.path.normpath(os.path.join(chunk_dir, "metadata", meta_filename))
        with open(meta_filepath, "w", encoding="utf-8") as mf:
            json.dump(chunk_meta, mf, ensure_ascii=False, indent=2)
        logger.info("Lưu metadata chunk %d vào file: %s", chunk_idx+1, os.path.abspath(meta_filepath))

    try:
        doc_filepath = os.path.normpath(os.path.join(document_dir, "doc", f"{doc_id}.md"))
        logger.info("Đang mở file nguồn: %s", os.path.abspath(doc_filepath))

        try:
            with open(doc_filepath, "r", encoding="utf-8") as f:
                md_text = f.read()
        except Exception as e:
            logger.error("Lỗi khi đọc file markdown: %s", e)
            return False

        corpus = parse_markdown_to_corpus(md_text, max_row_words=max_row_words)
        chunker = HeadingChunker(corpus, L=L)
        chunks = chunker.run()

        logger.info("Chunking doc_id %s thành %d chunks", doc_id, len(chunks))

        for i, chunk in enumerate(chunks):
            save_chunk(chunk, i)
        return True

    except Exception as e:
        logger.error("Lỗi khi chunking doc_id %s: %s", doc_id, e)
        return False


def chunking_below_scope(scope: str = CHUNKING_SCOPE,
                         L: int = CHUNK_SIZE,
                         max_row_words: int = MAX_ROW_WORDS):
    """Chunking tất cả document trong một scope.

    Args:
        scope (str, optional): Scope ("all", "medical", "other", "testing"). Defaults to CHUNKING_SCOPE.
        L (int, optional): Ngưỡng số token tối đa cho chunk. Defaults to CHUNK_SIZE.
        max_row_words (int, optional): Số từ tối đa mỗi row. Defaults to MAX_ROW_WORDS.
    """
    try:
        scopes = []
        if scope == "all":
            scopes = [
                os.path.normpath(os.path.join(DOCUMENTS_DIR, d, "cleaned"))
                for d in os.listdir(DOCUMENTS_DIR)
                if os.path.isdir(os.path.join(DOCUMENTS_DIR, d))
            ]
        else:
            scopes = [os.path.normpath(os.path.join(DOCUMENTS_DIR, scope, "cleaned"))]

        logger.info("Chunking tất cả document trong scope: %s", scopes)
    except Exception as e:
        logger.error("Lỗi khi xác định scope documents: %s", e)
        return

    for doc_scope in scopes:
        chunk_scope = os.path.normpath(
            doc_scope.replace("documents", "chunks").replace("cleaned", "")
        )
        os.makedirs(chunk_scope, exist_ok=True)

        logger.info("Đang xử lý thư mục: %s", os.path.abspath(doc_scope))

        for filename in os.listdir(os.path.normpath(os.path.join(doc_scope, "doc"))):
            if filename.endswith(".md"):
                doc_id = filename[:-3]
                logger.info("Chunking doc_id: %s", doc_id)
                success = chunking(
                    document_dir=doc_scope,
                    chunk_dir=chunk_scope,
                    doc_id=doc_id,
                    L=L,
                    max_row_words=max_row_words,
                )
                if not success:
                    logger.error("Chunking doc_id %s thất bại", doc_id)
                else:
                    logger.info("Chunking doc_id %s thành công", doc_id)
