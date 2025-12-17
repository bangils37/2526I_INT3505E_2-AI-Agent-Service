from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class SourceItem(BaseModel):
    """Simple source item used by `QueryResponse`.

    Attributes:
        text (str): Text of the source snippet.
        score (float): Relevance score for the snippet.
    """

    text: str = Field(..., description="Nội dung đoạn trích nguồn (snippet)", example="Một đoạn văn bản ngắn từ nguồn")
    score: float = Field(..., description="Điểm liên quan của đoạn trích", example=0.9)


class SearchResult(BaseModel):
    """Schema for a single search result (a chunk / passage).

    Attributes:
        doc_id (str): ID of the source document.
        chunk_id (str): ID of the chunk inside the document.
        text (str): Text content of the chunk.
        score (float): Combined ranking score (final ranking value).
        bm25_score (Optional[float]): BM25 score if available.
        vector_sim (Optional[float]): Vector similarity score if available.
        metadata (Optional[Dict[str, Any]]): Arbitrary metadata for the chunk/document.
        provenance (Optional[Dict[str, Any]]): Provenance / source tracing info.
    """

    doc_id: str = Field(..., description="ID của tài liệu nguồn", example="doc_001")
    chunk_id: str = Field(..., description="ID của chunk trong tài liệu", example="chunk_001_1")
    text: str = Field(..., description="Nội dung văn bản của chunk",
                      example="Bệnh tiểu đường type 2 thường xuất hiện ở người lớn tuổi...")
    score: float = Field(..., description="Điểm số tổng hợp (điểm xếp hạng cuối)", example=0.85)
    bm25_score: Optional[float] = Field(None, description="Điểm BM25 (nếu có)", example=0.72)
    vector_sim: Optional[float] = Field(None, description="Độ tương đồng vector (nếu có)", example=0.91)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata liên quan đến chunk/tài liệu",
                                             example={"category": "programming", "source": "tutorial"})
    provenance: Optional[Dict[str, Any]] = Field(None, description="Thông tin truy vết nguồn gốc (provenance)")


class SearchResponse(BaseModel):
    """Response schema for the Search API.

    Attributes:
        query (str): Original query string sent by the user.
        results (List[SearchResult]): List of search result objects.
        meta (Dict[str, Any]): Additional metadata about the search (e.g. timing, params).
    """

    query: str = Field(..., description="Câu truy vấn gốc mà người dùng gửi", example="Các triệu chứng của bệnh tiểu đường")
    results: List[SearchResult] = Field(..., description="Danh sách các kết quả tìm kiếm (mảng các SearchResult)")
    meta: Dict[str, Any] = Field(default_factory=dict,
                                 description="Metadata bổ sung về truy vấn (ví dụ: thời gian xử lý, tham số)",
                                 example={"took_ms": 12, "k": 5})


class DocumentUploadResponse(BaseModel):
    """Response returned by the retrieval service after uploading a document.

    Attributes:
        success (bool): True if upload succeeded.
        message (Optional[str]): Human-readable message.
        document_id (str): The uploaded document id.
        collection (str): The collection name.
    """

    success: bool = Field(..., description="True nếu upload thành công", example=True)
    message: Optional[str] = Field(None, description="Thông điệp mô tả (nếu có)", example="Document uploaded successfully")
    document_id: str = Field(..., description="ID tài liệu đã upload", example="doc_001")
    collection: str = Field(..., description="Tên collection chứa tài liệu", example="lecture")


class DocumentCheckResponse(BaseModel):
    """Response for document existence checks.

    Attributes:
        exists (bool): True if the document exists.
        document_id (str): The document id that was checked.
        collection (str): The collection name.
    """

    exists: bool = Field(..., description="True nếu tài liệu tồn tại", example=True)
    document_id: str = Field(..., description="ID tài liệu", example="doc_001")
    collection: str = Field(..., description="Tên collection", example="lecture")


