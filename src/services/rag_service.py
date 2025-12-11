from typing import Dict, Any, List
from src.services.retrieval_client import RetrievalClient
from src.services.llm_client import LLMClient
from src.core.utils import course_collection
import logging

logger = logging.getLogger(__name__)


class RagService:
    def __init__(self, retrieval: RetrievalClient, llm: LLMClient):
        self.retrieval = retrieval
        self.llm = llm
        logger.info("RagService initialized")

    async def answer(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Generating answer using RAG service, processing payload:\n{payload}")
        
        question = payload["user_question"]
        course_id = int(payload["course_id"])
        top_k = int(payload.get("top_k", 5))
        collection = payload.get("collection") or "lecture"
        search_body = {"collection": collection, "q": question, "k": top_k}
        logger.info(f"Searching for question in collection: {collection}")
        res = await self.retrieval.search(collection, search_body)
        results = res.get("results", [])
        contexts: List[str] = [r.get("text", "") for r in results]
        logger.info(f"Retrieved {len(results)} results")
        answer = self.llm.generate(question, contexts)
        sources = [{"text": r.get("text", ""), "score": r.get("score", 0)} for r in results]
        meta = {"course_id": course_id, "session_id": payload.get("session_id")}
        logger.info("Answer generated successfully")
        return {"answer": answer, "sources": sources, "meta": meta}
