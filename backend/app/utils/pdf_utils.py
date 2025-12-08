import io

from pypdf import PdfReader


def pdf_bytes_to_text(content: bytes) -> str:
    """
    Convert raw PDF bytes to plain text.
    Reads all pages and joins with newlines.

    Args:
        content: Raw PDF file bytes.

    Returns:
        Extracted text with normalized line endings (\\r replaced with \\n).

    Raises:
        pypdf.errors.PdfReadError: If the PDF is invalid or corrupted.
    """
    with io.BytesIO(content) as buf:
        reader = PdfReader(buf)
        parts: list[str] = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")

    text = "\n".join(parts)
    return text.replace("\r", "\n")
