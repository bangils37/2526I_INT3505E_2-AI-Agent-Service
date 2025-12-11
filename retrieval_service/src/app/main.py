# retrieval_service/src/app/main.py
# -*- coding: utf-8 -*-
"""
Main FastAPI app cho retrieval_service.

Nhiệm vụ chính:
- Import và mount routers từ `retrieval_service.src.app.api.v1.search` và `retrieval_service.src.app.api.v1.health`.
- Thiết lập middleware (CORS), logging, và lifecycle events (startup/shutdown).
- Khởi tạo clients (elastic/openai/qdrant) nếu module client có sẵn và gán vào app.state
  để các router/service khác có thể dùng.
"""

from typing import List
import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from retrieval_service.src.app.log.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# Import routers
try:
    from retrieval_service.src.app.api.v1.search import router as search_router
except Exception as e:
    search_router = None
    logger.warning("Không thể import app.api.v1.search.router: %s", e)

try:
    from retrieval_service.src.app.api.v1.health import router as health_router
except Exception as e:
    health_router = None
    logger.warning("Không thể import app.api.v1.health.router: %s", e)
    
try:
    from retrieval_service.src.app.api.v1.document import router as document_router
except Exception as e:
    document_router = None
    logger.warning("Không thể import app.api.v1.document.router: %s", e)

# Import settings
try:
    from retrieval_service.src.app.config import get_settings as settings
except Exception:
    class _DummySettings:
        APP_NAME = "retrieval_service"
        VERSION = "0.0.0"
        ALLOWED_ORIGINS: List[str] = ["*"]
        HOST = "0.0.0.0"
        PORT = 8001

    settings = _DummySettings()
    logger.warning("Sử dụng settings mặc định (app.config không có hoặc lỗi import).")

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)


def create_app() -> FastAPI:
    """Khởi tạo FastAPI app, mount routers và thêm middleware.

    Returns:
        FastAPI: Instance FastAPI đã cấu hình.
    """
    app = FastAPI(
        title=getattr(settings, "APP_NAME", "retrieval_service"),
        version=getattr(settings, "VERSION", "0.1.0"),
        description="""
        ## LMS Retrieval Service API

        Dịch vụ truy xuất thông tin (Retrieval Service) cho hệ thống LMS (Learning Management System) Agent. 
        Cung cấp các chức năng upload tài liệu, tìm kiếm thông tin, và kiểm tra sức khỏe hệ thống.

        ### Chức năng chính:
        - **Upload & Quản lý Tài liệu**: Upload, kiểm tra, và indexing tài liệu vào các collection (testing, lecture).
        - **Tìm kiếm**: Tìm kiếm thông tin trong collection sử dụng hybrid search (lexical + vector).
        - **Health Check**: Giám sát trạng thái các thành phần phụ trợ (Elasticsearch, Qdrant, OpenAI).

        ### Collections hỗ trợ:
        - `testing`: Tài liệu kiểm thử và bài tập
        - `lecture`: Tài liệu bài giảng và học liệu

        ### Authentication:
        Hiện tại không yêu cầu authentication. Trong môi trường production, nên thêm JWT hoặc API key.

        ### Contact:
        - Email: support@example.com
        - Docs: [GitHub Repository](https://github.com/bangils37/2526I_INT3505E_2-AI-Agent-Service)
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Cấu hình CORS
    origins = getattr(settings, "ALLOWED_ORIGINS", ["*"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount routers
    if search_router:
        app.include_router(search_router, tags=["Search"])
        logger.info("Mounted router: retrieval_service.src.app.api.v1.search")
    else:
        logger.warning("search_router không được mount vì import thất bại.")

    if health_router:
        app.include_router(health_router, tags=["Health"])
        logger.info("Mounted router: retrieval_service.src.app.api.v1.health")
    else:
        logger.warning("health_router không được mount vì import thất bại.")
        
    if document_router:
        app.include_router(document_router, tags=["Documents"])
        logger.info("Mounted router: retrieval_service.src.app.api.v1.document")
    else:
        logger.warning("document_router không được mount vì import thất bại.")


    # Lifecycle events
    @app.on_event("startup")
    async def startup_event():
        """Thực thi khi service khởi động. Khởi tạo clients và services."""
        logger.info("App starting up...")
        
        # Qdrant client
        try:
            from retrieval_service.src.app.clients.qdrant_client import QdrantDB as QdrantClient
            app.state.qdrant_client = QdrantClient()
            logger.info("Qdrant client initialized.")
        except Exception as e:
            app.state.qdrant_client = None
            logger.warning("Qdrant client not initialized: %s", e)

        # Elastic client
        try:
            from retrieval_service.src.app.clients.elastic_client import ElasticClient
            app.state.elastic_client = ElasticClient()
            logger.info("Elastic client initialized.")
        except Exception as e:
            app.state.elastic_client = None
            logger.warning("Elastic client not initialized: %s", e)

        # OpenAI client
        try:
            from retrieval_service.src.app.clients.openai_client import OpenAIEmbeddingClient
            app.state.openai_client = OpenAIEmbeddingClient()
            logger.info("OpenAI client initialized.")
        except Exception as e:
            app.state.openai_client = None
            logger.warning("OpenAI client not initialized: %s", e)

        # SearchService
        try:
            from retrieval_service.src.app.services.search_service import SearchService
            app.state.search_service = SearchService()
            logger.info("SearchService initialized.")
        except Exception as e:
            app.state.search_service = None
            logger.warning("SearchService not initialized: %s", e)
                
        # DocumentService
        try:
            from retrieval_service.src.app.services.document_service import DocumentService
            app.state.document_service = DocumentService()
            logger.info("DocumentService initialized.")
        except Exception as e:
            app.state.document_service = None
            logger.warning("DocumentService not initialized: %s", e)

    @app.on_event("shutdown")
    async def shutdown_event():
        """Thực thi khi service shutdown. Đóng các kết nối external clients."""
        logger.info("App shutting down...")

        # Elastic client
        es_client = getattr(app.state, "elastic_client", None)
        if es_client:
            try:
                await maybe_awaitable(es_client.close())
                logger.info("Elastic client closed.")
            except Exception as e:
                logger.warning("Error when closing elastic client: %s", e)

        # OpenAI client
        openai_client = getattr(app.state, "openai_client", None)
        if openai_client:
            try:
                await maybe_awaitable(openai_client.close())
                logger.info("OpenAI client closed.")
            except Exception as e:
                logger.warning("Error when closing OpenAI client: %s", e)
                
        # Qdrant client
        qdrant_client = getattr(app.state, "qdrant_client", None)
        if qdrant_client:
            try:
                await maybe_awaitable(qdrant_client.close())
                logger.info("Qdrant client closed.")
            except Exception as e:
                logger.warning("Error when closing Qdrant client: %s", e)


    return app


async def maybe_awaitable(obj_result):
    """Nếu đối tượng là coroutine thì await, ngược lại trả về trực tiếp.

    Args:
        obj_result (Any): Đối tượng có thể là coroutine hoặc giá trị thường.

    Returns:
        Any: Kết quả sau khi await (nếu cần).
    """
    try:
        if hasattr(obj_result, "__await__"):
            return await obj_result
    except Exception:
        return None
    return obj_result


app = create_app()

if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description="Run retrieval_service FastAPI app")
    parser.add_argument("--host", type=str, default=getattr(settings, "HOST", "0.0.0.0"), help="Host IP")
    parser.add_argument("--port", type=int, default=getattr(settings, "PORT", 8001), help="Port number")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code changes")
    args = parser.parse_args()

    uvicorn.run(
        "retrieval_service.src.app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
        access_log=True
    )
