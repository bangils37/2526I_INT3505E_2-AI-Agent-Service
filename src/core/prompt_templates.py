import logging

logger = logging.getLogger(__name__)

def build_qa_prompt(question: str, contexts: list[str]) -> str:
    ctx = "\n\n".join(contexts)
    prompt = f"Trả lời dựa trên ngữ cảnh sau:\n{ctx}\n\nCâu hỏi: {question}"
    logger.debug(f"Built QA prompt with {len(contexts)} contexts")
    return prompt
