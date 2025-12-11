"""Convert JSONL file into Markdown + Metadata JSON files.
- Đọc file JSONL, chuyển đổi mỗi đối tượng JSON thành file Markdown và file metadata JSON riêng.
- Lưu các file đã chuyển đổi vào thư mục tương ứng.
- Bỏ qua các đối tượng JSON không hợp lệ hoặc thiếu trường `doc_id`.
- Cung cấp hàm chính để chạy như một script độc lập.
"""

from __future__ import annotations

import os
import json
import sys
import re
import logging
from pathlib import Path
from typing import Optional

from retrieval_service.src.app.config import DOCUMENTS_DIR
from retrieval_service.src.app.log.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


# --- Configuration ---
DEFAULT_LIMIT = 100000
SKIP_FIELDS = {"content", "parse_confidence", "extracted_article_links", "raw_html"}

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def sanitize_filename(name: str) -> str:
    """Convert a string into a safe filename."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)


def format_content_to_markdown(content: str) -> str:
    """Convert raw content to Markdown format with simple heading detection."""
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    markdown_lines = []

    for p in paragraphs:
        if re.match(r"^(I{1,3}|IV|V?I{0,3})\.", p):  # Roman numeral
            markdown_lines.append(f"## {p}")
        elif re.match(r"^\d+\.", p):  # Numbered list
            markdown_lines.append(f"### {p}")
        else:
            markdown_lines.append(p)

    return "\n\n".join(markdown_lines)


def convert_jsonl_to_docs_and_metadata(
    collection: str,
    document_id: str,
    limit: int = DEFAULT_LIMIT,
) -> list[str]:
    """
    Convert JSONL file into Markdown + Metadata JSON files.

    Args:
        input_path (Path): Path to the JSONL input file.
        output_doc_dir (Path): Directory to save Markdown files.
        output_meta_dir (Path): Directory to save metadata JSON files.
        limit (int): Maximum number of JSON objects to process.

    Returns:
        int: Number of files successfully saved.
    """
    convert_logs = ["--- JSONL CONVERTING PHASE ---"]
    
    input_path = Path(os.path.normpath(DOCUMENTS_DIR + f"/{collection}/raw/{document_id}.jsonl"))
    output_doc_dir = Path(os.path.normpath(DOCUMENTS_DIR + f"/{collection}/cleaned/{document_id}/doc"))
    output_meta_dir = Path(os.path.normpath(DOCUMENTS_DIR + f"/{collection}/cleaned/{document_id}/metadata"))
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_doc_dir.mkdir(parents=True, exist_ok=True)
    output_meta_dir.mkdir(parents=True, exist_ok=True)
    
    # Xoá hết các file cũ trong thư mục output
    for file in output_doc_dir.glob("*.md"):
        file.unlink()

    for file in output_meta_dir.glob("*.json"):
        file.unlink()

    saved_files = 0
    existing = {p.stem for p in output_doc_dir.glob("*.md")}

    with input_path.open("r", encoding="utf-8") as f:
        total_files = sum(1 for _ in f)
        f.seek(0)   # Reset file pointer to the beginning
        for i, line in enumerate(f):
            if i >= limit:
                break

            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                logging.warning(f"Skipping invalid JSON line: {e}")
                convert_logs.append(f"Skipping invalid JSON line: {e}")
                continue

            doc_id = obj.get("doc_id")
            if not doc_id:
                logging.warning("Skipping object without `doc_id` field.")
                convert_logs.append("Skipping object without `doc_id` field.")
                continue

            safe_id = sanitize_filename(str(doc_id))
            if safe_id in existing:
                logging.info(f"Skipping duplicate doc_id: {safe_id}")
                convert_logs.append(f"Skipping duplicate doc_id: {safe_id}")
                continue

            title = obj.get("title", "Untitled")
            content = obj.get("content", "")

            # --- Save Markdown ---
            markdown = f"# {title}\n\n{format_content_to_markdown(content)}"
            markdown_path = output_doc_dir / f"{safe_id}.md"
            try:
                markdown_path.write_text(markdown, encoding="utf-8")
            except OSError as e:
                logging.error(f"Failed to write Markdown for {safe_id}: {e}")
                continue

            # --- Save Metadata ---
            metadata = {k: v for k, v in obj.items() if k not in SKIP_FIELDS}
            metadata_path = output_meta_dir / f"{safe_id}.json"
            try:
                metadata_path.write_text(
                    json.dumps(metadata, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            except OSError as e:
                logging.error(f"Failed to write metadata for {safe_id}: {e}")
                continue

            saved_files += 1
            existing.add(safe_id)
            logging.info(f"✅ Saved: {safe_id}")

    logging.info(f"✅ Finished processing {saved_files}/{total_files} files from {input_path}")
    convert_logs.append(f"✅ Finished processing {saved_files}/{total_files} files from {input_path}")
    return convert_logs

# Testing as a script
def main() -> int:
    try:
        convert_jsonl_to_docs_and_metadata(collection="testing", document_id="small_sample_data_prepared")
    except Exception as e:
        logging.exception(f"❌ Error while converting file: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
