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
        return f"Bạn là một gia sư thân thiện. Phong cách trả lời:\n- Bỏ qua lời chào, đi thẳng vào nội dung\n-Lịch sự, thân thiện, ân cần\nTrả lời dựa trên ngữ cảnh sau:\n{ctx}\n\nCâu hỏi của học sinh: {question}"
