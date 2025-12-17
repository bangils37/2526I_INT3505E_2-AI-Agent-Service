from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Any, Dict, Optional
import httpx
import logging
from src.config.settings import get_settings
from src.services.retrieval_client import RetrievalClient
from src.models.response_models import UploadToVectorDBResponse
from src.models.request_models import UploadForm

router = APIRouter()
logger = logging.getLogger(__name__)


@router.put("/upload/{collection}/{document_id}", response_model=UploadToVectorDBResponse)
async def upload_document(
	collection: str,
	document_id: str,
	file: Optional[UploadFile] = File(None),
	url_download: Optional[str] = Form(None),
	filename: Optional[str] = Form(None),
) -> UploadToVectorDBResponse:
	"""Upload tài liệu, kiểm tra sự tồn tại và kích hoạt indexing.

	Endpoint này chấp nhận một trong hai hình thức:
	1. Upload một tệp tin (multipart file).
	2. Cung cấp URL để dịch vụ Retrieval tự tải xuống.

	Sau khi upload thành công, endpoint sẽ kiểm tra xem tài liệu có tồn tại 
	trên server và kích hoạt quá trình chunking/embedding/indexing.

	Args:
		collection (str): Tên collection (ví dụ: "lecture").
		document_id (str): ID đăng ký cho tài liệu.
		file (Optional[UploadFile]): Tệp tin upload bởi client.
		url_download (Optional[str]): URL để dịch vụ tải xuống tài liệu.
		filename (Optional[str]): Tên file để gửi cùng multipart.

	Returns:
		UploadToVectorDBResponse: Kết quả upload, exists, và index.

	Raises:
		HTTPException 400: Nếu cả file và url_download đều không có.
		HTTPException 502: Nếu dịch vụ Retrieval gặp lỗi.
		HTTPException 500: Nếu có lỗi bất ngờ.
	"""

	s = get_settings()
	client = RetrievalClient(s.RETRIEVAL_SERVICE_URL)

	try:
		file_bytes = None
		final_filename = filename
		if file is not None:
			file_bytes = await file.read()
			final_filename = final_filename or file.filename

		result = await client.upload_document_full_flow(
			collection, document_id, file=file_bytes, filename=final_filename, url_download=url_download
		)

		logger.info(f"Document {document_id} uploaded to collection {collection}")
		return result

	except ValueError as e:
		logger.error(f"Validation error on upload: {e}")
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
	except httpx.HTTPStatusError as e:
		# Propagate upstream service errors as 502 Bad Gateway
		logger.error(f"Retrieval service error during upload: {e.response.status_code} - {e.response.text}")
		raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Retrieval service error")
	except Exception as e:
		logger.exception("Unexpected error while uploading document")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

