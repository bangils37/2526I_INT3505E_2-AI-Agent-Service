from typing import List, Optional
import google.generativeai as genai
import openai
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, openai_api_key: Optional[str], openai_model: str, gemini_api_key: Optional[str], gemini_model: str):
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self.gemini_api_key = gemini_api_key
        self.gemini_model = gemini_model
        self._openai_configured = bool(openai_api_key)
        self._gemini_configured = bool(gemini_api_key)
        if self._gemini_configured:
            genai.configure(api_key=gemini_api_key)
            logger.info("Gemini API configured")
        else:
            logger.warning("Gemini API key not provided")
        if self._openai_configured:
            logger.info("OpenAI API configured")
        else:
            logger.warning("OpenAI API key not provided")

    def generate(self, question: str, contexts: List[str]) -> str:
        logger.debug(f"Generating response for question: {question[:50]}...")
        if self._gemini_configured:
            prompt = self._build_prompt(question, contexts)
            model = genai.GenerativeModel(self.gemini_model)
            r = model.generate_content(prompt)
            response = getattr(r, "text", "") or str(getattr(r, "candidates", "")) or ""
            logger.info("Generated response using Gemini")
            return response
        elif self._openai_configured:
            prompt = self._build_prompt(question, contexts)
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.choices[0].message.content
            logger.info("Generated response using OpenAI")
            return answer
        else:
            merged = "\n".join(contexts)
            response = f"{merged}\n{question}"
            logger.info("Generated fallback response")
            return response

    def _build_prompt(self, question: str, contexts: List[str]) -> str:
        ctx = "\n\n".join(contexts)
        return f"""Bạn là một gia sư thân thiện.
    Trả lời học sinh dựa trên thông tin sau:\n
    {ctx}\n\n
    Câu hỏi của học sinh: 
    {question}\n\n
    Phong cách trả lời:\n
    - Lịch sự, thân thiện, ân cần\n
    - Trả lời ngắn gọn, súc tích, dễ hiểu\n
    - Sử dụng ví dụ minh họa khi cần thiết\n
    - Giữ nguyên dạng Tiếng Anh của các từ vựng chuyên ngành nếu nó giúp dễ hiểu hơn\n
    - Nếu không biết câu trả lời, hãy thừa nhận rằng bạn không biết\n\n
    - Không nhắc đến nguồn thông tin ban đầu\n\n
    """
