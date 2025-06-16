import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import os

def extract_text_from_pdf(filepath: str) -> str:
    text = ""
    try:
        doc = fitz.open(filepath)
        for page in doc:
            text += page.get_text()
        if text.strip():
            return text
    except Exception:
        pass

    images = convert_from_path(filepath)
    for img in images:
        text += pytesseract.image_to_string(img)

    return text