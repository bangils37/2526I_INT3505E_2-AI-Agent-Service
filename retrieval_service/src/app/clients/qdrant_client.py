# retrieval_service/src/app/clients/qdrant_client.py
# -*- coding: utf-8 -*-
"""
Client wrapper cho Qdrant vector database.
Cung cấp API đồng bộ để tạo collection, upsert points và tìm kiếm.
"""
import logging
from qdrant_client import QdrantClient as BaseQdrantClient
from qdrant_client.models import PointStruct
from retrieval_service.src.app.config import (
    QDRANT_API_KEY,
    QDRANT_URL,
)
from retrieval_service.src.app.log.logging_config import setup_logging

# ------------------------------
# Setup logging
# ------------------------------
setup_logging()
logger = logging.getLogger(__name__)


class QdrantDB:
    """Wrapper tiện ích cho Qdrant Client."""

    def __init__(self, host: str = "localhost", port: int = 6333, vector_size: int = 768):
        """Khởi tạo QdrantDB wrapper.

        Ưu tiên kết nối tới Qdrant Cloud nếu có `QDRANT_API_KEY` và `QDRANT_URL`.
        Nếu không, fallback sang kết nối Qdrant Local.

        Args:
            host (str, optional): Host Qdrant local. Defaults to "localhost".
            port (int, optional): Port Qdrant local. Defaults to 6333.
            vector_size (int, optional): Kích thước vector embedding. Defaults to 768.
        """
        self.collection_name = None
        self.vector_size = vector_size

        # Kết nối Qdrant (Cloud hoặc Local)
        if QDRANT_API_KEY and QDRANT_URL:
            logger.info(f"🔑 Connecting to Qdrant Cloud at {QDRANT_URL}")
            self.client = BaseQdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        else:
            logger.info(f"💻 Connecting to Qdrant Local at {host}:{port}")
            self.client = BaseQdrantClient(host=host, port=port)

    def create_collection(self, collection_name: str):
        """Tạo mới hoặc reset một collection.

        Args:
            collection_name (str): Tên collection cần tạo/reset.
        """
        self.collection_name = collection_name
        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config={"size": self.vector_size, "distance": "Cosine"},
        )
        logger.info(f"📂 Collection '{collection_name}' created with vector_size={self.vector_size}")

    def upsert_points(self, points: list):
        """Thêm hoặc update points vào collection hiện tại.

        Args:
            points (list): Danh sách `PointStruct` cần insert/update.

        Raises:
            ValueError: Nếu collection chưa được tạo.
        """
        if not self.collection_name:
            raise ValueError("❌ Collection chưa được tạo. Hãy gọi create_collection() trước.")

        self.client.upsert(collection_name=self.collection_name, points=points)
        logger.info(f"📌 Inserted {len(points)} points into '{self.collection_name}'")

    def search_points(self, query_vector: list, limit: int = 3):
        """Tìm kiếm các vector gần nhất trong collection.

        Args:
            query_vector (list): Vector query.
            limit (int, optional): Số lượng kết quả cần trả về. Defaults to 3.

        Returns:
            list: Danh sách kết quả search (`ScoredPoint`).
        
        Raises:
            ValueError: Nếu collection chưa được tạo.
        """
        if not self.collection_name:
            raise ValueError("❌ Collection chưa được tạo. Hãy gọi create_collection() trước.")

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
        )
        logger.info(f"🔍 Search in '{self.collection_name}' returned {len(results)} results")
        return results


# ------------------------------
# Ví dụ chạy thử
# ------------------------------
if __name__ == "__main__":
    db = QdrantDB(vector_size=4)
    db.create_collection("test_collection")

    # Insert sample data
    points = [
        PointStruct(id=1, vector=[0.1, 0.2, 0.3, 0.4], payload={"text": "Xin chào"}),
        PointStruct(id=2, vector=[0.2, 0.1, 0.4, 0.3], payload={"text": "Qdrant là vector DB"}),
    ]
    db.upsert_points(points)

    # Search thử
    results = db.search_points(query_vector=[0.1, 0.2, 0.25, 0.35], limit=2)
    for hit in results:
        print(f"ID={hit.id}, Score={hit.score}, Payload={hit.payload}")
