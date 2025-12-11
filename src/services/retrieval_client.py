from typing import Any, Dict, Optional
import httpx
import logging

logger = logging.getLogger(__name__)


class RetrievalClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
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
