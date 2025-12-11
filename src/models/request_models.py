from typing import Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    user_question: str
    session_id: Optional[str] = None
    user_id: int
    course_id: int
    video_id: int
    top_k: int = Field(default=5, ge=1, le=50)
    collection: Optional[str] = None
