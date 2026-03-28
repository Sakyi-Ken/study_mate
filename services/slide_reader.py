import logging
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """Extracts readable text from all pages in a PDF file."""
    try:
        reader = PdfReader(file_path)
        page_texts = []

        for page in reader.pages:
            text = page.extract_text() or ""
            normalized = " ".join(text.split())
            if normalized:
                page_texts.append(normalized)

        return "\n\n".join(page_texts)
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""
