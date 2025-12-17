# AI Agent Service - API Documentation

## Overview

AI Agent Service là một dịch vụ RAG (Retrieval-Augmented Generation) được xây dựng trên FastAPI. Dịch vụ này kết hợp tìm kiếm vector, xử lý tài liệu và LLM để cung cấp câu trả lời chính xác và được tham chiếu từ các tài liệu.

**Base URL**: `http://localhost:8000`

---

## API Endpoints

### 1. Health Check

#### `GET /`

Kiểm tra tình trạng hoạt động của agent và các dịch vụ phụ thuộc.

**Description**: 
Truy vấn trạng thái của agent, Retrieval Service, LMS Backend, OpenAI API và Gemini API.

**Request Parameters**: None

**Response Model**: `HealthResponse`

```json
{
  "agent_status": "ok",
  "retrieval_status": "ok",
  "dependencies": {
    "lms_backend": "ok",
    "openai": "ok",
    "gemini": "ok"
  }
}
```

**Response Fields**:
- `agent_status` (string): Trạng thái của agent ("ok" hoặc "down")
- `retrieval_status` (string): Trạng thái Retrieval Service ("ok" hoặc "down")
- `dependencies` (object):
  - `lms_backend` (string): Trạng thái LMS Backend ("ok" hoặc "down")
  - `openai` (string): API key OpenAI có tồn tại hay không ("ok" hoặc "down")
  - `gemini` (string): API key Gemini có tồn tại hay không ("ok" hoặc "down")

**Example**:
```bash
curl -X GET "http://localhost:8000/"
```

**Success Response** (200 OK):
```json
{
  "agent_status": "ok",
  "retrieval_status": "ok",
  "dependencies": {
    "lms_backend": "ok",
    "openai": "ok",
    "gemini": "ok"
  }
}
```

---

### 2. Query Endpoint (RAG)

#### `POST /query`

Xử lý câu hỏi của người dùng và trả về câu trả lời kèm thông tin nguồn.

**Description**:
Sử dụng dịch vụ RAG để:
1. Tìm kiếm các đoạn văn bản liên quan từ Retrieval Service
2. Đưa dữ liệu vào LLM để tạo ra câu trả lời
3. Trả về kết quả cùng với thông tin nguồn (sources)

**Request Model**: `QueryRequest`

```json
{
  "user_question": "Các triệu chứng của bệnh tiểu đường",
  "session_id": "abc-123",
  "user_id": 123,
  "lesson_id": "lesson_123",
  "serie_id": "serie_123",
  "is_in_lesson": true,
  "top_k": 5,
  "collection": "lecture"
}
```

**Request Fields**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `user_question` | string | ✅ | Câu hỏi của người dùng | "Các triệu chứng của bệnh tiểu đường" |
| `session_id` | string | ❌ | ID phiên làm việc (tùy chọn) | "abc-123" |
| `user_id` | string | ✅ | ID người dùng | 123 |
| `lesson_id` | string | ✅ | ID của bài học hiện tại | "lesson_123" |
| `serie_id` | string | ❌ | ID của khóa học/serie | "serie_123" |
| `is_in_lesson` | boolean | ❌ | Người dùng có đang ở trong bài học hay không | true |
| `top_k` | integer | ❌ | Số related context được tìm kiếm (1-50, mặc định: 5) | 5 |
| `collection` | string | ❌ | Tên collection để ghi đè (nếu muốn) | "lecture" |

**Response Model**: `QueryResponse`

```json
{
  "answer": "Bệnh tiểu đường type 2 có các triệu chứng chính như: đặc biệt không có triệu chứng rõ ràng trong giai đoạn đầu, sau đó có thể xuất hiện khát nước nhiều, tiểu nhiều lần, mệt mỏi, tăng cân hoặc giảm cân bất thường.",
  "sources": [
    {
      "text": "Bệnh tiểu đường type 2 thường xuất hiện ở người lớn tuổi...",
      "score": 0.95
    },
    {
      "text": "Các triệu chứng bao gồm: khát nước, tiểu nhiều, mệt mỏi...",
      "score": 0.89
    }
  ],
  "meta": {
    "lesson_id": "lesson_123",
    "serie_id": "serie_123",
    "is_in_lesson": true,
    "session_id": "abc-123",
    "search_results_count": 5,
    "processing_time_ms": 234
  }
}
```

**Response Fields**:

- `answer` (string): Câu trả lời được tạo bởi LLM
- `sources` (array): Danh sách các nguồn tham chiếu
  - `text` (string): Nội dung đoạn trích
  - `score` (float): Điểm liên quan (0-1)
- `meta` (object): Metadata về truy vấn
  - `lesson_id` (string): ID bài học
  - `serie_id` (string): ID khóa học
  - `is_in_lesson` (boolean): Người dùng có đang trong bài học
  - `session_id` (string): ID phiên
  - `search_results_count` (integer): Số kết quả tìm kiếm
  - `processing_time_ms` (integer): Thời gian xử lý (miligiây)

