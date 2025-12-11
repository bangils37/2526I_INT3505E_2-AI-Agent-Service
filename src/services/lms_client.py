from typing import Any, Dict, Optional
import httpx
import logging

logger = logging.getLogger(__name__)


class LMSClient:
    def __init__(self, base_url: Optional[str]):
        self.base_url = base_url.rstrip("/") if base_url else None
        self._client = httpx.AsyncClient(timeout=10)
        logger.info(f"LMSClient initialized with base_url: {self.base_url}")

    async def ping(self) -> bool:
        if not self.base_url:
            logger.warning("LMS backend URL not configured")
            return False
        try:
            r = await self._client.get(f"{self.base_url}/health")
            success = r.status_code < 500
            logger.debug(f"LMS ping status: {r.status_code}, success: {success}")
            return success
        except Exception as e:
            logger.error(f"LMS ping failed: {str(e)}")
            return False

    async def proxy(self, method: str, path: str, params: Dict[str, Any], body: Optional[Dict[str, Any]]) -> httpx.Response:
        if not self.base_url:
            logger.error("LMS backend URL is not configured")
            raise RuntimeError("LMS backend URL is not configured")
        url = f"{self.base_url}/{path.lstrip('/')}"
        logger.debug(f"Proxying {method} {url}")
        r = await self._client.request(method.upper(), url, params=params, json=body)
        logger.debug(f"Proxy response status: {r.status_code}")
        return r
