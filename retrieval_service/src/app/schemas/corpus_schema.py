# retrieval_service/src/app/pipeline/chunker/corpus_schema.py
# -*- coding: utf-8 -*-
"""
Định nghĩa các data model cho Corpus parsing:
- Row
- Corpus
- Chunk
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Row:
    """Đại diện cho một dòng (row) trong Corpus.

    Attributes:
        text (str): Nội dung văn bản của row.
        heading (int): Chỉ số heading mà row này thuộc về.
        heading_type (int): Cấp độ heading (0 => '#', 1 => '##', ...).
        is_heading (bool): True nếu là dòng heading, False nếu là nội dung thường.
    """
    text: str
    heading: int
    heading_type: int
    is_heading: bool

    def size(self) -> int:
        """Trả về số từ trong row.

        Returns:
            int: Số từ (tách theo whitespace).
        """
        return len(self.text.split())


@dataclass
class Corpus:
    """Đại diện cho một tài liệu đã parse từ markdown.

    Attributes:
        headings (List[str]): Danh sách chuỗi heading (theo index).
        rows (List[Row]): Các dòng đã flatten từ markdown.
    """
    headings: List[str]
    rows: List[Row]


@dataclass
class Chunk:
    """Đại diện cho một đoạn chunk.

    Attributes:
        main_heading (str): Heading chính của chunk.
        headings (str): Chuỗi tất cả headings (đã join).
        main_text (str): Văn bản thuộc main heading.
        outside_text (str): Văn bản thuộc các heading khác.
        text (str): Nội dung kết hợp headings + main_text + outside_text.
    """
    main_heading: str = ""
    headings: str = ""
    main_text: str = ""
    outside_text: str = ""
    text: str = ""
