#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test để kiểm tra OpenAI Embedding model có hoạt động không.
"""

import asyncio
import sys
import os

# Thêm path để import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.app.clients.openai_client import OpenAIEmbeddingClient
from src.app.log.logging_config import setup_logging

setup_logging()

async def test_embedding():
    """Test embedding client."""
    print("🔍 Đang kiểm tra OpenAI Embedding Client...")

    client = OpenAIEmbeddingClient()

    # Kiểm tra is_ready
    print("📡 Kiểm tra trạng thái client...")
    ready = await client.is_ready()
    if not ready:
        print("❌ Client không sẵn sàng!")
        return False

    print("✅ Client sẵn sàng!")

    # Test embed query
    print("🧪 Test embedding một query đơn giản...")
    try:
        query = "Đây là một câu test để kiểm tra embedding."
        embedding = await client.embed_query(query)
        print(f"✅ Embedding thành công! Vector length: {len(embedding)}")
        print(f"📊 Sample values: {embedding[:5]}...")
    except Exception as e:
        print(f"❌ Lỗi khi embedding: {e}")
        return False

    # Test embed texts
    print("🧪 Test embedding nhiều văn bản...")
    try:
        texts = [
            "Bệnh tiểu đường là một bệnh lý chuyển hóa.",
            "Triệu chứng thường gặp là khát nước và đi tiểu nhiều.",
            "Điều trị bao gồm thay đổi lối sống và dùng thuốc."
        ]
        embeddings = await client.embed_texts(texts)
        print(f"✅ Embedding {len(texts)} văn bản thành công!")
        print(f"📊 Vector lengths: {[len(emb) for emb in embeddings]}")
    except Exception as e:
        print(f"❌ Lỗi khi embedding texts: {e}")
        return False

    print("🎉 Tất cả test đều thành công! Embedding model hoạt động bình thường.")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_embedding())
    sys.exit(0 if success else 1)