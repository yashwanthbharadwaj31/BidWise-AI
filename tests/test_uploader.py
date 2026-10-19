from io import BytesIO
from pathlib import Path
import pytest
import src.ingestion.uploader as uploader
def test_rejects_invalid_pdf_and_cleans_up_temporary_file(monkeypatch):
    created_paths = []
    original_named_temporary_file = uploader.NamedTemporaryFile
    def tracked_temporary_file(*args, **kwargs):
        temporary_file = original_named_temporary_file(*args, **kwargs)
        created_paths.append(Path(temporary_file.name))
        return temporary_file
    monkeypatch.setattr(
        uploader,
        "NamedTemporaryFile",
        tracked_temporary_file,
    )
    uploaded_file = BytesIO(b"This is not a real PDF")
    is_valid, message, temporary_path = uploader.save_uploaded_document(
        uploaded_file,
        "invalid_test.pdf",
    )
    assert is_valid is False
    assert message == "File does not appear to be a valid PDF."
    assert temporary_path is None
    assert len(created_paths) == 1
    assert not created_paths[0].exists()
def test_cleans_up_temporary_file_when_unexpected_error_occurs(monkeypatch):
    created_paths = []
    original_named_temporary_file = uploader.NamedTemporaryFile
    def tracked_temporary_file(*args, **kwargs):
        temporary_file = original_named_temporary_file(*args, **kwargs)
        created_paths.append(Path(temporary_file.name))
        return temporary_file
    def raise_unexpected_error(*args, **kwargs):
        raise RuntimeError("Simulated upload failure")
    monkeypatch.setattr(
        uploader,
        "NamedTemporaryFile",
        tracked_temporary_file,
    )
    monkeypatch.setattr(
        uploader,
        "validate_document",
        raise_unexpected_error,
    )
    uploaded_file = BytesIO(b"Simulated PDF content")
    with pytest.raises(RuntimeError, match="Simulated upload failure"):
        uploader.save_uploaded_document(
            uploaded_file,
            "unexpected_error.pdf",
        )
    assert len(created_paths) == 1
    assert not created_paths[0].exists()
def test_valid_pdf_is_stored_permanently(monkeypatch, tmp_path):
    storage_dir = tmp_path / "tenders"
    monkeypatch.setattr(uploader, "STORAGE_DIRECTORY", storage_dir)
    uploaded_file = BytesIO(b"%PDF-1.7\nsample PDF content")
    is_valid, message, stored_path = uploader.save_uploaded_document(
        uploaded_file,
        "tender.pdf",
    )
    assert is_valid is True
    assert stored_path is not None
    saved_file = Path(stored_path)
    assert saved_file.exists()
    assert saved_file.parent == storage_dir
    assert saved_file.suffix == ".pdf"
    assert saved_file.read_bytes() == b"%PDF-1.7\nsample PDF content"
def test_duplicate_filenames_do_not_overwrite(monkeypatch, tmp_path):
    storage_dir = tmp_path / "tenders"
    monkeypatch.setattr(uploader, "STORAGE_DIRECTORY", storage_dir)
    first_content = b"%PDF-1.7\nfirst tender"
    second_content = b"%PDF-1.7\nsecond tender"
    first_result = uploader.save_uploaded_document(
        BytesIO(first_content),
        "tender.pdf",
    )
    second_result = uploader.save_uploaded_document(
        BytesIO(second_content),
        "tender.pdf",
    )
    assert first_result[0] is True
    assert second_result[0] is True
    first_path = Path(first_result[2])
    second_path = Path(second_result[2])
    assert first_path != second_path
    assert first_path.read_bytes() == first_content
    assert second_path.read_bytes() == second_content
    assert len(list(storage_dir.glob("*.pdf"))) == 2
