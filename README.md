# 2526I_INT3505E_2-AI-Agent-Service

Dịch vụ AI Agent sử dụng RAG (Retrieval-Augmented Generation) để trả lời câu hỏi dựa trên dữ liệu từ hệ thống LMS và các mô hình LLM như OpenAI và Gemini.

## Cài đặt và Chạy

### Sử dụng Virtual Environment (venv)

1. **Tạo virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Kích hoạt virtual environment:**
   - Trên Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Trên Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. **Cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Chạy ứng dụng:**
   ```bash
   uvicorn src.app:app --host 0.0.0.0 --port 8000
   ```

Ứng dụng sẽ chạy tại `http://localhost:8000`.

### Sử dụng Docker

1. **Xây dựng image:**
   ```bash
   docker build -t ai-agent-service .
   ```

2. **Chạy container:**
   ```bash
   docker run -p 8000:8000 ai-agent-service
   ```

Ứng dụng sẽ chạy tại `http://localhost:8000`.

## API Endpoints

### Health Check
- **GET** `/health`
  - Kiểm tra trạng thái của dịch vụ và các dependencies.
  - Response: JSON với trạng thái của agent, retrieval, LMS backend, OpenAI, và Gemini.

### Query
- **POST** `/query`
  - Gửi câu hỏi để nhận câu trả lời từ RAG service.
  - Request Body: JSON với trường `query` (string).
  - Response: JSON với trường `answer` (string).

## Dependencies

- fastapi==0.115.5
- uvicorn==0.32.0
- httpx==0.27.2
- pydantic==2.9.2
- pydantic-settings==2.6.0
- openai==1.54.0
- google-generativeai==0.8.3
- pytest==8.3.3
- pytest-asyncio==0.23.0

## Testing

Chạy tests với pytest:

```bash
pytest
```

## Cấu hình

Cấu hình được quản lý qua biến môi trường trong file `src/config/settings.py`. Các biến cần thiết bao gồm:
- `RETRIEVAL_SERVICE_URL`
- `LMS_BACKEND_URL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`