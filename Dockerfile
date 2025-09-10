# syntax=docker/dockerfile:1
FROM python:3.11-slim

# System deps: tesseract for OCR
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY frontend ./frontend

EXPOSE 8000 8501

# Default: run both backend and streamlit using simple process manager
CMD sh -c "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py --server.headless true --server.port 8501 --server.address 0.0.0.0"
