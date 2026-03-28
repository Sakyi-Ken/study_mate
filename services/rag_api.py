import httpx
import logging

logger = logging.getLogger(__name__)

API_BASE_URL = "https://upgraded-xylophone-v66gx6g755r5hx6xw-8000.app.github.dev"

async def ingest_document(file_path: str, namespace: str):
    url = f"{API_BASE_URL}/ingest"
    async with httpx.AsyncClient(timeout=120.0) as client:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = await client.post(url, files=files, params={"namespace": namespace})
            response.raise_for_status()
            return response.json()

async def retrieve_chunks(query: str, namespace: str):
    url = f"{API_BASE_URL}/retrieve"
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Assuming typical payload. Often "query" or "question" is used.
        payload = {"query": query, "namespace": namespace}
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return "\n\n".join(str(item) for item in data)
            elif isinstance(data, dict):
                chunks = data.get("chunks", data.get("documents", data.get("results", [str(data)])))
                return "\n\n".join(str(c) for c in chunks)
            return str(data)
        except Exception as e:
            logger.error(f"Error querying retrieve API: {e}")
            return ""

