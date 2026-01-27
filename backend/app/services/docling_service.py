"""Docling PDF to Markdown conversion service."""

import logging
import threading

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

logger = logging.getLogger("inquiro")

# Module-level cached converter (singleton)
_CONVERTER: DocumentConverter | None = None
_CONVERTER_LOCK = threading.Lock()


def _get_converter() -> DocumentConverter:
    """Get or create the cached DocumentConverter instance (thread-safe)."""
    global _CONVERTER  # pylint: disable=global-statement
    if _CONVERTER is None:
        with _CONVERTER_LOCK:
            # Double-check after acquiring lock
            if _CONVERTER is None:
                pdf_options = PdfPipelineOptions(
                    do_ocr=False,
                    do_table_structure=False,
                )
                _CONVERTER = DocumentConverter(
                    format_options={
                        InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options),
                    }
                )
                logger.info("Initialized Docling converter with fast dev configuration")
    return _CONVERTER


class DoclingConverter:
    """Wrapper around Docling for PDF to Markdown conversion."""


    @staticmethod
    def convert_pdf_to_markdown(path: str) -> str:
        """
         Convert a PDF at the given path or URL to a markdown string.

        Uses a cached converter instance to avoid reloading model weights.
        Thread-safe for parallel worker usage.
        """
        try:
            converter = _get_converter()
            result = converter.convert(path)
            return result.document.export_to_markdown()
        except Exception as e:
            logger.error("Docling conversion failed: %s", e)
            raise ValueError(f"Failed to convert PDF: {e}") from e
