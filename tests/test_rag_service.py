import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.rag_service import RagService
from src.services.retrieval_client import RetrievalClient
from src.services.llm_client import LLMClient

@pytest.fixture
def mock_retrieval_client():
    mock = AsyncMock(spec=RetrievalClient)
    mock.search.return_value = {"results": [{"text": "context1", "score": 0.9}, {"text": "context2", "score": 0.8}]}
    return mock

@pytest.fixture
def mock_llm_client():
    mock = AsyncMock(spec=LLMClient)
    mock.generate.return_value = "Generated answer based on contexts."
    return mock

@pytest.mark.asyncio
async def test_rag_service_answer(mock_retrieval_client, mock_llm_client):
    rag_service = RagService(retrieval=mock_retrieval_client, llm=mock_llm_client)
    payload = {
        "user_question": "What is RAG?",
        "lesson_id": "lesson_123",
        "serie_id": "serie_456",
        "is_in_lesson": True,
        "top_k": 2,
        "session_id": "abc-123"
    }
    response = await rag_service.answer(payload)

    mock_retrieval_client.search.assert_called_once_with(
        "lecture",
        {"collection": "lecture", "q": "What is RAG?", "k": 2}
    )
    mock_llm_client.generate.assert_called_once_with(
        "What is RAG?",
        ["context1", "context2"]
    )

    assert response["answer"] == "Generated answer based on contexts."
    assert len(response["sources"]) == 2
    assert response["sources"][0]["text"] == "context1"
    assert response["sources"][0]["score"] == 0.9
    assert response["meta"] == {"lesson_id": "lesson_123", "serie_id": "serie_456", "is_in_lesson": True, "session_id": "abc-123"}

@pytest.mark.asyncio
async def test_rag_service_answer_no_results(mock_retrieval_client, mock_llm_client):
    mock_retrieval_client.search.return_value = {"results": []}
    mock_llm_client.generate.return_value = "No answer found."

    rag_service = RagService(retrieval=mock_retrieval_client, llm=mock_llm_client)
    payload = {
        "user_question": "Empty search?",
        "lesson_id": "lesson_456",
        "is_in_lesson": False,
        "top_k": 1
    }
    response = await rag_service.answer(payload)

    assert response["answer"] == "No answer found."
    assert len(response["sources"]) == 0
    assert response["meta"] == {"lesson_id": "lesson_456", "serie_id": None, "is_in_lesson": False, "session_id": None}
