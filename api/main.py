from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from src.ingestion.uploader import save_uploaded_document
app = FastAPI(
    title="BidWise-AI",
    description="Tender and RFP Copilot API",
    version="0.1.0",
)
@app.get("/health")
def health_check():
    """Check whether the API is running."""
    return {"status": "healthy"}
@app.post("/documents/upload")
def upload_document(file: UploadFile = File(...)):
    """Upload and validate a tender PDF."""
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required.",
        )
    try:
        is_valid, message, temporary_path = save_uploaded_document(
            file.file,
            file.filename,
        )
    finally:
        file.file.close()
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=message,
        )
    return {
        "message": message,
        "filename": Path(file.filename).name,
        "status": "validated",
    }
