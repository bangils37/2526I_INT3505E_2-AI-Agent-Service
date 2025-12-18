FROM python:3.11-slim

WORKDIR /app

# Copy requirements từ thư mục con ra root để cài đặt
COPY retrieval_service/requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn của retrieval_service vào container
COPY retrieval_service ./retrieval_service

# Thiết lập PYTHONPATH để Python hiểu được module retrieval_service
ENV PYTHONPATH=/app

# Expose port 8001 (Port mặc định của Retrieval Service)
EXPOSE 8001

# Lệnh chạy ứng dụng
CMD ["uvicorn", "retrieval_service.src.app.main:app", "--host", "0.0.0.0", "--port", "8001"]