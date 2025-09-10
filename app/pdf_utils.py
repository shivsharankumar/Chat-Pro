from pypdf import PdfReader
# from typing import list,Optional
from io import BytesIO

def extract_text_from_pdf(pdf_path:str)->str:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ''
    return text

def extract_text_from_pdf_bytes(pdf_bytes:bytes)->str:
    reader = PdfReader(BytesIO(pdf_bytes))
    text = ""