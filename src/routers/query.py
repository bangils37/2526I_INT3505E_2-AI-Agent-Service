from fastapi import APIRouter, HTTPException
from src.config.settings import get_settings
from src.models.request_models import QueryRequest
from src.models.response_models import QueryResponse
from src.services.retrieval_client import RetrievalClient, check_existence_lesson, upload_lesson
from src.services.llm_client import LLMClient
from src.services.rag_service import RagService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest):
    """Xử lý câu hỏi người dùng và trả về câu trả lời kèm thông tin nguồn.

    Sử dụng dịch vụ RAG (Đóm Tập Hợp - Tạo Ra) để:
    1. Tìm kiếm các đoạn văn bản liên quan.
    2. Đưa dữ liệu vào LLM để tạo ra câu trả lời.
    3. Trả về kết quả cùng với thông tin nguồn.

    Args:
        payload (QueryRequest): Yêu cầu truy vấn.

    Returns:
        QueryResponse: Chứa answer, sources, và meta.

    Raises:
        HTTPException: HTTP 500 nếu có lỗi xử lý.
    """
    logger.info(f"Received query request: {payload.user_question[:50]}...")
    s = get_settings()
    retrieval = RetrievalClient(s.RETRIEVAL_SERVICE_URL)
    llm = LLMClient(s.OPENAI_API_KEY, s.OPENAI_MODEL, s.GEMINI_API_KEY, s.GEMINI_MODEL)
    rag = RagService(retrieval, llm)
    try:
        if not check_existence_lesson(lession_id=payload.lesson_id, serie_id=payload.serie_id):
            logger.warning(f"Lesson ID {payload.lesson_id} with Serie ID {payload.serie_id} does not exist.")
            retrieval.upload_lesson(payload.user_id)
        res = await rag.answer(payload.dict())
        logger.info("Query processed successfully")
        return res
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
