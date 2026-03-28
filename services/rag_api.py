import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)

API_BASE_URL = settings.rag_api_base_url

async def ingest_document(file_path: str, namespace: str):
    url = f"{API_BASE_URL.rstrip('/')}/ingest-pdf"
    async with httpx.AsyncClient(timeout=120.0) as client:
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"namespace": namespace}
            response = await client.post(url, files=files, data=data)
            response.raise_for_status()
            return response.json()

async def retrieve_chunks(query: str, namespace: str):
    url = f"{API_BASE_URL.rstrip('/')}/retrieve"
    async with httpx.AsyncClient(timeout=30.0) as client:
        params = {"query": query, "namespace": namespace}
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return "\n\n".join(str(item) for item in data)
            elif isinstance(data, dict):
                chunks = data.get("chunks") or data.get("documents") or data.get("results")
                if chunks:
                    return "\n\n".join(str(c) for c in chunks)
                return str(data)
            return str(data)
        except Exception as e:
            logger.error(f"Error querying retrieve API at {url}: {e}")
            return ""

