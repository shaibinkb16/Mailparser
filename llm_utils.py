from langchain_groq import ChatGroq
from config import Config
import json
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

def extract_invoice_data(text: str) -> dict:
    """Extract invoice data using a flexible, schema-free LLM approach"""
    return try_flexible_llm_extraction(text)

def try_flexible_llm_extraction(text: str) -> dict:
    """Let LLM extract any relevant invoice fields in JSON format"""
    try:
        prompt = f"""
You will be given raw invoice text. Extract all relevant data as flexible JSON.
Focus on:
- PO number, Invoice number
- Invoice date, PO date, due date, delivery date
- Buyer and Seller company info
- Line items (description, quantity, price, total)
- Totals: subtotal, tax, shipping, total
- Payment terms, notes

Rules:
1. Return ONLY valid JSON
2. Omit missing fields or set as null
3. Remove any currency symbols or commas from numeric values

Content:
{text}

JSON Output:"""

        model = ChatGroq(
            model_name="llama3-70b-8192",
            temperature=0,
            groq_api_key=Config.GROQ_API_KEY
        )

        response = model.invoke(prompt)
        json_data = extract_and_validate_json(response.content)
        return normalize_invoice_data(json_data)

    except Exception as e:
        logger.error(f"Flexible LLM extraction failed: {str(e)}")
        return {
            "error": "Failed to extract invoice data",
            "details": str(e),
            "input_sample": text[:500] + "..." if len(text) > 500 else text
        }

def extract_and_validate_json(text: str) -> dict:
    """Safely extract and validate JSON from LLM output"""
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON found in response")

        json_str = text[start:end]
        data = json.loads(json_str)

        if not isinstance(data, dict):
            raise ValueError("Expected JSON object")

        print(f"Extracted JSON: {json_str}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"JSON extraction failed: {str(e)}")
        raise

def normalize_invoice_data(data: dict) -> dict:
    """Normalize amounts inside invoice data"""
    amount_fields = ['subtotal', 'tax', 'shipping', 'total', 'total_amount']
    for field in amount_fields:
        if field in data and isinstance(data[field], str):
            data[field] = float(re.sub(r'[^\d.]', '', data[field]))

    if 'line_items' in data:
        for item in data['line_items']:
            for amt_field in ['unit_price', 'total', 'price']:
                if amt_field in item and isinstance(item[amt_field], str):
                    item[amt_field] = float(re.sub(r'[^\d.]', '', item[amt_field]))
    return data
