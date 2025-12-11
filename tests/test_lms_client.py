import pytest
from unittest.mock import AsyncMock, patch
from src.services.lms_client import LMSClient
import httpx

@pytest.fixture
def mock_httpx_async_client():
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.mark.asyncio
async def test_lms_client_ping_success(mock_httpx_async_client):
    mock_httpx_async_client.get.return_value = AsyncMock(status_code=200)
    client = LMSClient(base_url="http://test-lms")
    result = await client.ping()
    assert result is True
    mock_httpx_async_client.get.assert_called_once_with("http://test-lms/health")

@pytest.mark.asyncio
async def test_lms_client_ping_failure(mock_httpx_async_client):
    mock_httpx_async_client.get.side_effect = httpx.RequestError("Connection error", request=httpx.Request("GET", "http://test-lms/health"))
    client = LMSClient(base_url="http://test-lms")
    result = await client.ping()
    assert result is False

@pytest.mark.asyncio
async def test_lms_client_ping_unconfigured():
    client = LMSClient(base_url=None)
    result = await client.ping()
    assert result is False

@pytest.mark.asyncio
async def test_lms_client_proxy_success(mock_httpx_async_client):
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "proxied"}
    mock_httpx_async_client.request.return_value = mock_response

    client = LMSClient(base_url="http://test-lms")
    response = await client.proxy("GET", "/api/data", {"param": "value"}, None)
    assert response.status_code == 200
    assert response.json() == {"message": "proxied"}
    mock_httpx_async_client.request.assert_called_once_with("GET", "http://test-lms/api/data", params={'param': 'value'}, json=None)

@pytest.mark.asyncio
async def test_lms_client_proxy_unconfigured():
    client = LMSClient(base_url=None)
    with pytest.raises(RuntimeError, match="LMS backend URL is not configured"):
        await client.proxy("GET", "/api/data", {}, None)
