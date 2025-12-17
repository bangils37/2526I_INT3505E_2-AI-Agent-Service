"""Client cho LMS Backend Service.

Module này cung cấp BackendClient để tương tác với các endpoint của LMS Backend,
bao gồm theo dõi thông tin người dùng hiện tại và health check.
"""

import logging
from typing import Optional

import httpx

from src.config.settings import get_settings
from src.models.response_models import UserTrackingResponse


logger = logging.getLogger(__name__)


class BackendClient:
    """Client HTTP async cho LMS Backend Service.
    
    Cập nhật thông tin theo dõi người dùng từ LMS Backend,
    bao gồm bài học hiện tại, khóa học và chi tiết dữ liệu.
    
    Attributes:
        base_url (str): URL cơ sở của LMS Backend service.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """Khởi tạo BackendClient.
        
        Args:
            base_url (Optional[str]): URL cơ sở của LMS Backend service.
                Nếu không cung cấp, sẽ lấy từ LMS_BACKEND_URL trong settings.
        """
        self.base_url = base_url or get_settings().LMS_BACKEND_URL
        logger.debug(f"Khởi tạo BackendClient với base_url: {self.base_url}")
    
    async def ping(self) -> bool:
        """Kiểm tra kết nối với LMS Backend service.
        
        Returns:
            bool: True nếu service sẵn sàng, False nếu không thể kết nối.
            
        Example:
            >>> client = BackendClient()
            >>> is_ready = await client.ping()
            >>> print(is_ready)  # True or False
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                is_healthy = response.status_code == 200
                logger.debug(f"LMS Backend health check: {is_healthy}")
                return is_healthy
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error(f"LMS Backend health check failed: {str(e)}")
            return False
    
    async def tracking_user(self, user_id: str) -> UserTrackingResponse:
        """Lấy thông tin theo dõi hiện tại của người dùng từ LMS Backend.
        
        Gọi endpoint GET /api/tracking/user/{user_id}/current để lấy
        thông tin bài học, khóa học, và chi tiết dữ liệu của người dùng.
        
        Args:
            user_id (str): ID của người dùng. Ví dụ: "09bab53c-00e1-705e-b547-ea3d1a5bc01b"
        
        Returns:
            UserTrackingResponse: Đối tượng chứa thông tin theo dõi người dùng bao gồm:
                - user_id: ID người dùng
                - lesson_id: ID bài học hiện tại
                - serie_id: ID khóa học
                - lesson_title: Tiêu đề bài học
                - last_updated: Thời gian cập nhật
                - is_in_lesson: Người dùng có đang trong bài học
                - lesson_data: Chi tiết dữ liệu bài học (video, transcript, tài liệu, etc.)
        
        Raises:
            httpx.HTTPStatusError: Khi API trả về lỗi HTTP (4xx, 5xx).
            httpx.RequestError: Khi không thể kết nối tới service.
            ValueError: Khi response không hợp lệ.
        
        Example:
            >>> client = BackendClient()
            >>> tracking = await client.tracking_user("09bab53c-00e1-705e-b547-ea3d1a5bc01b")
            >>> print(tracking.lesson_id)  # "693d70aaf318d0552e112242"
            >>> print(tracking.is_in_lesson)  # True
            >>> print(tracking.lesson_data.lesson_title)  # "Test 1312"
        """
        try:
            # Kết nối tới endpoint tracking của LMS Backend
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/api/tracking/user/{user_id}/current"
                logger.debug(f"Gọi endpoint theo dõi người dùng: {url}")
                
                # Thực hiện GET request
                response = await client.get(url)
                response.raise_for_status()
                
                # Parse JSON response và validate với Pydantic model
                data = response.json()
                logger.debug(f"Nhận được response từ backend: {data}")
                
                # Tạo UserTrackingResponse từ dữ liệu nhận được
                tracking = UserTrackingResponse(**data)
                logger.info(f"Lấy thông tin theo dõi cho người dùng {user_id}: bài học {tracking.lesson_id}")
                
                return tracking
                
        except httpx.HTTPStatusError as e:
            # Lỗi HTTP từ server (4xx, 5xx)
            logger.error(f"LMS Backend trả về lỗi HTTP {e.response.status_code}: {str(e)}")
            raise
        except httpx.RequestError as e:
            # Lỗi kết nối hoặc timeout
            logger.error(f"Lỗi kết nối tới LMS Backend: {str(e)}")
            raise
        except ValueError as e:
            # Lỗi parse hoặc validation
            logger.error(f"Lỗi validate response từ LMS Backend: {str(e)}")
            raise
        
        # Mock response để test chức năng
        # mock_data = {
        #     "user_id": "09bab53c-00e1-705e-b547-ea3d1a5bc01b",
        #     "lesson_id": "693d70aaf318d0552e112242",
        #     "serie_id": "693d708cf318d0552e112241",
        #     "lesson_title": None,
        #     "last_updated": "2025-12-15T14:39:54.662000",
        #     "is_in_lesson": True,
        #     "lesson_data": {
        #         "lesson_title": "Test 1312",
        #         "lesson_description": "Test 1312",
        #         "lesson_serie": "693d708cf318d0552e112241",
        #         "lesson_video": "https://edu-connect-s3.s3.ap-southeast-1.amazonaws.com/files/user-49aa257c-40a1-7054-70b6-f8f3375330d4/videos/ddac5fbe-61bf-40b6-b121-13e998fc840d_index%20(1).mp4",
        #         "lesson_transcript": "https://edu-connect-s3.s3.ap-southeast-1.amazonaws.com/files/user-49aa257c-40a1-7054-70b6-f8f3375330d4/transcripts/ddac5fbe-61bf-40b6-b121-13e998fc840d_index%20(1)_transcript.txt",
        #         "transcript_status": "completed",
        #         "lesson_documents": [],
        #         "createdAt": "2025-12-13T13:56:58.770000",
        #         "updatedAt": "2025-12-13T13:58:01.723000",
        #         "lesson_summary": "https://edu-connect-s3.s3.ap-southeast-1.amazonaws.com/files/user-49aa257c-40a1-7054-70b6-f8f3375330d4/summaries/ddac5fbe-61bf-40b6-b121-13e998fc840d_index%20(1)_summary.txt",
        #         "lesson_timeline": "https://edu-connect-s3.s3.ap-southeast-1.amazonaws.com/files/user-49aa257c-40a1-7054-70b6-f8f3375330d4/summaries/ddac5fbe-61bf-40b6-b121-13e998fc840d_index%20(1)_timeline.txt"
        #     }
        # }

        # return UserTrackingResponse(**mock_data)
