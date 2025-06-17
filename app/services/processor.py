from app.services.llm_service import extract_invoice_data
from app.utils.file_handler import save_json
from app.models.schemas import ExtractedInvoice

def process_raw_text(text: str) -> ExtractedInvoice:
    print("[processor] Sending to LLM...")
    structured = extract_invoice_data(text)

    # Save result to file
    save_json(structured.dict())
    print("[processor] Saved to processed_orders.json")

    return structured
