from pathlib import Path
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
from src.ingestion.validator import validate_document

def save_uploaded_document(file_object, filename: str) -> tuple[bool, str, str | None]:
    """Validate an uploaded tender PDF and save it to a temporary file."""
    if Path(filename).suffix.lower() != ".pdf":
        return False, "Only PDF documents are allowed.", None
    with NamedTemporaryFile(
        suffix=".pdf",
        delete=False,
    ) as temporary_file:
        try:
            copyfileobj(file_object, temporary_file)
            temporary_path = temporary_file.name
            is_valid, message = validate_document(temporary_path)
            if not is_valid:
                Path(temporary_path).unlink(missing_ok=True)
                return False, message, None
            return True, "Document uploaded and validated successfully.", temporary_path
        except Exception:
            Path(temporary_file.name).unlink(missing_ok=True)
            raise
