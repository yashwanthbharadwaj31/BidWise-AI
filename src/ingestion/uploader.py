from pathlib import Path
from tempfile import NamedTemporaryFile
from src.ingestion.validator import validate_document
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024
def save_uploaded_document(file_object, filename: str) -> tuple[bool, str, str | None]:
    """Validate and temporarily save an uploaded PDF."""
    if Path(filename).suffix.lower() != ".pdf":
        return False, "Only PDF documents are allowed.", None
    temporary_path = None
    total_bytes = 0
    try:
        with NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temporary_file:
            temporary_path = temporary_file.name
            while True:
                chunk = file_object.read(CHUNK_SIZE)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > MAX_FILE_SIZE_BYTES:
                    temporary_file.close()
                    Path(temporary_path).unlink(missing_ok=True)
                    return False, "File exceeds the 50 MiB size limit.", None
                temporary_file.write(chunk)
        is_valid, message = validate_document(temporary_path)
        if not is_valid:
            Path(temporary_path).unlink(missing_ok=True)
            return False, message, None
        return (
            True,
            "Document uploaded and validated successfully.",
            temporary_path,
        )
    except Exception:
        if temporary_path:
            Path(temporary_path).unlink(missing_ok=True)
        raise
