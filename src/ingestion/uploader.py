from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4
from src.ingestion.validator import validate_document
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024
PROJECT_ROOT = Path(__file__).resolve().parents[2]
STORAGE_DIRECTORY = PROJECT_ROOT / "documents" / "tenders"
def save_uploaded_document(
    file_object,
    filename: str,
) -> tuple[bool, str, str | None]:
    """Validate and permanently save an uploaded PDF."""
    if Path(filename).suffix.lower() != ".pdf":
        return False, "Only PDF documents are allowed.", None
    temporary_path = None
    try:
        STORAGE_DIRECTORY.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            mode="wb",
            suffix=".pdf",
            prefix=".upload-",
            dir=STORAGE_DIRECTORY,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            total_bytes = 0
            while True:
                chunk = file_object.read(CHUNK_SIZE)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > MAX_FILE_SIZE_BYTES:
                    return (
                        False,
                        "File exceeds the 50 MiB size limit.",
                        None,
                    )
                temporary_file.write(chunk)
        is_valid, message = validate_document(str(temporary_path))
        if not is_valid:
            return False, message, None
        stored_path = STORAGE_DIRECTORY / f"{uuid4().hex}.pdf"
        temporary_path.replace(stored_path)
        temporary_path = None
        return (
            True,
            "Document uploaded and validated successfully.",
            str(stored_path),
        )
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
