from typing import Any, Dict, List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class SourceItem(BaseModel):
    text: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    meta: Dict[str, Any]
