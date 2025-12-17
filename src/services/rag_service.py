from typing import Dict, Any, List
from src.services.retrieval_client import RetrievalClient
from src.services.llm_client import LLMClient
from src.core.utils import course_collection
import logging

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
        logger.info("RagService initialized - Sẵn sàng xử lý truy vấn RAG")
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
        lesson_id = payload["lesson_id"]  # ID bài học
        serie_id = payload.get("serie_id")  # ID khóa học (có thể None)
        is_in_lesson = bool(payload.get("is_in_lesson", False))  # Kiểm tra người dùng có đang trong bài học không
        top_k = int(payload.get("top_k", 5))  # Số lượng kết quả muốn lấy
        collection = payload.get("collection") or "lecture"  # Tên collection để tìm kiếm
        
        # === Bước 2: Xây dựng body tìm kiếm dựa vào ngữ cảnh ===
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
        contexts: List[str] = [r.get("text", "") for r in results]
        
        logger.info(f"Retrieved {len(results)} results - Tìm thấy {len(results)} kết quả")
        
        # === Bước 4: Tạo câu trả lời sử dụng LLM với các context vừa tìm được ===
        answer = self.llm.generate(question, contexts)
        
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
