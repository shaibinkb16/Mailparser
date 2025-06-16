import json
from datetime import datetime

def save_json(data, filename="processed_orders.json"):
    entry = data.copy()
    entry["timestamp"] = datetime.now().isoformat()
    try:
        with open(filename, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"Failed to write to file: {e}")

# Directory: app/services/processor.py
from app.services.llm_service import extract_po_from_text
from app.services.pdf_extractor import extract_text_from_pdf
from app.utils.file_handler import save_json
from app.models.schemas import ProcessedOrder
from typing import Dict, Any
from fastapi import UploadFile
import tempfile

async def process_purchase_order(metadata: Dict[str, str], body: str, attachment: UploadFile = None):
    if body and ("PO" in body.upper() or "purchase order" in body.lower()):
        po_data = extract_po_from_text(body)
        po_data.update({"source": "email_body", "email_metadata": metadata})
        save_json(po_data)
        return ProcessedOrder(**po_data)

    if attachment:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await attachment.read()
            tmp.write(content)
            pdf_text = extract_text_from_pdf(tmp.name)
            po_data = extract_po_from_text(pdf_text)
            po_data.update({
                "source": "pdf_attachment",
                "email_metadata": metadata,
                "filename": attachment.filename
            })
            save_json(po_data)
            return ProcessedOrder(**po_data)

    return ProcessedOrder(
        email_metadata=metadata,
        source="none",
        status="No PO details found",
        note="Neither body nor PDF had usable content"
    )
