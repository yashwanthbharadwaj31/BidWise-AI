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
    "NamedTemporaryFile",
    tracked_temporary_file,
)
    monkeypatch.setattr(
    uploader,
    "CHUNK_SIZE",
    10,
)
def raise_unexpected_error(*args, **kwargs):
    raise RuntimeError("Simulated upload failure")

    monkeypatch.setattr(
    uploader,
    "validate_document",
    raise_unexpected_error,
)    
    uploaded_file = BytesIO(b"Simulated PDF content")
    import pytest
    with pytest.raises(RuntimeError, match="Simulated upload failure"):
        uploader.save_uploaded_document(
            uploaded_file,
            "unexpected_error.pdf",
        )
    assert len(created_paths) == 1
    assert not created_paths[0].exists()
