"""Test cases for RetrievalClient.upload_lesson() và make_jsonl_from_lesson()."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from io import BytesIO

from src.services.retrieval_client import RetrievalClient
from src.models.response_models import UserTrackingResponse, LessonData


# Mock data - UserTrackingResponse từ LMS Backend
MOCK_CURRENT_TRACKING = {
    "user_id": "09bab53c-00e1-705e-b547-ea3d1a5bc01b",
    "lesson_id": "693d70aaf318d0552e112242",
    "serie_id": "693d708cf318d0552e112241",
    "lesson_title": None,
    "last_updated": "2025-12-15T14:39:54.662000",
    "is_in_lesson": True,
    "lesson_data": {
        "lesson_title": "Test 1312",
        "lesson_description": "Test 1312",
        "lesson_serie": "693d708cf318d0552e112241",
        "lesson_video": "https://edu-connect-s3.s3.ap-southeast-1.amazonaws.com/files/user-49aa257c-40a1-7054-70b6-f8f3375330d4/videos/ddac5fbe-61bf-40b6-b121-13e998fc840d_index (1).mp4",
        "lesson_transcript": "https://edu-connect-s3.s3.ap-southeast-1.amazonaws.com/files/user-49aa257c-40a1-7054-70b6-f8f3375330d4/transcripts/ddac5fbe-61bf-40b6-b121-13e998fc840d_index (1)_transcript.txt",
        "transcript_status": "completed",
        "lesson_documents": [],
        "createdAt": "2025-12-13T13:56:58.770000",
        "updatedAt": "2025-12-13T13:58:01.723000",
        "lesson_summary": "https://edu-connect-s3.s3.ap-southeast-1.amazonaws.com/files/user-49aa257c-40a1-7054-70b6-f8f3375330d4/summaries/ddac5fbe-61bf-40b6-b121-13e998fc840d_index (1)_summary.txt",
        "lesson_timeline": "https://edu-connect-s3.s3.ap-southeast-1.amazonaws.com/files/user-49aa257c-40a1-7054-70b6-f8f3375330d4/summaries/ddac5fbe-61bf-40b6-b121-13e998fc840d_index (1)_timeline.txt"
    }
}

MOCK_TRANSCRIPT_TEXT = """Bài học này giới thiệu về các khái niệm cơ bản.
Nội dung bao gồm các ví dụ thực tế.
Học viên sẽ nắm vững các kỹ năng cần thiết."""

MOCK_LESSON_SUMMARY = """Tóm tắt: Bài học này cung cấp kiến thức nền tảng về chủ đề.
- Điểm 1: Khái niệm A
- Điểm 2: Khái niệm B
- Điểm 3: Ứng dụng thực tế"""


@pytest.fixture
def mock_backend_client():
    """Tạo mock BackendClient."""
    return MagicMock()


@pytest.fixture
def mock_httpx_client():
    """Tạo mock httpx.AsyncClient."""
    return AsyncMock()


@pytest.fixture
def retrieval_client(mock_backend_client):
    """Tạo RetrievalClient với mock BackendClient."""
    client = RetrievalClient(base_url="http://localhost:8010")
    client._backend = mock_backend_client
    return client


@pytest.mark.asyncio
async def test_make_jsonl_from_lesson_success(retrieval_client, mock_backend_client):
    """Test make_jsonl_from_lesson() tạo file JSONL đúng định dạng."""
    
    # Tạo UserTrackingResponse từ mock data
    tracking = UserTrackingResponse(**MOCK_CURRENT_TRACKING)
    lesson_data = tracking.lesson_data
    lesson_id = tracking.lesson_id
    
    # Mock httpx.AsyncClient để trả về transcript và summary
    with patch("src.services.retrieval_client.httpx.AsyncClient") as mock_httpx:
        mock_client_instance = AsyncMock()
        mock_httpx.return_value.__aenter__.return_value = mock_client_instance
        
        # Mock GET requests
        async def mock_get(url):
            response = AsyncMock()
            response.raise_for_status = MagicMock()  # Ensure raise_for_status exists
            if "transcript" in url:
                response.text = MOCK_TRANSCRIPT_TEXT
            elif "summary" in url:
                response.text = MOCK_LESSON_SUMMARY
            else:
                response.text = ""
            return response
        
        mock_client_instance.get = mock_get
        
        # Gọi hàm
        jsonl_bytes = await retrieval_client.make_jsonl_from_lesson(lesson_data, lesson_id)
        
        # Kiểm tra kết quả
        assert isinstance(jsonl_bytes, bytes), "Kết quả phải là bytes"
        
        # Parse lại JSON để verify structure
        jsonl_line = json.loads(jsonl_bytes.decode("utf-8").strip())
        
        # Verify các trường bắt buộc
        assert jsonl_line["doc_id"] == lesson_id
        assert jsonl_line["serie_id"] == lesson_data.lesson_serie
        assert jsonl_line["lesson_id"] == lesson_id
        assert jsonl_line["title"] == "Test 1312"
        assert jsonl_line["author"] is None
        assert jsonl_line["data"] == "2025-12-13T13:58:01.723000"
        
        # Verify content chứa title và transcript
        assert "# Test 1312" in jsonl_line["content"]
        assert "Bài học này giới thiệu" in jsonl_line["content"]


@pytest.mark.asyncio
async def test_make_jsonl_from_lesson_no_transcript_url(retrieval_client):
    """Test make_jsonl_from_lesson() khi không có transcript URL."""
    
    # Tạo UserTrackingResponse
    tracking = UserTrackingResponse(**MOCK_CURRENT_TRACKING)
    lesson_data = tracking.lesson_data
    lesson_data.lesson_transcript = None  # Xóa transcript URL
    lesson_id = tracking.lesson_id
    
    # Mock httpx.AsyncClient
    with patch("src.services.retrieval_client.httpx.AsyncClient") as mock_httpx:
        # Gọi hàm
        jsonl_bytes = await retrieval_client.make_jsonl_from_lesson(lesson_data, lesson_id)
        
        # Kiểm tra kết quả
        assert isinstance(jsonl_bytes, bytes)
        jsonl_line = json.loads(jsonl_bytes.decode("utf-8").strip())
        
        # Transcript phải empty
        assert "Bài học này giới thiệu" not in jsonl_line["content"]


@pytest.mark.asyncio
async def test_make_jsonl_from_lesson_transcript_fetch_error(retrieval_client):
    """Test make_jsonl_from_lesson() khi tải transcript bị lỗi."""
    
    # Tạo UserTrackingResponse
    tracking = UserTrackingResponse(**MOCK_CURRENT_TRACKING)
    lesson_data = tracking.lesson_data
    lesson_id = tracking.lesson_id
    
    # Mock httpx.AsyncClient để raise error
    with patch("src.services.retrieval_client.httpx.AsyncClient") as mock_httpx:
        mock_client_instance = AsyncMock()
        mock_httpx.return_value.__aenter__.return_value = mock_client_instance
        
        # Mock GET request để raise error
        mock_client_instance.get.side_effect = Exception("Network error")
        
        # Gọi hàm - không nên raise, chỉ log warning
        jsonl_bytes = await retrieval_client.make_jsonl_from_lesson(lesson_data, lesson_id)
        
        # Kiểm tra kết quả - phải vẫn return bytes
        assert isinstance(jsonl_bytes, bytes)
        jsonl_line = json.loads(jsonl_bytes.decode("utf-8").strip())
        
        # Content phải có title và summary, nhưng không có transcript
        assert "# Test 1312" in jsonl_line["content"]


@pytest.mark.asyncio
async def test_upload_lesson_success(retrieval_client, mock_backend_client):
    """Test upload_lesson() hoàn toàn thành công."""
    
    # Tạo UserTrackingResponse
    tracking = UserTrackingResponse(**MOCK_CURRENT_TRACKING)
    
    # Mock BackendClient.tracking_user()
    mock_backend_client.tracking_user = AsyncMock(return_value=tracking)
    
    # Mock RetrievalClient.upload_to_vector_db()
    mock_upload_result = {
        "upload": {"success": True, "message": "Uploaded", "document_id": tracking.lesson_id, "collection": "lecture"},
        "exists": {"exists": True, "document_id": tracking.lesson_id, "collection": "lecture"},
        "index": {"success": True, "message": "Indexed", "document_id": tracking.lesson_id, "collection": "lecture", "logs": []}
    }
    retrieval_client.upload_to_vector_db = AsyncMock(return_value=mock_upload_result)
    
    # Mock httpx.AsyncClient để tải transcript
    with patch("src.services.retrieval_client.httpx.AsyncClient") as mock_httpx:
        mock_client_instance = AsyncMock()
        mock_httpx.return_value.__aenter__.return_value = mock_client_instance
        
        async def mock_get(url):
            response = AsyncMock()
            response.raise_for_status = MagicMock()
            response.text = MOCK_TRANSCRIPT_TEXT
            return response
        
        mock_client_instance.get = mock_get
        
        # Gọi hàm
        user_id = "09bab53c-00e1-705e-b547-ea3d1a5bc01b"
        await retrieval_client.upload_lesson(user_id)
        
        # Verify BackendClient.tracking_user() được gọi
        mock_backend_client.tracking_user.assert_called_once_with(user_id)
        
        # Verify upload_to_vector_db() được gọi với parameters đúng
        retrieval_client.upload_to_vector_db.assert_called_once()
        call_kwargs = retrieval_client.upload_to_vector_db.call_args[1]
        
        assert call_kwargs["collection"] == "lecture"
        assert call_kwargs["document_id"] == tracking.lesson_id
        assert call_kwargs["filename"] == f"{tracking.lesson_id}.jsonl"
        assert isinstance(call_kwargs["file"], bytes)


@pytest.mark.asyncio
async def test_upload_lesson_no_lesson_data(retrieval_client, mock_backend_client):
    """Test upload_lesson() khi không có lesson_data."""
    
    # Tạo UserTrackingResponse nhưng set lesson_data = None
    tracking_data = MOCK_CURRENT_TRACKING.copy()
    tracking_data["lesson_data"] = None
    tracking = UserTrackingResponse(**tracking_data)
    
    # Mock BackendClient.tracking_user()
    mock_backend_client.tracking_user = AsyncMock(return_value=tracking)
    
    # Gọi hàm - phải raise ValueError
    user_id = "09bab53c-00e1-705e-b547-ea3d1a5bc01b"
    
    with pytest.raises(ValueError, match="No lesson data available"):
        await retrieval_client.upload_lesson(user_id)


@pytest.mark.asyncio
async def test_upload_lesson_backend_error(retrieval_client, mock_backend_client):
    """Test upload_lesson() khi BackendClient.tracking_user() bị lỗi."""
    
    # Mock BackendClient.tracking_user() để raise error
    mock_backend_client.tracking_user = AsyncMock(side_effect=Exception("Backend service error"))
    
    # Gọi hàm - phải raise exception
    user_id = "09bab53c-00e1-705e-b547-ea3d1a5bc01b"
    
    with pytest.raises(Exception, match="Backend service error"):
        await retrieval_client.upload_lesson(user_id)


@pytest.mark.asyncio
async def test_upload_lesson_upload_to_vector_db_error(retrieval_client, mock_backend_client):
    """Test upload_lesson() khi upload_to_vector_db() bị lỗi."""
    
    # Tạo UserTrackingResponse
    tracking = UserTrackingResponse(**MOCK_CURRENT_TRACKING)
    
    # Mock BackendClient.tracking_user()
    mock_backend_client.tracking_user = AsyncMock(return_value=tracking)
    
    # Mock upload_to_vector_db() để raise error
    retrieval_client.upload_to_vector_db = AsyncMock(side_effect=RuntimeError("Upload failed"))
    
    # Mock httpx.AsyncClient
    with patch("src.services.retrieval_client.httpx.AsyncClient") as mock_httpx:
        mock_client_instance = AsyncMock()
        mock_httpx.return_value.__aenter__.return_value = mock_client_instance
        
        async def mock_get(url):
            response = AsyncMock()
            response.text = MOCK_TRANSCRIPT_TEXT
            return response
        
        mock_client_instance.get = mock_get
        
        # Gọi hàm - phải raise exception
        user_id = "09bab53c-00e1-705e-b547-ea3d1a5bc01b"
        
        with pytest.raises(RuntimeError, match="Upload failed"):
            await retrieval_client.upload_lesson(user_id)


@pytest.mark.asyncio
async def test_jsonl_format_complete():
    """Test định dạng JSONL đầy đủ với tất cả fields."""
    
    # Tạo UserTrackingResponse
    tracking = UserTrackingResponse(**MOCK_CURRENT_TRACKING)
    lesson_data = tracking.lesson_data
    lesson_id = tracking.lesson_id
    
    # Tạo RetrievalClient
    client = RetrievalClient(base_url="http://localhost:8010")
    
    # Mock httpx.AsyncClient
    with patch("src.services.retrieval_client.httpx.AsyncClient") as mock_httpx:
        mock_client_instance = AsyncMock()
        mock_httpx.return_value.__aenter__.return_value = mock_client_instance
        
        call_count = [0]
        
        async def mock_get(url):
            call_count[0] += 1
            response = AsyncMock()
            if "transcript" in url:
                response.text = MOCK_TRANSCRIPT_TEXT
            elif "summary" in url:
                response.text = MOCK_LESSON_SUMMARY
            return response
        
        mock_client_instance.get = mock_get
        
        # Gọi hàm
        jsonl_bytes = await client.make_jsonl_from_lesson(lesson_data, lesson_id)
        
        # Parse JSON
        jsonl_line = json.loads(jsonl_bytes.decode("utf-8").strip())
        
        # Verify tất cả fields
        expected_fields = ["doc_id", "serie_id", "lesson_id", "title", "content", "author", "data"]
        for field in expected_fields:
            assert field in jsonl_line, f"Field '{field}' không có trong JSONL"
        
        # Verify kiểu dữ liệu
        assert isinstance(jsonl_line["doc_id"], str)
        assert isinstance(jsonl_line["serie_id"], str)
        assert isinstance(jsonl_line["lesson_id"], str)
        assert isinstance(jsonl_line["title"], str)
        assert isinstance(jsonl_line["content"], str)
        assert jsonl_line["author"] is None
        assert isinstance(jsonl_line["data"], str)
        
        # Verify content length > 0
        assert len(jsonl_line["content"]) > 0
        
        print(f"✅ JSONL format test passed!")
        print(f"JSONL output:\n{json.dumps(jsonl_line, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
