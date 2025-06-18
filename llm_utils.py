from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from schemas import InvoiceData, PartialInvoiceData
from config import Config
import logging
import json

logger = logging.getLogger(__name__)

def extract_invoice_data(text: str) -> dict:
    """Extract structured invoice data from text or email content"""
    try:
        parser = PydanticOutputParser(pydantic_object=InvoiceData)
        
        prompt = ChatPromptTemplate.from_template(
            """Extract invoice data from the following content. The content may be:
            - Direct invoice text in email body
            - PDF text content
            - Combination of both
            
            Follow these rules:
            1. Extract all available fields
            2. Convert amounts to numbers (remove $, commas)
            3. For missing fields, use null
            4. For manager approval, accept both strings and objects
            
            Schema Instructions:
            {format_instructions}
            
            Content to parse:
            {text}
            
            Return ONLY valid JSON:"""
        )
        
        model = ChatGroq(
            model_name="llama3-70b-8192",
            temperature=0,
            groq_api_key=Config.GROQ_API_KEY
        )
        
        chain = prompt | model | parser
        
        # First attempt with strict parsing
        try:
            result = chain.invoke({
                "text": text,
                "format_instructions": parser.get_format_instructions()
            })
            return result.dict()
        except Exception as e:
            logger.warning(f"Strict parsing failed, trying flexible parsing: {str(e)}")
            return flexible_parse_invoice(text)

    except Exception as e:
        logger.error(f"LLM extraction failed: {str(e)}")
        return {"error": f"Failed to extract invoice data: {str(e)}"}

def flexible_parse_invoice(text: str) -> dict:
    """Fallback parsing with more flexible handling"""
    try:
        # Get raw LLM output
        raw_prompt = """Extract invoice data from this content. 
        Return as JSON with these fields: 
        - po_number, po_date, billing_info, shipping_info, 
        - line_items (description, quantity, unit_price, total), 
        - amounts (subtotal, tax, shipping, total_amount),
        - dates, approval_info, special_instructions
        
        Content:
        {text}
        """
        
        model = ChatGroq(
            model_name="llama3-70b-8192",
            temperature=0,
            groq_api_key=Config.GROQ_API_KEY
        )
        
        raw_output = model.invoke(raw_prompt.format(text=text))
        
        # Extract JSON from output
        json_str = extract_json_string(raw_output.content)
        data = json.loads(json_str)
        
        # Convert to proper schema
        return normalize_invoice_data(data)
    except Exception as e:
        logger.error(f"Flexible parsing failed: {str(e)}")
        return {"error": str(e)}