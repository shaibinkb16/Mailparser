import os
import openai  # This works with Groq's OpenAI-compatible API
from app.models.schemas import ExtractedInvoice
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("GROQ_API_KEY")
openai.api_base = "https://api.groq.com/openai/v1"  # Groq API endpoint

def extract_invoice_data(raw_text: str) -> ExtractedInvoice:
    prompt = f"""
You will be given a raw email and/or purchase order text. Extract the following structured data in JSON format:
- invoice_number
- invoice_date
- due_date
- payment_terms
- vendor (company name)
- buyer (company name)
- contact_email
- contact_phone
- shipping_address
- billing_address
- items: list of item_code, description, quantity, unit_price, line_total
- subtotal, tax, shipping_charges, total
- delivery_date
- budget_code
- approval_manager

Raw Text:
\"\"\"{raw_text}\"\"\"
    """
    response = openai.ChatCompletion.create(
        model="mixtral-8x7b-32768",  # Example Groq model
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts structured invoice data."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    json_data = response.choices[0].message['content']
    print("[llm_service] LLM output received")
    return ExtractedInvoice.parse_raw(json_data)
