from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, Optional
import os

from backend.services.extractors import extract_from_pdf, extract_from_image


app = FastAPI(title="Document Extraction API", version="0.1.0")

# CORS for local Streamlit dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MedicalData(BaseModel):
    name: Optional[str] = None
    age: Optional[str] = None
    history: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    surgeries: Optional[str] = None
    notes: Optional[str] = None
    is_medical_document: bool = False


class ExtractResponse(BaseModel):
    filename: str
    file_type: str
    method: str
    num_pages: int | None = None
    text: str
    structured_data: Optional[MedicalData] = None


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
async def extract(file: UploadFile = File(...)) -> ExtractResponse:
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        content_type = (file.content_type or "").lower()
        extension = os.path.splitext(file.filename or "")[1].lower()

        is_pdf = content_type == "application/pdf" or extension == ".pdf"
        is_image = content_type.startswith("image/") or extension in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}

        if is_pdf:
            result = extract_from_pdf(content)
            structured_data = result.get("structured_data", {})
            medical_data = MedicalData(**structured_data) if structured_data else None
            
            return ExtractResponse(
                filename=file.filename or "uploaded.pdf",
                file_type="pdf",
                method=result.get("method", "unknown"),
                num_pages=result.get("num_pages"),
                text=result.get("text", ""),
                structured_data=medical_data,
            )
        elif is_image:
            result = extract_from_image(content)
            structured_data = result.get("structured_data", {})
            medical_data = MedicalData(**structured_data) if structured_data else None
            
            return ExtractResponse(
                filename=file.filename or "uploaded-image",
                file_type="image",
                method=result.get("method", "ocr"),
                num_pages=None,
                text=result.get("text", ""),
                structured_data=medical_data,
            )
        else:
            raise HTTPException(status_code=415, detail=f"Unsupported file type: {content_type or extension}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {exc}")
