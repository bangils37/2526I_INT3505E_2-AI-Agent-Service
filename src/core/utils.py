import logging

logger = logging.getLogger(__name__)

def course_collection(course_id: int) -> str:
    collection = f"course_{course_id}"
    logger.debug(f"Generated collection name: {collection}")
    return collection
