import os
import openai
import logging
import json  # <-- Add this import

openai.api_key = os.getenv("xai-e67Jfw2e94IOR8r6Wte1TFbBoBYWaRSMiEpkZktybOJhDuKPLueoYEKnPEV7ZTpRwjR5uoi4egDTrCnZ")
logger = logging.getLogger(__name__)

def extract_po_from_text(text: str):
    try:
        response = openai.ChatCompletion.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "Extract purchase order details from given text."},
                {"role": "user", "content": text}
            ]
        )
        content = response["choices"][0]["message"]["content"]
        return json.loads(content)  # SAFER than eval!
    except Exception as e:
        logger.error(f"LLM extraction failed: {str(e)}")
        return {
            "po_number": None,
            "customer": None,
            "items": [],
            "total": None,
            "status": "LLM Error",
            "note": str(e)
        }
