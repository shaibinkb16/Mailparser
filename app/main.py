from fastapi import FastAPI, UploadFile, File, Form
from app.services.processor import process_purchase_order
from app.models.schemas import ProcessedOrder
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/webhook", response_model=ProcessedOrder)
async def webhook_endpoint(
    email_body: str = Form(None),
    email_from: str = Form(...),
    email_to: str = Form(...),
    email_subject: str = Form(...),
    file: UploadFile = File(None)
):
    logger.info("Received webhook request")
    metadata = {
        "from": email_from,
        "to": email_to,
        "subject": email_subject
    }
    result = await process_purchase_order(metadata, email_body, file)
    return result