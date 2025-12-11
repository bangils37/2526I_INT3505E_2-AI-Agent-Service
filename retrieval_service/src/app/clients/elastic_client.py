# retrieval_service/src/app/clients/elastic_client.py
# -*- coding: utf-8 -*-
"""
Client wrapper cho Elasticsearch.

Cung cấp API async để quản lý index, thực hiện search,
bulk index và các thao tác quản lý kết nối.
"""

import logging
from typing import List, Dict, Any, Optional

from elasticsearch import AsyncElasticsearch, helpers

from retrieval_service.src.app.config import (
    ELASTIC_URL,
    ELASTIC_USER,
    ELASTIC_PASS,
)
from retrieval_service.src.app.log.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class ElasticClient:
    """Wrapper cho Elasticsearch client async."""

    def __init__(
        self,
        url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Khởi tạo Elasticsearch client.

        Args:
            url (Optional[str]): URL của Elasticsearch.
            username (Optional[str]): Tài khoản Elasticsearch.
            password (Optional[str]): Mật khẩu Elasticsearch.
        """
        self.url = url or ELASTIC_URL or "http://localhost:9200"
        self.username = username or ELASTIC_USER
        self.password = password or ELASTIC_PASS

        # Khởi tạo client gốc
        self._client = AsyncElasticsearch(
            self.url,
            basic_auth=(self.username, self.password)
            if self.username and self.password
            else None,
        )
        logger.info("ElasticClient khởi tạo với endpoint %s", self.url)

    @property
    def client(self) -> AsyncElasticsearch:
        """Trả về Elasticsearch client gốc.

        Returns:
            AsyncElasticsearch: Đối tượng client Elasticsearch.
        """
        return self._client

    async def ping(self) -> bool:
        """Kiểm tra kết nối tới Elasticsearch.

        Returns:
            bool: True nếu ping thành công, False nếu thất bại.
        """
        try:
            return await self._client.ping()
        except Exception as e:
            logger.error("Ping tới Elasticsearch thất bại: %s", e)
            return False

    async def create_index(self, index_name: str, mapping: Dict[str, Any]) -> None:
        """Tạo index với mapping nếu chưa tồn tại.

        Args:
            index_name (str): Tên index cần tạo.
            mapping (Dict[str, Any]): Cấu hình mapping cho index.

        Raises:
            Exception: Nếu quá trình tạo index thất bại.
        """
        try:
            exists = await self._client.indices.exists(index=index_name)
            if not exists:
                await self._client.indices.create(index=index_name, body=mapping)
                logger.info("Đã tạo index mới: %s", index_name)
            else:
                logger.info("Index %s đã tồn tại, bỏ qua.", index_name)
        except Exception as e:
            logger.error("Lỗi khi tạo index %s: %s", index_name, e)
            raise

    async def search(
        self, index: str, query: Dict[str, Any], size: int = 10
    ) -> Dict[str, Any]:
        """Thực hiện search query trên một index.

        Args:
            index (str): Tên index cần search.
            query (Dict[str, Any]): Query Elasticsearch.
            size (int, optional): Số lượng kết quả trả về. Defaults to 10.

        Returns:
            Dict[str, Any]: Kết quả tìm kiếm từ Elasticsearch.

        Raises:
            Exception: Nếu search thất bại.
        """
        try:
            resp = await self._client.search(index=index, body=query, size=size)
            return resp
        except Exception as e:
            logger.error("Lỗi khi search trên index %s: %s", index, e)
            raise

    async def bulk_index(self, index: str, docs: List[Dict[str, Any]]) -> None:
        """Thực hiện bulk index documents.

        Args:
            index (str): Tên index.
            docs (List[Dict[str, Any]]): Danh sách tài liệu với các field:
                - `_id`: ID của tài liệu.
                - `doc`: Nội dung tài liệu.

        Raises:
            Exception: Nếu bulk index thất bại.
        """
        try:
            actions = [
                {
                    "_op_type": "index",
                    "_index": index,
                    "_id": doc.get("_id"),
                    "_source": doc["doc"],
                }
                for doc in docs
            ]
            success, failed = await helpers.async_bulk(self._client, actions)
            logger.info(
                "Bulk index hoàn tất: thành công=%s, thất bại=%s", success, failed
            )
        except Exception as e:
            logger.error("Lỗi khi bulk index vào %s: %s", index, e)
            raise

    async def delete_index(self, index_name: str) -> None:
        """Xoá index nếu tồn tại.

        Args:
            index_name (str): Tên index cần xoá.

        Raises:
            Exception: Nếu xoá index thất bại.
        """
        try:
            exists = await self._client.indices.exists(index=index_name)
            if exists:
                await self._client.indices.delete(index=index_name)
                logger.info("Đã xoá index: %s", index_name)
        except Exception as e:
            logger.error("Lỗi khi xoá index %s: %s", index_name, e)
            raise

    async def close(self) -> None:
        """Đóng kết nối Elasticsearch."""
        try:
            await self._client.close()
            logger.info("Đã đóng kết nối Elasticsearch.")
        except Exception as e:
            logger.warning("Lỗi khi đóng Elasticsearch client: %s", e)
