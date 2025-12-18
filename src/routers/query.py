from fastapi import APIRouter, HTTPException
from src.config.settings import get_settings
from src.models.request_models import QueryRequest
from src.models.response_models import QueryResponse
from src.services.retrieval_client import RetrievalClient, check_existence_lesson
from src.services.llm_client import LLMClient
from src.services.rag_service import RagService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest):
    """Xử lý câu hỏi người dùng và trả về câu trả lời kèm thông tin nguồn.

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
        # Only check lesson existence if:
        # 1. User is in a specific lesson (not general chat)
        # 2. AND frontend didn't provide lesson_data (if lesson_data exists, skip upload)
        if payload.lesson_id != "general_chat" and not payload.lesson_data:
            if not check_existence_lesson(lession_id=payload.lesson_id, serie_id=payload.serie_id):
                logger.warning(f"Lesson ID {payload.lesson_id} with Serie ID {payload.serie_id} does not exist.")
                await retrieval.upload_lesson(payload.user_id)
        elif payload.lesson_data:
            logger.info(f"Skipping lesson upload - using lesson_data from frontend payload")

        res = await rag.answer(payload.dict())
        logger.info("Query processed successfully")
        return res
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