**Example**:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_question": "Các triệu chứng của bệnh tiểu đường",
    "user_id": 123,
    "lesson_id": "lesson_123",
    "is_in_lesson": true,
    "top_k": 5
  }'
```

**Success Response** (200 OK):
```json
{
  "answer": "Bệnh tiểu đường type 2 có các triệu chứng chính...",
  "sources": [
    {
      "text": "Bệnh tiểu đường type 2 thường xuất hiện...",
      "score": 0.95
    }
  ],
  "meta": {
    "lesson_id": "lesson_123",
    "is_in_lesson": true
  }
}
```

**Error Responses**:
- **400 Bad Request**: Dữ liệu nhập không hợp lệ
- **500 Internal Server Error**: Lỗi xử lý câu hỏi

---

### 3. Document Upload (Chưa cần sử dụng)

#### `PUT /upload/{collection}/{document_id}`

Upload tài liệu, kiểm tra sự tồn tại và kích hoạt indexing.

**Description**:
Endpoint này chấp nhận một trong hai hình thức:
1. Upload một tệp tin (multipart file)
2. Cung cấp URL để dịch vụ Retrieval tự tải xuống

Sau khi upload thành công, endpoint sẽ:
1. Kiểm tra xem tài liệu có tồn tại trên server
2. Kích hoạt quá trình chunking/embedding/indexing

**URL Parameters**:

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `collection` | string | ✅ | Tên collection | "lecture" |
| `document_id` | string | ✅ | ID đăng ký cho tài liệu | "doc_001" |

**Form Data** (multipart/form-data):

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `file` | file | ❌ | Tệp tin upload | `document.pdf` |
| `url_download` | string | ❌ | URL để tải xuống | `https://example.com/doc.pdf` |
| `filename` | string | ❌ | Tên file (nếu upload URL) | `doc_001.pdf` |

**Response Model**: `UploadToVectorDBResponse`

```json
{
  "upload": {
    "success": true,
    "message": "Document uploaded successfully",
    "document_id": "doc_001",
    "collection": "lecture"
  },
  "exists": {
    "exists": true,
    "document_id": "doc_001",
    "collection": "lecture"
  },
  "index": {
    "success": true,
    "message": "Document indexed successfully",
    "document_id": "doc_001",
    "collection": "lecture",
    "logs": ["chunked 10 passages", "embedded 10 chunks", "indexed 10 documents"]
  }
}
```

**Response Fields**:

- `upload` (object): Kết quả upload
  - `success` (boolean): Có upload thành công không
  - `message` (string): Thông điệp mô tả
  - `document_id` (string): ID tài liệu
  - `collection` (string): Tên collection
  
- `exists` (object): Kết quả kiểm tra sự tồn tại
  - `exists` (boolean): Tài liệu có tồn tại không
  - `document_id` (string): ID tài liệu
  - `collection` (string): Tên collection
  
- `index` (object): Kết quả indexing
  - `success` (boolean): Có index thành công không
  - `message` (string): Thông điệp kết quả
  - `document_id` (string): ID tài liệu
  - `collection` (string): Tên collection
  - `logs` (array): Các log chi tiết từ pipeline indexing

**Example 1: Upload tệp tin**:
```bash
curl -X PUT "http://localhost:8000/upload/lecture/doc_001" \
  -F "file=@document.pdf"
```

**Example 2: Upload từ URL**:
```bash
curl -X PUT "http://localhost:8000/upload/lecture/doc_001" \
  -F "url_download=https://example.com/document.pdf" \
  -F "filename=document.pdf"
```

**Success Response** (200 OK):
```json
{
  "upload": {
    "success": true,
    "message": "Document uploaded successfully",
    "document_id": "doc_001",
    "collection": "lecture"
  },
  "exists": {
    "exists": true,
    "document_id": "doc_001",
    "collection": "lecture"
  },
  "index": {
    "success": true,
    "message": "Document indexed successfully",
    "document_id": "doc_001",
    "collection": "lecture",
    "logs": ["chunked 10 passages"]
  }
}
```

**Error Responses**:
- **400 Bad Request**: Cả file và url_download đều không được cung cấp
  ```json
  {
    "detail": "Either file or url_download must be provided"
  }
  ```
  
- **502 Bad Gateway**: Dịch vụ Retrieval gặp lỗi
  ```json
  {
    "detail": "Retrieval service error"
  }
  ```
  
- **500 Internal Server Error**: Lỗi bất ngờ
  ```json
  {
    "detail": "Error message"
  }
  ```

---

## Data Models

### QueryRequest

```python
{
  "user_question": str,          # Câu hỏi của người dùng (bắt buộc)
  "session_id": Optional[str],   # ID phiên (tùy chọn)
  "user_id": int,                # ID người dùng (bắt buộc)
  "lesson_id": str,              # ID bài học (bắt buộc)
  "serie_id": Optional[str],     # ID khóa học (tùy chọn)
  "is_in_lesson": bool,          # Đang trong bài học (mặc định: False)
  "top_k": int,                  # Số kết quả (1-50, mặc định: 5)
  "collection": Optional[str]    # Tên collection (tùy chọn)
}
```

