from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from schemas import InvoiceData, PartialInvoiceData
from config import Config
import logging
import json
import re

logger = logging.getLogger(__name__)

def extract_invoice_data(text: str) -> dict:
    """Extract structured invoice data with comprehensive error handling"""
    try:
        # First attempt with strict parsing
        strict_result = try_strict_parsing(text)
        if strict_result and "error" not in strict_result:
            return strict_result
        
        # Fallback to flexible parsing
        logger.warning("Strict parsing failed, attempting flexible parsing")
        flexible_result = try_flexible_parsing(text)
        if flexible_result and "error" not in flexible_result:
            return flexible_result
        
        # Final fallback to manual extraction
        logger.warning("Flexible parsing failed, attempting manual extraction")
        return manual_extraction(text)
        
    except Exception as e:
        logger.error(f"Complete extraction failure: {str(e)}")
        return {
            "error": "Failed to extract invoice data",
            "details": str(e),
            "input_sample": text[:500] + "..." if len(text) > 500 else text
        }

def try_strict_parsing(text: str) -> dict:
    """Attempt strict schema validation"""
    try:
        parser = PydanticOutputParser(pydantic_object=InvoiceData)
        prompt = get_strict_prompt(parser)
        model = get_groq_model()
        chain = prompt | model | parser
        result = chain.invoke({
            "text": text,
            "format_instructions": parser.get_format_instructions()
        })
        return result.dict()
    except Exception as e:
        logger.warning(f"Strict parsing attempt failed: {str(e)}")
        return {"error": str(e)}

def try_flexible_parsing(text: str) -> dict:
    """Attempt with more flexible schema"""
    try:
        parser = PydanticOutputParser(pydantic_object=PartialInvoiceData)
        prompt = get_flexible_prompt(parser)
        model = get_groq_model()
        chain = prompt | model | parser
        result = chain.invoke({
            "text": text,
            "format_instructions": parser.get_format_instructions()
        })
        return result.dict()
    except Exception as e:
        logger.warning(f"Flexible parsing attempt failed: {str(e)}")
        return {"error": str(e)}

def manual_extraction(text: str) -> dict:
    """Manual extraction as last resort"""
    try:
        model = get_groq_model()
        prompt = """Extract invoice data from this text. Return JSON with these fields:
        - po_number, po_date
        - billing_info (company, address)
        - shipping_info (company, address)
        - line_items (description, quantity, unit_price, total)
        - amounts (subtotal, tax, shipping, total_amount)
        - payment_terms, delivery_date
        
        Return ONLY the JSON object. If a field is missing, use null.
        
        Text:
        {text}"""
        
        raw_output = model.invoke(prompt.format(text=text))
        
        # Handle case where LLM returns None
        if raw_output.content is None:
            raise ValueError("LLM returned None")
            
        # Extract JSON from output
        json_str = extract_json_from_text(raw_output.content)
        data = json.loads(json_str)
        
        # Normalize data
        return normalize_invoice_data(data)
    except Exception as e:
        logger.error(f"Manual extraction failed: {str(e)}")
        raise

def get_strict_prompt(parser):
    return ChatPromptTemplate.from_template(
        """Extract invoice data EXACTLY matching this schema:
        {format_instructions}
        
        Rules:
        1. Return ONLY valid JSON
        2. Convert amounts to numbers
        3. For missing fields, use null
        
        Text:
        {text}
        
        JSON Output:"""
    )

def get_flexible_prompt(parser):
    return ChatPromptTemplate.from_template(
        """Extract invoice data with partial matching:
        {format_instructions}
        
        Rules:
        1. Include whatever fields you can extract
        2. Convert amounts to numbers
        3. For missing fields, use null
        
        Text:
        {text}
        
        JSON Output:"""
    )

def get_groq_model():
    return ChatGroq(
        model_name="llama3-70b-8192",
        temperature=0,
        groq_api_key=Config.GROQ_API_KEY
    )

def extract_json_from_text(text: str) -> str:
    """Robust JSON extraction from LLM output"""
    if text is None:
        raise ValueError("No text to parse")
    
    # Find JSON boundaries
    start = text.find('{')
    end = text.rfind('}') + 1
    
    if start == -1 or end == 0:
        raise ValueError("No JSON found in text")
    
    json_str = text[start:end]
    
    # Basic validation
    if not json_str.startswith('{') or not json_str.endswith('}'):
        raise ValueError("Invalid JSON structure")
    
    return json_str

def normalize_invoice_data(data: dict) -> dict:
    """Normalize invoice data to standard format"""
    if not isinstance(data, dict):
        raise ValueError("Input data must be a dictionary")
    
    # Convert amounts
    amount_fields = ['subtotal', 'tax', 'shipping', 'total_amount']
    for field in amount_fields:
        if field in data and isinstance(data[field], str):
            data[field] = float(re.sub(r'[^\d.]', '', data[field]))
    
    # Normalize line items
    if 'line_items' in data:
        if not isinstance(data['line_items'], list):
            data['line_items'] = []
        for item in data['line_items']:
            if isinstance(item, dict):
                for amt_field in ['unit_price', 'total']:
                    if amt_field in item and isinstance(item[amt_field], str):
                        item[amt_field] = float(re.sub(r'[^\d.]', '', item[amt_field]))
    
    return data