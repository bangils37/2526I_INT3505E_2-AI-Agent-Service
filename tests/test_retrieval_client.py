import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.retrieval_client import RetrievalClient
import httpx

@pytest.fixture
def mock_httpx_async_client():
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.mark.asyncio
async def test_retrieval_client_ping_success(mock_httpx_async_client):
    mock_httpx_async_client.get.return_value = AsyncMock(status_code=200)
    client = RetrievalClient(base_url="http://test-retrieval")
    result = await client.ping()
    assert result is True
    mock_httpx_async_client.get.assert_called_once_with("http://test-retrieval")

@pytest.mark.asyncio
async def test_retrieval_client_ping_failure(mock_httpx_async_client):
    mock_httpx_async_client.get.side_effect = httpx.RequestError("Connection error", request=httpx.Request("GET", "http://test-retrieval"))
    client = RetrievalClient(base_url="http://test-retrieval")
    result = await client.ping()
    assert result is False

@pytest.mark.asyncio
async def test_retrieval_client_search_success(mock_httpx_async_client):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value={"results": [{"text": "doc1"}]})
    mock_response.raise_for_status = MagicMock(return_value=None)
    mock_httpx_async_client.post.return_value = mock_response

    client = RetrievalClient(base_url="http://test-retrieval")
    response = await client.search("test_collection", {"q": "query"})
    assert response == {"results": [{"text": "doc1"}]}
    mock_httpx_async_client.post.assert_called_once_with("http://test-retrieval/search/test_collection", json={'q': 'query'})

@pytest.mark.asyncio
async def test_retrieval_client_post_json_success(mock_httpx_async_client):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value={"status": "ok"})
    mock_response.raise_for_status = MagicMock(return_value=None)
    mock_httpx_async_client.post.return_value = mock_response
    client = RetrievalClient(base_url="http://test-retrieval")
    response = await client.post_json("/path", {"data": "value"})
    assert response == {"status": "ok"}
    mock_httpx_async_client.post.assert_called_once_with("http://test-retrieval/path", json={'data': 'value'})