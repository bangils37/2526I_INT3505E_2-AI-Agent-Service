import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.llm_client import LLMClient

@pytest.fixture
def mock_gemini_model():
    with patch('src.services.llm_client.genai.GenerativeModel') as mock_genai_model:
        mock_instance = MagicMock()
        mock_genai_model.return_value = mock_instance
        mock_instance.generate_content.return_value = MagicMock(text="Gemini response")
        yield mock_instance

@pytest.mark.asyncio
async def test_llm_client_gemini_priority(mock_gemini_model):
    client = LLMClient(None, "", "test_gemini_key", "gemma-3-27b-it")
    response = client.generate("test question", ["context1", "context2"])
    assert response == "Gemini response"
    mock_gemini_model.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_llm_client_no_llm_fallback():
    client = LLMClient(None, "", None, "gemma-3-27b-it")
    response = client.generate("test question", ["context1", "context2"])
    assert "test question" in response
    assert "context1" in response
    assert "context2" in response

@pytest.mark.asyncio
async def test_llm_client_build_prompt():
    client = LLMClient(None, "", None, "")
    prompt = client._build_prompt("test question", ["context1", "context2"])
    assert "Trả lời dựa trên ngữ cảnh sau:" in prompt
    assert "context1" in prompt
    assert "context2" in prompt
    assert "Câu hỏi của học sinh: test question" in prompt
