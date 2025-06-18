from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from schemas import InvoiceData
from config import Config
import logging

logger = logging.getLogger(__name__)

def extract_invoice_data(text: str) -> dict:
    """Extract structured invoice data using LLM"""
    try:
        if not getattr(Config, 'GROQ_API_KEY', None):
            logger.error("GROQ_API_KEY is missing in Config.")
            return {"error": "GROQ API key is not configured."}

        parser = PydanticOutputParser(pydantic_object=InvoiceData)
        
    prompt = ChatPromptTemplate.from_template(
    "You are an intelligent document parser that extracts invoice data accurately. "
    "Your job is to extract every possible field from the invoice text below.\n\n"
    "➡️ You must return ONLY a single valid JSON object that strictly matches the Pydantic schema provided.\n"
    "➡️ Return all fields, even if they are missing — use null or empty values as needed.\n"
    "➡️ Do NOT include any markdown, commentary, or code blocks — just the raw JSON object.\n\n"
    "### Schema:\n{format_instructions}\n\n"
    "### Invoice Text:\n{text}\n\n"
    "### Instructions:\n"
    "- If any numeric value has symbols (like ₹ or $), remove them.\n"
    "- If fields like subtotal, tax, or shipping are not found, set to 0.0.\n"
    "- For fields that do not appear at all, use null.\n"
    "- For line_items, include item_code, description, quantity, unit_price, and total.\n"
    "- Maintain correct field names and JSON structure at all times.\n"
)
        
        model = ChatGroq(
            model_name="llama3-70b-8192",
            temperature=0,
            groq_api_key=Config.GROQ_API_KEY
        )
        
        chain = prompt | model | parser
        
        raw_chain = prompt | model
        raw_output = raw_chain.invoke({
            "text": text,
            "format_instructions": parser.get_format_instructions()
        })
        logger.debug(f"RAW LLM OUTPUT: {raw_output}")
        
        result = None
        try:
            result = parser.invoke(raw_output)
        except Exception as parse_err:
            logger.error(f"Parsing failed: {parse_err}")
            return {
                "error": f"Failed to parse LLM output: {parse_err}",
                "llm_output": str(raw_output)
            }
            
        if result is None:
            logger.error("LLM output is None after parsing.")
            return {
                "error": "LLM output is None after parsing.",
                "llm_output": str(raw_output)
            }
            
        return result.dict()
        
    except Exception as e:
        logger.error(f"LLM extraction failed: {str(e)}")
        return {"error": f"Failed to extract invoice data: {str(e)}"}