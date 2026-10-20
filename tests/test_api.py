from io import BytesIO
from pathlib import Path
from fastapi.testclient import TestClient
import api.main as api_main
import src.ingestion.uploader as uploader
client = TestClient(api_main.app, raise_server_exceptions=False)
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
def test_upload_valid_pdf(monkeypatch, tmp_path):
    storage_dir = tmp_path / "tenders"
    monkeypatch.setattr(uploader, "STORAGE_DIRECTORY", storage_dir)
    pdf_content = b"%PDF-1.7\nsample tender content"
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "tender.pdf",
                BytesIO(pdf_content),
                "application/pdf",
            )
        },
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["filename"] == "tender.pdf"
    assert response_data["status"] == "validated"
    assert response_data["stored_filename"].endswith(".pdf")
    stored_file = storage_dir / response_data["stored_filename"]
    assert stored_file.exists()
    assert stored_file.read_bytes() == pdf_content
def test_upload_rejects_non_pdf(monkeypatch, tmp_path):
    storage_dir = tmp_path / "tenders"
    monkeypatch.setattr(uploader, "STORAGE_DIRECTORY", storage_dir)
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "tender.txt",
                BytesIO(b"not a PDF"),
                "text/plain",
            )
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF documents are allowed."
    assert not list(storage_dir.glob("*")) if storage_dir.exists() else True
def test_upload_rejects_invalid_pdf_content(monkeypatch, tmp_path):
    storage_dir = tmp_path / "tenders"
    monkeypatch.setattr(uploader, "STORAGE_DIRECTORY", storage_dir)
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "fake.pdf",
                BytesIO(b"This is not a real PDF"),
                "application/pdf",
            )
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "File does not appear to be a valid PDF."
    )
    assert not list(storage_dir.iterdir())
def test_upload_rejects_oversized_pdf(monkeypatch, tmp_path):
    storage_dir = tmp_path / "tenders"
    monkeypatch.setattr(uploader, "STORAGE_DIRECTORY", storage_dir)
    oversized_content = b"%PDF-1.7\n" + (
        b"x" * (50 * 1024 * 1024)
    )
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "oversized.pdf",
                BytesIO(oversized_content),
                "application/pdf",
            )
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "File exceeds the 50 MiB size limit."
    )
    assert not list(storage_dir.iterdir())
def test_upload_handles_unexpected_storage_error(monkeypatch, tmp_path):
    storage_dir = tmp_path / "tenders"
    monkeypatch.setattr(uploader, "STORAGE_DIRECTORY", storage_dir)
    def raise_unexpected_error(*args, **kwargs):
        raise RuntimeError("Simulated upload failure")
    monkeypatch.setattr(
        api_main,
        "save_uploaded_document",
        raise_unexpected_error,
    )
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "tender.pdf",
                BytesIO(b"%PDF-1.7\nsample content"),
                "application/pdf",
            )
        },
    )
    assert response.status_code == 500


