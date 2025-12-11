# retrieval_service/src/app/pipeline/indexing.py
# -*- coding: utf-8 -*-
"""
Pipeline indexing tài liệu vào Qdrant.

Quy trình:
    1. Đọc các cặp file chunk (.md) và metadata (.json) từ thư mục chỉ định.
    2. Gửi nội dung các chunk tới OpenAI client để embed thành vector.
    3. Upsert vector và metadata tương ứng vào Qdrant.
"""
import os
import asyncio
import json
import logging
import uuid
from pathlib import Path
from typing import List, Dict, Any, Tuple

from qdrant_client.models import PointStruct
from retrieval_service.src.app.clients.openai_client import OpenAIEmbeddingClient
from retrieval_service.src.app.clients.qdrant_client import QdrantDB
from retrieval_service.src.app.log.logging_config import setup_logging
from retrieval_service.src.app.config import (
    QDRANT_VECTOR_SIZE,
    CHUNKS_DIR,
    QDRANT_BATCH_SIZE,
)

# ---------- Logging ----------
setup_logging()
logger = logging.getLogger(__name__)


# ---------- IndexingPipeline ----------
class IndexingPipeline:
    """Pipeline quản lý toàn bộ luồng xử lý embedding và indexing vào Qdrant.

    Attributes:
        collection_name (str): Tên collection Qdrant.
        openai_client (OpenAIEmbeddingClient): Client để sinh embeddings.
        qdrant_client (QdrantDB): Client để thao tác với Qdrant.
        UUID_NAMESPACE (uuid.UUID): Namespace UUID cố định để sinh ID nhất quán.
    """

    def __init__(self):
        """Khởi tạo pipeline."""
        self.openai_client = OpenAIEmbeddingClient()
        self.qdrant_client = QdrantDB(vector_size=QDRANT_VECTOR_SIZE)
        self.UUID_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
        self.indexing_logs = []
        self.collection_name = ""

    def _load_data_from_path(self, data_path: Path) -> List[Tuple[str, str, Dict[str, Any]]]:
        """Đọc dữ liệu từ thư mục chunks và metadata.

        Args:
            data_path (Path): Đường dẫn tới thư mục gốc chứa "doc" và "metadata".

        Returns:
            List[Tuple[str, str, Dict[str, Any]]]: Danh sách các tuple
                (chunk_id, chunk_text, metadata).
        """
        doc_path = data_path / "doc"
        metadata_path = data_path / "metadata"

        if not doc_path.is_dir() or not metadata_path.is_dir():
            logger.error(f"Thư mục 'doc' hoặc 'metadata' không tồn tại trong '{data_path}'")
            raise FileNotFoundError(f"Đường dẫn không hợp lệ: {data_path}")

        data_to_process = []
        md_files = list(doc_path.glob("*.md"))
        logger.info(f"Tìm thấy {len(md_files)} file .md trong {doc_path}")
        self.indexing_logs.append(f"Tìm thấy {len(md_files)} file .md trong {doc_path}")

        for md_file in md_files:
            chunk_id = md_file.stem
            json_file = metadata_path / f"{chunk_id}.json"

            if not json_file.exists():
                logger.warning(
                    f"Bỏ qua {md_file.name}: Không tìm thấy file metadata {json_file.name}"
                )
                continue

            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    chunk_text = f.read()
                with open(json_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)

                metadata["text"] = chunk_text
                data_to_process.append((chunk_id, chunk_text, metadata))
            except Exception as e:
                logger.error(f"Lỗi khi đọc file cho chunk_id '{chunk_id}': {e}")

        logger.info(f"Đã tải thành công {len(data_to_process)} cặp chunk/metadata.")
        return data_to_process

    async def run(
        self, 
        document_id: str, 
        collection: str
    ) -> list[str]:
        """Thực thi toàn bộ pipeline indexing.

        Args:
            data_path (Path, optional): Thư mục chứa "doc" và "metadata".
                Defaults to Path(os.path.join(CHUNKS_DIR, "testing")).
        """
        self.indexing_logs = ["--- INDEXING PHASE ---"]
        
        data_path = Path(os.path.normpath(os.path.join(CHUNKS_DIR, collection, document_id)))
        self.collection_name = collection
        
        logger.info("--- BẮT ĐẦU PIPELINE INDEXING ---")
        logger.info(f"Collection: '{self.collection_name}'")
        logger.info(f"Đường dẫn dữ liệu: '{data_path}'")

        self.qdrant_client.create_collection(self.collection_name)

        data_to_process = self._load_data_from_path(Path(data_path))
        if not data_to_process:
            logger.warning("Không có dữ liệu để xử lý. Kết thúc pipeline.")
            self.indexing_logs.append("Không có dữ liệu để xử lý. Kết thúc pipeline.")
            return

        total_batches = (len(data_to_process) + QDRANT_BATCH_SIZE - 1) // QDRANT_BATCH_SIZE
        logger.info(
            f"Bắt đầu xử lý {len(data_to_process)} chunks trong {total_batches} batch "
            f"(batch size: {QDRANT_BATCH_SIZE})."
        )
        self.indexing_logs.append(
            f"Bắt đầu xử lý {len(data_to_process)} chunks trong {total_batches} batch "
            f"(batch size: {QDRANT_BATCH_SIZE})."
        )

        for i in range(0, len(data_to_process), QDRANT_BATCH_SIZE):
            batch_num = (i // QDRANT_BATCH_SIZE) + 1
            logger.info(f">> Đang xử lý Batch {batch_num}/{total_batches}...")

            batch_data = data_to_process[i : i + QDRANT_BATCH_SIZE]

            chunk_ids = [item[0] for item in batch_data]
            texts_to_embed = [item[1] for item in batch_data]
            payloads = [item[2] for item in batch_data]

            logger.info(f"   - Embedding {len(texts_to_embed)} chunks...")
            vectors = await self.openai_client.embed_texts(texts_to_embed)
            logger.info(f"   - Nhận {len(vectors)} vectors.")

            points_to_upsert = []
            for chunk_id, vector, payload in zip(chunk_ids, vectors, payloads):
                point_id = str(uuid.uuid5(self.UUID_NAMESPACE, chunk_id))
                payload["original_chunk_id"] = chunk_id
                points_to_upsert.append(
                    PointStruct(id=point_id, vector=vector, payload=payload)
                )

            logger.info(f"   - Upserting {len(points_to_upsert)} points vào Qdrant...")
            self.qdrant_client.upsert_points(points_to_upsert)
            logger.info(f"   - Hoàn thành Batch {batch_num}/{total_batches}.")
            self.indexing_logs.append(f"   - Hoàn thành Batch {batch_num}/{total_batches}.")

        logger.info("--- HOÀN THÀNH PIPELINE INDEXING ---")
        logger.info(
            f"Đã index thành công {len(data_to_process)} chunks vào collection '{self.collection_name}'."
        )
        self.indexing_logs.append(
            f"Đã index thành công {len(data_to_process)} chunks vào collection '{self.collection_name}'."
        )
        
        return self.indexing_logs
        

__indexing_pipeline_instance = IndexingPipeline()

def get_indexing_pipeline() -> IndexingPipeline:
    """Lấy instance singleton của IndexingPipeline."""
    return __indexing_pipeline_instance


# Testing as a script
async def main():
    """Entry point để chạy pipeline từ command line."""
    pipeline = get_indexing_pipeline()
    await pipeline.run(document_id="small_vinmec_data_prepared", collection="medical")


if __name__ == "__main__":
    asyncio.run(main())
