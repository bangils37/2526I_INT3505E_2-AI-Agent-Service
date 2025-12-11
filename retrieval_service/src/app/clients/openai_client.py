# retrieval_service/src/app/clients/openai_client.py
# -*- coding: utf-8 -*-
"""
Client wrapper cho OpenAI/Azure OpenAI.

Cung cấp lớp tiện ích để làm việc với embeddings và chat models.
- Ưu tiên sử dụng Azure nếu có cấu hình endpoint và API key.
- Fallback sang OpenAI mặc định nếu không có.
"""

import logging
from typing import List, Optional

from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from retrieval_service.src.app.config import (
    ENDPOINT_TEXT3_EMBEDDING,
    API_KEY_TEXT3_EMBEDDING,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT,
)
from retrieval_service.src.app.log.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class OpenAIEmbeddingClient:
    """Wrapper cho OpenAI/Azure Embeddings."""

    def __init__(self):
        """Khởi tạo embeddings client.

        Ưu tiên sử dụng `AzureOpenAIEmbeddings` nếu có cấu hình endpoint và API key.
        Nếu không, fallback sang `OpenAIEmbeddings`.
        """
        endpoint = ENDPOINT_TEXT3_EMBEDDING
        api_key = API_KEY_TEXT3_EMBEDDING

        # Chọn embeddings backend
        if endpoint and api_key:
            self._embeddings = AzureOpenAIEmbeddings(
                model="text-embedding-3-small",
                azure_endpoint=endpoint,
                api_key=api_key,
                openai_api_version="2023-05-15",
            )
            logger.info("Dùng AzureOpenAIEmbeddings với endpoint %s", endpoint)
        else:
            self._embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            logger.info("Dùng OpenAIEmbeddings mặc định (không Azure).")

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed nhiều văn bản.

        Args:
            texts (List[str]): Danh sách văn bản cần embedding.

        Returns:
            List[List[float]]: Danh sách vector embedding.
        """
        return await self._embeddings.aembed_documents(texts)

    async def embed_query(self, query: str) -> List[float]:
        """Embed một query người dùng.

        Args:
            query (str): Câu query người dùng.

        Returns:
            List[float]: Vector embedding của query.
        """
        return await self._embeddings.aembed_query(query)

    async def get_embedding(self):
        """Lấy object embedding client gốc.

        Returns:
            Union[AzureOpenAIEmbeddings, OpenAIEmbeddings]: Client embeddings.
        """
        return self._embeddings


class OpenAIChatGPTClient:
    """Wrapper cho OpenAI/Azure ChatGPT."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ):
        """Khởi tạo ChatGPT client.

        Ưu tiên sử dụng `AzureChatOpenAI` nếu có cấu hình endpoint, API key và deployment.
        Nếu không, fallback sang `ChatOpenAI`.

        Args:
            model (str, optional): Tên model. Defaults to "gpt-4o-mini".
            temperature (float, optional): Mức độ đa dạng câu trả lời. Defaults to 0.0.
            max_tokens (Optional[int], optional): Số token tối đa trả về. Defaults to None.
        """
        endpoint = AZURE_OPENAI_ENDPOINT
        api_key = AZURE_OPENAI_API_KEY

        # Chọn chat backend
        if endpoint and api_key and AZURE_OPENAI_DEPLOYMENT:
            self._chat = AzureChatOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                openai_api_version=AZURE_OPENAI_API_VERSION or "2023-05-15",
                deployment_name=AZURE_OPENAI_DEPLOYMENT,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            logger.info("Dùng AzureChatOpenAI với endpoint %s", endpoint)
        else:
            self._chat = ChatOpenAI(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            logger.info("Dùng ChatOpenAI mặc định (không Azure).")

    async def chat(self, messages: List[dict]) -> str:
        """Gửi danh sách messages tới ChatGPT và lấy câu trả lời.

        Args:
            messages (List[dict]): Danh sách messages, mỗi phần tử có dạng:
                {"role": "system|user|assistant", "content": "nội dung"}.

        Returns:
            str: Câu trả lời từ ChatGPT.

        Raises:
            Exception: Nếu gọi API thất bại.
        """
        try:
            response = await self._chat.ainvoke(messages)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            logger.error("Lỗi khi gọi ChatGPT: %s", e)
            raise
