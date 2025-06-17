from fastapi import FastAPI, Request
from app.services.processor import process_raw_text
from app.models.schemas import ExtractedInvoice

app = FastAPI()

@app.post("/webhook")
async def receive_mailparser_data(req: Request) -> ExtractedInvoice:
    body = await req.json()
    print("[main] Received webhook")

    email_text = body.get("email_body", "")
    pdf_text = body.get("pdf_text", "")
    combined_text = f"{email_text}\n\n{pdf_text}"

    print("[main] Combined text length:", len(combined_text))
    structured_data = process_raw_text(combined_text)

    return structured_data
