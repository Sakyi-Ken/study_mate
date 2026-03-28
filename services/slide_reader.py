import logging
import re
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def _merge_spaced_letters(match: re.Match) -> str:
    """Merge tokens like 'T h i s' into 'This' for cleaner TTS."""
    return re.sub(r"\s+", "", match.group(0))


def clean_text_for_tts(text: str) -> str:
    """Clean common PDF extraction artifacts so speech sounds natural."""
    cleaned = text or ""

    # Remove invisible soft-hyphen artifacts and fix broken line hyphenation.
    cleaned = cleaned.replace("\u00ad", "")
    cleaned = re.sub(r"(\w)-\s+(\w)", r"\1\2", cleaned)

    # Remove long underscore artifacts, but preserve useful identifiers like x_1 or snake_case.
    cleaned = re.sub(r"_{2,}", " ", cleaned)
    cleaned = re.sub(r"(?<![A-Za-z0-9])_(?![A-Za-z0-9])", " ", cleaned)
    cleaned = re.sub(r"(?<![A-Za-z0-9])_(?=[A-Za-z0-9])", " ", cleaned)
    cleaned = re.sub(r"(?<=[A-Za-z0-9])_(?![A-Za-z0-9])", " ", cleaned)

    # Merge words split into single-letter sequences by poor extraction.
    cleaned = re.sub(r"\b(?:[A-Za-z]\s+){2,}[A-Za-z]\b", _merge_spaced_letters, cleaned)

    # Make common operators sound natural in TTS.
    cleaned = cleaned.replace("<=", " less than or equal to ")
    cleaned = cleaned.replace(">=", " greater than or equal to ")
    cleaned = cleaned.replace("!=", " not equal to ")
    cleaned = cleaned.replace("==", " equals ")
    cleaned = cleaned.replace("->", " leads to ")
    cleaned = cleaned.replace("=>", " implies ")
    cleaned = cleaned.replace("=", " equals ")

    # Speak standalone math symbols more clearly.
    cleaned = re.sub(r"\s\+\s", " plus ", cleaned)
    cleaned = re.sub(r"\s-\s", " minus ", cleaned)
    cleaned = re.sub(r"\s\*\s", " times ", cleaned)
    cleaned = re.sub(r"\s/\s", " divided by ", cleaned)

    # Normalize whitespace while preserving paragraph breaks.
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"\n", " ", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)

    return cleaned.strip()


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
            normalized = clean_text_for_tts(text)
            if normalized:
                page_texts.append(normalized)

        return "\n\n".join(page_texts), total_pages
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return "", 0
