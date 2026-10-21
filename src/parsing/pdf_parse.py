from pathlib import Path
import pymupdf
class PDFParsingError(Exception):
    """Raised when a PDF cannot be parsed or contains no extractable text."""
def parse_pdf(file_path: str | Path) -> dict:
    """
    Extract text page by page from a PDF.
    Returns document metadata and individual page contents.
    """
    path = Path(file_path)
    if not path.is_file():
        raise PDFParsingError("PDF file does not exist.")
    if path.suffix.lower() != ".pdf":
        raise PDFParsingError("Only PDF files can be parsed.")
    try:
        with pymupdf.open(path) as document:
            if not document.is_pdf:
                raise PDFParsingError("The supplied file is not a valid PDF.")
            if document.needs_pass:
                raise PDFParsingError("Password-protected PDFs are not supported.")
            if document.page_count == 0:
                raise PDFParsingError("The PDF contains no pages.")
            pages = []
            for page_number, page in enumerate(document, start=1):
                text = page.get_text("text").strip()
                pages.append({
                    "page_number": page_number,
                    "text": text,
                })
            if not any(page["text"] for page in pages):
                raise PDFParsingError(
                    "The PDF contains no extractable text. "
                    "It may require OCR."
                )
            metadata = document.metadata or {}
            return {
                "filename": path.name,
                "page_count": document.page_count,
                "metadata": {
                    "title": metadata.get("title") or None,
                    "author": metadata.get("author") or None,
                    "subject": metadata.get("subject") or None,
                    "creator": metadata.get("creator") or None,
                },
                "pages": pages,
            }
    except PDFParsingError:
        raise
    except (pymupdf.FileDataError, pymupdf.EmptyFileError) as exc:
        raise PDFParsingError(
        "The PDF is malformed or unreadable."
        ) from exc