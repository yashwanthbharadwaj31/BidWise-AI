from pathlib import Path
from src.ingestion.validator import validate_document
def test_accepts_pdf_within_size_limit(tmp_path: Path):
    pdf_file = tmp_path / "tender.pdf"
    pdf_file.write_bytes(b"%PDF-1.7\nsample PDF content")
    is_valid, message = validate_document(str(pdf_file))
    assert is_valid is True
    assert message == "Document passed validation."
def test_rejects_non_pdf_file(tmp_path: Path):
    text_file = tmp_path / "tender.txt"
    text_file.write_text("sample text", encoding="utf-8")
    is_valid, message = validate_document(str(text_file))
    assert is_valid is False
    assert message == "Only PDF documents are allowed."
def test_rejects_missing_file(tmp_path: Path):
    missing_file = tmp_path / "missing.pdf"
    is_valid, message = validate_document(str(missing_file))
    assert is_valid is False
    assert message == "File does not exist."
def test_rejects_file_over_size_limit(tmp_path: Path):
    oversized_file = tmp_path / "large_tender.pdf"
    with oversized_file.open("wb") as file:
        file.truncate(50 * 1024 * 1024 + 1)
    is_valid, message = validate_document(str(oversized_file))
    assert is_valid is False
    assert message == "File exceeds the 50 MB size limit."
def test_rejects_file_with_pdf_extension_but_invalid_content(tmp_path: Path):
    fake_pdf = tmp_path / "fake_tender.pdf"
    fake_pdf.write_text("This is not a real PDF.", encoding="utf-8")
    is_valid, message = validate_document(str(fake_pdf))
    assert is_valid is False
    assert message == "File does not appear to be a valid PDF."