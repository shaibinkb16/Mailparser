from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from schemas import InvoiceData
from config import Config
import logging
import json
import re
from typing import Optional

logger = logging.getLogger(__name__)

def extract_invoice_data(text: str) -> dict:
    """Robust invoice data extraction with multiple fallback strategies"""
    # First try standard parsing
    result = try_standard_parsing(text)
    if result and not result.get("error"):
        return result
    
    # If standard fails, try simplified parsing
    logger.warning("Standard parsing failed, trying simplified approach")
    simplified_result = try_simplified_parsing(text)
    if simplified_result and not simplified_result.get("error"):
        return simplified_result
    
    # Final fallback - direct JSON generation
    logger.warning("Simplified parsing failed, trying direct JSON generation")
    return try_direct_json_generation(text)

def try_standard_parsing(text: str) -> Optional[dict]:
    """Attempt parsing with full schema validation"""
    try:
        parser = PydanticOutputParser(pydantic_object=InvoiceData)
        prompt = ChatPromptTemplate.from_template(
            """Extract invoice data exactly matching this schema:
            {format_instructions}
            
            Rules:
            1. Return ONLY valid JSON
            2. Convert amounts to numbers (remove $, commas)
            3. For missing fields, use null
            
            Content:
            {text}
            
            JSON Output:"""
        )
        
        model = ChatGroq(
            model_name="llama3-70b-8192",
            temperature=0,
            groq_api_key=Config.GROQ_API_KEY
        )
        
        chain = prompt | model | parser
        result = chain.invoke({
            "text": text,
            "format_instructions": parser.get_format_instructions()
        })
        return result.dict()
    except Exception as e:
        logger.warning(f"Standard parsing failed: {str(e)}")
        return None

def try_simplified_parsing(text: str) -> Optional[dict]:
    """Simpler parsing with fewer required fields"""
    try:
        prompt = """Extract key invoice fields from this content:
        - po_number
        - po_date
        - billing_info (company, address)
        - line_items (description, quantity, unit_price)
        - total_amount
        - payment_terms
        
        Return as JSON. Convert amounts to numbers. Use null for missing fields.
        
        Content:
        {text}
        
        JSON Output:"""
        
        model = ChatGroq(
            model_name="llama3-70b-8192",
            temperature=0,
            groq_api_key=Config.GROQ_API_KEY
        )
        
        raw_output = model.invoke(prompt.format(text=text))
        json_data = extract_and_validate_json(raw_output.content)
        return normalize_invoice_data(json_data)
    except Exception as e:
        logger.warning(f"Simplified parsing failed: {str(e)}")
        return None

def try_direct_json_generation(text: str) -> dict:
    """Final fallback with maximum flexibility"""
    try:
        prompt = """Extract any invoice data you can find in this content.
        Return as simple JSON with whatever fields you can identify.
        Focus on:
        - Purchase order numbers
        - Dates
        - Company names
        - Item descriptions
        - Quantities
        - Amounts
        
        Content:
        {text}
        
        JSON Output:"""
        
        model = ChatGroq(
            model_name="llama3-70b-8192",
            temperature=0,
            groq_api_key=Config.GROQ_API_KEY
        )
        
        raw_output = model.invoke(prompt.format(text=text))
        json_data = extract_and_validate_json(raw_output.content)
        return normalize_invoice_data(json_data)
    except Exception as e:
        logger.error(f"All extraction methods failed: {str(e)}")
        return {
            "error": "Failed to extract invoice data",
            "details": str(e),
            "input_sample": text[:500] + "..." if len(text) > 500 else text
        }

def extract_and_validate_json(text: str) -> dict:
    """Safely extract and validate JSON from LLM output"""
    try:
        # Find JSON portion
        start = text.find('{')
        end = text.rfind('}') + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON found in response")
        
        json_str = text[start:end]
        data = json.loads(json_str)
        
        # Basic validation
        if not isinstance(data, dict):
            raise ValueError("Expected JSON object")
        
        print(f"Extracted JSON: {json_str}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {str(e)}")
        raise ValueError(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        logger.error(f"JSON extraction failed: {str(e)}")
        raise

def normalize_invoice_data(data: dict) -> dict:
    """Normalize invoice data structure"""
    # Ensure required top-level fields exist
    if 'line_items' not in data:
        data['line_items'] = []
    
    # Normalize amounts
    amount_fields = ['subtotal', 'tax', 'shipping', 'total_amount']
    for field in amount_fields:
        if field in data and isinstance(data[field], str):
            data[field] = float(re.sub(r'[^\d.]', '', data[field]))
    
    # Normalize line items
    for item in data.get('line_items', []):
        for amt_field in ['unit_price', 'total']:
            if amt_field in item and isinstance(item[amt_field], str):
                item[amt_field] = float(re.sub(r'[^\d.]', '', item[amt_field]))
    print(data)
    return data