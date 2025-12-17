from typing import Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    """Model for query requests from clients.

    Attributes:
        user_question (str): The user's question.
        session_id (Optional[str]): Optional session identifier.
        user_id (str): ID of the user issuing the query.
        lesson_id (str): Identifier of the lesson the user refers to.
        serie_id (Optional[str]): Identifier of the course/series (if applicable).
        is_in_lesson (bool): Whether the user is currently inside the lesson context.
        top_k (int): Number of search results to retrieve.
        collection (Optional[str]): Optional explicit collection name override.
    """

    user_question: str = Field(..., description="Câu hỏi của người dùng", example="Các triệu chứng của bệnh tiểu đường")
    session_id: Optional[str] = Field(None, description="ID phiên làm việc (tùy chọn)", example="abc-123")
    user_id: str = Field(..., description="ID người dùng", example=123)
    lesson_id: str = Field(..., description="ID của bài học", example="lesson_123")
    serie_id: Optional[str] = Field(None, description="ID của khóa học/serie (nếu có)", example="serie_123")
    is_in_lesson: bool = Field(default=False, description="Người dùng có đang ở trong bài học hay không", example=True)
    top_k: int = Field(default=5, ge=1, le=50, description="Số kết quả tìm kiếm trả về", example=5)
    collection: Optional[str] = Field(None, description="Tên collection (nếu muốn ghi đè)", example="lecture")


class UploadForm(BaseModel):
    """Convenience schema for the upload form fields.

    Note: file uploads are handled as multipart files and are not part of this model.
    This model documents the optional form fields `filename` and `url_download`.

    Attributes:
        filename (Optional[str]): Optional filename to include in multipart payload.
        url_download (Optional[str]): Optional URL that the retrieval service should fetch.
    """

    filename: Optional[str] = Field(None, description="Optional filename for the upload", example="doc_001.jsonl")
    url_download: Optional[str] = Field(None, description="URL for the service to download the document", example="https://example.com/doc_001.jsonl")
