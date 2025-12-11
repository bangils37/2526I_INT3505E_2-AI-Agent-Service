# retrieval_service/src/app/pipeline/chunker/corpus_parser.py
# -*- coding: utf-8 -*-
"""
Module để parse markdown thành Corpus bằng cách sử dụng các schema
(Row, Corpus, Chunk) từ corpus_schema.
"""

import re
from typing import List
import logging

from retrieval_service.src.app.log.logging_config import setup_logging
from retrieval_service.src.app.config import MAX_ROW_WORDS
from retrieval_service.src.app.schemas.corpus_schema import Row, Corpus

setup_logging()
logger = logging.getLogger(__name__)


# ---------- Helpers to build Corpus from markdown ----------
def split_row(text: str, max_words: int = 20) -> List[str]:
    """Tách một chuỗi thành nhiều đoạn (row) theo số từ tối đa.

    Args:
        text (str): Chuỗi cần tách.
        max_words (int, optional): Số từ tối đa trong mỗi đoạn. Defaults to 20.

    Returns:
        List[str]: Danh sách các đoạn text đã tách.
    """
    words = text.split()
    if not words:
        return []
    chunks: List[str] = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks


def parse_markdown_to_corpus(md_text: str, max_row_words: int = MAX_ROW_WORDS) -> Corpus:
    """Phân tích markdown thành Corpus với headings và rows.

    Args:
        md_text (str): Nội dung markdown.
        max_row_words (int, optional): Số từ tối đa cho mỗi row. Defaults to MAX_ROW_WORDS.

    Returns:
        Corpus: Kết quả gồm danh sách headings và rows.
    """
    logger.info("Bắt đầu parse markdown thành Corpus (max_row_words=%d)", max_row_words)

    headings: List[str] = []
    rows: List[Row] = []

    # tạo root heading ở index 0
    headings.append("")
    current_heading_idx = 0
    current_heading_type = 0

    lines = md_text.splitlines()
    logger.debug("Số dòng đầu vào: %d", len(lines))

    for lineno, raw_line in enumerate(lines):
        line = raw_line.rstrip("\n")
        if not line.strip():
            continue

        # phát hiện heading
        m = re.match(r"^(#{1,6})\s*(.*)$", line)
        if m:
            hashes = m.group(1)
            heading_type = max(0, len(hashes) - 1)

            heading_full = line.strip()
            headings.append(heading_full)
            current_heading_idx = len(headings) - 1
            current_heading_type = heading_type

            logger.debug(
                "Dòng %d: phát hiện heading (idx=%d, type=%d): %s",
                lineno,
                current_heading_idx,
                current_heading_type,
                heading_full,
            )

            heading_row_chunks = split_row(heading_full, max_row_words)
            if not heading_row_chunks:
                rows.append(Row(
                    text=heading_full,
                    heading=current_heading_idx,
                    heading_type=current_heading_type,
                    is_heading=True,
                ))
            else:
                first = "\n" + heading_row_chunks[0] + "\n"
                rows.append(Row(
                    text=first,
                    heading=current_heading_idx,
                    heading_type=current_heading_type,
                    is_heading=True,
                ))
                for cont in heading_row_chunks[1:]:
                    rows.append(Row(
                        text=cont,
                        heading=current_heading_idx,
                        heading_type=current_heading_type,
                        is_heading=False,
                    ))
        else:
            if current_heading_idx is None:
                current_heading_idx = 0
                current_heading_type = 0

            chunks = split_row(line, max_row_words)
            if not chunks:
                continue
            for chunk in chunks:
                rows.append(Row(
                    text=chunk,
                    heading=current_heading_idx,
                    heading_type=current_heading_type,
                    is_heading=False,
                ))

    logger.info("Kết thúc parse: headings=%d, rows=%d", len(headings), len(rows))

    # kiểm tra row nào vượt giới hạn
    bad = [i for i, r in enumerate(rows) if r.size() > max_row_words]
    if bad:
        logger.warning(
            "Phát hiện %d row vượt giới hạn từ (max_row_words=%d): ví dụ indices %s",
            len(bad),
            max_row_words,
            bad[:10],
        )

    return Corpus(headings=headings, rows=rows)