### QueryResponse

```python
{
  "answer": str,                 # Câu trả lời
  "sources": [SourceItem],       # Danh sách nguồn
  "meta": Dict[str, Any]         # Metadata
}
```

### SourceItem

```python
{
  "text": str,                   # Nội dung đoạn trích
  "score": float                 # Điểm liên quan (0-1)
}
```

### SearchResult

```python
{
  "doc_id": str,                 # ID tài liệu
  "chunk_id": str,               # ID chunk
  "text": str,                   # Nội dung văn bản
  "score": float,                # Điểm tổng hợp
  "bm25_score": Optional[float], # BM25 score
  "vector_sim": Optional[float], # Vector similarity
  "metadata": Optional[Dict],    # Metadata
  "provenance": Optional[Dict]   # Provenance info
}
```

### UserTrackingResponse

```python
{
  "user_id": str,                      # ID người dùng
  "lesson_id": str,                    # ID bài học hiện tại
  "serie_id": str,                     # ID khóa học
  "lesson_title": Optional[str],       # Tiêu đề bài học
  "last_updated": str,                 # Thời gian cập nhật (ISO format)
  "is_in_lesson": bool,                # Đang trong bài học
  "lesson_data": Optional[LessonData]  # Chi tiết bài học
}
```

### LessonData

```python
{
  "lesson_title": str,                     # Tiêu đề bài học
  "lesson_description": str,               # Mô tả bài học
  "lesson_serie": str,                     # ID khóa học
  "lesson_video": Optional[str],           # URL video
  "lesson_transcript": Optional[str],      # URL transcript
  "transcript_status": Optional[str],      # Trạng thái transcript
  "lesson_documents": Optional[List],      # Danh sách tài liệu
  "lesson_summary": Optional[str],         # URL tóm tắt
  "lesson_timeline": Optional[str],        # URL timeline
  "createdAt": Optional[str],              # Thời gian tạo
  "updatedAt": Optional[str]               # Thời gian cập nhật
}
```

### UploadToVectorDBResponse

```python
{
  "upload": DocumentUploadResponse,   # Kết quả upload
  "exists": DocumentCheckResponse,    # Kết quả kiểm tra
  "index": DocumentIndexResponse      # Kết quả indexing
}
```

### DocumentUploadResponse

```python
{
  "success": bool,                    # Upload thành công
  "message": Optional[str],           # Thông điệp
  "document_id": str,                 # ID tài liệu
  "collection": str                   # Tên collection
}
```

### DocumentCheckResponse

```python
{
  "exists": bool,                     # Tài liệu tồn tại
  "document_id": str,                 # ID tài liệu
  "collection": str                   # Tên collection
}
```

### DocumentIndexResponse

```python
{
  "success": bool,                    # Index thành công
  "message": Optional[str],           # Thông điệp
  "document_id": str,                 # ID tài liệu
  "collection": str,                  # Tên collection
  "logs": Optional[List[str]]         # Log messages
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Yêu cầu thành công |
| 400 | Bad Request | Dữ liệu nhập không hợp lệ |
| 502 | Bad Gateway | Lỗi từ dịch vụ upstream |
| 500 | Internal Server Error | Lỗi máy chủ bất ngờ |

### Error Response Format

```json
{
  "detail": "Mô tả lỗi"
}
```

---

## Usage Examples

### Example 1: Basic Query

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_question": "Bệnh tiểu đường là gì?",
    "user_id": 1,
    "lesson_id": "lesson_001"
  }'
```

### Example 2: Query with Session Context

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_question": "Các triệu chứng?",
    "user_id": 1,
    "lesson_id": "lesson_001",
    "session_id": "session_123",
    "is_in_lesson": true,
    "top_k": 10
  }'
```

### Example 3: Health Check

```bash
curl -X GET "http://localhost:8000/"
```

### Example 4: Upload Document

```bash
# Upload từ tệp
curl -X PUT "http://localhost:8000/upload/lecture/doc_001" \
  -F "file=@document.pdf"

# Upload từ URL
curl -X PUT "http://localhost:8000/upload/lecture/doc_002" \
  -F "url_download=https://example.com/doc.pdf" \
  -F "filename=doc_002.pdf"
```

---

## Performance Notes

- **Timeout**: Mỗi HTTP request có timeout 10 giây
- **Search Results**: Mặc định trả về 5 kết quả, có thể chỉnh từ 1-50
- **Processing Time**: Thời gian xử lý truy vấn thường từ 200-500ms tùy vào độ phức tạp

---

## Development

**Framework**: FastAPI
**Language**: Python 3.8+
**Database**: Vector Database (Retrieval Service)
**LLM Integration**: OpenAI, Gemini

---

## Support

Để báo cáo lỗi hoặc đề xuất cải thiện, vui lòng liên hệ team phát triển.
