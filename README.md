## Document Extraction (FastAPI + Streamlit)

End-to-end app to extract text from PDFs and images with accurate fallbacks.

- Backend: FastAPI `/extract` endpoint
- Frontend: Streamlit file uploader UI
- Extraction flow:
  - Try native PDF text layer (pdfminer.six)
  - If text is sparse, OCR pages/images with Tesseract via `pytesseract`

### Prerequisites (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr libtesseract-dev
```

### Setup

```bash
# 1) Create and activate a virtualenv (recommended)
python3 -m venv .venv
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 4) Run Streamlit UI (in a separate terminal)
streamlit run frontend/app.py --server.headless true --server.port 8501
```

Open the UI at http://localhost:8501 and set API base as http://localhost:8000

### API

- `GET /health` → `{ "status": "ok" }`
- `POST /extract` → multipart with `file` field; returns JSON:

```json
{
  "filename": "document.pdf",
  "file_type": "pdf",
  "method": "text-layer | ocr | error:...",
  "num_pages": 3,
  "text": "...extracted text..."
}
```

### Notes

- For PDF scans or images, quality of OCR depends on Tesseract data. To use other languages, make sure language packs are installed (e.g., `tesseract-ocr-chi-sim`) and pass the language in code as needed.
- Heuristic: fallback to OCR if PDF text layer is too short (< 20 chars). Adjust `extract_from_pdf` if desired.
- If running inside Docker or a minimal environment, ensure Tesseract is installed and available in PATH.
