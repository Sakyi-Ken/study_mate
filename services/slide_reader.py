import logging
import re
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def parse_page_range(caption: str) -> tuple[int | None, int | None, str | None]:
    """Parse caption page range. Supports '2' or '1-3'."""
    raw = (caption or "").strip()
    if not raw:
        return None, None, None

    range_match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", raw)
    if range_match:
        start_page = int(range_match.group(1))
        end_page = int(range_match.group(2))
        if start_page < 1 or end_page < 1 or end_page < start_page:
            return None, None, "Invalid page range. Use values like 1-3."
        return start_page, end_page, None

    single_match = re.fullmatch(r"(\d+)", raw)
    if single_match:
        page = int(single_match.group(1))
        if page < 1:
            return None, None, "Invalid page number. Page numbers start at 1."
        return page, page, None

    return None, None, "Invalid caption format. Use caption '2' or '1-3' for page range."


def extract_text_from_pdf(file_path: str, start_page: int | None = None, end_page: int | None = None) -> tuple[str, int]:
    """Extract readable text from all pages or a selected page range in a PDF file."""
    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)

        from_page = start_page or 1
        to_page = end_page or total_pages

        if from_page < 1 or to_page < 1 or to_page < from_page or from_page > total_pages:
            return "", total_pages

        to_page = min(to_page, total_pages)
        page_texts = []

        for idx in range(from_page - 1, to_page):
            page = reader.pages[idx]
            text = page.extract_text() or ""
            normalized = " ".join(text.split())
            if normalized:
                page_texts.append(normalized)

        return "\n\n".join(page_texts), total_pages
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return "", 0
