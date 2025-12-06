import io

from pypdf import PdfReader


def pdf_bytes_to_text(content: bytes) -> str:
    """
    Convert raw PDF bytes to plain text.
    Reads all pages and joins with newlines.
    """
    with io.BytesIO(content) as buf:
        reader = PdfReader(buf)
        parts: list[str] = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")

    text = "\n".join(parts)
    return text.replace("\r", "\n")
