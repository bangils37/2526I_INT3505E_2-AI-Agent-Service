from fastapi import APIRouter, HTTPException
from src.config.settings import get_settings
from src.models.request_models import QueryRequest
from src.models.response_models import QueryResponse
from src.services.retrieval_client import RetrievalClient
from src.services.llm_client import LLMClient
from src.services.rag_service import RagService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest):
    logger.info(f"Received query request: {payload.user_question[:50]}...")
    s = get_settings()
    retrieval = RetrievalClient(s.RETRIEVAL_SERVICE_URL)
    llm = LLMClient(s.OPENAI_API_KEY, s.OPENAI_MODEL, s.GEMINI_API_KEY, s.GEMINI_MODEL)
    rag = RagService(retrieval, llm)
    try:
        res = await rag.answer(payload.dict())
        logger.info("Query processed successfully")
        return res
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
