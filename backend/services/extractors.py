from __future__ import annotations

import io
from typing import Dict, List

from PIL import Image
import pytesseract
from pdfminer.high_level import extract_text as pdfminer_extract_text
import pypdfium2 as pdfium
from .medical_parser import extract_structured_medical_data


def _ocr_image_bytes(image_bytes: bytes, language: str = "eng") -> str:
	image = Image.open(io.BytesIO(image_bytes))
	# Ensure consistent mode for OCR
	if image.mode not in ("L", "RGB"):
		image = image.convert("RGB")
	text = pytesseract.image_to_string(image, lang=language)
	return text.strip()


def _pdf_bytes_to_pil_images(pdf_bytes: bytes, scale: float = 2.0) -> List[Image.Image]:
	doc = pdfium.PdfDocument(io.BytesIO(pdf_bytes))
	images: List[Image.Image] = []
	for i in range(len(doc)):
		page = doc[i]
		bitmap = page.render(scale=scale).to_pil()
		images.append(bitmap)
	return images


def extract_from_pdf(pdf_bytes: bytes, language: str = "eng") -> Dict[str, object]:
	# Try text-layer extraction first (fast, accurate when available)
	try:
		text_layer = pdfminer_extract_text(io.BytesIO(pdf_bytes)) or ""
	except Exception:
		text_layer = ""

	method = "text-layer"
	num_pages = 0
	try:
		num_pages = len(pdfium.PdfDocument(io.BytesIO(pdf_bytes)))
	except Exception:
		pass

	cleaned = (text_layer or "").strip()

	# If text layer is too small, fallback to OCR per-page
	if len(cleaned) < 20:  # heuristic threshold
		try:
			images = _pdf_bytes_to_pil_images(pdf_bytes)
			ocr_texts: List[str] = []
			for image in images:
				if image.mode not in ("L", "RGB"):
					image = image.convert("RGB")
				ocr_texts.append(pytesseract.image_to_string(image, lang=language).strip())
			cleaned = "\n\n".join(t for t in ocr_texts if t)
			method = "ocr"
			num_pages = len(images)
		except Exception as ocr_exc:
			# If OCR also fails, surface what we have
			if cleaned:
				method = "text-layer"
			else:
				cleaned = f""
				method = f"error: {ocr_exc}"

	# Try to extract structured medical data
	structured_data = extract_structured_medical_data(cleaned)
	
	return {
		"text": cleaned,
		"num_pages": num_pages,
		"method": method,
		"structured_data": structured_data,
	}


def extract_from_image(image_bytes: bytes, language: str = "eng") -> Dict[str, object]:
	try:
		text = _ocr_image_bytes(image_bytes, language=language)
	except Exception as exc:
		text = ""
		method = f"error: {exc}"
	else:
		method = "ocr"

	# Try to extract structured medical data
	structured_data = extract_structured_medical_data(text)
	
	return {
		"text": text,
		"method": method,
		"structured_data": structured_data,
	}
