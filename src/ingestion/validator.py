from pathlib import Path
ALLOWED_EXTENSION = ".pdf"
MAX_FILE_SIZE_MB = 50
def validate_document(file_path: str) -> tuple[bool, str]:
    """Validate a tender PDF before ingestion."""
    path = Path(file_path)
    if not path.exists():
        return False, "File does not exist."
    if not path.is_file():
        return False, "The provided path is not a file."
    if path.suffix.lower() != ALLOWED_EXTENSION:
        return False, "Only PDF documents are allowed."
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, "File exceeds the 50 MB size limit."
    # Inspect the file header instead of trusting its extension.
    with path.open("rb") as file:
        header = file.read(1024)
    if b"%PDF-" not in header:
        return False, "File does not appear to be a valid PDF."
    return True, "Document passed validation."

def test_rejects_file_with_pdf_extension_but_invalid_content(tmp_path: Path):
    fake_pdf = tmp_path / "fake_tender.pdf"
    fake_pdf.write_text("This is not a real PDF.", encoding="utf-8")
    is_valid, message = validate_document(str(fake_pdf))
    assert is_valid is False
    assert message == "File does not appear to be a valid PDF."