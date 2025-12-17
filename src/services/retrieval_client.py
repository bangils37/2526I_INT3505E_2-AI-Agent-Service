from typing import Any, Dict, Optional
import httpx
import logging
from src.config.settings import get_settings
from src.services.backend_client import BackendClient

logger = logging.getLogger(__name__)


class RetrievalClient:
    def __init__(self, base_url: Optional[str] = None):
        # Use provided base_url or fall back to settings.RETRIEVAL_SERVICE_URL
        if base_url:
            self.base_url = base_url.rstrip("/")
        else:
            settings = get_settings()
            self.base_url = settings.RETRIEVAL_SERVICE_URL.rstrip("/")
        self._client = httpx.AsyncClient(timeout=10)
        logger.info(f"RetrievalClient initialized with base_url: {self.base_url}")

    async def ping(self) -> bool:
        try:
            r = await self._client.get(self.base_url)
            success = r.status_code < 500
            logger.debug(f"Retrieval ping status: {r.status_code}, success: {success}")
            return success
        except Exception as e:
            logger.error(f"Retrieval ping failed: {str(e)}")
            return False

    async def search(self, collection: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Search a collection using the Retrieval service.

        Sends a POST request to ``/search/{collection}`` with a search request body and returns
        a SearchResponse-like dictionary.

        Args:
            collection (str): The collection to search (e.g. "lecture").
            body (Dict[str, Any]): Search request body with possible keys:
                q (str): User query string. Example: "Các triệu chứng của bệnh tiểu đường"
                filters (Optional[Dict[str, Any]]): Metadata filters. Example: {"category": "health"}
                k (int): Number of results to return. Default: 10.
                hybrid_weight (float): Weight between lexical and vector scoring (0.0-1.0).
                rerank (bool): Whether to perform reranking on top results.
                top_k_rerank (int): Number of top documents to rerank if ``rerank`` is True.

        Returns:
            Dict[str, Any]: A dict with keys:
                "query" (str): Original query string.
                "results" (List[Dict[str, Any]]): List of result objects. Each object includes
                    "doc_id", "chunk_id", "text", "score" and optional
                    "bm25_score", "vector_sim", "metadata", "provenance".
                "meta" (Dict[str, Any]): Additional metadata about the search.

        Raises:
            httpx.HTTPStatusError: If the remote returns a non-success HTTP status code.

        Example:
            >>> body = {
            ...     "q": "Các triệu chứng của bệnh tiểu đường",
            ...     "k": 5,
            ...     "hybrid_weight": 0.7,
            ...     "rerank": True,
            ...     "top_k_rerank": 3,
            ... }
            >>> await client.search("lecture", body)
        """
        url = f"{self.base_url}/search/{collection}"
        logger.debug(f"Searching collection {collection} with query: {body.get('q', '')[:50]}...")
        r = await self._client.post(url, json=body)
        r.raise_for_status()
        result = r.json()
        logger.debug(f"Search returned {len(result.get('results', []))} results")
        return result

    async def post_json(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        logger.debug(f"Posting to {url}")
        r = await self._client.post(url, json=json)
        r.raise_for_status()
        result = r.json()
        logger.debug("Post successful")
        return result

    async def upload_document(self, collection: str, document_id: str, file: Optional[bytes] = None, filename: Optional[str] = None, url_download: Optional[str] = None) -> Dict[str, Any]:
        """Upload or overwrite a document.

        Uploads a document to ``/documents/{collection}/{document_id}`` using a
        multipart/form-data PUT request. Either raw file bytes or a download URL
        must be provided.

        Args:
            collection (str): Collection name to store the document (e.g. "lecture").
            document_id (str): Identifier for the document.
            file (Optional[bytes]): Raw bytes of the file to upload. Either ``file`` or ``url_download`` must be provided.
            filename (Optional[str]): Optional filename to include in the multipart payload. Defaults to ``document_id`` when omitted.
            url_download (Optional[str]): Optional URL that the server should fetch to obtain the document.

        Returns:
            Dict[str, Any]: DocumentUploadResponse dict with keys ``success``, ``message``, ``document_id`` and ``collection``.

        Raises:
            ValueError: If neither ``file`` nor ``url_download`` is provided.
            httpx.HTTPStatusError: If the remote service returns an error status for the upload request.

        Example:
            >>> await client.upload_document("lecture", "doc_001", file=b"...", filename="doc_001.jsonl")
        """
        if not file and not url_download:
            raise ValueError("Must provide `file` or `url_download`")

        url = f"{self.base_url}/documents/{collection}/{document_id}"
        logger.debug(f"Uploading document {document_id} to collection {collection} (url: {url})")

        # Build multipart form fields. Use files for file upload and for url_download send as a form field.
        files = {}
        if file is not None:
            files['file'] = (filename or document_id, file)
        if url_download is not None:
            files['url_download'] = (None, url_download)

        r = await self._client.put(url, files=files if files else None)
        r.raise_for_status()
        result = r.json()
        logger.debug("Upload successful")
        return result

    async def check_exists_document(self, collection: str, document_id: str) -> Dict[str, Any]:
        """Check whether a document exists in a collection.

        Sends a GET request to ``/documents/{collection}/{document_id}`` and returns a
        structured response indicating presence.

        Args:
            collection (str): The collection to check (e.g. "lecture").
            document_id (str): The document id to check for existence.

        Returns:
            Dict[str, Any]: DocumentCheckResponse with keys ``exists`` (bool), ``document_id`` (str),
                and ``collection`` (str). If the server returns 404, the method returns
                {"exists": False, "document_id": ..., "collection": ...}.

        Raises:
            httpx.HTTPStatusError: For non-200 and non-404 HTTP responses from the service.

        Example:
            >>> await client.check_exists_document("lecture", "doc_001")  # -> {"exists": True, ...}
        """
        url = f"{self.base_url}/documents/{collection}/{document_id}"
        logger.debug(f"Checking existence of document {document_id} in collection {collection} (url: {url})")

        r = await self._client.get(url)
        # If the service explicitly says 200, return parsed JSON

        if r.status_code == 200:
            return r.json()
        # 404 means not found -> return exists: False
        if r.status_code == 404:
            logger.debug("Document not found (404)")
            return {"exists": False, "document_id": document_id, "collection": collection}

        # Other statuses should raise
        r.raise_for_status()
        return r.json()
    async def index_document(self, collection: str, document_id: str) -> Dict[str, Any]:
        """Trigger chunking and indexing for an uploaded document.

        Sends a POST request to ``/documents/{collection}/{document_id}/index`` to start
        server-side chunking/embedding/indexing for the given document.

        Args:
            collection (str): The collection containing the document.
            document_id (str): The document id to index.

        Returns:
            Dict[str, Any]: DocumentIndexResponse with keys such as ``success``, ``message``,
                ``document_id``, ``collection`` and optional ``logs`` (list of strings).

        Raises:
            httpx.HTTPStatusError: If the server returns an error status for the indexing request.

        Example:
            >>> await client.index_document("lecture", "doc_001")
        """
        url = f"{self.base_url}/documents/{collection}/{document_id}/index"
        logger.info(f"Triggering index for document {document_id} in collection {collection} (url: {url})")

        r = await self._client.post(url)
        # Let non-200 statuses raise via raise_for_status
        r.raise_for_status()
        result = r.json()
        logger.debug("Indexing request completed")
        return result

    async def upload_to_vector_db(self, collection: str, document_id: str, file: Optional[bytes] = None, filename: Optional[str] = None, url_download: Optional[str] = None) -> Dict[str, Any]:
        """Upload a document, verify its presence, and trigger indexing.

        Convenience flow that uploads a document, confirms it exists on the server,
        and then triggers indexing (chunking/embedding) for the document.

        Args:
            collection (str): The collection to upload into.
            document_id (str): The identifier to use for the uploaded document.
            file (Optional[bytes]): Optional file bytes to upload.
            filename (Optional[str]): Optional filename to include in the multipart form.
            url_download (Optional[str]): Optional URL for the service to download instead of sending raw file bytes.

        Returns:
            Dict[str, Any]: Dictionary containing results of each step:
                {
                    "upload": DocumentUploadResponse,
                    "exists": DocumentCheckResponse,
                    "index": DocumentIndexResponse
                }

        Raises:
            RuntimeError: If the document is not found after upload ("exists" is False).
            httpx.HTTPStatusError: Propagates any HTTP errors raised by the underlying requests.

        Example:
            >>> await client.upload_to_vector_db("lecture", "doc_001", file=b"...", filename="doc_001.jsonl")
        """
        # Upload (validations are performed in upload_document)
        upload_res = await self.upload_document(collection, document_id, file=file, filename=filename, url_download=url_download)

        # Verify upload: check existence
        exists_res = await self.check_exists_document(collection, document_id)
        if not exists_res.get("exists"):
            raise RuntimeError(f"Document {document_id} not found after upload")

        # Trigger indexing
        index_res = await self.index_document(collection, document_id)

        return {"upload": upload_res, "exists": exists_res, "index": index_res}
    
    async def upload_lesson(self, user_id: str):
        """Gọi hàm """
        
        
        await self.upload_to_vector_db(
            collection = "lecture",
            document_id = f"",
        )
    
    
def check_existence_lesson(lession_id: str, serie_id: str) -> bool:
    """Xem/Tạo lesson_tracking.json để kiểm tra sự tồn tại của serie_id, lesson_id trong hệ thống. 
    
    lesson_tracking.json theo cấu trúc {serie_id: [lesson_id, ...]}"""
    import json
    import os

    file_path = "lesson_tracking.json"
    if not os.path.exists(file_path):
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    lessons = data.get(serie_id, []) if serie_id else []
    return lession_id in lessons
    
def save_lesson(serie_id: str, lesson_id: str):
    """Lưu thông tin lesson_id vào trong file lesson_tracking.json theo cấu trúc {serie_id: [lesson_id, ...]}"""
    import json
    import os

    file_path = "lesson_tracking.json"
    data = {}

    # Nếu file đã tồn tại, đọc dữ liệu hiện có
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    # Cập nhật dữ liệu với lesson mới
    if serie_id not in data:
        data[serie_id] = []
    if lesson_id not in data[serie_id]:
        data[serie_id].append(lesson_id)

    # Ghi lại dữ liệu vào file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)