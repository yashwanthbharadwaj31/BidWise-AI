import pymupdf
import pytest
from src.parsing.pdf_parse import PDFParsingError, parse_pdf
def create_pdf(path, page_texts):
    """Create a real PDF fixture with the supplied page text."""
    document = pymupdf.open()
    for text in page_texts:
        page = document.new_page()
        page.insert_text((72, 72), text)
    document.save(path)
    document.close()
    return path
def test_parse_multi_page_pdf_preserves_page_boundaries(tmp_path):
    pdf_path = create_pdf(
        tmp_path / "tender.pdf",
        ["Eligibility requirements", "Submission deadline"],
    )
    result = parse_pdf(pdf_path)
    assert result["filename"] == "tender.pdf"
    assert result["page_count"] == 2
    assert result["pages"] == [
        {"page_number": 1, "text": "Eligibility requirements"},
        {"page_number": 2, "text": "Submission deadline"},
    ]
def test_parse_pdf_returns_metadata(tmp_path):
    pdf_path = tmp_path / "metadata.pdf"
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Tender information")
    document.set_metadata({
        "title": "Public Tender",
        "author": "Procurement Department",
        "subject": "Tender notice",
        "creator": "BidWise-AI test",
    })
    document.save(pdf_path)
    document.close()
    result = parse_pdf(pdf_path)
    assert result["metadata"]["title"] == "Public Tender"
    assert result["metadata"]["author"] == "Procurement Department"
    assert result["metadata"]["subject"] == "Tender notice"
    assert result["metadata"]["creator"] == "BidWise-AI test"
def test_parse_pdf_rejects_missing_file(tmp_path):
    with pytest.raises(PDFParsingError, match="does not exist"):
        parse_pdf(tmp_path / "missing.pdf")
def test_parse_pdf_rejects_wrong_extension(tmp_path):
    file_path = tmp_path / "tender.txt"
    file_path.write_text("Some text", encoding="utf-8")
    with pytest.raises(PDFParsingError, match="Only PDF"):
        parse_pdf(file_path)
def test_parse_pdf_rejects_malformed_pdf(tmp_path):
    file_path = tmp_path / "broken.pdf"
    file_path.write_bytes(b"This is not a valid PDF document")
    with pytest.raises(PDFParsingError, match="malformed or unreadable"):
        parse_pdf(file_path)
def test_parse_pdf_rejects_pdf_without_extractable_text(tmp_path):
    file_path = tmp_path / "image_only.pdf"
    document = pymupdf.open()
    document.new_page()
    document.save(file_path)
    document.close()
    with pytest.raises(
        PDFParsingError,
        match="no extractable text",
    ):
        parse_pdf(file_path)
def test_parse_pdf_rejects_password_protected_pdf(tmp_path):
    file_path = tmp_path / "protected.pdf"
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Confidential tender")
    document.save(
        file_path,
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        owner_pw="owner-secret",
        user_pw="user-secret",
    )
    document.close()
    with pytest.raises(PDFParsingError, match="Password-protected"):
        parse_pdf(file_path)
def test_parse_pdf_preserves_blank_pages(tmp_path):
    pdf_path = tmp_path / "tender_with_blank_page.pdf"
    document = pymupdf.open()
    first_page = document.new_page()
    first_page.insert_text((72, 72), "Eligibility requirements")
    document.new_page()  # Intentionally blank page
    third_page = document.new_page()
    third_page.insert_text((72, 72), "Submission deadline")
    document.save(pdf_path)
    document.close()
    result = parse_pdf(pdf_path)
    assert result["page_count"] == 3
    assert result["pages"] == [
        {"page_number": 1, "text": "Eligibility requirements"},
        {"page_number": 2, "text": ""},
        {"page_number": 3, "text": "Submission deadline"},
    ]