class DocumentIndexResponse(BaseModel):
    """Response returned after triggering indexing for a document.

    Attributes:
        success (bool): True if indexing succeeded.
        message (Optional[str]): Optional result message.
        document_id (str): The indexed document id.
        collection (str): The collection name.
        logs (Optional[List[str]]): Optional log messages from the indexing pipeline.
    """

    success: bool = Field(..., description="True nếu indexing thành công", example=True)
    message: Optional[str] = Field(None, description="Thông điệp kết quả (nếu có)", example="Document indexed successfully")
    document_id: str = Field(..., description="ID tài liệu đã được index", example="doc_001")
    collection: str = Field(..., description="Tên collection", example="lecture")
    logs: Optional[List[str]] = Field(None, description="Các log chi tiết từ pipeline indexing", example=["chunked 10 passages"])


class UploadToVectorDBResponse(BaseModel):
    """Aggregate response for the upload-to-vector-db convenience flow.

    Attributes:
        upload (DocumentUploadResponse): Result of the upload step.
        exists (DocumentCheckResponse): Result of the existence check.
        index (DocumentIndexResponse): Result of the indexing step.
    """

    upload: DocumentUploadResponse
    exists: DocumentCheckResponse
    index: DocumentIndexResponse


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    meta: Dict[str, Any]


class LessonData(BaseModel):
    """Chi tiết dữ liệu bài học từ LMS Backend.
    
    Attributes:
        lesson_title (str): Tiêu đề bài học.
        lesson_description (str): Mô tả bài học.
        lesson_serie (str): ID khóa học chứa bài học này.
        lesson_video (Optional[str]): URL video bài học.
        lesson_transcript (Optional[str]): URL transcript (văn bản) của video.
        transcript_status (Optional[str]): Trạng thái transcript ("completed", "pending", etc.).
        lesson_documents (Optional[List[Any]]): Danh sách tài liệu liên quan.
        lesson_summary (Optional[str]): URL tóm tắt bài học.
        lesson_timeline (Optional[str]): URL timeline/mốc thời gian bài học.
        createdAt (Optional[str]): Thời gian tạo bài học.
        updatedAt (Optional[str]): Thời gian cập nhật gần nhất.
    """
    
    lesson_title: str = Field(..., description="Tiêu đề bài học", example="Test 1312")
    lesson_description: str = Field(..., description="Mô tả bài học", example="Test 1312")
    lesson_serie: str = Field(..., description="ID khóa học", example="693d708cf318d0552e112241")
    lesson_video: Optional[str] = Field(None, description="URL video bài học")
    lesson_transcript: Optional[str] = Field(None, description="URL transcript bài học")
    transcript_status: Optional[str] = Field(None, description="Trạng thái transcript", example="completed")
    lesson_documents: Optional[List[Any]] = Field(None, description="Danh sách tài liệu")
    lesson_summary: Optional[str] = Field(None, description="URL tóm tắt bài học")
    lesson_timeline: Optional[str] = Field(None, description="URL timeline bài học")
    createdAt: Optional[str] = Field(None, description="Thời gian tạo")
    updatedAt: Optional[str] = Field(None, description="Thời gian cập nhật")


class UserTrackingResponse(BaseModel):
    """Response từ endpoint tracking của LMS Backend.
    
    Chứa thông tin theo dõi hiện tại của người dùng bao gồm bài học hiện tại,
    khóa học, trạng thái và chi tiết dữ liệu bài học.
    
    Attributes:
        user_id (str): ID người dùng.
        lesson_id (str): ID bài học hiện tại.
        serie_id (str): ID khóa học hiện tại.
        lesson_title (Optional[str]): Tiêu đề bài học.
        last_updated (str): Thời gian cập nhật thông tin theo dõi gần nhất.
        is_in_lesson (bool): Người dùng có đang trong bài học hay không.
        lesson_data (Optional[LessonData]): Chi tiết dữ liệu bài học.
    """
    
    user_id: str = Field(..., description="ID người dùng", example="09bab53c-00e1-705e-b547-ea3d1a5bc01b")
    lesson_id: str = Field(..., description="ID bài học hiện tại", example="693d70aaf318d0552e112242")
    serie_id: str = Field(..., description="ID khóa học hiện tại", example="693d708cf318d0552e112241")
    lesson_title: Optional[str] = Field(None, description="Tiêu đề bài học")
    last_updated: str = Field(..., description="Thời gian cập nhật gần nhất", example="2025-12-15T14:39:54.662000")
    is_in_lesson: bool = Field(..., description="Người dùng có đang trong bài học", example=True)
    lesson_data: Optional[LessonData] = Field(None, description="Chi tiết dữ liệu bài học")

