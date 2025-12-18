from typing import Dict, Any, List, Optional
from src.services.retrieval_client import RetrievalClient
from src.services.llm_client import LLMClient
from src.services.backend_client import BackendClient
from src.core.utils import course_collection
import logging
import httpx

# Khởi tạo logger để ghi log các hoạt động của RagService
logger = logging.getLogger(__name__)


class RagService:
    """Dịch vụ RAG (Đóm Tập Hợp - Tạo Ra) cho trả lời câu hỏi.

    Kết hợp dịch vụ Retrieval (tìm kiếm đoạn văn bản liên quan) và
    LLM (tạo ra câu trả lời dựa trên các đoạn văn bản lấy được).

    Attributes:
        retrieval (RetrievalClient): Client để tìm kiếm văn bản.
        llm (LLMClient): Client để tạo ra câu trả lời.
    """

    def __init__(self, retrieval: RetrievalClient, llm: LLMClient):
        """Khởi tạo RagService.

        Args:
            retrieval (RetrievalClient): Client dịch vụ Retrieval.
            llm (LLMClient): Client dịch vụ LLM.
        """
        # Lưu reference đến client Retrieval để tìm kiếm tài liệu
        self.retrieval = retrieval
        # Lưu reference đến client LLM để tạo câu trả lời
        self.llm = llm
        # Lưu reference đến BackendClient để lấy lesson data
        self.backend = BackendClient()
        logger.info("RagService initialized - Sẵn sàng xử lý truy vấn RAG")

    async def _download_text_content(self, url: str) -> Optional[str]:
        """Download nội dung text từ URL (S3).

        Args:
            url (str): URL của file text (transcript, summary, timeline)

        Returns:
            Optional[str]: Nội dung text hoặc None nếu lỗi
        """
        if not url:
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                content = response.text
                logger.info(f"Downloaded {len(content)} chars from {url[:100]}...")
                return content
        except Exception as e:
            logger.error(f"Error downloading content from {url}: {str(e)}")
            return None

    async def answer(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Xử lý payload truy vấn và trả về câu trả lời kèm nguồn.

        1. Lấy câu hỏi và thông tin mã khóa từ payload.
        2. Tìm kiếm các đoạn văn bản liên quan.
        3. Đưa vào LLM để tạo câu trả lời.
        4. Trả về kết quả cùng metadata.

        Args:
            payload (Dict[str, Any]): Điều kiện chứa user_question, lesson_id, etc.

        Returns:
            Dict[str, Any]: Kết quả chứa answer, sources, và meta.

        Example:
            >>> payload = {"user_question": "...", "lesson_id": "...", ...}
            >>> result = await rag_service.answer(payload)
            >>> result["answer"]
            'Câu trả lời....'
        """
        logger.info(f"Generating answer using RAG service, processing payload:\n{payload}")

        # === Bước 1: Trích xuất thông tin từ payload ===
        question = payload["user_question"]  # Câu hỏi của người dùng
        user_id = payload.get("user_id", "guest_user")  # ID người dùng
        lesson_id = payload["lesson_id"]  # ID bài học
        serie_id = payload.get("serie_id")  # ID khóa học (có thể None)
        is_in_lesson = bool(payload.get("is_in_lesson", False))  # Kiểm tra người dùng có đang trong bài học không
        top_k = int(payload.get("top_k", 5))  # Số lượng kết quả muốn lấy
        collection = payload.get("collection") or "lecture"  # Tên collection để tìm kiếm

        # === Bước 1.5: Lấy lesson data (ưu tiên từ payload, nếu không có thì gọi backend) ===
        lesson_contexts: List[str] = []
        lesson_data_dict = payload.get("lesson_data")  # Frontend có thể truyền trực tiếp lesson_data

        if is_in_lesson:
            # Nếu frontend đã gửi lesson_data trong payload, sử dụng luôn
            if lesson_data_dict:
                logger.info(f"Nhận được lesson_data từ frontend payload")

                # Download và thêm transcript vào context
                transcript_url = lesson_data_dict.get("lesson_transcript")
                if transcript_url:
                    transcript_content = await self._download_text_content(transcript_url)
                    if transcript_content:
                        lesson_contexts.append(f"=== LESSON TRANSCRIPT ===\n{transcript_content}")
                        logger.info(f"Added transcript to context ({len(transcript_content)} chars)")

                # Download và thêm summary vào context
                summary_url = lesson_data_dict.get("lesson_summary")
                if summary_url:
                    summary_content = await self._download_text_content(summary_url)
                    if summary_content:
                        lesson_contexts.append(f"=== LESSON SUMMARY ===\n{summary_content}")
                        logger.info(f"Added summary to context ({len(summary_content)} chars)")

                # Download và thêm timeline vào context
                timeline_url = lesson_data_dict.get("lesson_timeline")
                if timeline_url:
                    timeline_content = await self._download_text_content(timeline_url)
                    if timeline_content:
                        lesson_contexts.append(f"=== LESSON TIMELINE ===\n{timeline_content}")
                        logger.info(f"Added timeline to context ({len(timeline_content)} chars)")

                # Thêm lesson metadata vào context
                lesson_title = lesson_data_dict.get("lesson_title", "N/A")
                lesson_description = lesson_data_dict.get("lesson_description", "N/A")
                lesson_info = f"=== LESSON INFO ===\nTitle: {lesson_title}\nDescription: {lesson_description}"
                lesson_contexts.append(lesson_info)
                logger.info(f"Added {len(lesson_contexts)} lesson contexts from frontend payload")

            # Nếu không có lesson_data trong payload, thử gọi backend (fallback)
            else:
                try:
                    logger.info(f"Không có lesson_data trong payload, thử lấy từ backend cho user {user_id}...")
                    tracking_info = await self.backend.tracking_user(user_id)

                    if tracking_info and hasattr(tracking_info, 'lesson_data') and tracking_info.lesson_data:
                        lesson_data = tracking_info.lesson_data
                        logger.info(f"Nhận được lesson_data từ backend: {lesson_data.lesson_title}")

                        # Download và thêm transcript vào context
                        if lesson_data.lesson_transcript:
                            transcript_content = await self._download_text_content(lesson_data.lesson_transcript)
                            if transcript_content:
                                lesson_contexts.append(f"=== LESSON TRANSCRIPT ===\n{transcript_content}")
                                logger.info(f"Added transcript to context ({len(transcript_content)} chars)")

                        # Download và thêm summary vào context
                        if lesson_data.lesson_summary:
                            summary_content = await self._download_text_content(lesson_data.lesson_summary)
                            if summary_content:
                                lesson_contexts.append(f"=== LESSON SUMMARY ===\n{summary_content}")
                                logger.info(f"Added summary to context ({len(summary_content)} chars)")

                        # Download và thêm timeline vào context
                        if lesson_data.lesson_timeline:
                            timeline_content = await self._download_text_content(lesson_data.lesson_timeline)
                            if timeline_content:
                                lesson_contexts.append(f"=== LESSON TIMELINE ===\n{timeline_content}")
                                logger.info(f"Added timeline to context ({len(timeline_content)} chars)")

                        # Thêm lesson metadata vào context
                        lesson_info = f"=== LESSON INFO ===\nTitle: {lesson_data.lesson_title}\nDescription: {lesson_data.lesson_description or 'N/A'}"
                        lesson_contexts.append(lesson_info)
                        logger.info(f"Added {len(lesson_contexts)} lesson contexts from backend")
                    else:
                        logger.warning(f"No lesson_data found from backend for user {user_id}")

                except Exception as e:
                    logger.error(f"Error fetching lesson data from backend: {str(e)}")
                    # Tiếp tục với flow bình thường nếu lỗi

        # === Bước 2: Xây dựng body tìm kiếm dựa vào ngữ cảnh ===
        retrieval_contexts: List[str] = []
        results = []

        # Nếu đã có lesson_data từ frontend, skip retrieval search để tiết kiệm
        if lesson_contexts:
            logger.info(f"Đã có {len(lesson_contexts)} lesson contexts từ frontend, skip retrieval search")
        else:
            # Chỉ gọi retrieval search khi KHÔNG có lesson_data
            try:
                # Nếu người dùng đang ở trong bài học, thêm filter để chỉ tìm kiếm trong bài học đó
                if is_in_lesson:
                    search_body = {
                        "collection": collection,
                        "q": question,
                        "k": top_k,
                        # Thêm filter để lọc kết quả chỉ trong bài học/khóa học hiện tại
                        "filter": {
                            "lesson_id": lesson_id,
                            "serie_id": serie_id
                        }
                    }
                else:
                    # Nếu không ở trong bài học, tìm kiếm từ toàn bộ collection
                    search_body = {
                        "collection": collection,
                        "q": question,
                        "k": top_k
                    }

                logger.info(f"Searching for question in collection: {collection}")

                # === Bước 3: Tìm kiếm tài liệu liên quan từ dịch vụ Retrieval ===
                res = await self.retrieval.search(collection, search_body)
                results = res.get("results", [])  # Lấy danh sách kết quả tìm kiếm
                # Trích xuất nội dung văn bản từ mỗi kết quả để làm context cho LLM
                retrieval_contexts = [r.get("text", "") for r in results]

                logger.info(f"Retrieved {len(results)} results - Tìm thấy {len(results)} kết quả")
            except Exception as e:
                logger.error(f"Retrieval search failed: {str(e)}, tiếp tục với lesson contexts")
                # Nếu retrieval fail, vẫn tiếp tục với lesson_contexts

        # === Bước 3.5: Merge lesson contexts với retrieval contexts ===
        # Lesson contexts được ưu tiên đầu tiên để LLM có thể sử dụng thông tin lesson trước
        all_contexts = lesson_contexts + retrieval_contexts
        logger.info(f"Total contexts for LLM: {len(all_contexts)} (lesson: {len(lesson_contexts)}, retrieval: {len(retrieval_contexts)})")

        # === Bước 4: Tạo câu trả lời sử dụng LLM với các context vừa tìm được ===
        answer = self.llm.generate(question, all_contexts)
        
        # === Bước 5: Chuẩn bị kết quả trả về ===
        # Tạo danh sách sources (các đoạn văn bản được sử dụng)
        sources = [{"text": r.get("text", ""), "score": r.get("score", 0)} for r in results]
        # Tạo metadata chứa thông tin ngữ cảnh của truy vấn
        meta = {
            "lesson_id": lesson_id,  # ID bài học
            "serie_id": serie_id,  # ID khóa học
            "is_in_lesson": is_in_lesson,  # Trạng thái người dùng
            "session_id": payload.get("session_id"),  # ID phiên làm việc
        }
        
        logger.info("Answer generated successfully - Câu trả lời đã được tạo thành công")
        
        # === Trả về kết quả cuối cùng ===
        return {"answer": answer, "sources": sources, "meta": meta}
