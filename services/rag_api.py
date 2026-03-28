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
            logger.info(f"RAG retrieve response for namespace '{namespace}': {data}")
            
            chunks_text = ""
            if isinstance(data, list):
                # Extract text content from each chunk if it's a dict
                extracted = []
                for item in data:
                    if isinstance(item, dict):
                        # Try common text fields
                        text = item.get("text") or item.get("content") or item.get("page_content") or item.get("chunk")
                        if text:
                            extracted.append(str(text))
                        else:
                            extracted.append(str(item))
                    else:
                        extracted.append(str(item))
                chunks_text = "\n\n".join(extracted)
            elif isinstance(data, dict):
                chunks = data.get("chunks") or data.get("documents") or data.get("results") or data.get("matches")
                if chunks and isinstance(chunks, list):
                    extracted = []
                    for c in chunks:
                        if isinstance(c, dict):
                            text = c.get("text") or c.get("content") or c.get("page_content") or c.get("chunk") or c.get("metadata", {}).get("text")
                            if text:
                                extracted.append(str(text))
                            else:
                                extracted.append(str(c))
                        else:
                            extracted.append(str(c))
                    chunks_text = "\n\n".join(extracted)
                else:
                    chunks_text = str(data)
            else:
                chunks_text = str(data)
            
            logger.info(f"Retrieved chunks for query '{query[:50]}...': {chunks_text[:500]}...")
            return chunks_text
        except Exception as e:
            logger.error(f"Error querying retrieve API at {url}: {e}")
            return ""

