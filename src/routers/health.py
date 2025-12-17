from fastapi import APIRouter
import logging
from src.config.settings import get_settings
from src.services.retrieval_client import RetrievalClient
from src.services.lms_client import LMSClient

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("")
async def health():
    """Kiểm tra tình trạng của agent và các dịch vụ phụ thuộc.

    Kết quả truy vấn trạng thái của agent, Retrieval, LMS backend, 
    OpenAI API key và Gemini API key.

    Returns:
        Dict[str, Any]: Điều kiện chứa trạng thái agent, retrieval và dependencies.

    Example:
        >>> response = await health()
        >>> response["agent_status"]
        'ok'
    """
    logger.info("Health check started")
    s = get_settings()
    logger.info(f"Settings loaded: RETRIEVAL_SERVICE_URL={s.RETRIEVAL_SERVICE_URL}, LMS_BACKEND_URL={s.LMS_BACKEND_URL}")
    retrieval = RetrievalClient(s.RETRIEVAL_SERVICE_URL)
    lms = LMSClient(s.LMS_BACKEND_URL)
    agent_ok = True
    logger.info("Pinging retrieval service...")
    try:
        retrieval_ok = await retrieval.ping()
        logger.info(f"Retrieval ping result: {retrieval_ok}")
    except Exception as e:
        logger.error(f"Retrieval ping failed: {e}")
        retrieval_ok = False
    logger.info("Pinging LMS service...")
    try:
        lms_ok = await lms.ping()
        logger.info(f"LMS ping result: {lms_ok}")
    except Exception as e:
        logger.error(f"LMS ping failed: {e}")
        lms_ok = False
    openai_ok = bool(s.OPENAI_API_KEY)
    gemini_ok = bool(s.GEMINI_API_KEY)
    logger.info(f"OpenAI API key present: {openai_ok}, Gemini API key present: {gemini_ok}")
    response = {
        "agent_status": "ok" if agent_ok else "down",
        "retrieval_status": "ok" if retrieval_ok else "down",
        "dependencies": {
            "lms_backend": "ok" if lms_ok else "down",
            "openai": "ok" if openai_ok else "down",
            "gemini": "ok" if gemini_ok else "down",
        },
    }
    logger.info(f"Health check response: {response}")
    return response
